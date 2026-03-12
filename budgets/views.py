from __future__ import annotations

import csv
import io
import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import BudgetCategoryForm, BudgetForm, ProfileForm, RegisterForm
from .models import Budget, BudgetCategory


@login_required
def dashboard(request):
    budgets_qs = Budget.objects.filter(user=request.user)
    current_budget = budgets_qs.first()

    # Budget creation (creates a new historical record each submit)
    if request.method == "POST" and request.POST.get("action") == "budget":
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, "Budget saved.")
            if budget.total_expenses > budget.salary:
                messages.error(request, "Alert: Your total expenses exceed your salary.")
            return redirect("dashboard")
    else:
        form = BudgetForm()

    # Category add
    cat_form = BudgetCategoryForm(prefix="cat")
    if request.method == "POST" and request.POST.get("action") == "category":
        if not current_budget:
            messages.error(request, "Create a budget first, then add categories.")
            return redirect("dashboard")
        cat_form = BudgetCategoryForm(request.POST, prefix="cat")
        if cat_form.is_valid():
            category = cat_form.save(commit=False)
            category.budget = current_budget
            category.save()
            messages.success(request, "Category saved.")
            return redirect("dashboard")

    allocation = current_budget.allocation() if current_budget else None

    allocation_for_js = None
    categories_js = None
    if allocation and current_budget:
        allocation_for_js = {
            "savings": float(allocation["savings"]),
            "needs": float(allocation["needs"]),
            "wants": float(allocation["wants"]),
            "needs_breakdown": {k: float(v) for k, v in allocation["needs_breakdown"].items()},
            "wants_breakdown": {k: float(v) for k, v in allocation["wants_breakdown"].items()},
        }
        categories_js = [
            {"name": c.name, "percentage": float(c.percentage), "kind": c.kind}
            for c in current_budget.categories.all()
        ]

    # Category percentage warnings (sum > 100 per bucket)
    for kind in ["needs", "wants"]:
        total_pct = current_budget.categories.filter(kind=kind).aggregate(total=Sum("percentage"))["total"] if current_budget else 0
        if total_pct and total_pct > 100:
            messages.warning(request, f"{kind.title()} categories exceed 100% of the bucket.")

    monthly_trends = Budget.monthly_trends_for_user(request.user)
    history = budgets_qs[1:6]  # show last 5 previous budgets

    context = {
        "form": form,
        "cat_form": cat_form,
        "budget": current_budget,
        "history": history,
        "allocation": allocation,
        "allocation_json": json.dumps(allocation_for_js) if allocation_for_js else None,
        "categories_json": json.dumps(categories_js) if categories_js else None,
        "monthly_trends_json": json.dumps(monthly_trends) if monthly_trends else None,
    }
    return render(request, "budgets/dashboard.html", context)


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
            )
            messages.success(request, "Account created. You are now logged in.")
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


@login_required
def category_delete(request, pk):
    category = get_object_or_404(BudgetCategory, pk=pk, budget__user=request.user)
    category.delete()
    messages.success(request, "Category removed.")
    return redirect("dashboard")


@login_required
def history(request):
    budgets = Budget.objects.filter(user=request.user)
    return render(request, "budgets/history.html", {"budgets": budgets})


@login_required
def profile(request):
    from .models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(request, "budgets/profile.html", {"form": form})


@login_required
def export_csv(request, pk=None):
    budget = _get_budget_or_latest(request.user, pk)
    if not budget:
        messages.error(request, "No budget to export.")
        return redirect("dashboard")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="budget_{budget.id}.csv"'
    writer = csv.writer(response)
    writer.writerow(["Budget ID", budget.id])
    writer.writerow(["Created", budget.created_at])
    writer.writerow(["Salary", budget.salary])
    writer.writerow(["Housing", budget.housing])
    writer.writerow(["Food", budget.food])
    writer.writerow(["Transport", budget.transport])
    writer.writerow(["Other Expenses", budget.other_expenses])
    writer.writerow(["Savings Goal", budget.savings_goal])
    writer.writerow(["Total Expenses", budget.total_expenses])
    writer.writerow(["Remaining Balance", budget.remaining_balance])
    allocation = budget.allocation()
    writer.writerow(["Savings (20%)", allocation["savings"]])
    writer.writerow(["Needs (50%)", allocation["needs"]])
    writer.writerow(["Wants (30%)", allocation["wants"]])
    writer.writerow([])
    writer.writerow(["Needs Breakdown"])
    for k, v in allocation["needs_breakdown"].items():
        writer.writerow([k, v])
    writer.writerow([])
    writer.writerow(["Wants Breakdown"])
    for k, v in allocation["wants_breakdown"].items():
        writer.writerow([k, v])
    return response


@login_required
def export_pdf(request, pk=None):
    budget = _get_budget_or_latest(request.user, pk)
    if not budget:
        messages.error(request, "No budget to export.")
        return redirect("dashboard")
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        messages.error(request, "PDF export requires reportlab. Install via 'pip install reportlab'.")
        return redirect("dashboard")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    text = p.beginText(40, 750)
    text.textLine(f"Budget #{budget.id} ({budget.created_at:%Y-%m-%d})")
    text.textLine("")
    text.textLine(f"Salary: {budget.salary}")
    text.textLine(f"Housing: {budget.housing}")
    text.textLine(f"Food: {budget.food}")
    text.textLine(f"Transport: {budget.transport}")
    text.textLine(f"Other Expenses: {budget.other_expenses}")
    text.textLine(f"Savings Goal: {budget.savings_goal}")
    text.textLine(f"Total Expenses: {budget.total_expenses}")
    text.textLine(f"Remaining: {budget.remaining_balance}")
    text.textLine("")
    alloc = budget.allocation()
    text.textLine("Allocations (50/30/20):")
    text.textLine(f"  Savings: {alloc['savings']}")
    text.textLine(f"  Needs: {alloc['needs']}")
    text.textLine(f"  Wants: {alloc['wants']}")
    text.textLine("")
    text.textLine("Needs breakdown:")
    for k, v in alloc["needs_breakdown"].items():
        text.textLine(f"  {k}: {v}")
    text.textLine("")
    text.textLine("Wants breakdown:")
    for k, v in alloc["wants_breakdown"].items():
        text.textLine(f"  {k}: {v}")
    p.drawText(text)
    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=\"budget_{budget.id}.pdf\"'
    return response


def _get_budget_or_latest(user, pk):
    if pk:
        return get_object_or_404(Budget, pk=pk, user=user)
    return Budget.objects.filter(user=user).first()
