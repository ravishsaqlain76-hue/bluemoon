from django import forms
from .models import PageSeo, Testimonial, FAQ, Property


class PageSeoForm(forms.ModelForm):
    class Meta:
        model = PageSeo
        fields = ['meta_title', 'meta_description', 'keywords']
        widgets = {
            'meta_title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 70}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 160}),
            'keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name', 'location', 'rating', 'text', 'date', 'room_type', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'room_type': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'category', 'order', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PropertyDiscountForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['discount_percentage', 'discount_active']
        widgets = {
            'discount_percentage': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'style': 'width: 120px;',
                'placeholder': '0',
            }),
            'discount_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'discount_percentage': 'Discount %',
            'discount_active': 'Active',
        }
