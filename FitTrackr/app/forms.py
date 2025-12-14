from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Exercise, Program, ProgramExercise, Workout, WorkoutSet, User


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


# ----------------------------------------
# EXERCICES
# ----------------------------------------
class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["name", "primary_muscle", "equipment", "difficulty", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


# ----------------------------------------
# SEANCES (WORKOUT)
# ----------------------------------------
class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ["workout_date", "title", "notes", "program", "duration_minutes"]
        widgets = {
            "workout_date": forms.DateInput(attrs={"type": "date"}),
            "duration_minutes": forms.NumberInput(
                attrs={
                    "type": "number",
                    "min": 0,
                    "placeholder": "Durée en minutes",
                }
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["program"].queryset = Program.objects.filter(
                created_by_user=user
            )


# ----------------------------------------
# SERIES D'EXERCICES
# ----------------------------------------
class WorkoutSetForm(forms.ModelForm):
    class Meta:
        model = WorkoutSet
        fields = [
            "exercise",
            "set_number",
            "reps",
            "weight_kg",
            "rpe",
            "rest_seconds",
        ]


# ----------------------------------------
# PROGRAMMES
# ----------------------------------------
class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ["name", "description", "level", "goal_type"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


# ----------------------------------------
# EXERCICES DANS UN PROGRAMME
# ----------------------------------------
class ProgramExerciseForm(forms.ModelForm):
    class Meta:
        model = ProgramExercise
        fields = [
            "exercise",
            "day_index",
            "order_index",
            "target_sets",
            "target_reps",
            "target_weight_kg",
        ]
