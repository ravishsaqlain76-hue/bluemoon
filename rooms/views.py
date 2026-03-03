from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Room


def room_list(request, property_slug=None):
    gh = getattr(request, 'guest_house', None)
    rooms = Room.objects.filter(status='available').select_related('guest_house')
    if gh:
        rooms = rooms.filter(guest_house=gh)

    room_type = request.GET.get('type')
    if room_type:
        rooms = rooms.filter(room_type=room_type)

    min_price = request.GET.get('min_price')
    if min_price:
        rooms = rooms.filter(price_per_night__gte=min_price)

    max_price = request.GET.get('max_price')
    if max_price:
        rooms = rooms.filter(price_per_night__lte=max_price)

    capacity = request.GET.get('capacity')
    if capacity:
        rooms = rooms.filter(capacity__gte=capacity)

    sort = request.GET.get('sort', 'name')
    if sort == 'price_low':
        rooms = rooms.order_by('price_per_night')
    elif sort == 'price_high':
        rooms = rooms.order_by('-price_per_night')
    elif sort == 'capacity':
        rooms = rooms.order_by('-capacity')
    else:
        rooms = rooms.order_by('name')

    paginator = Paginator(rooms, 9)
    page = request.GET.get('page')
    rooms = paginator.get_page(page)

    context = {
        'rooms': rooms,
        'room_types': Room.ROOM_TYPES,
        'current_type': room_type,
        'current_sort': sort,
        'current_min_price': min_price or '',
        'current_max_price': max_price or '',
        'current_capacity': capacity or '',
        'guest_house': gh,
        'business': gh,
    }
    return render(request, 'rooms/room_list.html', context)


def room_detail(request, slug, property_slug=None):
    gh = getattr(request, 'guest_house', None)
    if gh:
        room = get_object_or_404(Room, slug=slug, guest_house=gh)
        related_rooms = Room.objects.filter(
            guest_house=gh, room_type=room.room_type, status='available'
        ).select_related('guest_house').exclude(pk=room.pk)[:3]
    else:
        room = get_object_or_404(Room, slug=slug)
        related_rooms = Room.objects.filter(
            room_type=room.room_type, status='available'
        ).select_related('guest_house').exclude(pk=room.pk)[:3]

    return render(request, 'rooms/room_detail.html', {
        'room': room,
        'related_rooms': related_rooms,
        'guest_house': gh or room.guest_house,
        'business': gh or room.guest_house,
    })
