from django import forms
from django.utils import timezone
from .models import Booking


class BookingForm(forms.ModelForm):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )

    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'guests', 'special_requests']
        widgets = {
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out:
            today = timezone.now().date()
            if check_in < today:
                self.add_error('check_in', 'Check-in date cannot be in the past.')
            if check_out <= check_in:
                self.add_error('check_out', 'Check-out date must be after check-in date.')

        return cleaned_data


class GuestBookingForm(forms.ModelForm):
    guest_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
        label='Full Name',
    )
    guest_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
        label='Email Address',
    )
    guest_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
        label='Phone Number',
    )
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )

    class Meta:
        model = Booking
        fields = ['guest_name', 'guest_email', 'guest_phone', 'check_in', 'check_out', 'guests', 'special_requests']
        widgets = {
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out:
            today = timezone.now().date()
            if check_in < today:
                self.add_error('check_in', 'Check-in date cannot be in the past.')
            if check_out <= check_in:
                self.add_error('check_out', 'Check-out date must be after check-in date.')

        return cleaned_data
