import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import CartItem, Order, OrderItem, Payment, Product


def _parse_quantity(request):
    """Extract a positive quantity from request data."""
    raw = request.POST.get("quantity") or request.GET.get("quantity")
    try:
        qty = int(raw)
    except (TypeError, ValueError):
        return 1
    return max(1, qty)


def product_list(request):
    category_filter = request.GET.get("cat", "").strip()

    products_qs = Product.objects.all()
    if category_filter:
        products_qs = products_qs.filter(category__iexact=category_filter)

    categories = (
        Product.objects.values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    return render(
        request,
        "shop/product_list.html",
        {
            "products": products_qs,
            "categories": categories,
            "active_category": category_filter,
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "shop/product_detail.html", {"product": product})


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity = _parse_quantity(request)
    next_url = request.POST.get("next") or request.GET.get("next")

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, product=product
    )

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity
    cart_item.save()

    messages.success(
        request,
        f"{quantity} × {product.name} ajouté au panier (total: {cart_item.quantity}).",
    )

    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("shop")


@login_required
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity = _parse_quantity(request)
    next_url = request.POST.get("next") or request.GET.get("next")

    try:
        cart_item = CartItem.objects.get(user=request.user, product=product)
    except CartItem.DoesNotExist:
        messages.error(request, "Cet article n'est pas dans ton panier.")
        if next_url and next_url.startswith("/"):
            return redirect(next_url)
        return redirect("cart")

    if quantity >= cart_item.quantity:
        cart_item.delete()
        messages.success(request, f"{product.name} retiré du panier.")
    else:
        cart_item.quantity -= quantity
        cart_item.save()
        messages.success(
            request,
            f"{quantity} retiré(s). Nouveau total pour {product.name}: {cart_item.quantity}.",
        )

    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("cart")


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
