from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name="shop"),
    path('product/<int:pk>/', views.product_detail, name="product_detail"),
    path('add/<int:pk>/', views.add_to_cart, name="add_to_cart"),
    path('cart/', views.view_cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
]
