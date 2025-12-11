from django.shortcuts import render
from core.models import Workout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from datetime import date, timedelta
import csv
from django.http import HttpResponse
from core.models import Workout, UserBadge, Badge

@login_required
def dashboard(request):
    user = request.user
    today = date.today()
    start_week = today - timedelta(days=today.weekday())
    start_period = today - timedelta(weeks=4)  # dernière 4 semaines

    workouts = Workout.objects.filter(user=user, workout_date__gte=start_period)

    # Récapitulatif hebdo
    weekly_summary = workouts.filter(workout_date__gte=start_week)\
        .aggregate(nb_sessions=Count('id'), total_minutes=Sum('duration_minutes'))

    # Progression par semaine sur 4 semaines
    progression = []
    for i in range(4):
        week_start = start_period + timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        week_data = workouts.filter(workout_date__range=[week_start, week_end])
        progression.append({
            "week": week_start.strftime("%d %b"),
            "sessions": week_data.count(),
            "minutes": week_data.aggregate(total=Sum('duration_minutes'))['total'] or 0
        })

    return render(request, "suivi/dashboard.html", {
        "weekly_summary": weekly_summary,
        "progression": progression
    })


@login_required
def workout_journal(request):
    user = request.user
    workout_type_filter = request.GET.get("type", "")
    workouts = Workout.objects.filter(user=user)
    if workout_type_filter:
        workouts = workouts.filter(workout_type__iexact=workout_type_filter)
    return render(request, "suivi/journal.html", {"workouts": workouts, "filter_type": workout_type_filter})


@login_required
def export_workout_csv(request):
    user = request.user
    workouts = Workout.objects.filter(user=user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="workouts.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Titre', 'Type', 'Durée (min)', 'Notes'])
    for w in workouts:
        writer.writerow([w.workout_date, w.title, w.workout_type, w.duration_minutes, w.notes])

    return response


@login_required
def user_badges(request):
    user = request.user
    workouts = Workout.objects.filter(user=user)

    # Badge régularité : 3 séances/semaine sur 4 dernières semaines
    today = date.today()
    start_period = today - timedelta(weeks=4)
    recent_workouts = workouts.filter(workout_date__gte=start_period)
    weekly_counts = [recent_workouts.filter(workout_date__gte=start_period + timedelta(weeks=i),
                                            workout_date__lte=start_period + timedelta(weeks=i, days=6)).count()
                     for i in range(4)]
    regularity_badge = all(c >= 3 for c in weekly_counts)

    # Badge volume : 5 heures cumulées sur 4 semaines
    total_minutes = recent_workouts.aggregate(total=Sum('duration_minutes'))['total'] or 0
    volume_badge = total_minutes >= 5 * 60  # 5 heures

    return render(request, "suivi/badges.html", {
        "regularity_badge": regularity_badge,
        "volume_badge": volume_badge,
        "total_minutes": total_minutes
    })

@login_required
def progression(request):
    user = request.user
    workouts = Workout.objects.filter(user=user).order_by('workout_date')

    labels = []
    session_counts = []
    durations = []

    # Si l'utilisateur a au moins un entraînement
    if workouts.exists():
        first_date = workouts.first().workout_date
        last_date = workouts.last().workout_date

        current = first_date

        while current <= last_date:
            week_end = current + timedelta(days=6)

            week_workouts = workouts.filter(workout_date__range=[current, week_end])

            labels.append(current.strftime("%d %b"))
            session_counts.append(week_workouts.count())
            durations.append(
                week_workouts.aggregate(total=Sum('duration_minutes'))['total'] or 0
            )

            current += timedelta(weeks=1)

    return render(request, "suivi/progression.html", {
        "labels": labels,
        "session_counts": session_counts,
        "durations": durations,
    })