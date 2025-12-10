from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CustomerUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")


class OnboardingForm(forms.ModelForm):
    weight_goal = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "control"}),
        label="Objectif poids (kg)",
    )

    class Meta:
        model = User
        fields = ["age", "weight", "size"]
        widgets = {
            "age": forms.NumberInput(attrs={"class": "control"}),
            "weight": forms.NumberInput(attrs={"class": "control"}),
            "size": forms.NumberInput(attrs={"class": "control"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ["age", "weight", "size"]:
            self.fields[name].required = False


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "age", "weight", "size"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "control"}),
            "email": forms.EmailInput(attrs={"class": "control"}),
            "age": forms.NumberInput(attrs={"class": "control"}),
            "weight": forms.NumberInput(attrs={"class": "control"}),
            "size": forms.NumberInput(attrs={"class": "control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ["age", "weight", "size"]:
            self.fields[name].required = False


class AdminUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "role", "subscription", "age", "weight", "size"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "control"}),
            "email": forms.EmailInput(attrs={"class": "control"}),
            "role": forms.Select(attrs={"class": "control"}),
            "subscription": forms.Select(attrs={"class": "control"}),
            "age": forms.NumberInput(attrs={"class": "control"}),
            "weight": forms.NumberInput(attrs={"class": "control"}),
            "size": forms.NumberInput(attrs={"class": "control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ["age", "weight", "size", "subscription"]:
            self.fields[name].required = False
