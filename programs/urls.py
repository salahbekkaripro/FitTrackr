from django.urls import path
from . import views

urlpatterns = [
    # Exercices
    path('exercises/', views.exercise_list, name="exercise_list"),
    path('exercises/create/', views.create_exercise, name="create_exercise"),

    # Workouts
    path('workouts/', views.workout_list, name="workout_list"),
    path('workouts/create/', views.create_workout, name="create_workout"),
    path('workouts/<int:workout_id>/', views.workout_detail, name="workout_detail"),

    # Programmes
    path('programs/', views.program_list, name="program_list"),
    path('programs/create/', views.create_program, name="create_program"),
    path('programs/<int:program_id>/', views.program_detail, name="program_detail"),

    # Modifier / supprimer un programme
    path('programs/<int:program_id>/edit/', views.edit_program, name="edit_program"),
    path('programs/<int:program_id>/delete/', views.delete_program, name="delete_program"),

    # Ajouter un exercice à un programme
    path('programs/<int:program_id>/add_exercise/', views.add_exercise_to_program, name="add_exercise_to_program"),

    # Modifier / supprimer une séance
    path('workouts/<int:workout_id>/edit/', views.edit_workout, name="edit_workout"),
    path('workouts/<int:workout_id>/delete/', views.delete_workout, name="delete_workout"),

]
