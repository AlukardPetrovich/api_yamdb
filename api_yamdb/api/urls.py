from django.urls import path
from . import views


urlpatterns = [
    path('v1/auth/signup/', views.registrations),
    path(
        'v1/auth/token/', views.get_token),
]
