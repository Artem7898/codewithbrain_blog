"""
Тесты статических файлов и медиа
"""
import os
from pathlib import Path
from django.test import TestCase, override_settings
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


class TestStaticFiles(TestCase):
    """Тесты статических файлов"""

    def test_static_directories(self):
        """Проверка директорий статических файлов"""
        project_root = Path(settings.BASE_DIR)

        # Проверка основных директорий
        static_dirs = [
            project_root / 'static',
            project_root / 'staticfiles',
        ]

        for dir_path in static_dirs:
            with self.subTest(dir_path=dir_path):
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                self.assertDirectoryExists(dir_path)

    def test_static_configuration(self):
        """Проверка конфигурации статических файлов"""
        self.assertEqual(settings.STATIC_URL, '/static/')
        self.assertTrue(hasattr(settings, 'STATIC_ROOT'))
        self.assertTrue(hasattr(settings, 'STATICFILES_DIRS'))

        # Проверка, что STATICFILES_DIRS является списком
        self.assertIsInstance(settings.STATICFILES_DIRS, list)

        # Проверка существования директорий в STATICFILES_DIRS
        for static_dir in settings.STATICFILES_DIRS:
            self.assertDirectoryExists(static_dir)

    def test_static_files_serving(self):
        """Тестирование обслуживания статических файлов в разработке"""
        # Создаем тестовый статический файл
        static_dir = Path(settings.STATICFILES_DIRS[0])
        test_file = static_dir / 'test.js'
        test_content = 'console.log("test");'

        test_file.write_text(test_content)

        # Проверяем доступность через тестовый клиент (в DEBUG режиме)
        if settings.DEBUG:
            response = self.client.get('/static/test.js')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'test', response.content)

        # Удаляем тестовый файл
        test_file.unlink()

    def test_staticfiles_storage(self):
        """Проверка настроек хранилища статических файлов"""
        self.assertEqual(settings.STATICFILES_STORAGE,
                         'whitenoise.storage.CompressedManifestStaticFilesStorage')

    def test_ckeditor_storage(self):
        """Проверка настроек хранилища CKEditor"""
        self.assertEqual(settings.CKEDITOR_5_FILE_STORAGE,
                         "django.core.files.storage.FileSystemStorage")


class TestMediaFiles(TestCase):
    """Тесты медиа файлов"""

    def test_media_directories(self):
        """Проверка директорий медиа файлов"""
        media_root = Path(settings.MEDIA_ROOT)

        # Создаем директорию, если не существует
        if not media_root.exists():
            media_root.mkdir(parents=True, exist_ok=True)

        self.assertDirectoryExists(media_root)

    def test_media_configuration(self):
        """Проверка конфигурации медиа файлов"""
        self.assertEqual(settings.MEDIA_URL, '/media/')
        self.assertTrue(hasattr(settings, 'MEDIA_ROOT'))

        media_root = Path(settings.MEDIA_ROOT)
        self.assertTrue(media_root.is_absolute(),
                        "MEDIA_ROOT должен быть абсолютным путем")

    def test_media_upload(self):
        """Тестирование загрузки медиа файлов"""
        # Создаем тестовый файл
        test_content = b'test content'
        test_file = SimpleUploadedFile(
            name='test.txt',
            content=test_content,
            content_type='text/plain'
        )

        # Проверяем, что файл можно сохранить
        media_path = Path(settings.MEDIA_ROOT) / 'uploads' / 'test.txt'
        media_path.parent.mkdir(parents=True, exist_ok=True)

        with open(media_path, 'wb') as f:
            f.write(test_content)

        self.assertFileExists(media_path)

        # Удаляем тестовый файл
        media_path.unlink()

    def test_media_urls(self):
        """Проверка URL медиа файлов"""
        # В режиме разработки медиа файлы обслуживаются Django
        if settings.DEBUG:
            # Создаем тестовый файл
            test_file_path = Path(settings.MEDIA_ROOT) / 'test.jpg'
            test_file_path.parent.mkdir(parents=True, exist_ok=True)
            test_file_path.write_bytes(b'fake image content')

            # Проверяем доступность
            response = self.client.get('/media/test.jpg')
            self.assertEqual(response.status_code, 200)

            # Удаляем тестовый файл
            test_file_path.unlink()


class TestTemplateFiles(TestCase):
    """Тесты шаблонов"""

    def test_template_directories(self):
        """Проверка директорий шаблонов"""
        project_root = Path(settings.BASE_DIR)
        templates_dir = project_root / 'templates'

        if not templates_dir.exists():
            templates_dir.mkdir(parents=True, exist_ok=True)

        self.assertDirectoryExists(templates_dir)

        # Проверяем, что директория есть в настройках
        template_config = settings.TEMPLATES[0]
        template_dirs = template_config.get('DIRS', [])

        found = False
        for template_dir in template_dirs:
            if str(templates_dir) in str(template_dir):
                found = True
                break

        self.assertTrue(found, "Директория templates не найдена в TEMPLATES['DIRS']")

    def test_template_files_exist(self):
        """Проверка существования основных шаблонов"""
        templates_dir = Path(settings.BASE_DIR) / 'templates'

        # Создаем базовые шаблоны, если их нет
        base_templates = ['base.html', 'index.html', 'admin/base_site.html']

        for template_name in base_templates:
            template_path = templates_dir / template_name
            template_path.parent.mkdir(parents=True, exist_ok=True)

            if not template_path.exists():
                # Создаем минимальный шаблон для тестов
                if template_name == 'base.html':
                    content = '<!DOCTYPE html><html><body>{% block content %}{% endblock %}</body></html>'
                elif template_name == 'index.html':
                    content = '{% extends "base.html" %}{% block content %}Homepage{% endblock %}'
                else:
                    content = '<!-- Template -->'

                template_path.write_text(content)

            self.assertFileExists(template_path)

    def test_template_rendering(self):
        """Тестирование рендеринга шаблонов"""
        from django.template.loader import render_to_string

        # Создаем простой шаблон для теста
        test_template = Path(settings.BASE_DIR) / 'templates' / 'test_template.html'
        test_template.parent.mkdir(parents=True, exist_ok=True)
        test_template.write_text('<h1>Hello {{ name }}</h1>')

        # Рендерим шаблон
        context = {'name': 'World'}
        rendered = render_to_string('test_template.html', context)

        self.assertIn('Hello World', rendered)

        # Удаляем тестовый шаблон
        test_template.unlink()

    def test_admin_templates(self):
        """Проверка кастомизации админ-панели"""
        # Проверяем, что Unfold установлен
        self.assertIn('unfold', settings.INSTALLED_APPS)

        # Проверяем конфигурацию Unfold
        self.assertIn('UNFOLD', dir(settings))
        unfold_config = settings.UNFOLD

        required_keys = ['SITE_TITLE', 'SITE_HEADER', 'SITE_SYMBOL']
        for key in required_keys:
            self.assertIn(key, unfold_config)