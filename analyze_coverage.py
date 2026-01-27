# analyze_coverage.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""
Скрипт для анализа покрытия кода тестами
"""
import os
import sys
import json
from pathlib import Path
import coverage

def analyze_coverage_db():
    """Анализ файла .coverage"""
    if not os.path.exists('.coverage'):
        print("Файл .coverage не найден!")
        print("Запустите сначала: pytest tests/ --cov=blog --cov=config")
        return

    # Используем coverage.py для анализа
    cov = coverage.Coverage()
    cov.load()

    print("=" * 80)
    print("АНАЛИЗ ПОКРЫТИЯ КОДА TESTS")
    print("=" * 80)

    # Получаем отчет в виде словаря
    print("\n1. Сводка по файлам:")
    print("-" * 80)

    # Получаем все файлы
    files = list(cov.get_data().measured_files())

    # Фильтруем файлы тестов и виртуального окружения
    source_files = []
    for file in files:
        file_str = str(file)
        if 'tests' in file_str or '.venv' in file_str or '/site-packages/' in file_str:
            continue
        source_files.append(file)

    # Группируем файлы по директориям
    files_by_dir = {}
    for file in source_files:
        file_path = Path(file)
        dir_name = str(file_path.parent)
        if dir_name not in files_by_dir:
            files_by_dir[dir_name] = []
        files_by_dir[dir_name].append(file)

    # Выводим отчет по директориям
    for dir_name, dir_files in sorted(files_by_dir.items()):
        print(f"\n📁 {dir_name}:")
        dir_total = 0
        dir_covered = 0

        for file in sorted(dir_files):
            # Получаем анализ для файла
            analysis = cov.analysis(file)
            if analysis:
                statements, excluded, missing, missing_str, _ = analysis

                if statements:
                    covered = len(statements) - len(missing)
                    percentage = (covered / len(statements)) * 100 if statements else 0

                    file_name = Path(file).name
                    status = "✅" if percentage >= 80 else "⚠️ " if percentage >= 50 else "❌"

                    print(f"   {status} {file_name}: {covered}/{len(statements)} ({percentage:.1f}%)")

                    if percentage < 80 and missing:
                        # Показываем первые 5 непокрытых строк
                        missing_preview = sorted(missing)[:5]
                        print(f"      Непокрытые строки: {missing_preview}")
                        if len(missing) > 5:
                            print(f"      ... и еще {len(missing) - 5} строк")

                    dir_total += len(statements)
                    dir_covered += covered

        if dir_total > 0:
            dir_percentage = (dir_covered / dir_total) * 100
            print(f"   Итого по директории: {dir_covered}/{dir_total} ({dir_percentage:.1f}%)")

    # Общая статистика
    print("\n" + "=" * 80)
    print("ОБЩАЯ СТАТИСТИКА:")
    print("-" * 80)

    # Используем встроенную функцию отчетности
    from io import StringIO
    import sys

    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        cov.report(show_missing=True, skip_covered=False)
        report_output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    print(report_output)

    # Получаем общую статистику
    total_stats = cov.get_data()
    total_statements = 0
    total_missing = 0

    for file in source_files:
        analysis = cov.analysis(file)
        if analysis:
            statements, excluded, missing, missing_str, _ = analysis
            total_statements += len(statements)
            total_missing += len(missing)

    if total_statements > 0:
        total_covered = total_statements - total_missing
        total_percentage = (total_covered / total_statements) * 100

        print(f"\n📊 Итоговое покрытие: {total_covered}/{total_statements} строк ({total_percentage:.1f}%)")

        # Рекомендации
        print("\n" + "=" * 80)
        print("РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ ПОКРЫТИЯ:")
        print("-" * 80)

        if total_percentage < 70:
            print("❌ КРИТИЧЕСКИ НИЗКОЕ ПОКРЫТИЕ (<70%)")
            print("   Необходимо срочно написать тесты для:")
        elif total_percentage < 80:
            print("⚠️  НИЗКОЕ ПОКРЫТИЕ (70-80%)")
            print("   Рекомендуется улучшить покрытие для:")
        elif total_percentage < 90:
            print("✅ ХОРОШЕЕ ПОКРЫТИЕ (80-90%)")
            print("   Можно улучшить покрытие в:")
        else:
            print("🏆 ОТЛИЧНОЕ ПОКРЫТИЕ (>90%)")
            print("   Поддерживайте текущий уровень!")

        # Находим файлы с самым низким покрытием
        low_coverage_files = []
        for file in source_files:
            analysis = cov.analysis(file)
            if analysis:
                statements, excluded, missing, missing_str, _ = analysis
                if statements:
                    percentage = (len(statements) - len(missing)) / len(statements) * 100
                    if percentage < 80:
                        low_coverage_files.append((file, percentage, len(missing)))

        if low_coverage_files:
            low_coverage_files.sort(key=lambda x: x[1])  # Сортируем по возрастанию покрытия
            print("\n📋 Приоритетные файлы для тестирования:")
            for file, percentage, missing_count in low_coverage_files[:10]:  # Топ-10
                file_name = Path(file).name
                print(f"   • {file_name}: {percentage:.1f}% ({missing_count} непокрытых строк)")

        # Конкретные рекомендации
        print("\n🔧 Конкретные рекомендации:")
        print("   1. Для blog/middleware.py (0%) - напишите тесты для AdminAccessLogMiddleware")
        print("   2. Для blog/signals.py (51%) - протестируйте все сигналы логирования")
        print("   3. Для blog/views.py (59%) - добавьте тесты для всех view функций")
        print("   4. Для blog/api.py (77%) - протестируйте оставшиеся API endpoints")
        print("   5. Для blog/models.py (82%) - добавьте тесты для edge cases моделей")

    # Генерация отчетов
    print("\n" + "=" * 80)
    print("ГЕНЕРАЦИЯ ОТЧЕТОВ:")
    print("-" * 80)

    # Создаем директорию для отчетов
    reports_dir = Path('test_reports')
    reports_dir.mkdir(exist_ok=True)

    # Генерируем различные отчеты
    print("📊 Генерация HTML отчета...")
    cov.html_report(directory=str(reports_dir / 'coverage_html'))

    print("📄 Генерация XML отчета (для CI/CD)...")
    cov.xml_report(outfile=str(reports_dir / 'coverage.xml'))

    print("📋 Генерация JSON отчета...")
    cov.json_report(outfile=str(reports_dir / 'coverage.json'))

    print("📝 Генерация текстового отчета...")
    with open(reports_dir / 'coverage.txt', 'w') as f:
        f.write(report_output)

    print(f"\n✅ Отчеты сохранены в {reports_dir}/")
    print(f"   Откройте в браузере: {reports_dir}/coverage_html/index.html")

    # Дополнительная информация
    print("\n" + "=" * 80)
    print("ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:")
    print("-" * 80)

    # Проверяем настройки coverage
    config_file = '.coveragerc'
    if os.path.exists(config_file):
        print(f"✓ Используется конфигурационный файл: {config_file}")
    else:
        print("⚠️ Конфигурационный файл .coveragerc не найден")
        print("   Создайте его для настройки параметров coverage")

    # Проверяем версию coverage
    import coverage as cov_module
    print(f"✓ Версия coverage.py: {cov_module.__version__}")

def main():
    """Основная функция"""
    print("🔍 Анализ покрытия кода тестами CodeWithBrain")
    print("=" * 80)

    if not os.path.exists('.coverage'):
        print("Файл .coverage не найден!")
        print("\nДля создания файла покрытия выполните:")
        print("1. pytest tests/ --cov=blog --cov=config")
        print("2. Или: python -m pytest --cov=blog --cov=config tests/")
        print("\nСначала запустите тесты:")
        print("   pip install pytest pytest-cov")
        print("   pytest tests/ --cov=blog --cov=config")
        return

    # Выполняем анализ
    analyze_coverage_db()

    print("\n" + "=" * 80)
    print("✅ Анализ завершен!")
    print("=" * 80)

if __name__ == '__main__':
    main()