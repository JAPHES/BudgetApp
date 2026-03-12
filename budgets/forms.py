from django import forms
from .models import Budget


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["salary", "housing", "food", "transport", "other_expenses"]
        widgets = {
            field: forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"})
            for field in fields
        }

    def clean_salary(self):
        salary = self.cleaned_data["salary"]
        if salary <= 0:
            raise forms.ValidationError("Salary must be greater than zero.")
        return salary

    def clean(self):
        cleaned = super().clean()
        for field in ["housing", "food", "transport", "other_expenses"]:
            value = cleaned.get(field)
            if value is not None and value < 0:
                self.add_error(field, "Value cannot be negative.")
        return cleaned


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return cleaned
