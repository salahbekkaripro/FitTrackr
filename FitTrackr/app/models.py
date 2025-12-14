from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


# =========================================================
#   SUBSCRIPTIONS
# =========================================================
class Subscription(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    price_monthly = models.DecimalField(max_digits=6, decimal_places=2)
    level_rank = models.IntegerField()
    commitment_months = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class SubscriptionEngagement(models.Model):
    user = models.ForeignKey(
        "app.User",
        on_delete=models.CASCADE,
        related_name="subscription_engagements",
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="engagements",
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    commitment_months = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-start_date",)

    @property
    def is_active(self):
        return self.commitment_months > 0 and self.end_date >= timezone.now().date()

    def __str__(self):
        return f"{self.user.username} · {self.subscription.code}"


# =========================================================
#   USERS (custom auth user)
# =========================================================
class User(AbstractUser):
    ROLE_MEMBER = "member"
    ROLE_COACH = "coach"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_MEMBER, "Utilisateur"),
        (ROLE_COACH, "Coach"),
        (ROLE_ADMIN, "Admin"),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER,
    )
    age = models.IntegerField(
        validators=[MinValueValidator(16)],
        null=True,
        blank=True,
    )
    weight = models.IntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
    )
    size = models.IntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    def __str__(self):
        return self.username

    @property
    def is_coach(self):
        return self.role == self.ROLE_COACH

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN


class CoachManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=User.ROLE_COACH)


class Coach(User):
    objects = CoachManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = self.ROLE_COACH
        return super().save(*args, **kwargs)


class AdminManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=User.ROLE_ADMIN)


class AdminUser(User):
    objects = AdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = self.ROLE_ADMIN
        return super().save(*args, **kwargs)


# =========================================================
#   GOALS & BADGES
# =========================================================
class Goal(models.Model):
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="goals")
    goal_type = models.CharField(max_length=50)
    target_value = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    weight_goal = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.goal_type} - {self.user.username}"


class Badge(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.badge.code}"


# =========================================================
#   PROGRAMS / EXERCISES / WORKOUTS
# =========================================================
LEVEL_CHOICES = [
    ("Débutant", "Débutant"),
    ("Intermédiaire", "Intermédiaire"),
    ("Avancé", "Avancé"),
]

GOAL_CHOICES = [
    ("Prise de masse", "Prise de masse"),
    ("Perte de poids", "Perte de poids"),
    ("Cardio", "Cardio"),
    ("Force", "Force"),
    ("Hypertrophie", "Hypertrophie"),
]


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    primary_muscle = models.CharField(max_length=50)
    equipment = models.CharField(max_length=50, blank=True, null=True)
    difficulty = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Program(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="Débutant")
    goal_type = models.CharField(max_length=50, choices=GOAL_CHOICES, default="Non défini")
    created_by_user = models.ForeignKey(
        "app.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="programs_created",
    )

    def __str__(self):
        return self.name


class ProgramExercise(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="program_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.RESTRICT, related_name="program_exercises_links")
    day_index = models.PositiveIntegerField()
    order_index = models.PositiveIntegerField()
    target_sets = models.PositiveIntegerField()
    target_reps = models.PositiveIntegerField()
    target_weight_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.program.name} - Day {self.day_index} - {self.exercise.name}"


class Workout(models.Model):
    user = models.ForeignKey(
        "app.User",
        on_delete=models.CASCADE,
        related_name="programs_workouts",
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="programs_workouts",
    )
    workout_date = models.DateField()
    workout_time = models.TimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    title = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class WorkoutSet(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="sets")
    exercise = models.ForeignKey(Exercise, on_delete=models.RESTRICT, related_name="programs_exercise_sets")
    set_number = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    rpe = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    rest_seconds = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.exercise.name} - Set {self.set_number}"


# =========================================================
#   SHOP
# =========================================================
class Product(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=80, default="Accessoire")

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey("app.User", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("paid", "Payée"),
        ("failed", "Échouée"),
    ]

    user = models.ForeignKey("app.User", on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Commande #{self.id} - {self.get_status_display()}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("paid", "Payé"),
        ("failed", "Échoué"),
    ]

    order = models.OneToOneField(Order, related_name="payment", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    method = models.CharField(max_length=30, default="card")
    reference = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement {self.reference} - {self.get_status_display()}"
