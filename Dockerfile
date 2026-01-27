FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Применяем миграции
RUN python manage.py migrate --noinput

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "
  echo 'Creating superuser if needed...' && \
  python -c \"
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
  \" && \
  echo 'Starting Gunicorn...' && \
  gunicorn --bind 0.0.0.0:8000 config.wsgi:application
"]
