from __future__ import annotations

from decimal import Decimal
from django.conf import settings
from django.db import models


class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    housing = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    food = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
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
        """Returns main buckets and breakdowns using 50/30/20 guideline."""
        salary = self.salary
        savings = (salary * Decimal("0.20")).quantize(Decimal("0.01"))
        needs = (salary * Decimal("0.50")).quantize(Decimal("0.01"))
        wants = (salary * Decimal("0.30")).quantize(Decimal("0.01"))

        needs_breakdown = {
            "Rent": (needs * Decimal("0.49")).quantize(Decimal("0.01")),
            "Fare": (needs * Decimal("0.12")).quantize(Decimal("0.01")),
            "Utilities": (needs * Decimal("0.06")).quantize(Decimal("0.01")),
            "Debt": (needs * Decimal("0.07")).quantize(Decimal("0.01")),
            "Groceries": (needs * Decimal("0.15")).quantize(Decimal("0.01")),
            "Personal care": (needs * Decimal("0.05")).quantize(Decimal("0.01")),
            "Gas": (needs * Decimal("0.06")).quantize(Decimal("0.01")),
        }

        wants_breakdown = {
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
