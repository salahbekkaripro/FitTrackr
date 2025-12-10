from datetime import timedelta, date
from calendar import monthrange

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from .form import CustomerUserCreationForm, OnboardingForm, ProfileForm, AdminUserForm
from .models import Goal, Subscription, SubscriptionEngagement, User

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
def subscriptions_view(request):
    user = request.user
    today = timezone.now().date()

    def compute_end_date(start_date: date, months: int) -> date:
        """Retourne la date de fin en ajoutant un nombre de mois à la date de départ."""
        if not months:
            return start_date
        month_index = start_date.month - 1 + months
        year = start_date.year + month_index // 12
        month = month_index % 12 + 1
        day = min(start_date.day, monthrange(year, month)[1])
        return date(year, month, day)

    subscriptions = Subscription.objects.order_by("level_rank", "price_monthly")
    active_engagement = (
        SubscriptionEngagement.objects.filter(
            user=user,
            end_date__gte=today,
            commitment_months__gt=0,
        )
        .select_related("subscription")
        .order_by("-end_date")
        .first()
    )

    current_subscription = user.subscription or (
        active_engagement.subscription if active_engagement else None
    )

    error_message = None
    info_message = None

    if request.method == "POST":
        selected_id = request.POST.get("subscription_id")
        if not selected_id:
            error_message = "Choisis un abonnement pour continuer."
        else:
            chosen = get_object_or_404(Subscription, pk=selected_id)
            is_same_subscription = (
                current_subscription.id == chosen.id if current_subscription else False
            )

            if active_engagement and not is_same_subscription:
                active_price = active_engagement.subscription.price_monthly
                if chosen.price_monthly <= active_price:
                    error_message = (
                        f"Tu es engagé sur {active_engagement.subscription.name} "
                        f"jusqu'au {active_engagement.end_date.strftime('%d/%m/%Y')}. "
                        "Tu peux changer maintenant uniquement vers une offre plus chère."
                    )
                else:
                    user.subscription = chosen
                    user.save(update_fields=["subscription"])

                    months = chosen.commitment_months or 0
                    end_date = compute_end_date(today, months)

                    SubscriptionEngagement.objects.create(
                        user=user,
                        subscription=chosen,
                        end_date=end_date,
                        commitment_months=months,
                    )

                    query = f"?changed=1&plan={chosen.code}"
                    return redirect(reverse("subscriptions") + query)
            elif is_same_subscription:
                info_message = "Tu es déjà sur cet abonnement."
            else:
                user.subscription = chosen
                user.save(update_fields=["subscription"])

                months = chosen.commitment_months or 0
                end_date = compute_end_date(today, months)

                SubscriptionEngagement.objects.create(
                    user=user,
                    subscription=chosen,
                    end_date=end_date,
                    commitment_months=months,
                )

                query = f"?changed=1&plan={chosen.code}"
                return redirect(reverse("subscriptions") + query)

    subscription_changed = request.GET.get("changed") == "1"
    selected_code = request.GET.get("plan")

    return render(
        request,
        "core/subscriptions.html",
        {
            "subscriptions": subscriptions,
            "active_engagement": active_engagement,
            "error_message": error_message,
            "info_message": info_message,
            "subscription_changed": subscription_changed,
            "selected_code": selected_code,
            "current_subscription": current_subscription,
        },
    )



@login_required
def profile_view(request):
    user = request.user
    updated = request.GET.get("updated") == "1"

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect(reverse("profile") + "?updated=1")
    else:
        form = ProfileForm(instance=user)

    return render(
        request,
        "core/profile.html",
        {
            "form": form,
            "user_profile": user,
            "updated": updated,
        },
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("connexion")  # renvoie vers la page de connexion


@login_required
def admin_users_list(request):
    if not getattr(request.user, "is_admin_role", False):
        raise PermissionDenied("Accès réservé aux admins.")

    search_query = request.GET.get("q", "").strip()
    users_qs = User.objects.select_related("subscription")

    if search_query:
        users_qs = users_qs.filter(
            Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(role__icontains=search_query)
        )

    users = users_qs.order_by("username")
    total_count = User.objects.count()
    results_count = users_qs.count()

    return render(
        request,
        "core/admin_users.html",
        {
            "users": users,
            "search_query": search_query,
            "total_count": total_count,
            "results_count": results_count,
        },
    )


@login_required
def admin_user_edit(request, user_id):
    if not getattr(request.user, "is_admin_role", False):
        raise PermissionDenied("Accès réservé aux admins.")

    target_user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        form = AdminUserForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur mis à jour.")
            return redirect(reverse("admin_user_edit", args=[target_user.id]))
    else:
        form = AdminUserForm(instance=target_user)

    return render(
        request,
        "core/admin_user_edit.html",
        {
            "form": form,
            "target_user": target_user,
        },
    )
