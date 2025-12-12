from django import forms
from .models import Exercise, Workout, WorkoutSet, Program, ProgramExercise

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'primary_muscle', 'equipment', 'difficulty', 'description']


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['workout_date', 'title', 'notes', 'program', 'duration']
        widgets = {
            'workout_date': forms.DateInput(attrs={'type': 'date'}),
            'workout_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # récupère l'utilisateur passé depuis la vue
        super().__init__(*args, **kwargs)
        if user:
            # Limite les programmes à ceux créés par l'utilisateur connecté
            self.fields['program'].queryset = Program.objects.filter(created_by_user=user)


class WorkoutSetForm(forms.ModelForm):
    class Meta:
        model = WorkoutSet
        fields = ['exercise', 'set_number', 'reps', 'weight_kg', 'rpe', 'rest_seconds']


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'description', 'level', 'goal_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProgramExerciseForm(forms.ModelForm):
    class Meta:
        model = ProgramExercise
        fields = [
            'exercise', 'day_index', 'order_index',
            'target_sets', 'target_reps', 'target_weight_kg'
        ]
