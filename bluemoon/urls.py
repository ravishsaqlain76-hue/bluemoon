from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.sitemaps import StaticSitemap, RoomSitemap, RoomListSitemap
from core.views import robots_txt, landing_page
from core import dashboard_views as core_dashboard_views

sitemaps = {
    'static': StaticSitemap,
    'rooms': RoomSitemap,
    'room_list': RoomListSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('api/', include('api.urls')),
    path('accounts/', include('accounts.urls')),
    path('bookings/', include('bookings.urls')),

    # Marketing dashboard
    path('marketing-dashboard/', core_dashboard_views.marketing_dashboard, name='marketing_dashboard'),
    path('marketing-dashboard/seo/<int:pk>/edit/', core_dashboard_views.edit_page_seo, name='edit_page_seo'),
    path('marketing-dashboard/testimonial/<int:pk>/edit/', core_dashboard_views.edit_testimonial, name='edit_testimonial'),
    path('marketing-dashboard/faq/<int:pk>/edit/', core_dashboard_views.edit_faq, name='edit_faq'),

    # Property-scoped public pages
    path('<slug:property_slug>/', include('core.urls_property')),

    # Root: property selector or redirect
    path('', landing_page, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
