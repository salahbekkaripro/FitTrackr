from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator
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
        settings.AUTH_USER_MODEL,
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

    # Email unique pour éviter les doublons
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
    # Optional FK → Subscription (0..1)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
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
#   WORKOUTS
# =========================================================
class Workout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workouts")
    workout_date = models.DateField()
    title = models.CharField(max_length=100)
    notes = models.TextField(null=True, blank=True)
    workout_type = models.CharField(max_length=50, default="Général")
    duration_minutes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

# =========================================================
#   EXERCISES
# =========================================================
class Exercise(models.Model):
    name = models.CharField(max_length=100)
    primary_muscle = models.CharField(max_length=50)
    equipment = models.CharField(max_length=50, null=True, blank=True)
    difficulty = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


# =========================================================
#   WORKOUT SETS
# =========================================================
class WorkoutSet(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="sets")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    set_number = models.IntegerField()
    reps = models.IntegerField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    rpe = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    rest_seconds = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.exercise.name} - {self.reps} reps"

# =========================================================
#   GOALS
# =========================================================
class Goal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals")
    goal_type = models.CharField(max_length=50)
    target_value = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    weight_goal = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.goal_type} - {self.user.username}"


# =========================================================
#   BADGES
# =========================================================
class Badge(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.badge.code}"


# =========================================================
#   PROGRAMS
# =========================================================
class Program(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    level = models.CharField(max_length=20, null=True, blank=True)
    goal_type = models.CharField(max_length=50, null=True, blank=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="programs")

    def __str__(self):
        return self.name


class ProgramExercise(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    day_index = models.IntegerField()
    order_index = models.IntegerField()
    target_sets = models.IntegerField()
    target_reps = models.IntegerField()
    target_weight_kg = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.program.name} - {self.exercise.name}"


# =========================================================
#   SHOP
# =========================================================
class ShopProduct(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock_qty = models.IntegerField()

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(ShopProduct, on_delete=models.CASCADE)

    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    