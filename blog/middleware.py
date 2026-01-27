import time
import logging
from django.utils.deprecation import MiddlewareMixin

access_logger = logging.getLogger('access_logger')


class AdminAccessLogMiddleware(MiddlewareMixin):
    """
    Middleware для логирования доступа к админ-панели
    """

    def process_request(self, request):
        # Начинаем отсчет времени для измерения длительности запроса
        request.start_time = time.time()

    def process_response(self, request, response):
        # Логируем только запросы к админке
        if request.path.startswith('/admin'):
            try:
                duration = time.time() - getattr(request, 'start_time', time.time())

                # Получаем информацию о пользователе
                user = 'Anonymous'
                if hasattr(request, 'user') and request.user.is_authenticated:
                    user = request.user.username

                # Логируем информацию о запросе
                access_logger.info(
                    '',
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code,
                        'duration': duration,
                        'user': user,
                        'ip': request.META.get('REMOTE_ADDR', 'Unknown'),
                    }
                )
            except Exception as e:
                access_logger.error(f'Ошибка при логировании доступа: {e}')

        return response