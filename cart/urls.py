from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_cart, name='cart.view_cart'),
    path('add/<int:id>/', views.add_to_cart, name='cart.add'),
    path('remove/<int:id>/', views.remove_from_cart, name='cart.remove'),
]
