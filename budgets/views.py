from __future__ import annotations

import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from .forms import BudgetForm, RegisterForm
from .models import Budget


@login_required
def dashboard(request):
    budget = Budget.objects.filter(user=request.user).first()

    if request.method == "POST":
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, "Budget saved.")
            return redirect("dashboard")
    else:
        form = BudgetForm(instance=budget)

    allocation = budget.allocation() if budget else None

    allocation_for_js = None
    if allocation:
        allocation_for_js = {
            "savings": float(allocation["savings"]),
            "needs": float(allocation["needs"]),
            "wants": float(allocation["wants"]),
            "needs_breakdown": {k: float(v) for k, v in allocation["needs_breakdown"].items()},
            "wants_breakdown": {k: float(v) for k, v in allocation["wants_breakdown"].items()},
        }

    context = {
        "form": form,
        "budget": budget,
        "allocation": allocation,
        "allocation_json": json.dumps(allocation_for_js) if allocation_for_js else None,
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
