from django.contrib import admin
from .models import Subscription, User, Goal, Badge, UserBadge, ShopProduct, Order, OrderItem
from programs.models import Exercise, Workout, WorkoutSet, Program, ProgramExercise  # tout depuis programs

# Enregistrement des modèles Core
admin.site.register(Subscription)
admin.site.register(User)
admin.site.register(Goal)
admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(ShopProduct)
admin.site.register(Order)
admin.site.register(OrderItem)

# Enregistrement des modèles Programs
admin.site.register(Exercise)
admin.site.register(Workout)
admin.site.register(WorkoutSet)
admin.site.register(Program)
admin.site.register(ProgramExercise)
