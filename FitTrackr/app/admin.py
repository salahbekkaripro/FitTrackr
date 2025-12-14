from django.contrib import admin

from .models import (
    AdminUser,
    Badge,
    CartItem,
    Coach,
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


admin.site.register(User)
admin.site.register(Coach)
admin.site.register(AdminUser)
admin.site.register(Subscription)
admin.site.register(SubscriptionEngagement)
admin.site.register(Goal)
admin.site.register(Badge)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Program)
admin.site.register(ProgramExercise)
admin.site.register(Workout)
admin.site.register(WorkoutSet)
