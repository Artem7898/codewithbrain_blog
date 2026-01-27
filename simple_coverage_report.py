
"""
Упрощенный скрипт для анализа покрытия
"""
import os
import subprocess
import sys


def run_coverage_analysis():
    """Запуск анализа покрытия через команду coverage"""

    print("📊 АНАЛИЗ ПОКРЫТИЯ КОДА TESTS")
    print("=" * 80)

    # Проверяем, установлен ли coverage
    try:
        import coverage
        print(f"✓ coverage.py версия {coverage.__version__}")
    except ImportError:
        print("❌ coverage не установлен!")
        print("Установите: pip install coverage")
        return

    # Проверяем наличие файла .coverage
    if not os.path.exists('.coverage'):
        print("❌ Файл .coverage не найден!")
        print("\nСначала запустите тесты с покрытием:")
        print("   pytest tests/ --cov=blog --cov=config")
        print("   или")
        print("   python -m pytest --cov=blog --cov=config tests/")
        return

    # Запускаем команды coverage
    commands = [
        ("📋 Краткий отчет", ["coverage", "report"]),
        ("📊 Подробный отчет", ["coverage", "report", "--show-missing"]),
        ("📈 HTML отчет", ["coverage", "html", "-d", "test_reports/coverage_html"]),
        ("📄 XML отчет", ["coverage", "xml", "-o", "test_reports/coverage.xml"]),
    ]

    # Создаем директорию для отчетов
    os.makedirs("test_reports", exist_ok=True)

    for name, cmd in commands:
        print(f"\n{name}:")
        print("-" * 40)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("Ошибки:", result.stderr)
        except Exception as e:
            print(f"Ошибка при выполнении команды: {e}")

    # Анализируем результаты
    print("\n" + "=" * 80)
    print("📊 СВОДКА ПОКРЫТИЯ:")
    print("-" * 80)

    try:
        cov = coverage.Coverage()
        cov.load()

        # Получаем отчет в виде словаря
        summary = {}
        total_statements = 0
        total_missing = 0

        for file in cov.get_data().measured_files():
            file_str = str(file)
            if 'tests' in file_str or '.venv' in file_str or '/site-packages/' in file_str:
                continue

            analysis = cov.analysis(file)
            if analysis:
                statements, excluded, missing, missing_str, _ = analysis
                if statements:
                    covered = len(statements) - len(missing)
                    percentage = (covered / len(statements)) * 100

                    summary[file_str] = {
                        'statements': len(statements),
                        'covered': covered,
                        'missing': len(missing),
                        'percentage': percentage
                    }

                    total_statements += len(statements)
                    total_missing += len(missing)

        # Выводим самые проблемные файлы
        if summary:
            sorted_files = sorted(summary.items(), key=lambda x: x[1]['percentage'])

            print("\n📉 ФАЙЛЫ С НИЗКИМ ПОКРЫТИЕМ (<80%):")
            for file, stats in sorted_files:
                if stats['percentage'] < 80:
                    print(f"   • {os.path.basename(file)}: {stats['percentage']:.1f}% "
                          f"({stats['missing']} непокрытых строк)")

            # Общая статистика
            if total_statements > 0:
                total_percentage = ((total_statements - total_missing) / total_statements) * 100
                print(f"\n📊 ОБЩЕЕ ПОКРЫТИЕ: {total_percentage:.1f}%")

                # Рекомендации
                print("\n🎯 РЕКОМЕНДАЦИИ:")
                if total_percentage < 70:
                    print("   ❌ Срочно улучшайте покрытие!")
                    print("   Начните с файлов с самым низким покрытием")
                elif total_percentage < 80:
                    print("   ⚠️  Покрытие ниже рекомендуемого уровня 80%")
                    print("   Добавьте тесты для приоритетных файлов")
                elif total_percentage < 90:
                    print("   ✅ Хороший уровень покрытия")
                    print("   Можно улучшить отдельные модули")
                else:
                    print("   🏆 Отличное покрытие! Так держать!")

    except Exception as e:
        print(f"Ошибка при анализе: {e}")

    print("\n" + "=" * 80)
    print("✅ Отчеты сохранены в папке test_reports/")
    print("   Для просмотра откройте: test_reports/coverage_html/index.html")


if __name__ == '__main__':
    run_coverage_analysis()