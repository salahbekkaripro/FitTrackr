from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.connexion, name="connexion"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path("logout/",views.logout_view,name="logout"),
    path("subscriptions/", views.subscriptions_view, name="subscriptions"),
    path("profile/", views.profile_view, name="profile"),
    path("admin/users/", views.admin_users_list, name="admin_users_list"),
    path("admin/users/<int:user_id>/edit/", views.admin_user_edit, name="admin_user_edit"),
]
