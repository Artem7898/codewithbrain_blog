"""
Тесты для middleware блога
"""
import time
from unittest.mock import Mock, patch
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from blog.middleware import AdminAccessLogMiddleware


class TestAdminAccessLogMiddleware(TestCase):
    """Тесты AdminAccessLogMiddleware"""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = AdminAccessLogMiddleware(lambda r: None)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Mock логгера
        self.logger_patcher = patch('blog.middleware.access_logger')
        self.mock_logger = self.logger_patcher.start()

    def tearDown(self):
        self.logger_patcher.stop()

    def test_process_request_sets_start_time(self):
        """Тест, что process_request устанавливает start_time"""
        request = self.factory.get('/admin/')

        # Проверяем, что start_time не установлен
        self.assertFalse(hasattr(request, 'start_time'))

        # Вызываем process_request
        self.middleware.process_request(request)

        # Проверяем, что start_time установлен
        self.assertTrue(hasattr(request, 'start_time'))
        self.assertIsInstance(request.start_time, float)

    def test_process_response_logs_admin_access(self):
        """Тест логирования доступа к админке"""
        request = self.factory.get('/admin/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        # Устанавливаем start_time
        request.start_time = time.time()

        # Mock ответ
        response = Mock()
        response.status_code = 200

        # Вызываем process_response
        result = self.middleware.process_response(request, response)

        # Проверяем, что вернулся тот же response
        self.assertEqual(result, response)

        # Проверяем, что логгер был вызван
        self.mock_logger.info.assert_called_once()

        # Проверяем параметры логирования
        call_args = self.mock_logger.info.call_args
        self.assertEqual(call_args[0], ('',))

        # Проверяем extra данные
        extra = call_args[1]['extra']
        self.assertEqual(extra['method'], 'GET')
        self.assertEqual(extra['path'], '/admin/')
        self.assertEqual(extra['status_code'], 200)
        self.assertEqual(extra['user'], 'testuser')
        self.assertEqual(extra['ip'], '127.0.0.1')
        self.assertIsInstance(extra['duration'], float)
        self.assertGreaterEqual(extra['duration'], 0)

    def test_process_response_logs_anonymous_user(self):
        """Тест логирования анонимного пользователя"""
        request = self.factory.get('/admin/')
        request.user = Mock(is_authenticated=False)
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.start_time = time.time()

        response = Mock()
        response.status_code = 404

        self.middleware.process_response(request, response)

        # Проверяем, что пользователь записан как Anonymous
        call_args = self.mock_logger.info.call_args
        extra = call_args[1]['extra']
        self.assertEqual(extra['user'], 'Anonymous')
        self.assertEqual(extra['status_code'], 404)

    def test_process_response_skips_non_admin_paths(self):
        """Тест, что не-админские пути не логируются"""
        request = self.factory.get('/blog/')
        request.user = self.user
        request.start_time = time.time()

        response = Mock()
        response.status_code = 200

        self.middleware.process_response(request, response)

        # Логгер не должен быть вызван
        self.mock_logger.info.assert_not_called()

    def test_process_response_handles_exception(self):
        """Тест обработки исключений при логировании"""
        request = self.factory.get('/admin/')
        request.start_time = time.time()

        # Заставляем логгер.info вызвать исключение
        self.mock_logger.info.side_effect = Exception("Test error")

        response = Mock()
        response.status_code = 200

        # Проверяем, что исключение не прокидывается
        try:
            result = self.middleware.process_response(request, response)
            self.assertEqual(result, response)
        except Exception:
            self.fail("Исключение не должно прокидываться")

        # Проверяем, что error был залогирован
        self.mock_logger.error.assert_called_once()
        error_call = self.mock_logger.error.call_args[0][0]
        self.assertIn('Ошибка при логировании доступа', error_call)

    def test_process_response_no_start_time(self):
        """Тест, когда start_time не установлен"""
        request = self.factory.get('/admin/')
        request.user = self.user

        # Не устанавливаем start_time

        response = Mock()
        response.status_code = 200

        self.middleware.process_response(request, response)

        # Проверяем, что логирование все равно работает
        self.mock_logger.info.assert_called_once()

        call_args = self.mock_logger.info.call_args
        extra = call_args[1]['extra']
        self.assertIsInstance(extra['duration'], float)

    def test_middleware_chain(self):
        """Тест работы middleware в цепочке"""

        # Создаем простое приложение
        def simple_app(request):
            response = Mock()
            response.status_code = 200
            return response

        # Создаем middleware с реальным приложением
        middleware = AdminAccessLogMiddleware(simple_app)

        request = self.factory.get('/admin/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        # Вызываем middleware
        response = middleware(request)

        # Проверяем, что response возвращен
        self.assertEqual(response.status_code, 200)

        # Проверяем, что было логирование
        self.mock_logger.info.assert_called_once()


class TestMiddlewareIntegration(TestCase):
    """Интеграционные тесты middleware"""

    def test_middleware_in_request_cycle(self):
        """Тест middleware в полном цикле запроса"""
        from django.test.client import Client

        client = Client()

        # Создаем суперпользователя и логинемся
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

        client.login(username='admin', password='admin123')

        # Делаем запрос к админке
        response = client.get('/admin/', follow=True)

        # Проверяем, что запрос прошел
        self.assertEqual(response.status_code, 200)

        # Проверяем, что логи создались (если настроено логирование в тестах)
        # Это зависит от вашей конфигурации logging в settings.py

    def test_multiple_admin_requests(self):
        """Тест множественных запросов к админке"""
        request1 = RequestFactory().get('/admin/')
        request2 = RequestFactory().get('/admin/blog/post/')

        middleware = AdminAccessLogMiddleware(lambda r: Mock(status_code=200))

        # Обрабатываем первый запрос
        response1 = middleware(request1)

        # Обрабатываем второй запрос
        response2 = middleware(request2)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)