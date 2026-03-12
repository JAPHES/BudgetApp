# Generated migration for enhanced budget features.
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("budgets", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="budget",
            name="savings_goal",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("preferred_currency", models.CharField(default="USD", max_length=8)),
                ("savings_goal", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BudgetCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("percentage", models.DecimalField(decimal_places=2, help_text="Percentage of its bucket (0-100)", max_digits=5)),
                ("kind", models.CharField(choices=[("needs", "Needs"), ("wants", "Wants")], max_length=10)),
                (
                    "budget",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="categories", to="budgets.budget"),
                ),
            ],
            options={"ordering": ["kind", "name"]},
        ),
    ]
