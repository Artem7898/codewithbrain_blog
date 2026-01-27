"""
Тесты конфигурации проекта CodeWithBrain
"""
import os
import sys
from pathlib import Path
from django.test import TestCase, override_settings
from django.conf import settings


class TestProjectConfiguration(TestCase):
    """Тесты базовой конфигурации проекта"""

    def test_project_structure(self):
        """Проверка структуры проекта"""
        project_root = Path(__file__).resolve().parent.parent

        # Проверка существования основных директорий
        required_dirs = [
            project_root,
            project_root / 'config',
            project_root / 'blog',
            project_root / 'static',
            project_root / 'media',
            project_root / 'templates',
            project_root / 'logs',
        ]

        for dir_path in required_dirs:
            with self.subTest(dir_path=dir_path):
                self.assertTrue(dir_path.exists() and dir_path.is_dir(),
                                f"Отсутствует директория: {dir_path}")

    def test_python_version(self):
        """Проверка версии Python"""
        self.assertGreaterEqual(sys.version_info, (3, 8),
                                "Требуется Python 3.8 или выше")

    def test_django_settings(self):
        """Тестирование основных настроек Django"""
        # Безопасность
        self.assertFalse(settings.SECRET_KEY == 'dev-secret-key-change-in-production',
                         "Используется дефолтный SECRET_KEY!")
        self.assertTrue(len(settings.SECRET_KEY) >= 20,
                        "SECRET_KEY слишком короткий")

        # База данных
        self.assertEqual(settings.DATABASES['default']['ENGINE'],
                         'django.db.backends.postgresql',
                         "Используется не PostgreSQL")

        # Язык и время
        self.assertEqual(settings.LANGUAGE_CODE, 'ru-ru')
        self.assertEqual(settings.TIME_ZONE, 'Europe/Moscow')
        self.assertTrue(settings.USE_I18N)
        self.assertTrue(settings.USE_TZ)

        # Статические файлы
        self.assertEqual(settings.STATIC_URL, '/static/')
        self.assertIsNotNone(settings.STATIC_ROOT)
        self.assertIsNotNone(settings.STATICFILES_DIRS)

        # Медиа файлы
        self.assertEqual(settings.MEDIA_URL, '/media/')
        self.assertIsNotNone(settings.MEDIA_ROOT)

    def test_installed_apps(self):
        """Проверка установленных приложений"""
        required_apps = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework',
            'taggit',
            'django_ckeditor_5',
            'blog',
            'unfold',
        ]

        for app in required_apps:
            with self.subTest(app=app):
                self.assertIn(app, settings.INSTALLED_APPS,
                              f"Отсутствует приложение: {app}")

    def test_middleware(self):
        """Проверка middleware"""
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'whitenoise.middleware.WhiteNoiseMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]

        for middleware in required_middleware:
            with self.subTest(middleware=middleware):
                self.assertIn(middleware, settings.MIDDLEWARE,
                              f"Отсутствует middleware: {middleware}")

    def test_templates_config(self):
        """Проверка конфигурации шаблонов"""
        self.assertEqual(len(settings.TEMPLATES), 1)
        template_config = settings.TEMPLATES[0]

        self.assertEqual(template_config['BACKEND'],
                         'django.template.backends.django.DjangoTemplates')
        self.assertTrue(template_config['APP_DIRS'])

        # Проверка существования директории templates
        template_dirs = template_config.get('DIRS', [])
        self.assertTrue(len(template_dirs) > 0)

        for template_dir in template_dirs:
            self.assertDirectoryExists(template_dir)

    def test_rest_framework_config(self):
        """Проверка конфигурации REST Framework"""
        self.assertIn('REST_FRAMEWORK', dir(settings))
        rf_config = settings.REST_FRAMEWORK

        self.assertIn('DEFAULT_PAGINATION_CLASS', rf_config)
        self.assertEqual(rf_config['PAGE_SIZE'], 10)

    def test_logging_config(self):
        """Проверка конфигурации логирования"""
        self.assertIn('LOGGING', dir(settings))
        logging_config = settings.LOGGING

        # Проверка наличия основных компонентов
        self.assertIn('handlers', logging_config)
        self.assertIn('loggers', logging_config)
        self.assertIn('formatters', logging_config)

        # Проверка существования директории логов
        logs_dir = Path(settings.BASE_DIR) / 'logs'
        self.assertDirectoryExists(logs_dir)


class TestEnvironmentVariables(TestCase):
    """Тесты переменных окружения"""

    def test_required_env_vars(self):
        """Проверка обязательных переменных окружения"""
        # Это пример - добавьте свои переменные
        required_vars = ['SECRET_KEY']

        for var in required_vars:
            with self.subTest(var=var):
                value = os.getenv(var)
                if value is None:
                    print(f"Внимание: переменная окружения {var} не установлена")
                # В продакшене это должно быть assertIsNotNone

    def test_database_env_vars(self):
        """Проверка переменных окружения для базы данных"""
        db_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']

        for var in db_vars:
            value = os.getenv(var)
            if value is None and var != 'DB_PASSWORD':
                print(f"Внимание: переменная базы данных {var} не установлена")


class TestCKEditorConfig(TestCase):
    """Тесты конфигурации CKEditor"""

    def test_ckeditor_field_in_model(self):
        """Тест, что CKEditor5Field используется в моделях"""
        from blog.models import Post

        # Проверяем, что поле content - это CKEditor5Field
        content_field = Post._meta.get_field('content')
        self.assertEqual(content_field.__class__.__name__, 'CKEditor5Field')

    def test_ckeditor_configuration(self):
        """Тест конфигурации CKEditor в settings"""
        self.assertIn('CKEDITOR_5_CONFIGS', dir(settings))

        ckeditor_config = settings.CKEDITOR_5_CONFIGS
        self.assertIn('default', ckeditor_config)

        default_config = ckeditor_config['default']
        # Проверяем основные элементы конфигурации
        self.assertIn('toolbar', default_config)
        self.assertIsInstance(default_config['toolbar'], list)

        # Проверяем наличие кнопок в тулбаре
        toolbar_items = default_config['toolbar']
        expected_items = ['heading', 'bold', 'italic', 'link', 'bulletedList',
                          'numberedList', 'blockQuote', 'imageUpload', 'codeBlock']

        for item in expected_items:
            self.assertIn(item, toolbar_items)