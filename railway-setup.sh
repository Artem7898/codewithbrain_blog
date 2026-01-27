#!/bin/bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Create superuser if environment variables exist
python -c "
import os
if os.getenv('DJANGO_SUPERUSER_USERNAME'):
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = os.getenv('DJANGO_SUPERUSER_USERNAME')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f'Admin user {username} created')
    else:
        print('Admin user already exists')
"

gunicorn --bind 0.0.0.0:8000 config.wsgi:application
