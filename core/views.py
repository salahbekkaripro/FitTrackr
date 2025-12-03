from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required

from .form import CustomerUserCreationForm, OnboardingForm
from .models import Goal

def home(request):
    """Page d'accueil FitTrackR."""
    return render(request, "core/home.html")



def signup_view(request):
    if request.method == "POST":  # l’utilisateur a cliqué sur “Envoyer”
        form = CustomerUserCreationForm(request.POST)  # on charge les données envoyées
        if form.is_valid():  # on vérifie que tout est ok (mots de passe identiques, etc.)
            user = form.save()  # on crée l’utilisateur en base
            auth_login(request, user)  # connexion automatique pour accéder à l’onboarding
            # réinitialise le flag d'onboarding pour ce nouveau compte
            request.session["onboarding_completed"] = False
            messages.success(request, "Compte créé, connecte-toi !")  # message de confirmation
            return redirect("onboarding")  # on envoie vers la page de connexion
    else:
        form = CustomerUserCreationForm()  # premier passage (GET) : formulaire vide
    return render(request, "core/signup.html", {"form": form})  # on affiche la page avec le formulaire

def connexion(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, "core/login.html")


@login_required
def onboarding(request):
    user = request.user

    # considère le profil “rempli” si ces trois champs sont présents
    profile_done = all([user.age, user.weight, user.size])

    if request.method == "POST":
        form = OnboardingForm(request.POST, instance=user)
        goal_type = request.POST.get("goal")
        if form.is_valid():
            form.save()
            if goal_type:
                target_val = form.cleaned_data.get("weight_goal") or 0
                unit_val = "kg" if form.cleaned_data.get("weight_goal") else ""
                Goal.objects.create(
                    user=user,
                    goal_type=goal_type,
                    target_value=target_val,
                    unit=unit_val,
                    status="pending",
                    weight_goal=form.cleaned_data.get("weight_goal"),
                )
            request.session["onboarding_completed"] = True
            return redirect("home")
    else:
        form = OnboardingForm(instance=user)

    return render(
        request,
        "core/onboarding.html",
        {"form": form, "profile_done": profile_done, "user": user},
    )




@login_required
def logout_view(request):
    logout(request)
    return redirect("login")  # ou une autre page
