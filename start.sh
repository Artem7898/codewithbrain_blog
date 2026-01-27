#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if needed..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME')
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
if username and password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print('✅ Суперпользователь создан!')
    print('Имя:', username)
    print('Email:', email)
    print('Пароль:', password)
elif User.objects.filter(username=username).exists():
    print('⚠️ Суперпользователь уже существует')
else:
    print('⏭️ Создание суперпользователя пропущено')
"

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application
