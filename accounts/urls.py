from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # Django's built-in LoginView/LogoutView handle authentication -
    # we only supply our own template for the login page.
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # LogoutView only accepts POST by default in modern Django, matching the
    # spec's "use Django's secure POST logout mechanism" requirement.
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', views.register, name='register'),

    # NOTE: Dashboard and My Bids were removed per request. My Won Auctions stays.
    path('my-wins/', views.my_wins, name='my_wins'),
]
