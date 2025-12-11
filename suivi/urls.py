from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('journal/', views.workout_journal, name='workout_journal'),
    path('journal/export/', views.export_workout_csv, name='export_workout_csv'),
    path('badges/', views.user_badges, name='user_badges'),
    path('progression/', views.progression, name='progression'),
]