from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Booking utilities (non-property-scoped)
    path('cancel/<int:pk>/', views.booking_cancel, name='booking_cancel'),
    path('lookup/', views.booking_lookup, name='booking_lookup'),
    path('api/calculate-price/', views.calculate_price, name='calculate_price'),

    # Legacy redirect (backward compat)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # CEO dashboard
    path('ceo-dashboard/', views.ceo_dashboard, name='ceo_dashboard'),
    path('ceo-dashboard/switch-property/', views.switch_property, name='switch_property'),
    path('ceo-dashboard/update-price/<int:room_id>/', views.update_room_price, name='update_room_price'),
    path('ceo-dashboard/update-discount/<int:property_id>/', views.update_property_discount, name='update_property_discount'),
    path('ceo-dashboard/upload-image/', views.upload_room_image, name='upload_room_image'),
    path('ceo-dashboard/delete-image/<int:image_id>/', views.delete_room_image, name='delete_room_image'),
    path('ceo-dashboard/set-primary-image/<int:image_id>/', views.set_primary_room_image, name='set_primary_room_image'),

    # Receptionist dashboard
    path('receptionist-dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('receptionist-dashboard/approve/<int:pk>/', views.approve_booking, name='approve_booking'),
    path('receptionist-dashboard/cancel/<int:pk>/', views.cancel_booking_staff, name='cancel_booking_staff'),
]
