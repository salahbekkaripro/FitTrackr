from django.db import models
from django.conf import settings

# =========================================================
#   EXERCISES
# =========================================================
class Exercise(models.Model):
    name = models.CharField(max_length=100)
    primary_muscle = models.CharField(max_length=50)
    equipment = models.CharField(max_length=50, blank=True, null=True)
    difficulty = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# =========================================================
#   PROGRAMS
# =========================================================
LEVEL_CHOICES = [
    ("Débutant", "Débutant"),
    ("Intermédiaire", "Intermédiaire"),
    ("Avancé", "Avancé"),
]

GOAL_CHOICES = [
    ("Prise de masse", "Prise de masse"),
    ("Perte de poids", "Perte de poids"),
    ("Cardio", "Cardio"),
    ("Force", "Force"),
    ("Hypertrophie", "Hypertrophie"),
]

class Program(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="Débutant")
    goal_type = models.CharField(max_length=50, choices=GOAL_CHOICES, default="Non défini")
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_programs"
    )

    def __str__(self):
        return self.name


class ProgramExercise(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="program_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.RESTRICT, related_name="program_exercises")
    day_index = models.PositiveIntegerField()
    order_index = models.PositiveIntegerField()
    target_sets = models.PositiveIntegerField()
    target_reps = models.PositiveIntegerField()
    target_weight_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.program.name} - Day {self.day_index} - {self.exercise.name}"


# =========================================================
#   WORKOUTS
# =========================================================
class Workout(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workouts"
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="workouts"
    )
    workout_date = models.DateField()
    workout_time = models.TimeField(null=True, blank=True)  # heure de début
    duration_minutes = models.PositiveIntegerField(default=60)
    title = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    duration = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class WorkoutSet(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="sets")
    exercise = models.ForeignKey(Exercise, on_delete=models.RESTRICT, related_name="exercise_sets")
    set_number = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    rpe = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    rest_seconds = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.exercise.name} - Set {self.set_number}"
