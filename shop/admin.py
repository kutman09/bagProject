from django.contrib import admin

from .models import Cart, CartItem, Category, Order, OrderItem, Product, ProductImage, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "stock_status", "is_active", "is_featured")
    list_filter = ("category", "stock_status", "is_active", "is_featured")
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "stars", "created_at")
    list_filter = ("stars", "created_at")
    search_fields = ("product__name", "user__username")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "phone")
    inlines = [OrderItemInline]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "updated_at")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")
