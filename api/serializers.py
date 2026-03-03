from rest_framework import serializers
from django.contrib.auth.models import User
from rooms.models import Room, RoomImage
from bookings.models import Booking
from accounts.models import UserProfile


class RoomImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = RoomImage
        fields = ['id', 'image', 'caption', 'is_primary']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class RoomListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'name', 'slug', 'room_type', 'room_type_display',
            'price_per_night', 'capacity', 'status', 'amenities_list',
            'featured', 'bed_type', 'room_size', 'primary_image',
        ]

    def get_primary_image(self, obj):
        img = obj.primary_image
        if img and img.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(img.image.url)
        return None


class RoomDetailSerializer(serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'name', 'slug', 'room_type', 'room_type_display',
            'description', 'price_per_night', 'capacity', 'status',
            'amenities_list', 'featured', 'bed_type', 'room_size',
            'images',
        ]


class BookingSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)
    num_nights = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'room', 'room_name', 'check_in', 'check_out',
            'guests', 'total_price', 'status', 'status_display',
            'booking_reference', 'payment_method', 'special_requests',
            'num_nights', 'created_at',
        ]
        read_only_fields = ['total_price', 'status', 'booking_reference', 'payment_method', 'created_at']


class BookingCreateSerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    guests = serializers.IntegerField(min_value=1)
    special_requests = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        from datetime import date
        if data['check_in'] < date.today():
            raise serializers.ValidationError({'check_in': 'Check-in date cannot be in the past.'})
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError({'check_out': 'Check-out must be after check-in.'})

        try:
            room = Room.objects.get(pk=data['room_id'])
        except Room.DoesNotExist:
            raise serializers.ValidationError({'room_id': 'Room not found.'})

        if room.status != 'available':
            raise serializers.ValidationError({'room_id': 'This room is not available.'})

        if data['guests'] > room.capacity:
            raise serializers.ValidationError({
                'guests': f'Maximum capacity is {room.capacity} guests.'
            })

        if Booking.has_overlap(room, data['check_in'], data['check_out']):
            raise serializers.ValidationError('This room is already booked for the selected dates.')

        data['room'] = room
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'avatar']

    def get_avatar(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already taken.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
        )
        UserProfile.objects.create(user=user, role='guest')
        return user
