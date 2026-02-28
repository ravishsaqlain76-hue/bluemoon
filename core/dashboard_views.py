from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import role_required
from accounts.utils import log_activity
from .models import SeoSettings, PageSeo, Testimonial, FAQ, NearbyAttraction
from .forms import PageSeoForm, TestimonialForm, FAQForm


@role_required('ceo', 'marketing')
def marketing_dashboard(request):
    seo_settings = SeoSettings.load()
    page_seos = PageSeo.objects.all()
    testimonials = Testimonial.objects.all()[:10]
    faqs = FAQ.objects.all()[:10]
    attractions = NearbyAttraction.objects.all()[:10]

    context = {
        'seo_settings': seo_settings,
        'page_seos': page_seos,
        'testimonials': testimonials,
        'faqs': faqs,
        'attractions': attractions,
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
                f'Updated SEO for page: {page_seo.get_page_display()}'
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
                f'Updated testimonial by {testimonial.name}'
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
                f'Updated FAQ: {faq.question[:50]}'
            )
            messages.success(request, 'FAQ updated.')
            return redirect('marketing_dashboard')
    else:
        form = FAQForm(instance=faq)
    return render(request, 'dashboards/edit_faq.html', {'form': form, 'faq': faq})
