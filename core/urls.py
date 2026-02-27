from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('guest-house-in-f6-2-islamabad/', views.location_landing, name='location_landing'),
    path('guest-house-in-islamabad/', views.location_islamabad, name='location_islamabad'),
    path('guest-house-near-faisal-mosque-islamabad/', views.location_near_faisal_mosque, name='location_near_faisal_mosque'),
]
