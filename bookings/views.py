from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from rooms.models import Room
from .models import Booking
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings as django_settings
from .forms import BookingForm, GuestBookingForm
from accounts.decorators import role_required
from accounts.utils import log_activity


# ─── Guest Booking Flow (unchanged) ───────────────────────────────────────────

@login_required
def booking_create(request, room_id):
    room = get_object_or_404(Room, pk=room_id, status='available')

    if request.method == 'POST':
        form = BookingForm(request.POST, room=room)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            num_nights = (booking.check_out - booking.check_in).days
            booking.total_price = room.price_per_night * num_nights
            booking.status = 'pending'
            booking.save()
            messages.success(request, 'Your booking request has been submitted! We will confirm it shortly.')
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
        form = BookingForm(initial=initial, room=room)

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

    if request.method == 'POST':
        form = GuestBookingForm(request.POST, room=room)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user if request.user.is_authenticated else None
            booking.room = room
            num_nights = (booking.check_out - booking.check_in).days
            booking.total_price = room.price_per_night * num_nights
            booking.status = 'pending'
            booking.save()
            _send_guest_confirmation_email(booking)
            messages.success(request, 'Your booking request has been submitted! We will confirm it shortly.')
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

        # Pre-fill from logged-in user
        if request.user.is_authenticated:
            initial['guest_name'] = request.user.get_full_name() or request.user.username
            initial['guest_email'] = request.user.email

        form = GuestBookingForm(initial=initial, room=room)

    return render(request, 'bookings/guest_booking_create.html', {
        'form': form,
        'room': room,
    })


def guest_confirmation(request, reference):
    booking = get_object_or_404(Booking, booking_reference=reference)
    return render(request, 'bookings/guest_confirmation.html', {'booking': booking})


def _send_guest_confirmation_email(booking):
    from core.models import SeoSettings
    seo = SeoSettings.load()
    subject = f'Booking Received — {booking.booking_reference} | Blue Moon Residency'
    message = render_to_string('bookings/email/guest_confirmation.txt', {
        'booking': booking,
        'site_url': getattr(django_settings, 'SITE_URL', ''),
        'address': seo.street_address if seo else '',
        'phone': seo.phone if seo else '',
        'email': seo.email if seo else '',
    })
    send_mail(
        subject,
        message,
        django_settings.DEFAULT_FROM_EMAIL,
        [booking.guest_email],
        fail_silently=True,
    )


def booking_lookup(request):
    booking = None
    reference = request.GET.get('ref', '').strip().upper()
    if reference:
        try:
            booking = Booking.objects.select_related('room').get(booking_reference=reference)
        except Booking.DoesNotExist:
            messages.error(request, 'No booking found with that reference number. Please check and try again.')
    return render(request, 'bookings/booking_lookup.html', {
        'booking': booking,
        'reference': reference,
    })


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


# ─── Legacy redirect ──────────────────────────────────────────────────────────

@login_required
def admin_dashboard(request):
    """Legacy URL — redirect to the correct role-based dashboard."""
    if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ceo'):
        return redirect('bookings:ceo_dashboard')
    elif hasattr(request.user, 'profile') and request.user.profile.role == 'receptionist':
        return redirect('bookings:receptionist_dashboard')
    elif hasattr(request.user, 'profile') and request.user.profile.role == 'marketing':
        return redirect('marketing_dashboard')
    else:
        return redirect('accounts:dashboard')


# ─── CEO Dashboard ─────────────────────────────────────────────────────────────

@role_required('ceo')
def ceo_dashboard(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(status='confirmed', check_out__gte=today).count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    total_revenue = Booking.objects.filter(
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0
    new_bookings_month = Booking.objects.filter(created_at__date__gte=thirty_days_ago).count()
    recent_bookings = Booking.objects.select_related('user', 'room').all()[:20]

    # Monthly revenue chart (last 6 months)
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

    rooms = Room.objects.all().order_by('name')

    from accounts.models import ActivityLog
    recent_activity = ActivityLog.objects.select_related('user').all()[:20]

    context = {
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'pending_bookings': pending_bookings,
        'total_revenue': total_revenue,
        'new_bookings_month': new_bookings_month,
        'recent_bookings': recent_bookings,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'rooms': rooms,
        'recent_activity': recent_activity,
    }
    return render(request, 'dashboards/ceo_dashboard.html', context)


@role_required('ceo')
def update_room_price(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        new_price = request.POST.get('price_per_night')
        try:
            new_price = Decimal(new_price)
            if new_price <= 0:
                raise ValueError
            old_price = room.price_per_night
            room.price_per_night = new_price
            room.save()
            log_activity(
                request.user, 'update', 'Room', room.pk,
                f'Changed price of "{room.name}" from PKR {old_price:,.0f} to PKR {new_price:,.0f}'
            )
            messages.success(request, f'Price for {room.name} updated to PKR {new_price:,.0f}.')
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, 'Invalid price. Please enter a positive number.')
    return redirect('bookings:ceo_dashboard')


# ─── Receptionist Dashboard ───────────────────────────────────────────────────

@role_required('ceo', 'receptionist')
def receptionist_dashboard(request):
    today = timezone.now().date()

    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(status='confirmed', check_out__gte=today).count()
    pending_bookings = Booking.objects.filter(status='pending').count()

    todays_checkins = Booking.objects.filter(
        check_in=today, status='confirmed'
    ).select_related('room', 'user')
    todays_checkouts = Booking.objects.filter(
        check_out=today, status='confirmed'
    ).select_related('room', 'user')

    recent_bookings = Booking.objects.select_related('user', 'room').all()[:30]

    context = {
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'pending_bookings': pending_bookings,
        'todays_checkins': todays_checkins,
        'todays_checkouts': todays_checkouts,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'dashboards/receptionist_dashboard.html', context)


@role_required('ceo', 'receptionist')
def approve_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status == 'pending':
        booking.status = 'confirmed'
        booking.save()
        log_activity(
            request.user, 'approve', 'Booking', booking.pk,
            f'Approved booking {booking.booking_reference} for {booking.guest_display_name}'
        )
        messages.success(request, f'Booking {booking.booking_reference} approved.')
    else:
        messages.error(request, 'Only pending bookings can be approved.')
    return redirect('bookings:receptionist_dashboard')


@role_required('ceo', 'receptionist')
def cancel_booking_staff(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status in ('pending', 'confirmed'):
        booking.status = 'cancelled'
        booking.save()
        log_activity(
            request.user, 'cancel', 'Booking', booking.pk,
            f'Cancelled booking {booking.booking_reference} for {booking.guest_display_name}'
        )
        messages.success(request, f'Booking {booking.booking_reference} cancelled.')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
    return redirect('bookings:receptionist_dashboard')
