from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='shop.index'),
    path('<int:id>/', views.show, name='shop.show'),
]