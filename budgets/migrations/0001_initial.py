# Generated manually to create Budget model initial table.
from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Budget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("salary", models.DecimalField(decimal_places=2, max_digits=12)),
                ("housing", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("food", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("transport", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("other_expenses", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="budgets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
