from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Product, CartItem, Order

def product_list(request):
    products = Product.objects.all()
    return render(request, "shop/product_list.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "shop/product_detail.html", {"product": product})


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("shop")

@login_required
def view_cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in items)

    return render(request, "shop/cart.html", {
        "items": items,
        "total": total
    })


@login_required
def checkout(request):
    items = CartItem.objects.filter(user=request.user)

    if request.method == "POST":
        address = request.POST.get("address")

        total = sum(item.total_price() for item in items)

        order = Order.objects.create(
            user=request.user,
            address=address,
            total=total
        )

        for item in items:
            order.items.add(item)

        items.delete()  # vider le panier

        return redirect("shop")  # retour à la boutique

    return render(request, "shop/checkout.html")

