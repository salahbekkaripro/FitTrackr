import uuid

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import CartItem, Order, OrderItem, Payment, Product


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
        user=request.user, product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("shop")


@login_required
def view_cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in items)

    return render(
        request,
        "shop/cart.html",
        {
            "items": items,
            "total": total,
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

    total = sum(item.total_price() for item in items)
    errors = []

    if request.method == "POST":
        address = request.POST.get("address", "").strip()
        card_name = request.POST.get("card_name", "").strip()
        card_number = request.POST.get("card_number", "").strip()
        card_expiry = request.POST.get("card_expiry", "").strip()
        card_cvc = request.POST.get("card_cvc", "").strip()

        if not address:
            errors.append("L'adresse de livraison est requise.")

        errors.extend(
            _validate_card_payload(card_name, card_number, card_expiry, card_cvc)
        )

        if not errors:
            order = Order.objects.create(
                user=request.user,
                address=address,
                total=total,
                status="paid",
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.price,
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
