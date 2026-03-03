#!/usr/bin/env bash
# Render Build Script
# Yeh har deploy pe automatically run hota hai

set -o errexit  # Koi bhi error aye toh ruk jao

# 1. Install all Python packages
pip install --upgrade pip
pip install -r requirements.txt

# 2. Collect static files (CSS, JS, images) into staticfiles/ folder
python manage.py collectstatic --no-input

# 3. Run database migrations (create/update tables in PostgreSQL)
python manage.py migrate

# 4. Create superuser automatically (sirf pehli dafa banega, baad mein skip hoga)
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
import os
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@bluemoon.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
if password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created!')
else:
    print('Superuser already exists or no password set, skipping.')
"
