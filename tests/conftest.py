# tests/conftest.py
"""
Конфигурация для pytest
"""
import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path
from django.conf import settings

# Добавляем корневую директорию проекта в путь Python
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def pytest_configure():
    """Настройка Django для pytest"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    import django
    django.setup()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Настройка тестовой базы данных"""
    with django_db_blocker.unblock():
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])


@pytest.fixture(scope='function')
def db_with_data(django_db_setup, django_db_blocker):
    """Создание тестовых данных в базе"""
    with django_db_blocker.unblock():
        from django.contrib.auth.models import User
        from blog.models import Category, Post

        # Создаем тестового пользователя
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        # Создаем тестовую категорию
        category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )

        # Создаем тестовый пост
        post = Post.objects.create(
            title='Test Post',
            author=user,
            category=category,
            excerpt='Test excerpt',
            content='Test content',
            status='published'
        )

        return {
            'user': user,
            'category': category,
            'post': post
        }


@pytest.fixture
def admin_client(django_db_setup, django_db_blocker):
    """Клиент с административными правами"""
    with django_db_blocker.unblock():
        from django.contrib.auth.models import User
        from django.test import Client

        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword123'
        )

        client = Client()
        client.force_login(admin_user)
        return client


@pytest.fixture
def client():
    """Обычный тестовый клиент"""
    from django.test import Client
    return Client()


@pytest.fixture
def temp_media_root():
    """Создание временной директории для медиа-файлов"""
    temp_dir = tempfile.mkdtemp()
    original_media_root = settings.MEDIA_ROOT
    settings.MEDIA_ROOT = temp_dir

    yield temp_dir

    # Очистка после тестов
    shutil.rmtree(temp_dir)
    settings.MEDIA_ROOT = original_media_root


@pytest.fixture
def temp_static_root():
    """Создание временной директории для статических файлов"""
    temp_dir = tempfile.mkdtemp()
    original_static_root = settings.STATIC_ROOT
    settings.STATIC_ROOT = temp_dir

    # Создаем структуру статических файлов
    static_dir = Path(temp_dir) / 'static'
    static_dir.mkdir(parents=True, exist_ok=True)

    # Создаем тестовый статический файл
    test_css = static_dir / 'test.css'
    test_css.write_text('body { color: red; }')

    yield temp_dir

    # Очистка после тестов
    shutil.rmtree(temp_dir)
    settings.STATIC_ROOT = original_static_root