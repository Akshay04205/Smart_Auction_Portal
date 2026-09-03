from django.urls import path

from . import views

urlpatterns = [
    path('auction/<int:auction_id>/bid/', views.place_bid_view, name='place_bid'),
]
