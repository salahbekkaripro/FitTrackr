from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

# =========================================================
#   CHOICES
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

# =========================================================
#   SUBSCRIPTIONS
# =========================================================
class Subscription(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    price_monthly = models.DecimalField(max_digits=6, decimal_places=2)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="Débutant")
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
#   USERS
# =========================================================
class User(AbstractUser):
    email = models.EmailField(unique=True)
    age = models.IntegerField(validators=[MinValueValidator(16)], null=True, blank=True)
    weight = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    size = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    def __str__(self):
        return self.username


# =========================================================
#   GOALS
# =========================================================
class Goal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals")
    goal_type = models.CharField(max_length=50, choices=GOAL_CHOICES, default="Non défini")
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
