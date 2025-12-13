from django import forms
from .models import Exercise, Workout, WorkoutSet, Program, ProgramExercise


# ----------------------------------------
# EXERCICES
# ----------------------------------------
class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'primary_muscle', 'equipment', 'difficulty', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


# ----------------------------------------
# SEANCES (WORKOUT)
# ----------------------------------------
class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['workout_date', 'title', 'notes', 'program', 'duration_minutes']
        widgets = {
            'workout_date': forms.DateInput(attrs={'type': 'date'}),
            'duration_minutes': forms.NumberInput(attrs={
                'type': 'number',
                'min': 0,
                'placeholder': 'Durée en minutes'
            }),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['program'].queryset = Program.objects.filter(
                created_by_user=user
            )


# ----------------------------------------
# SERIES D'EXERCICES
# ----------------------------------------
class WorkoutSetForm(forms.ModelForm):
    class Meta:
        model = WorkoutSet
        fields = [
            'exercise',
            'set_number',
            'reps',
            'weight_kg',
            'rpe',
            'rest_seconds'
        ]


# ----------------------------------------
# PROGRAMMES
# ----------------------------------------
class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'description', 'level', 'goal_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


# ----------------------------------------
# EXERCICES DANS UN PROGRAMME
# ----------------------------------------
class ProgramExerciseForm(forms.ModelForm):
    class Meta:
        model = ProgramExercise
        fields = [
            'exercise',
            'day_index',
            'order_index',
            'target_sets',
            'target_reps',
            'target_weight_kg'
        ]
