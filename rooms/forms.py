from django import forms
from .models import RoomImage


class RoomImageForm(forms.ModelForm):
    class Meta:
        model = RoomImage
        fields = ['room', 'image', 'caption', 'is_primary']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional caption'}),
        }
