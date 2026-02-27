from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from rooms.models import Room
from .models import Booking
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .forms import BookingForm, GuestBookingForm


@login_required
def booking_create(request, room_id):
    room = get_object_or_404(Room, pk=room_id, status='available')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            num_nights = (booking.check_out - booking.check_in).days
            booking.total_price = room.price_per_night * num_nights
            booking.status = 'confirmed'
            booking.save()
            messages.success(request, 'Your booking has been confirmed!')
            return redirect('bookings:confirmation', pk=booking.pk)
    else:
        initial = {}
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        guests = request.GET.get('guests')
        if check_in:
            initial['check_in'] = check_in
        if check_out:
            initial['check_out'] = check_out
        if guests:
            initial['guests'] = guests
        form = BookingForm(initial=initial)

    return render(request, 'bookings/booking_create.html', {
        'form': form,
        'room': room,
    })


@login_required
def booking_confirmation(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'bookings/confirmation.html', {'booking': booking})


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status in ('pending', 'confirmed'):
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Your booking has been cancelled.')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
    return redirect('accounts:dashboard')


def guest_booking_create(request, room_id):
    room = get_object_or_404(Room, pk=room_id, status='available')

    if request.user.is_authenticated:
        return redirect('bookings:booking_create', room_id=room.pk)

    if request.method == 'POST':
        form = GuestBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = None
            booking.room = room
            num_nights = (booking.check_out - booking.check_in).days
            booking.total_price = room.price_per_night * num_nights
            booking.status = 'confirmed'
            booking.save()
            _send_guest_confirmation_email(booking)
            messages.success(request, 'Your booking has been confirmed!')
            return redirect('bookings:guest_confirmation', reference=booking.booking_reference)
    else:
        initial = {}
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        guests = request.GET.get('guests')
        if check_in:
            initial['check_in'] = check_in
        if check_out:
            initial['check_out'] = check_out
        if guests:
            initial['guests'] = guests
        form = GuestBookingForm(initial=initial)

    return render(request, 'bookings/guest_booking_create.html', {
        'form': form,
        'room': room,
    })


def guest_confirmation(request, reference):
    booking = get_object_or_404(Booking, booking_reference=reference)
    return render(request, 'bookings/guest_confirmation.html', {'booking': booking})


def _send_guest_confirmation_email(booking):
    subject = f'Booking Confirmed — {booking.booking_reference} | Blue Moon Residency'
    message = render_to_string('bookings/email/guest_confirmation.txt', {'booking': booking})
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [booking.guest_email],
        fail_silently=True,
    )


def calculate_price(request):
    room_id = request.GET.get('room_id')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    try:
        room = Room.objects.get(pk=room_id)
        from datetime import date
        ci = date.fromisoformat(check_in)
        co = date.fromisoformat(check_out)
        num_nights = (co - ci).days
        if num_nights <= 0:
            return JsonResponse({'error': 'Invalid dates'}, status=400)
        total = float(room.price_per_night) * num_nights
        return JsonResponse({
            'num_nights': num_nights,
            'price_per_night': float(room.price_per_night),
            'total_price': total,
        })
    except (Room.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)


@staff_member_required
def admin_dashboard(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(status='confirmed', check_out__gte=today).count()
    total_revenue = Booking.objects.filter(
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0
    new_bookings_month = Booking.objects.filter(created_at__date__gte=thirty_days_ago).count()

    recent_bookings = Booking.objects.select_related('user', 'room').all()[:20]

    # Monthly revenue for chart (last 6 months)
    six_months_ago = today - timedelta(days=180)
    monthly_revenue = (
        Booking.objects.filter(
            status__in=['confirmed', 'completed'],
            created_at__date__gte=six_months_ago,
        )
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(revenue=Sum('total_price'), count=Count('id'))
        .order_by('month')
    )

    chart_labels = [entry['month'].strftime('%b %Y') for entry in monthly_revenue]
    chart_data = [float(entry['revenue']) for entry in monthly_revenue]

    context = {
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'total_revenue': total_revenue,
        'new_bookings_month': new_bookings_month,
        'recent_bookings': recent_bookings,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)
