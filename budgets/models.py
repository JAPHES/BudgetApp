from __future__ import annotations

from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone


class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    housing = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    food = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    savings_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Budget for {self.user} on {self.created_at:%Y-%m-%d}"

    @property
    def total_expenses(self) -> Decimal:
        return sum(
            [
                self.housing,
                self.food,
                self.transport,
                self.other_expenses,
            ],
            Decimal("0.00"),
        )

    @property
    def remaining_balance(self) -> Decimal:
        return self.salary - self.total_expenses

    def allocation(self) -> dict:
        """
        Returns main buckets and breakdowns using 50/30/20 guideline or user-defined categories.
        Needs/Wants breakdown will follow custom categories if any exist for that budget.
        """
        salary = self.salary
        savings = (salary * Decimal("0.20")).quantize(Decimal("0.01"))
        needs = (salary * Decimal("0.50")).quantize(Decimal("0.01"))
        wants = (salary * Decimal("0.30")).quantize(Decimal("0.01"))

        needs_breakdown = self._category_breakdown("needs", needs) or {
            "Rent": (needs * Decimal("0.49")).quantize(Decimal("0.01")),
            "Fare": (needs * Decimal("0.12")).quantize(Decimal("0.01")),
            "Utilities": (needs * Decimal("0.06")).quantize(Decimal("0.01")),
            "Debt": (needs * Decimal("0.07")).quantize(Decimal("0.01")),
            "Groceries": (needs * Decimal("0.15")).quantize(Decimal("0.01")),
            "Personal care": (needs * Decimal("0.05")).quantize(Decimal("0.01")),
            "Gas": (needs * Decimal("0.06")).quantize(Decimal("0.01")),
        }

        wants_breakdown = self._category_breakdown("wants", wants) or {
            "Eating Out": (wants * Decimal("0.37")).quantize(Decimal("0.01")),
            "Entertainment": (wants * Decimal("0.40")).quantize(Decimal("0.01")),
            "New Clothing": (wants * Decimal("0.23")).quantize(Decimal("0.01")),
        }

        return {
            "savings": savings,
            "needs": needs,
            "wants": wants,
            "needs_breakdown": needs_breakdown,
            "wants_breakdown": wants_breakdown,
        }

    def _category_breakdown(self, kind: str, bucket_amount: Decimal) -> dict:
        """
        Build a breakdown from custom categories for the given kind ('needs'/'wants').
        Percentages are relative to the bucket; values sum to bucket_amount.
        """
        categories = list(self.categories.filter(kind=kind))
        if not categories:
            return {}
        breakdown = {}
        for cat in categories:
            amount = (bucket_amount * cat.percentage / Decimal("100")).quantize(Decimal("0.01"))
            breakdown[cat.name] = amount
        return breakdown

    def goal_progress_percent(self) -> int:
        """Percentage of savings goal achieved using remaining balance."""
        if self.savings_goal <= 0:
            return 0
        percent = (self.remaining_balance / self.savings_goal) * 100
        return int(max(0, min(percent, 999)))  # clamp

    @staticmethod
    def monthly_trends_for_user(user):
        qs = (
            Budget.objects.filter(user=user)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                total_salary=Sum("salary"),
                housing_sum=Sum("housing"),
                food_sum=Sum("food"),
                transport_sum=Sum("transport"),
                other_sum=Sum("other_expenses"),
            )
            .order_by("month")
        )
        results = []
        for row in qs:
            expenses = sum(
                [
                    row.get("housing_sum") or 0,
                    row.get("food_sum") or 0,
                    row.get("transport_sum") or 0,
                    row.get("other_sum") or 0,
                ]
            )
            savings = (row["total_salary"] - expenses) if row["total_salary"] is not None else 0
            results.append(
                {
                    "month": row["month"].strftime("%Y-%m") if row["month"] else "",
                    "salary": float(row["total_salary"] or 0),
                    "expenses": float(expenses),
                    "savings": float(savings),
                }
            )
        return results


class BudgetCategory(models.Model):
    KIND_CHOICES = (("needs", "Needs"), ("wants", "Wants"))
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage of its bucket (0-100)")
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)

    class Meta:
        ordering = ["kind", "name"]

    def __str__(self):
        return f"{self.name} ({self.kind})"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    preferred_currency = models.CharField(max_length=8, default="USD")
    savings_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Profile for {self.user.username}"
