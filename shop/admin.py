from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product, CartItem, Order

admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order)
