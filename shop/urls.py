from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='shop.index'),
    path('<int:id>/', views.show, name='shop.show'),
    path('<int:id>/review/create/', views.create_review, name='shop.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='shop.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='shop.delete_review'),
]