from django.contrib import admin

# Register your models here.
from .models import Shoe, Size, Order, OrderItem

@admin.register(Shoe)
class ShoeAdmin(admin.ModelAdmin):
    list_display = ('shoe_number', 'name', 'brand', 'price', 'release_date')
    search_fields = ('shoe_number', 'name', 'brand')
    filter_horizontal = ('sizes',)  # Better UI for selecting sizes

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('size_code',)
    search_fields = ('size_code',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'order_date')
    search_fields = ('order_number', 'user__username')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'shoe', 'size', 'quantity')
    search_fields = ('order__order_number', 'shoe__shoe_number', 'size__size_code')

