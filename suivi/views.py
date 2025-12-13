from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from datetime import date, timedelta
import csv
from django.http import HttpResponse

from programs.models import Workout as ProgramWorkout, WorkoutSet as ProgramWorkoutSet

# ==========================================
# DASHBOARD
# ==========================================
@login_required
def dashboard(request):
    user = request.user
    today = date.today()
    start_week = today - timedelta(days=today.weekday())
    start_period = today - timedelta(weeks=4)

    # Récupérer les workouts de l'utilisateur sur les 4 dernières semaines
    workouts = ProgramWorkout.objects.filter(user=user, workout_date__gte=start_period)

    # Stats hebdomadaires
    weekly_summary = workouts.filter(workout_date__gte=start_week)\
        .aggregate(nb_sessions=Count('id'), total_minutes=Sum('duration_minutes'))

    # Progression par semaine
    progression = []
    for i in range(4):
        week_start = start_period + timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        week_workouts = workouts.filter(workout_date__range=[week_start, week_end])
        progression.append({
            "week": week_start.strftime("%d %b"),
            "sessions": week_workouts.count(),
            "minutes": week_workouts.aggregate(total=Sum('duration_minutes'))['total'] or 0
        })

    return render(request, "suivi/dashboard.html", {
        "weekly_summary": weekly_summary,
        "progression": progression
    })


# ==========================================
# WORKOUT JOURNAL
# ==========================================
@login_required
def workout_journal(request):
    user = request.user
    program_filter = request.GET.get("program", "")

    workouts = ProgramWorkout.objects.filter(user=user)
    if program_filter:
        workouts = workouts.filter(program__name__icontains=program_filter)

    return render(request, "suivi/journal.html", {
        "workouts": workouts,
        "filter_program": program_filter
    })


# ==========================================
# EXPORT CSV
# ==========================================
@login_required
def export_workout_csv(request):
    user = request.user
    workouts = ProgramWorkout.objects.filter(user=user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="workouts.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Titre', 'Programme', 'Durée (min)', 'Notes'])

    for w in workouts:
        writer.writerow([
            w.workout_date,
            w.title,
            w.program.name if w.program else '',
            w.duration_minutes,
            w.notes
        ])

    return response


# ==========================================
# PROGRESSION / GRAPH
# ==========================================
@login_required
def progression(request):
    user = request.user
    workouts = ProgramWorkout.objects.filter(user=user).order_by('workout_date')

    labels = []
    session_counts = []
    durations = []
    total_weight = []  # charge totale par semaine

    if workouts.exists():
        first_date = workouts.first().workout_date
        last_date = workouts.last().workout_date
        current = first_date

        while current <= last_date:
            week_end = current + timedelta(days=6)
            week_workouts = workouts.filter(workout_date__range=[current, week_end])

            # Nombre de séances et durée totale
            labels.append(current.strftime("%d %b"))
            session_counts.append(week_workouts.count())
            durations.append(week_workouts.aggregate(total=Sum('duration_minutes'))['total'] or 0)

            # Charge totale (somme des reps * poids pour les sets de la semaine)
            sets = ProgramWorkoutSet.objects.filter(workout__in=week_workouts)
            charge = sum((s.reps * (s.weight_kg or 0)) for s in sets)
            total_weight.append(charge)

            current += timedelta(weeks=1)

    return render(request, "suivi/progression.html", {
        "labels": labels,
        "session_counts": session_counts,
        "durations": durations,
        "total_weight": total_weight,
    })
# ==========================================
# BADGES
# ==========================================
@login_required
def user_badges(request):
    user = request.user
    today = date.today()
    start_period = today - timedelta(weeks=4)
    
    recent_workouts = ProgramWorkout.objects.filter(user=user, workout_date__gte=start_period)
    
    # Badge régularité : 3 séances/semaine sur 4 dernières semaines
    weekly_counts = [
        recent_workouts.filter(workout_date__gte=start_period + timedelta(weeks=i),
                               workout_date__lte=start_period + timedelta(weeks=i, days=6)).count()
        for i in range(4)
    ]
    regularity_badge = all(c >= 3 for c in weekly_counts)

    # Badge volume : 5 heures cumulées sur 4 semaines
    total_minutes = recent_workouts.aggregate(total=Sum('duration_minutes'))['total'] or 0
    volume_badge = total_minutes >= 5 * 60  # 5 heures

    return render(request, "suivi/badges.html", {
        "regularity_badge": regularity_badge,
        "volume_badge": volume_badge,
        "total_minutes": total_minutes
    })