from .models import Cart


def cart_data(request):
    if not request.user.is_authenticated:
        return {"cart_items_count": 0}

    cart = Cart.objects.filter(user=request.user).first()
    count = sum(item.quantity for item in cart.items.all()) if cart else 0
    return {"cart_items_count": count}
