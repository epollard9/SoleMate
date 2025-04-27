# cart/urls.py

from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('',                         views.detail,          name='view_cart'),
    path('add/',                     views.add_to_cart,     name='add_to_cart'),
    path('update-quantity/',         views.update_quantity, name='update_quantity'),
    # <-- changed size_id converter from <int:...> to <str:...> -->
    path('remove/<int:shoe_id>/<str:size_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/',                views.checkout,        name='checkout'),
    path('completed/<int:order_id>/',views.completed,       name='completed'),
    path('history/',                 views.history,         name='history'),
]
