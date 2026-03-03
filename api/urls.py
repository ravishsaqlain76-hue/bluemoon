from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'api'

urlpatterns = [
    # Auth
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Rooms
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('rooms/<slug:slug>/', views.RoomDetailView.as_view(), name='room_detail'),

    # Bookings
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),

    # Profile
    path('profile/', views.profile_view, name='profile'),
]
