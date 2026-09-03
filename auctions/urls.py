from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auctions/', views.auction_list, name='auction_list'),
    path('auction/<int:auction_id>/', views.auction_detail, name='auction_detail'),
]
