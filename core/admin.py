from django.contrib import admin
from .models import (
    Subscription,
    User,
    Workout,
    Exercise,
    WorkoutSet,
    Goal,
    Badge,
    UserBadge,
    Program,
    ProgramExercise,
    ShopProduct,
    Order,
    OrderItem
)

admin.site.register(Subscription)
admin.site.register(User)
admin.site.register(Workout)
admin.site.register(Exercise)
admin.site.register(WorkoutSet)
admin.site.register(Goal)
admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(Program)
admin.site.register(ProgramExercise)
admin.site.register(ShopProduct)
admin.site.register(Order)
admin.site.register(OrderItem)
