from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import role_required
from accounts.utils import log_activity
from .models import Property, SeoSettings, PageSeo, Testimonial, FAQ, NearbyAttraction
from .forms import PageSeoForm, TestimonialForm, FAQForm


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


@role_required('ceo', 'marketing')
def marketing_dashboard(request):
    gh = _get_dashboard_guest_house(request)
    seo_settings = SeoSettings.load()

    page_seos = PageSeo.objects.all()
    testimonials = Testimonial.objects.all()[:10]
    faqs = FAQ.objects.all()[:10]
    attractions = NearbyAttraction.objects.all()[:10]

    if gh:
        page_seos = page_seos.filter(guest_house=gh)
        testimonials = Testimonial.objects.filter(guest_house=gh)[:10]
        faqs = FAQ.objects.filter(guest_house=gh)[:10]
        attractions = NearbyAttraction.objects.filter(guest_house=gh)[:10]

    is_ceo = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ceo')
    all_properties = Property.objects.filter(is_active=True)

    context = {
        'seo_settings': seo_settings,
        'page_seos': page_seos,
        'testimonials': testimonials,
        'faqs': faqs,
        'attractions': attractions,
        'current_guest_house': gh,
        'all_properties': all_properties,
        'is_ceo': is_ceo,
    }
    return render(request, 'dashboards/marketing_dashboard.html', context)


@role_required('ceo', 'marketing')
def edit_page_seo(request, pk):
    page_seo = get_object_or_404(PageSeo, pk=pk)
    if request.method == 'POST':
        form = PageSeoForm(request.POST, instance=page_seo)
        if form.is_valid():
            form.save()
            log_activity(
                request.user, 'update', 'PageSeo', page_seo.pk,
                f'Updated SEO for page: {page_seo.get_page_display()}',
                guest_house=page_seo.guest_house,
            )
            messages.success(request, f'SEO for "{page_seo.get_page_display()}" updated.')
            return redirect('marketing_dashboard')
    else:
        form = PageSeoForm(instance=page_seo)
    return render(request, 'dashboards/edit_page_seo.html', {'form': form, 'page_seo': page_seo})


@role_required('ceo', 'marketing')
def edit_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        form = TestimonialForm(request.POST, instance=testimonial)
        if form.is_valid():
            form.save()
            log_activity(
                request.user, 'update', 'Testimonial', testimonial.pk,
                f'Updated testimonial by {testimonial.name}',
                guest_house=testimonial.guest_house,
            )
            messages.success(request, f'Testimonial by "{testimonial.name}" updated.')
            return redirect('marketing_dashboard')
    else:
        form = TestimonialForm(instance=testimonial)
    return render(request, 'dashboards/edit_testimonial.html', {'form': form, 'testimonial': testimonial})


@role_required('ceo', 'marketing')
def edit_faq(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            log_activity(
                request.user, 'update', 'FAQ', faq.pk,
                f'Updated FAQ: {faq.question[:50]}',
                guest_house=faq.guest_house,
            )
            messages.success(request, 'FAQ updated.')
            return redirect('marketing_dashboard')
    else:
        form = FAQForm(instance=faq)
    return render(request, 'dashboards/edit_faq.html', {'form': form, 'faq': faq})
