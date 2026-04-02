from django.urls import path

from .views import (
    UserLoginView,
    UserLogoutView,
    add_to_cart_view,
    cart_view,
    checkout_view,
    order_success_view,
    product_detail_view,
    product_list_view,
    register_view,
    update_cart_item_view,
)

app_name = "shop"

urlpatterns = [
    path("", product_list_view, name="product_list"),
    path("product/<slug:slug>/", product_detail_view, name="product_detail"),
    path("cart/", cart_view, name="cart"),
    path("cart/add/<int:product_id>/", add_to_cart_view, name="add_to_cart"),
    path("cart/item/<int:item_id>/<str:action>/", update_cart_item_view, name="update_cart_item"),
    path("checkout/", checkout_view, name="checkout"),
    path("order-success/<int:order_id>/", order_success_view, name="order_success"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("register/", register_view, name="register"),
]
