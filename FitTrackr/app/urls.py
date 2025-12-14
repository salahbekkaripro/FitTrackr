from django.urls import path

from . import views


urlpatterns = [
    # Core & auth
    path("", views.home, name="home"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.connexion, name="connexion"),
    path("logout/", views.logout_view, name="logout"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path("subscriptions/", views.subscriptions_view, name="subscriptions"),
    path("profile/", views.profile_view, name="profile"),
    path("admin/users/", views.admin_users_list, name="admin_users_list"),
    path("admin/users/<int:user_id>/edit/", views.admin_user_edit, name="admin_user_edit"),

    # Programs / workouts
    path("programs/exercises/", views.exercise_list, name="exercise_list"),
    path("programs/exercises/create/", views.create_exercise, name="create_exercise"),
    path("programs/workouts/", views.workout_list, name="workout_list"),
    path("programs/workouts/create/", views.create_workout, name="create_workout"),
    path("programs/workouts/<int:workout_id>/", views.workout_detail, name="workout_detail"),
    path("programs/workouts/<int:workout_id>/edit/", views.edit_workout, name="edit_workout"),
    path("programs/workouts/<int:workout_id>/delete/", views.delete_workout, name="delete_workout"),
    path("programs/", views.program_list, name="program_list"),
    path("programs/create/", views.create_program, name="create_program"),
    path("programs/<int:program_id>/", views.program_detail, name="program_detail"),
    path("programs/<int:program_id>/edit/", views.edit_program, name="edit_program"),
    path("programs/<int:program_id>/delete/", views.delete_program, name="delete_program"),
    path("programs/<int:program_id>/add_exercise/", views.add_exercise_to_program, name="add_exercise_to_program"),

    # Shop
    path("shop/", views.product_list, name="shop"),
    path("shop/product/<int:pk>/", views.product_detail, name="product_detail"),
    path("shop/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("shop/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path("shop/cart/", views.view_cart, name="cart"),
    path("shop/orders/", views.order_history, name="order_history"),
    path("shop/checkout/", views.checkout, name="checkout"),

    # Suivi
    path("suivi/dashboard/", views.dashboard, name="dashboard"),
    path("suivi/journal/", views.workout_journal, name="workout_journal"),
    path("suivi/journal/export/", views.export_workout_csv, name="export_workout_csv"),
    path("suivi/badges/", views.user_badges, name="user_badges"),
    path("suivi/progression/", views.progression, name="progression"),
]
