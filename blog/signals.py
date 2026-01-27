import logging
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils.encoding import force_str


# Получаем логгер для админки
admin_logger = logging.getLogger('admin_logger')
access_logger = logging.getLogger('access_logger')

# Словарь для преобразования флагов действий
ACTION_FLAGS = {
    ADDITION: 'ADDITION',
    CHANGE: 'CHANGE',
    DELETION: 'DELETION',
}


@receiver(post_save, sender=LogEntry)
def log_admin_action(sender, instance, created, **kwargs):
    """
    Логирует действия в админ-панели через модель LogEntry
    """
    if created:  # Только для новых записей LogEntry
        try:
            user = instance.user.username if instance.user else 'Anonymous'
            action = ACTION_FLAGS.get(instance.action_flag, 'UNKNOWN')

            # Получаем название модели
            try:
                model = ContentType.objects.get_for_id(instance.content_type_id)
                model_name = model.model
            except:
                model_name = 'Unknown'

            # Формируем детали
            details = instance.change_message[:200] if instance.change_message else 'No details'

            # Логируем действие
            admin_logger.info(
                '',
                extra={
                    'user': user,
                    'action': action,
                    'model': model_name,
                    'object_id': instance.object_id,
                    'details': details,
                }
            )

        except Exception as e:
            admin_logger.error(f'Ошибка при логировании действия админки: {e}')


@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    """
    Логирует создание/изменение пользователей
    """
    if created:
        admin_logger.info(
            '',
            extra={
                'user': 'System' if not instance.username else instance.username,
                'action': 'USER_CREATED',
                'model': 'User',
                'object_id': instance.id,
                'details': f'Создан пользователь: {instance.username}',
            }
        )
    else:
        # Можно логировать изменения пользователей
        pass


# Логирование входа/выхода пользователей
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    admin_logger.info(
        '',
        extra={
            'user': user.username,
            'action': 'LOGIN',
            'model': 'User',
            'object_id': user.id,
            'details': f'Успешный вход с IP: {request.META.get("REMOTE_ADDR")}',
        }
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        admin_logger.info(
            '',
            extra={
                'user': user.username,
                'action': 'LOGOUT',
                'model': 'User',
                'object_id': user.id,
                'details': f'Выход с IP: {request.META.get("REMOTE_ADDR")}',
            }
        )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    admin_logger.warning(
        '',
        extra={
            'user': credentials.get('username', 'Unknown'),
            'action': 'LOGIN_FAILED',
            'model': 'User',
            'object_id': 'N/A',
            'details': f'Неудачная попытка входа с IP: {request.META.get("REMOTE_ADDR")}',
        }
    )