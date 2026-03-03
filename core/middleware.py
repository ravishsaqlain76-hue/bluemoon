from django.shortcuts import get_object_or_404
from .models import Property


class PropertyMiddleware:
    """Resolve property_slug from URL kwargs and attach Property to request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.guest_house = None
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        property_slug = view_kwargs.get('property_slug')
        if property_slug:
            request.guest_house = get_object_or_404(
                Property, slug=property_slug, is_active=True
            )
