from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from rooms.models import Room
from bookings.models import Booking
from accounts.models import UserProfile
from .serializers import (
    RoomListSerializer, RoomDetailSerializer,
    BookingSerializer, BookingCreateSerializer,
    UserProfileSerializer, RegisterSerializer,
)


# ─── Auth ────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {'detail': 'Invalid username or password.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    refresh = RefreshToken.for_user(user)
    # Ensure profile exists
    UserProfile.objects.get_or_create(user=user, defaults={'role': 'guest'})
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
    }, status=status.HTTP_201_CREATED)


# ─── Rooms ───────────────────────────────────────────────────────────────────

class RoomListView(generics.ListAPIView):
    serializer_class = RoomListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Room.objects.filter(status='available').prefetch_related('images')
        # Property filter
        property_slug = self.request.query_params.get('property')
        if property_slug:
            qs = qs.filter(guest_house__slug=property_slug)
        room_type = self.request.query_params.get('type')
        if room_type:
            qs = qs.filter(room_type=room_type)
        min_price = self.request.query_params.get('min_price')
        if min_price:
            qs = qs.filter(price_per_night__gte=min_price)
        max_price = self.request.query_params.get('max_price')
        if max_price:
            qs = qs.filter(price_per_night__lte=max_price)
        capacity = self.request.query_params.get('capacity')
        if capacity:
            qs = qs.filter(capacity__gte=capacity)
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            qs = qs.filter(featured=True)
        sort = self.request.query_params.get('sort')
        if sort == 'price_asc':
            qs = qs.order_by('price_per_night')
        elif sort == 'price_desc':
            qs = qs.order_by('-price_per_night')
        elif sort == 'capacity':
            qs = qs.order_by('-capacity')
        return qs


class RoomDetailView(generics.RetrieveAPIView):
    serializer_class = RoomDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        qs = Room.objects.prefetch_related('images')
        property_slug = self.request.query_params.get('property')
        if property_slug:
            qs = qs.filter(guest_house__slug=property_slug)
        return qs


# ─── Bookings ────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def booking_create(request):
    from decimal import Decimal

    serializer = BookingCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    room = data['room']
    num_nights = (data['check_out'] - data['check_in']).days
    base_total = room.price_per_night * num_nights

    discount_pct = Decimal('0')
    original_price = None
    if room.has_discount:
        original_price = base_total
        discount_pct = room.discount_percentage
        discount_factor = 1 - (discount_pct / Decimal('100'))
        total_price = (base_total * discount_factor).quantize(Decimal('1'))
    else:
        total_price = base_total

    booking = Booking.objects.create(
        user=request.user,
        room=room,
        guest_house=room.guest_house,
        check_in=data['check_in'],
        check_out=data['check_out'],
        guests=data['guests'],
        total_price=total_price,
        original_price=original_price,
        discount_percentage=discount_pct,
        special_requests=data.get('special_requests', ''),
    )
    return Response(
        BookingSerializer(booking).data,
        status=status.HTTP_201_CREATED,
    )


class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('room')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def booking_cancel(request, pk):
    try:
        booking = Booking.objects.get(pk=pk, user=request.user)
    except Booking.DoesNotExist:
        return Response(
            {'detail': 'Booking not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    if booking.status not in ('pending', 'confirmed'):
        return Response(
            {'detail': 'This booking cannot be cancelled.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    booking.status = 'cancelled'
    booking.save()
    return Response(BookingSerializer(booking).data)


# ─── Profile ─────────────────────────────────────────────────────────────────

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user, defaults={'role': 'guest'}
    )
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
