from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CheckoutForm, RegisterForm, ReviewForm
from .models import Cart, CartItem, Category, Order, OrderItem, Product, Review


class UserLoginView(LoginView):
    template_name = "shop/auth/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = "shop:product_list"


def register_view(request):
    if request.user.is_authenticated:
        return redirect("shop:product_list")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("shop:product_list")
    return render(request, "shop/auth/register.html", {"form": form})


def product_list_view(request):
    products = Product.objects.filter(is_active=True, stock_status=Product.StockStatus.IN_STOCK).select_related("category")
    categories = Category.objects.filter(is_active=True)

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    sort = request.GET.get("sort", "new")

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(sku__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort_map = {
        "price_asc": "price",
        "price_desc": "-price",
        "rating": "-reviews__stars",
        "name": "name",
        "new": "-created_at",
    }
    products = products.order_by(sort_map.get(sort, "-created_at")).distinct()

    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "query": query,
        "current_category": category_slug,
        "sort": sort,
        "min_price": min_price or "",
        "max_price": max_price or "",
    }
    return render(request, "shop/product_list.html", context)


def product_detail_view(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    reviews = product.reviews.select_related("user")
    can_review = request.user.is_authenticated and not Review.objects.filter(product=product, user=request.user).exists()

    form = ReviewForm(request.POST or None)
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Только зарегистрированные пользователи могут оставлять отзывы.")
            return redirect("shop:login")
        if not can_review:
            messages.warning(request, "Вы уже оставляли отзыв на этот товар.")
            return redirect(product.get_absolute_url())
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Спасибо! Ваш отзыв добавлен.")
            return redirect(product.get_absolute_url())

    return render(
        request,
        "shop/product_detail.html",
        {"product": product, "reviews": reviews, "form": form, "can_review": can_review},
    )


@login_required
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        item.quantity += 1
    item.save()
    messages.success(request, f"Товар '{product.name}' добавлен в корзину.")
    return redirect(request.META.get("HTTP_REFERER", "shop:product_list"))


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "shop/cart.html", {"cart": cart})


@login_required
def update_cart_item_view(request, item_id, action):
    item = get_object_or_404(CartItem.objects.select_related("cart"), id=item_id, cart__user=request.user)
    if action == "plus":
        item.quantity += 1
        item.save()
    elif action == "minus" and item.quantity > 1:
        item.quantity -= 1
        item.save()
    elif action == "remove":
        item.delete()
    return redirect("shop:cart")


@login_required
@transaction.atomic
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("product")
    if not items.exists():
        messages.warning(request, "Корзина пуста.")
        return redirect("shop:product_list")

    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        order: Order = form.save(commit=False)
        order.user = request.user
        order.total_price = cart.total_price
        order.save()

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity,
            )

        items.delete()
        messages.success(request, "Заказ успешно оформлен.")
        return redirect("shop:order_success", order_id=order.id)

    return render(request, "shop/checkout.html", {"cart": cart, "form": form})


@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), id=order_id, user=request.user)
    return render(request, "shop/order_success.html", {"order": order})
