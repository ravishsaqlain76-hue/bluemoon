from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db.models import Sum, Count, Prefetch
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from rooms.models import Room, RoomImage
from rooms.forms import RoomImageForm
from .models import Booking
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings as django_settings
from .forms import BookingForm, GuestBookingForm
from accounts.decorators import role_required
from accounts.utils import log_activity
from core.models import Property


def _get_dashboard_guest_house(request):
    """Return the property to filter by, or None for CEO (all properties)."""
    profile = request.user.profile
    if profile.is_ceo or request.user.is_superuser:
        selected_pk = request.session.get('selected_property_id')
        if selected_pk:
            try:
                return Property.objects.get(pk=selected_pk)
            except Property.DoesNotExist:
                pass
        return None
    return profile.guest_house


# ─── Booking Landing Page ─────────────────────────────────────────────────────

def booking_landing(request, property_slug=None):
    """Show available rooms for this property with Book Now buttons."""
    gh = getattr(request, 'guest_house', None)
    rooms = Room.objects.filter(status='available').select_related('guest_house').prefetch_related('images')
    if gh:
        rooms = rooms.filter(guest_house=gh)
    return render(request, 'bookings/booking_landing.html', {
        'rooms': rooms,
        'guest_house': gh,
    })


# ─── Guest Booking Flow ──────────────────────────────────────────────────────

@login_required
def booking_create(request, room_id, property_slug=None):
    room = get_object_or_404(Room, pk=room_id, status='available')
    prop = getattr(request, 'guest_house', None)
    if prop and room.guest_house != prop:
        raise Http404

    if request.method == 'POST':
        form = BookingForm(request.POST, room=room)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            booking.guest_house = room.guest_house
            num_nights = (booking.check_out - booking.check_in).days
            base_total = room.price_per_night * num_nights
            if room.has_discount:
                booking.original_price = base_total
                booking.discount_percentage = room.discount_percentage
                discount_factor = 1 - (room.discount_percentage / Decimal('100'))
                booking.total_price = (base_total * discount_factor).quantize(Decimal('1'))
            else:
                booking.total_price = base_total
            booking.status = 'pending'
            booking.save()
            messages.success(request, 'Your booking request has been submitted! We will confirm it shortly.')
            return redirect('property_booking_confirmation', property_slug=room.guest_house.slug, pk=booking.pk)
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
def booking_confirmation(request, pk, property_slug=None):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    prop = getattr(request, 'guest_house', None)
    if prop and booking.guest_house != prop:
        raise Http404
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


def guest_booking_create(request, room_id, property_slug=None):
    room = get_object_or_404(Room, pk=room_id, status='available')
    prop = getattr(request, 'guest_house', None)
    if prop and room.guest_house != prop:
        raise Http404

    if request.method == 'POST':
        form = GuestBookingForm(request.POST, room=room)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user if request.user.is_authenticated else None
            booking.room = room
            booking.guest_house = room.guest_house
            num_nights = (booking.check_out - booking.check_in).days
            base_total = room.price_per_night * num_nights
            if room.has_discount:
                booking.original_price = base_total
                booking.discount_percentage = room.discount_percentage
                discount_factor = 1 - (room.discount_percentage / Decimal('100'))
                booking.total_price = (base_total * discount_factor).quantize(Decimal('1'))
            else:
                booking.total_price = base_total
            booking.status = 'pending'
            booking.save()
            _send_guest_confirmation_email(booking)
            messages.success(request, 'Your booking request has been submitted! We will confirm it shortly.')
            return redirect('property_guest_confirmation', property_slug=room.guest_house.slug, reference=booking.booking_reference)
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


def guest_confirmation(request, reference, property_slug=None):
    booking = get_object_or_404(Booking, booking_reference=reference)
    prop = getattr(request, 'guest_house', None)
    if prop and booking.guest_house != prop:
        raise Http404
    return render(request, 'bookings/guest_confirmation.html', {'booking': booking})


