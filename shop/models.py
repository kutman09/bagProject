from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=140, unique=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True, verbose_name="Изображение")
    is_active = models.BooleanField(default=True, verbose_name="Активная")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    class StockStatus(models.TextChoices):
        IN_STOCK = "in_stock", "В наличии"
        OUT_OF_STOCK = "out_of_stock", "Нет в наличии"

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name="Категория")
    name = models.CharField(max_length=150, verbose_name="Название")
    slug = models.SlugField(max_length=170, unique=True)
    sku = models.CharField(max_length=40, unique=True, verbose_name="Артикул")
    description = models.TextField(verbose_name="Описание")
    material = models.CharField(max_length=120, blank=True, verbose_name="Материал")
    color = models.CharField(max_length=80, blank=True, verbose_name="Цвет")
    width_cm = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Ширина, см")
    height_cm = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Высота, см")
    depth_cm = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Глубина, см")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Старая цена")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество")
    stock_status = models.CharField(
        max_length=20,
        choices=StockStatus.choices,
        default=StockStatus.IN_STOCK,
        verbose_name="Статус наличия",
    )
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый")
    is_active = models.BooleanField(default=True, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    @property
    def discount_percent(self) -> int:
        if not self.old_price or self.old_price <= self.price:
            return 0
        discount = (self.old_price - self.price) / self.old_price * Decimal(100)
        return int(discount)

    @property
    def average_rating(self) -> float:
        value = self.reviews.aggregate(avg=models.Avg("stars"))["avg"]
        return round(value or 0, 1)

    def get_absolute_url(self):
        return reverse("shop:product_detail", kwargs={"slug": self.slug})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", verbose_name="Фото")
    is_main = models.BooleanField(default=False, verbose_name="Главное")

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"
        ordering = ["-is_main", "id"]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.id}"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self) -> str:
        return f"Корзина {self.user.username}"

    @property
    def total_price(self) -> Decimal:
        return sum((item.total_price for item in self.items.select_related("product")), Decimal("0"))


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"
        unique_together = ("cart", "product")

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self) -> Decimal:
        return self.product.price * self.quantity


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        CONFIRMED = "confirmed", "Подтвержден"
        SHIPPED = "shipped", "Отправлен"
        DELIVERED = "delivered", "Доставлен"
        CANCELED = "canceled", "Отменен"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="orders")
    full_name = models.CharField(max_length=150, verbose_name="ФИО")
    phone = models.CharField(max_length=30, verbose_name="Телефон")
    city = models.CharField(max_length=120, verbose_name="Город")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Заказ #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    @property
    def total_price(self) -> Decimal:
        return self.price * self.quantity


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка",
    )
    comment = models.TextField(verbose_name="Отзыв")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]
        unique_together = ("product", "user")

    def __str__(self) -> str:
        return f"{self.product.name}: {self.stars}"
