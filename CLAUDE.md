# Blue Moon

## Project Overview
A Django guest house booking platform for **Blue Moon Residency** in F-6/2 Islamabad. Guests can browse rooms, register, book rooms with "Pay at Check-in" flow, and manage bookings from their dashboard. Includes full Local SEO optimization.

## Tech Stack
- Python 3.12 / Django 5.0
- Tabler 1.2.0 (UI framework)
- Pillow (image uploads)
- SQLite (default database)
- django.contrib.sitemaps (SEO)

## Project Structure
- `bluemoon/` — Django project configuration (settings, urls, wsgi, asgi)
- `core/` — Public pages (home, about, contact, location landing), SEO models, sitemaps, context processor
- `accounts/` — User registration, login, profile, dashboard
- `rooms/` — Room model, listing with filters, detail pages
- `bookings/` — Booking flow, confirmation, admin analytics dashboard
- `templates/` — Django HTML templates
- `static/` — CSS, JS, and Tabler assets
- `media/` — User-uploaded images (avatars, room photos, SEO)

## Django Apps
| App | URL Prefix | Purpose |
|-----|-----------|---------|
| core | `/` | Home, about, contact, location landing, robots.txt |
| accounts | `/accounts/` | Auth (register, login, logout), dashboard, profile |
| rooms | `/rooms/` | Room listing with filters, room detail |
| bookings | `/bookings/` | Booking creation, confirmation, cancellation, admin dashboard |

## Commands
- Run dev server: `python manage.py runserver`
- Run migrations: `python manage.py migrate`
- Create migrations: `python manage.py makemigrations`
- System check: `python manage.py check`
- Create superuser: `python manage.py createsuperuser`
- Seed sample rooms: `python manage.py seed_rooms`

## Key URLs
- `/` — Home page with hero, featured rooms, location content, Google Map
- `/rooms/` — Room listing with filters
- `/rooms/<id>/` — Room detail
- `/guest-house-in-f6-2-islamabad/` — SEO location landing page
- `/accounts/register/` — Registration
- `/accounts/login/` — Login
- `/accounts/dashboard/` — User booking dashboard
- `/bookings/book/<room_id>/` — Create booking
- `/bookings/admin-dashboard/` — Staff analytics dashboard
- `/admin/` — Django admin
- `/sitemap.xml` — XML sitemap
- `/robots.txt` — Robots file

## SEO Features
- Dynamic meta title/description per page (admin editable via PageSeo model)
- Site-wide SEO settings (SeoSettings singleton in admin)
- JSON-LD LocalBusiness/LodgingBusiness structured data on every page
- Open Graph + Twitter Card tags for social sharing
- Canonical URLs to prevent duplicate content
- Geo meta tags for local search
- XML sitemap with all pages + rooms
- robots.txt blocking admin/private pages
- Location landing page at `/guest-house-in-f6-2-islamabad/`
- Google Maps embed on homepage and contact page
- Image lazy loading
- Cache-ready (locmem cache configured, HTTPS security settings ready)

## Conventions
- Templates use Django template inheritance with `base.html` as the base layout
- Auth pages use `base_auth.html` (centered card layout)
- Static files live in `static/css/` and `static/js/`
- All forms include CSRF protection
- URL names use app namespaces (`accounts:login`, `rooms:room_list`, `bookings:booking_create`)
- Bookings use "Pay at Check-in" — no online payment integration
- SEO blocks in templates: `{% block title %}`, `{% block meta_description %}`, `{% block meta_keywords %}`, `{% block og_title %}`, `{% block og_description %}`, `{% block extra_schema %}`
