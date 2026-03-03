from django.urls import path
from . import views

# No app_name here — these URLs are non-namespaced to avoid conflict with bookings/urls.py
# Use {% url 'property_booking_create' ... %} in templates

urlpatterns = [
    path('', views.booking_landing, name='property_booking_landing'),
    path('<int:room_id>/', views.booking_create, name='property_booking_create'),
    path('guest/<int:room_id>/', views.guest_booking_create, name='property_guest_booking_create'),
    path('confirmation/<int:pk>/', views.booking_confirmation, name='property_booking_confirmation'),
    path('guest-confirmation/<str:reference>/', views.guest_confirmation, name='property_guest_confirmation'),
]
