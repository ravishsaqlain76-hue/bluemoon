from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:room_id>/', views.booking_create, name='booking_create'),
    path('guest-book/<int:room_id>/', views.guest_booking_create, name='guest_booking_create'),
    path('confirmation/<int:pk>/', views.booking_confirmation, name='confirmation'),
    path('guest-confirmation/<str:reference>/', views.guest_confirmation, name='guest_confirmation'),
    path('cancel/<int:pk>/', views.booking_cancel, name='booking_cancel'),
    path('api/calculate-price/', views.calculate_price, name='calculate_price'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
