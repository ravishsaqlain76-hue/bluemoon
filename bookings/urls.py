from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Guest booking flow
    path('book/<int:room_id>/', views.booking_create, name='booking_create'),
    path('guest-book/<int:room_id>/', views.guest_booking_create, name='guest_booking_create'),
    path('confirmation/<int:pk>/', views.booking_confirmation, name='confirmation'),
    path('guest-confirmation/<str:reference>/', views.guest_confirmation, name='guest_confirmation'),
    path('cancel/<int:pk>/', views.booking_cancel, name='booking_cancel'),
    path('lookup/', views.booking_lookup, name='booking_lookup'),
    path('api/calculate-price/', views.calculate_price, name='calculate_price'),

    # Legacy redirect (backward compat)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # CEO dashboard
    path('ceo-dashboard/', views.ceo_dashboard, name='ceo_dashboard'),
    path('ceo-dashboard/update-price/<int:room_id>/', views.update_room_price, name='update_room_price'),

    # Receptionist dashboard
    path('receptionist-dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('receptionist-dashboard/approve/<int:pk>/', views.approve_booking, name='approve_booking'),
    path('receptionist-dashboard/cancel/<int:pk>/', views.cancel_booking_staff, name='cancel_booking_staff'),
]
