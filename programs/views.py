from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Exercise, Workout, WorkoutSet, Program, ProgramExercise
from .forms import (
    ExerciseForm, WorkoutForm, WorkoutSetForm,
    ProgramForm, ProgramExerciseForm
)

# ----------------------------------------
# EXERCICES
# ----------------------------------------
def exercise_list(request):
    exercises = Exercise.objects.all()
    return render(request, 'programs/exercise_list.html', {'exercises': exercises})

@login_required
def create_exercise(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Exercice créé avec succès !")
            return redirect('exercise_list')
        else:
            messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = ExerciseForm()
    return render(request, 'programs/create_exercise.html', {'form': form})

# ----------------------------------------
# SÉANCES / WORKOUTS
# ----------------------------------------
@login_required
def workout_list(request):
    today = timezone.now().date()
    past_workouts = Workout.objects.filter(user=request.user, workout_date__lt=today).order_by('-workout_date')
    upcoming_workouts = Workout.objects.filter(user=request.user, workout_date__gte=today).order_by('workout_date')
    return render(request, 'programs/workout_list.html', {
        'past_workouts': past_workouts,
        'upcoming_workouts': upcoming_workouts
    })

@login_required
def workout_detail(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if workout.program:
        exercises = workout.program.program_exercises.all().order_by('day_index', 'order_index')
    else:
        exercises = workout.sets.all()
    return render(request, 'programs/workout_detail.html', {
        'workout': workout,
        'exercises': exercises
    })

@login_required
def create_workout(request):
    if request.method == 'POST':
        form = WorkoutForm(request.POST, user=request.user)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            if workout.program:
                for prog_ex in workout.program.program_exercises.all():
                    WorkoutSet.objects.create(
                        workout=workout,
                        exercise=prog_ex.exercise,
                        set_number=1,
                        reps=prog_ex.target_reps,
                        weight_kg=prog_ex.target_weight_kg
                    )
            messages.success(request, "Séance créée avec succès !")
            return redirect('workout_list')
        else:
            messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = WorkoutForm(user=request.user)
    return render(request, 'programs/create_workout.html', {'form': form})

@login_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        form = WorkoutForm(request.POST, instance=workout, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Séance modifiée avec succès !")
            return redirect('workout_list')
        else:
            messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = WorkoutForm(instance=workout, user=request.user)
    return render(request, 'programs/create_workout.html', {'form': form, 'edit': True, 'workout': workout})

@login_required
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        workout.delete()
        messages.success(request, "Séance supprimée !")
        return redirect('workout_list')
    return render(request, 'programs/confirm_delete.html', {'workout': workout})

# ----------------------------------------
# PROGRAMMES
# ----------------------------------------
@login_required
def program_list(request):
    programs = Program.objects.filter(created_by_user=request.user)
    return render(request, 'programs/program_list.html', {'programs': programs})

@login_required
def create_program(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save(commit=False)
            program.created_by_user = request.user
            program.save()
            messages.success(request, "Programme créé avec succès !")
            return redirect('program_list')
        else:
            messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = ProgramForm()
    return render(request, 'programs/create_program.html', {'form': form})

@login_required
def program_detail(request, program_id):
    program = get_object_or_404(Program, id=program_id, created_by_user=request.user)
    exercises = program.program_exercises.all().order_by('day_index', 'order_index')
    return render(request, 'programs/program_detail.html', {'program': program, 'exercises': exercises})

@login_required
def edit_program(request, program_id):
    program = get_object_or_404(Program, id=program_id, created_by_user=request.user)
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, "Programme modifié avec succès !")
            return redirect('program_detail', program_id=program.id)
        else:
            messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = ProgramForm(instance=program)
    return render(request, 'programs/create_program.html', {'form': form, 'edit': True, 'program': program})

@login_required
def delete_program(request, program_id):
    program = get_object_or_404(Program, id=program_id, created_by_user=request.user)
    if request.method == 'POST':
        program.delete()
        messages.success(request, "Programme supprimé !")
        return redirect('program_list')
    return render(request, 'programs/confirm_delete.html', {'program': program})

# ----------------------------------------
# AJOUTER EXERCICE À UN PROGRAMME
# ----------------------------------------
@login_required
def add_exercise_to_program(request, program_id):
    program = get_object_or_404(Program, id=program_id, created_by_user=request.user)
    if request.method == 'POST':
        form = ProgramExerciseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.program = program
            obj.save()
            messages.success(request, "Exercice ajouté au programme !")
            return redirect('program_detail', program_id=program.id)
        else:
            messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = ProgramExerciseForm()
    return render(request, 'programs/add_exercise_to_program.html', {'form': form, 'program': program})
