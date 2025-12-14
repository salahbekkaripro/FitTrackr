import csv
import uuid
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    AdminUserForm,
    CustomerUserCreationForm,
    OnboardingForm,
    ProfileForm,
    ExerciseForm,
    WorkoutForm,
    WorkoutSetForm,
    ProgramForm,
    ProgramExerciseForm,
)
from .models import (
    Badge,
    CartItem,
    Goal,
    Order,
    OrderItem,
    Payment,
    Product,
    Program,
    ProgramExercise,
    Subscription,
    SubscriptionEngagement,
    User,
    Workout,
    WorkoutSet,
)


def _shop_discount_rate(user):
    subscription_code = getattr(getattr(user, "subscription", None), "code", "")
    if subscription_code == "SUPER_POWER":
        return Decimal("0.20")
    return Decimal("0.00")


def require_subscription(min_level_rank=0, feature_name="cette fonctionnalité"):
    """
    Redirects to subscriptions if user has no plan or an insufficient level.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            subscription = getattr(request.user, "subscription", None)
            if not subscription:
                messages.warning(
                    request,
                    f"Prends un abonnement pour accéder à {feature_name}.",
                )
                return redirect("subscriptions")
            if subscription.level_rank < min_level_rank:
                messages.warning(
                    request,
                    f"Ton offre actuelle ne permet pas d'accéder à {feature_name}. Passe sur une offre supérieure.",
                )
                return redirect("subscriptions")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


# ==========================================
# CORE PAGES & AUTH
# ==========================================
def home(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())

        workouts = Workout.objects.filter(user=user)
        weekly_summary = workouts.filter(workout_date__gte=start_week).aggregate(
            nb_sessions=Count("id"), total_minutes=Sum("duration_minutes")
        )

        upcoming_workouts = (
            workouts.filter(workout_date__gte=today)
            .select_related("program")
            .order_by("workout_date")[:4]
        )
        next_workout = upcoming_workouts[0] if upcoming_workouts else None

        program_from_workout = (
            workouts.filter(program__isnull=False)
            .select_related("program")
            .order_by("-workout_date")
            .first()
        )
        current_program = (
            program_from_workout.program
            if program_from_workout
            else Program.objects.filter(created_by_user=user).order_by("-id").first()
        )

        context.update(
            {
                "weekly_summary": weekly_summary,
                "upcoming_workouts": upcoming_workouts,
                "next_workout": next_workout,
                "current_program": current_program,
                "program_count": Program.objects.filter(created_by_user=user).count(),
                "user_badges": user.badges.select_related("badge").all(),
                "subscription": user.subscription,
                "latest_goal": Goal.objects.filter(user=user).order_by("-id").first(),
            }
        )

    return render(request, "core/home.html", context)


def signup_view(request):
    if request.method == "POST":
        form = CustomerUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            request.session["onboarding_completed"] = False
            messages.success(request, "Compte créé, connecte-toi !")
            return redirect("onboarding")
    else:
        form = CustomerUserCreationForm()
    return render(request, "core/signup.html", {"form": form})


def connexion(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("home")
        messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, "core/login.html")


@login_required
def onboarding(request):
    user = request.user
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

    plan_features = {
        "FREE": [
            "Suivi détaillé des séances",
            "Objectifs et badges motivation",
            "Accès boutique sans remise",
        ],
        "POWER": [
            "Tout le Free + séries/charges illimitées",
            "RPE, notes et suivi des temps de repos",
            "Programmes et exercices complets",
            "Support prioritaire",
        ],
        "SUPER_POWER": [
            "Tout le Power + historique/export complet",
            "Réduction de 20% sur la boutique",
            "Support prioritaire rapide",
            "Accès anticipé aux nouveaux contenus",
        ],
    }
    default_features = [
        "Suivi détaillé des séances",
        "Badges et rappels motivation",
        "Support prioritaire selon ton niveau",
    ]

    def compute_end_date(start_date: date, months: int) -> date:
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
    for sub in subscriptions:
        setattr(sub, "features", plan_features.get(sub.code, default_features))

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
            "plan_features": plan_features,
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
    return redirect("connexion")


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


# ==========================================
# PROGRAMS / WORKOUTS
# ==========================================
@login_required
@require_subscription(min_level_rank=0, feature_name="la bibliothèque d'exercices")
def exercise_list(request):
    exercises = Exercise.objects.all()
    return render(request, "programs/exercise_list.html", {"exercises": exercises})


@login_required
@require_subscription(min_level_rank=1, feature_name="la création d'exercices")
def create_exercise(request):
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Exercice créé avec succès !")
            return redirect("exercise_list")
        messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = ExerciseForm()
    return render(request, "programs/create_exercise.html", {"form": form})


@login_required
@require_subscription(min_level_rank=0, feature_name="tes séances")
def workout_list(request):
    today = timezone.now().date()
    past_workouts = Workout.objects.filter(user=request.user, workout_date__lt=today).order_by(
        "-workout_date"
    )
    upcoming_workouts = Workout.objects.filter(
        user=request.user, workout_date__gte=today
    ).order_by("workout_date")
    return render(
        request,
        "programs/workout_list.html",
        {"past_workouts": past_workouts, "upcoming_workouts": upcoming_workouts},
    )


@login_required
@require_subscription(min_level_rank=0, feature_name="le détail de séance")
def workout_detail(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if workout.program:
        exercises = workout.program.program_exercises.all().order_by("day_index", "order_index")
    else:
        exercises = workout.sets.all()
    return render(
        request,
        "programs/workout_detail.html",
        {"workout": workout, "exercises": exercises},
    )


@login_required
@require_subscription(min_level_rank=1, feature_name="la création de séances")
def create_workout(request):
    if request.method == "POST":
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
                        weight_kg=prog_ex.target_weight_kg,
                    )
            messages.success(request, "Séance créée avec succès !")
            return redirect("workout_list")
        messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = WorkoutForm(user=request.user)
    return render(request, "programs/create_workout.html", {"form": form})


@login_required
@require_subscription(min_level_rank=1, feature_name="la modification de séances")
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == "POST":
        form = WorkoutForm(request.POST, instance=workout, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Séance modifiée avec succès !")
            return redirect("workout_list")
        messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = WorkoutForm(instance=workout, user=request.user)
    return render(
        request,
        "programs/create_workout.html",
        {"form": form, "edit": True, "workout": workout},
    )


@login_required
@require_subscription(min_level_rank=1, feature_name="la suppression de séances")
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == "POST":
        workout.delete()
        messages.success(request, "Séance supprimée !")
        return redirect("workout_list")
    return render(request, "programs/confirm_delete.html", {"workout": workout})


@login_required
@require_subscription(min_level_rank=0, feature_name="les programmes")
def program_list(request):
    programs = Program.objects.filter(created_by_user=request.user)
    return render(request, "programs/program_list.html", {"programs": programs})


@login_required
@require_subscription(min_level_rank=1, feature_name="la création de programmes")
def create_program(request):
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save(commit=False)
            program.created_by_user = request.user
            program.save()
            messages.success(request, "Programme créé avec succès !")
            return redirect("program_list")
        messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = ProgramForm()
    return render(request, "programs/create_program.html", {"form": form})


@login_required
@require_subscription(min_level_rank=0, feature_name="les programmes")
def program_detail(request, program_id):
    program = get_object_or_404(Program, id=program_id, created_by_user=request.user)
    exercises = program.program_exercises.all().order_by("day_index", "order_index")
    return render(
        request,
        "programs/program_detail.html",
        {"program": program, "exercises": exercises},
    )


@login_required
@require_subscription(min_level_rank=1, feature_name="l'édition de programmes")
def edit_program(request, program_id):
    program = get_object_or_404(Program, id=program_id, created_by_user=request.user)
    if request.method == "POST":
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, "Programme modifié avec succès !")
            return redirect("program_detail", program_id=program.id)
        messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = ProgramForm(instance=program)
    return render(
        request,
        "programs/create_program.html",
        {"form": form, "edit": True, "program": program},
    )


@login_required
@require_subscription(min_level_rank=1, feature_name="la suppression de programmes")
def delete_program(request, program_id):
    program = get_object_or_404(Program, id=program_id, created_by_user=request.user)
    if request.method == "POST":
        program.delete()
        messages.success(request, "Programme supprimé !")
        return redirect("program_list")
    return render(request, "programs/confirm_delete.html", {"program": program})


@login_required
@require_subscription(min_level_rank=1, feature_name="l'ajout d'exercices aux programmes")
def add_exercise_to_program(request, program_id):
    program = get_object_or_404(Program, id=program_id, created_by_user=request.user)
    if request.method == "POST":
        form = ProgramExerciseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.program = program
            obj.save()
            messages.success(request, "Exercice ajouté au programme !")
            return redirect("program_detail", program_id=program.id)
        messages.error(request, "Erreur : vérifie les champs du formulaire.")
    else:
        form = ProgramExerciseForm()
    return render(
        request,
        "programs/add_exercise_to_program.html",
        {"form": form, "program": program},
    )


# ==========================================
# SHOP
# ==========================================
def _parse_quantity(request):
    raw = request.POST.get("quantity") or request.GET.get("quantity")
    try:
        qty = int(raw)
    except (TypeError, ValueError):
        return 1
    return max(1, qty)


def product_list(request):
    category_filter = request.GET.get("cat", "").strip()
    products_qs = Product.objects.all()
    if category_filter:
        products_qs = products_qs.filter(category__iexact=category_filter)

    categories = Product.objects.values_list("category", flat=True).distinct().order_by("category")

    return render(
        request,
        "shop/product_list.html",
        {
            "products": products_qs,
            "categories": categories,
            "active_category": category_filter,
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "shop/product_detail.html", {"product": product})


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity = _parse_quantity(request)
    next_url = request.POST.get("next") or request.GET.get("next")

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity
    cart_item.save()

    messages.success(
        request,
        f"{quantity} × {product.name} ajouté au panier (total: {cart_item.quantity}).",
    )

    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("shop")


@login_required
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity = _parse_quantity(request)
    next_url = request.POST.get("next") or request.GET.get("next")

    try:
        cart_item = CartItem.objects.get(user=request.user, product=product)
    except CartItem.DoesNotExist:
        messages.error(request, "Cet article n'est pas dans ton panier.")
        if next_url and next_url.startswith("/"):
            return redirect(next_url)
        return redirect("cart")

    if quantity >= cart_item.quantity:
        cart_item.delete()
        messages.success(request, f"{product.name} retiré du panier.")
    else:
        cart_item.quantity -= quantity
        cart_item.save()
        messages.success(
            request,
            f"{quantity} retiré(s). Nouveau total pour {product.name}: {cart_item.quantity}.",
        )

    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("cart")


@login_required
def view_cart(request):
    items = CartItem.objects.filter(user=request.user)
    subtotal = sum(Decimal(item.total_price()) for item in items)
    discount_rate = _shop_discount_rate(request.user)
    discount_amount = (subtotal * discount_rate).quantize(Decimal("0.01"))
    total = (subtotal - discount_amount).quantize(Decimal("0.01"))
    discount_percent = int(discount_rate * 100)

    return render(
        request,
        "shop/cart.html",
        {
            "items": items,
            "total": total,
            "subtotal": subtotal,
            "discount_rate": discount_rate,
            "discount_amount": discount_amount,
            "discount_percent": discount_percent,
        },
    )


def _validate_card_payload(card_name, card_number, card_expiry, card_cvc):
    errors = []

    if not card_name:
        errors.append("Le nom sur la carte est requis.")

    digits_only = card_number.replace(" ", "")
    if not digits_only.isdigit() or len(digits_only) not in (15, 16):
        errors.append("Numéro de carte invalide (15 ou 16 chiffres attendus).")

    if "/" not in card_expiry or len(card_expiry) != 5:
        errors.append("Date d'expiration invalide (format MM/AA).")
    else:
        month, year = card_expiry.split("/", 1)
        if not (month.isdigit() and year.isdigit()):
            errors.append("Date d'expiration invalide (format MM/AA).")
        else:
            month_val = int(month)
            if month_val < 1 or month_val > 12:
                errors.append("Le mois d'expiration doit être entre 01 et 12.")

    if not card_cvc.isdigit() or len(card_cvc) not in (3, 4):
        errors.append("CVC invalide (3 ou 4 chiffres attendus).")

    return errors


@login_required
def checkout(request):
    items = CartItem.objects.filter(user=request.user)
    if not items.exists():
        return redirect("cart")

    subtotal = sum(Decimal(item.total_price()) for item in items)
    discount_rate = _shop_discount_rate(request.user)
    discount_amount = (subtotal * discount_rate).quantize(Decimal("0.01"))
    total = (subtotal - discount_amount).quantize(Decimal("0.01"))
    discount_percent = int(discount_rate * 100)
    errors = []

    if request.method == "POST":
        address = request.POST.get("address", "").strip()
        card_name = request.POST.get("card_name", "").strip()
        card_number = request.POST.get("card_number", "").strip()
        card_expiry = request.POST.get("card_expiry", "").strip()
        card_cvc = request.POST.get("card_cvc", "").strip()

        if not address:
            errors.append("L'adresse de livraison est requise.")

        errors.extend(_validate_card_payload(card_name, card_number, card_expiry, card_cvc))

        if not errors:
            order = Order.objects.create(
                user=request.user,
                address=address,
                total=total,
                status="paid",
            )

            for item in items:
                unit_price = Decimal(item.product.price)
                if discount_rate > 0:
                    unit_price = (unit_price * (Decimal("1.00") - discount_rate)).quantize(Decimal("0.01"))
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=unit_price,
                )

            payment = Payment.objects.create(
                order=order,
                amount=total,
                status="paid",
                method="card",
                reference=f"PAY-{uuid.uuid4().hex[:10].upper()}",
            )

            items.delete()

            return render(
                request,
                "shop/checkout_success.html",
                {
                    "order": order,
                    "payment": payment,
                },
            )

    return render(
        request,
        "shop/checkout.html",
        {
            "items": items,
            "total": total,
            "subtotal": subtotal,
            "discount_rate": discount_rate,
            "discount_amount": discount_amount,
            "discount_percent": discount_percent,
            "errors": errors,
        },
    )


@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .select_related("payment")
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    return render(
        request,
        "shop/order_history.html",
        {
            "orders": orders,
        },
    )


# ==========================================
# SUIVI / DASHBOARD
# ==========================================
@login_required
@require_subscription(min_level_rank=0, feature_name="le dashboard")
def dashboard(request):
    user = request.user
    today = date.today()
    start_week = today - timedelta(days=today.weekday())
    start_period = today - timedelta(weeks=4)

    workouts = Workout.objects.filter(user=user, workout_date__gte=start_period)

    weekly_summary = workouts.filter(workout_date__gte=start_week).aggregate(
        nb_sessions=Count("id"), total_minutes=Sum("duration_minutes")
    )

    progression = []
    labels = []
    session_counts = []
    durations = []
    total_weight = []

    for i in range(4):
        week_start = start_period + timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        week_workouts = workouts.filter(workout_date__range=[week_start, week_end])

        sessions = week_workouts.count()
        minutes = week_workouts.aggregate(total=Sum("duration_minutes"))["total"] or 0
        progression.append(
            {
                "week": week_start.strftime("%d %b"),
                "sessions": sessions,
                "minutes": minutes,
            }
        )

        labels.append(week_start.strftime("%d %b"))
        session_counts.append(sessions)
        durations.append(minutes)

        sets = WorkoutSet.objects.filter(workout__in=week_workouts)
        charge = sum(
            (
                s.reps * (s.weight_kg or Decimal("0"))
                for s in sets
            ),
            Decimal("0"),
        )
        total_weight.append(charge)

    return render(
        request,
        "suivi/dashboard.html",
        {
            "weekly_summary": weekly_summary,
            "progression": progression,
            "labels": labels,
            "session_counts": session_counts,
            "durations": durations,
            "total_weight": total_weight,
        },
    )


@login_required
@require_subscription(min_level_rank=0, feature_name="ton journal d'entraînement")
def workout_journal(request):
    user = request.user
    program_filter = request.GET.get("program", "")

    workouts = Workout.objects.filter(user=user)
    if program_filter:
        workouts = workouts.filter(program__name__icontains=program_filter)

    return render(
        request,
        "suivi/journal.html",
        {
            "workouts": workouts,
            "filter_program": program_filter,
        },
    )


@login_required
@require_subscription(min_level_rank=1, feature_name="l'export des séances")
def export_workout_csv(request):
    user = request.user
    workouts = Workout.objects.filter(user=user)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="workouts.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Titre", "Programme", "Durée (min)", "Notes"])

    for workout in workouts:
        writer.writerow(
            [
                workout.workout_date,
                workout.title,
                workout.program.name if workout.program else "",
                workout.duration_minutes,
                workout.notes,
            ]
        )

    return response


@login_required
@require_subscription(min_level_rank=0, feature_name="le suivi de progression")
def progression(request):
    user = request.user
    workouts = Workout.objects.filter(user=user).order_by("workout_date")

    labels = []
    session_counts = []
    durations = []
    total_weight = []

    if workouts.exists():
        first_date = workouts.first().workout_date
        last_date = workouts.last().workout_date
        current = first_date

        while current <= last_date:
            week_end = current + timedelta(days=6)
            week_workouts = workouts.filter(workout_date__range=[current, week_end])

            labels.append(current.strftime("%d %b"))
            session_counts.append(week_workouts.count())
            durations.append(week_workouts.aggregate(total=Sum("duration_minutes"))["total"] or 0)

            sets = WorkoutSet.objects.filter(workout__in=week_workouts)
            charge = sum(
                (
                    s.reps * (s.weight_kg or Decimal("0"))
                    for s in sets
                ),
                Decimal("0"),
            )
            total_weight.append(charge)

            current += timedelta(weeks=1)

    return render(
        request,
        "suivi/progression.html",
        {
            "labels": labels,
            "session_counts": session_counts,
            "durations": durations,
            "total_weight": total_weight,
        },
    )


@login_required
@require_subscription(min_level_rank=0, feature_name="tes badges")
def user_badges(request):
    user = request.user
    today = date.today()
    start_period = today - timedelta(weeks=4)

    recent_workouts = Workout.objects.filter(user=user, workout_date__gte=start_period)

    weekly_counts = [
        recent_workouts.filter(
            workout_date__gte=start_period + timedelta(weeks=i),
            workout_date__lte=start_period + timedelta(weeks=i, days=6),
        ).count()
        for i in range(4)
    ]
    regularity_badge = all(count >= 3 for count in weekly_counts)

    total_minutes = recent_workouts.aggregate(total=Sum("duration_minutes"))["total"] or 0
    volume_badge = total_minutes >= 5 * 60

    return render(
        request,
        "suivi/badges.html",
        {
            "regularity_badge": regularity_badge,
            "volume_badge": volume_badge,
            "total_minutes": total_minutes,
        },
    )
