import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Управление лог-файлами'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            nargs='?',
            default='show',
            choices=['clear', 'show', 'list', 'size'],
            help='Действие: clear - очистить, show - показать, list - список, size - размер'
        )

    def handle(self, *args, **options):
        action = options['action']
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        log_file = os.path.join(log_dir, 'debug.log')

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        if action == 'clear':
            self.clear_logs(log_file, log_dir)
        elif action == 'show':
            self.show_logs(log_file)
        elif action == 'list':
            self.list_logs(log_dir)
        elif action == 'size':
            self.show_size(log_file)

    def clear_logs(self, log_file, log_dir):
        """Очистить основной лог-файл"""
        if os.path.exists(log_file):
            # Сохраняем старые логи в архивный файл перед очисткой
            import datetime
            archive_file = os.path.join(
                log_dir,
                f'debug_archive_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
            )

            with open(log_file, 'r') as f:
                content = f.read()
                if content.strip():
                    with open(archive_file, 'w') as af:
                        af.write(content)
                    self.stdout.write(
                        self.style.SUCCESS(f'Старые логи сохранены в {archive_file}')
                    )

            # Очищаем основной файл
            open(log_file, 'w').close()
            self.stdout.write(
                self.style.SUCCESS('Основной лог-файл очищен!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Лог-файл не найден. Создан новый.')
            )
            open(log_file, 'w').close()

    def show_logs(self, log_file, lines=50):
        """Показать последние N строк логов"""
        if os.path.exists(log_file):
            import subprocess
            try:
                result = subprocess.run(
                    ['tail', '-n', str(lines), log_file],
                    capture_output=True,
                    text=True
                )
                self.stdout.write(result.stdout)
                if not result.stdout.strip():
                    self.stdout.write('Лог-файл пуст.')
            except:
                # Fallback для Windows
                with open(log_file, 'r') as f:
                    all_lines = f.readlines()
                    for line in all_lines[-lines:]:
                        self.stdout.write(line)
        else:
            self.stdout.write(self.style.ERROR('Лог-файл не найден!'))

    def list_logs(self, log_dir):
        """Показать все лог-файлы"""
        if os.path.exists(log_dir):
            self.stdout.write(f'Файлы в папке {log_dir}:')
            for file in os.listdir(log_dir):
                file_path = os.path.join(log_dir, file)
                size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
                self.stdout.write(f'  {file} - {size / 1024:.2f} KB')
        else:
            self.stdout.write('Папка с логами не найдена.')

    def show_size(self, log_file):
        """Показать размер лог-файла"""
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            self.stdout.write(
                f'Размер {log_file}: {size / 1024 / 1024:.2f} MB'
            )
        else:
            self.stdout.write('Лог-файл не найден.')