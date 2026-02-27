from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from core.models import SeoSettings
from .models import Room


def room_list(request):
    rooms = Room.objects.filter(status='available')

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

    settings = SeoSettings.load()
    context = {
        'rooms': rooms,
        'room_types': Room.ROOM_TYPES,
        'current_type': room_type,
        'current_sort': sort,
        'current_min_price': min_price or '',
        'current_max_price': max_price or '',
        'current_capacity': capacity or '',
        'currency': settings.currency_symbol,
    }
    return render(request, 'rooms/room_list.html', context)


def room_detail(request, slug):
    room = get_object_or_404(Room, slug=slug)
    related_rooms = Room.objects.filter(
        room_type=room.room_type, status='available'
    ).exclude(pk=room.pk)[:3]
    settings = SeoSettings.load()
    return render(request, 'rooms/room_detail.html', {
        'room': room,
        'related_rooms': related_rooms,
        'business': settings,
    })
