from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='shop.index'),
    path('seller', views.seller, name='shop.seller'),
    path('sell', views.sell, name='shop.sell'),
    path('my_listings', views.my_listings, name='shop.my_listings'),
    path('<int:id>/edit', views.edit_shoe, name='shop.edit_shoe'),
    path('sell/shoe', views.create_shoe, name='shop.create_shoe'),
    path('<int:id>/', views.show, name='shop.show'),
    path('<int:id>/edit/shoe', views.edit_shoe_entry, name='shop.edit_shoe_entry'),
    path('<int:id>/review/create/', views.create_review, name='shop.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='shop.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='shop.delete_review'),
]