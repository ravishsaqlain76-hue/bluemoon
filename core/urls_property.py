from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.property_home, name='property_home'),
    path('about/', views.property_about, name='property_about'),
    path('contact/', views.property_contact, name='property_contact'),
    path('rooms/', include('rooms.urls_property')),
    path('booking/', include('bookings.urls_property')),
    # SEO landing pages
    path('guest-house-in-f6-2-islamabad/', views.property_location_landing, name='property_location_landing'),
    path('guest-house-in-f8-3-islamabad/', views.property_location_landing, name='property_location_f8'),
    path('guest-house-in-islamabad/', views.property_location_islamabad, name='property_location_islamabad'),
    path('guest-house-near-faisal-mosque-islamabad/', views.property_location_near_faisal_mosque, name='property_location_near_faisal_mosque'),
]
