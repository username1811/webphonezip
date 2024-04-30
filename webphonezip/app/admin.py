from django.contrib import admin
from .models import Product, Order, OrderItem, Slider, Profile, Cart, CartItem

# Register your models here.
admin.site.register(Profile)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Slider)