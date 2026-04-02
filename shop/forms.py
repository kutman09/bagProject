from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Order, Review


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="Имя")
    last_name = forms.CharField(max_length=150, required=False, label="Фамилия")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("full_name", "phone", "city", "address", "comment")
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("stars", "comment")
        widgets = {
            "stars": forms.Select(choices=[(i, f"{i} звезда(ы)") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Напишите ваше мнение о товаре"}),
        }