def _send_guest_confirmation_email(booking):
    gh = booking.guest_house
    gh_name = gh.name if gh else 'Blue Moon'
    subject = f'Booking Received — {booking.booking_reference} | {gh_name}'
    message = render_to_string('bookings/email/guest_confirmation.txt', {
        'booking': booking,
        'gh_name': gh_name,
        'site_url': getattr(django_settings, 'SITE_URL', ''),
        'address': gh.street_address if gh else '',
        'phone': gh.phone if gh else '',
        'email': gh.email if gh else '',
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
        room = Room.objects.select_related('guest_house').get(pk=room_id)
        from datetime import date
        ci = date.fromisoformat(check_in)
        co = date.fromisoformat(check_out)
        num_nights = (co - ci).days
        if num_nights <= 0:
            return JsonResponse({'error': 'Invalid dates'}, status=400)

        base_total = float(room.price_per_night) * num_nights
        effective_total = float(room.effective_price) * num_nights

        response = {
            'num_nights': num_nights,
            'price_per_night': float(room.price_per_night),
            'total_price': effective_total,
        }
        if room.has_discount:
            response['original_total'] = base_total
            response['discount_percentage'] = float(room.discount_percentage)
            response['effective_price_per_night'] = float(room.effective_price)

        return JsonResponse(response)
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
    """CEO dashboard: room pricing + discount management for all properties."""
    from core.forms import PropertyDiscountForm

    properties = Property.objects.filter(is_active=True).prefetch_related(
        Prefetch('rooms', queryset=Room.objects.order_by('name'))
    )

    property_sections = []
    for prop in properties:
        discount_form = PropertyDiscountForm(
            instance=prop,
            prefix=f'discount_{prop.pk}',
        )
        property_sections.append({
            'property': prop,
            'rooms': prop.rooms.all(),
            'discount_form': discount_form,
        })

    context = {
        'property_sections': property_sections,
        'is_ceo': True,
        'all_properties': properties,
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
                f'Changed price of "{room.name}" from PKR {old_price:,.0f} to PKR {new_price:,.0f}',
                guest_house=room.guest_house,
            )
            messages.success(request, f'Price for {room.name} updated to PKR {new_price:,.0f}.')
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, 'Invalid price. Please enter a positive number.')
    return redirect('bookings:ceo_dashboard')


@role_required('ceo')
def update_property_discount(request, property_id):
    """CEO: update discount percentage and active status for a property."""
    prop = get_object_or_404(Property, pk=property_id)
    if request.method == 'POST':
        from core.forms import PropertyDiscountForm
        form = PropertyDiscountForm(
            request.POST,
            instance=prop,
            prefix=f'discount_{prop.pk}',
        )
        if form.is_valid():
            old_pct = prop.discount_percentage
            old_active = prop.discount_active
            form.save()
            prop.refresh_from_db()
            log_activity(
                request.user, 'update', 'Property', prop.pk,
                f'Updated discount for "{prop.name}": {prop.discount_percentage}% '
                f'({"active" if prop.discount_active else "inactive"}), '
                f'was {old_pct}% ({"active" if old_active else "inactive"})',
                guest_house=prop,
            )
            messages.success(
                request,
                f'Discount for {prop.name} updated to {prop.discount_percentage}% '
                f'({"Active" if prop.discount_active else "Inactive"}).',
            )
        else:
            messages.error(request, 'Invalid discount value. Enter a number between 0 and 100.')
    return redirect('bookings:ceo_dashboard')


@role_required('ceo')
def upload_room_image(request):
    if request.method == 'POST':
        form = RoomImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save()
            if img.is_primary:
                RoomImage.objects.filter(room=img.room, is_primary=True).exclude(pk=img.pk).update(is_primary=False)
            log_activity(
                request.user, 'create', 'RoomImage', img.pk,
                f'Uploaded image for "{img.room.name}"{"  (set as primary)" if img.is_primary else ""}',
                guest_house=img.room.guest_house,
            )
            messages.success(request, f'Image uploaded for {img.room.name}.')
        else:
            messages.error(request, 'Failed to upload image. Please check the form.')
    return redirect('bookings:ceo_dashboard')


@role_required('ceo')
def delete_room_image(request, image_id):
    image = get_object_or_404(RoomImage, pk=image_id)
    room_name = image.room.name
    if request.method == 'POST':
        log_activity(
            request.user, 'delete', 'RoomImage', image.pk,
            f'Deleted image for "{room_name}"',
            guest_house=image.room.guest_house,
        )
        image.image.delete(save=False)
        image.delete()
        messages.success(request, f'Image for {room_name} deleted.')
    return redirect('bookings:ceo_dashboard')


@role_required('ceo')
def set_primary_room_image(request, image_id):
    image = get_object_or_404(RoomImage, pk=image_id)
    if request.method == 'POST':
        RoomImage.objects.filter(room=image.room, is_primary=True).update(is_primary=False)
        image.is_primary = True
        image.save()
        log_activity(
            request.user, 'update', 'RoomImage', image.pk,
            f'Set primary image for "{image.room.name}"',
            guest_house=image.room.guest_house,
        )
        messages.success(request, f'Primary image for {image.room.name} updated.')
    return redirect('bookings:ceo_dashboard')


# ─── Property Switch (CEO) ────────────────────────────────────────────────────

@role_required('ceo')
def switch_property(request):
    """CEO: switch selected property in session."""
    if request.method == 'POST':
        prop_id = request.POST.get('property_id', '')
        if prop_id == 'all':
            request.session.pop('selected_property_id', None)
        else:
            try:
                prop = Property.objects.get(pk=prop_id)
                request.session['selected_property_id'] = prop.pk
            except Property.DoesNotExist:
                pass
    return redirect(request.META.get('HTTP_REFERER', 'bookings:ceo_dashboard'))


# ─── Receptionist Dashboard ───────────────────────────────────────────────────

@role_required('receptionist')
def receptionist_dashboard(request):
    gh = _get_dashboard_guest_house(request)
    today = timezone.now().date()

    bookings_qs = Booking.objects.all()
    if gh:
        bookings_qs = bookings_qs.filter(guest_house=gh)

    total_bookings = bookings_qs.count()
    active_bookings = bookings_qs.filter(status='confirmed', check_out__gte=today).count()
    pending_bookings = bookings_qs.filter(status='pending').count()

    todays_checkins = bookings_qs.filter(
        check_in=today, status='confirmed'
    ).select_related('room', 'user')
    todays_checkouts = bookings_qs.filter(
        check_out=today, status='confirmed'
    ).select_related('room', 'user')

    recent_bookings = bookings_qs.select_related('user', 'room')[:30]

    all_properties = Property.objects.filter(is_active=True)
    is_ceo = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ceo')

    context = {
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'pending_bookings': pending_bookings,
        'todays_checkins': todays_checkins,
        'todays_checkouts': todays_checkouts,
        'recent_bookings': recent_bookings,
        'current_guest_house': gh,
        'all_properties': all_properties,
        'is_ceo': is_ceo,
    }
    return render(request, 'dashboards/receptionist_dashboard.html', context)


@role_required('receptionist')
def approve_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    profile = request.user.profile
    if booking.guest_house != profile.guest_house:
        messages.error(request, 'You can only manage bookings for your property.')
        return redirect('bookings:receptionist_dashboard')
    if booking.status == 'pending':
        booking.status = 'confirmed'
        booking.save()
        log_activity(
            request.user, 'approve', 'Booking', booking.pk,
            f'Approved booking {booking.booking_reference} for {booking.guest_display_name}',
            guest_house=booking.guest_house,
        )
        messages.success(request, f'Booking {booking.booking_reference} approved.')
    else:
        messages.error(request, 'Only pending bookings can be approved.')
    return redirect('bookings:receptionist_dashboard')


@role_required('receptionist')
def cancel_booking_staff(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    profile = request.user.profile
    if booking.guest_house != profile.guest_house:
        messages.error(request, 'You can only manage bookings for your property.')
        return redirect('bookings:receptionist_dashboard')
    if booking.status in ('pending', 'confirmed'):
        booking.status = 'cancelled'
        booking.save()
        log_activity(
            request.user, 'cancel', 'Booking', booking.pk,
            f'Cancelled booking {booking.booking_reference} for {booking.guest_display_name}',
            guest_house=booking.guest_house,
        )
        messages.success(request, f'Booking {booking.booking_reference} cancelled.')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
    return redirect('bookings:receptionist_dashboard')
