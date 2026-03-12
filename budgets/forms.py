from django import forms
from .models import Budget, BudgetCategory, UserProfile


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["salary", "housing", "food", "transport", "other_expenses", "savings_goal"]
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


class BudgetCategoryForm(forms.ModelForm):
    class Meta:
        model = BudgetCategory
        fields = ["name", "percentage", "kind"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "maxlength": 100}),
            "percentage": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "100"}),
            "kind": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_percentage(self):
        pct = self.cleaned_data["percentage"]
        if pct < 0 or pct > 100:
            raise forms.ValidationError("Percentage must be between 0 and 100.")
        return pct


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = UserProfile
        fields = ["preferred_currency", "savings_goal"]
        widgets = {
            "preferred_currency": forms.TextInput(attrs={"class": "form-control"}),
            "savings_goal": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["email"].initial = user.email
            self.user = user

    def save(self, commit=True):
        profile = super().save(commit=False)
        if hasattr(self, "user"):
            self.user.email = self.cleaned_data["email"]
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile
