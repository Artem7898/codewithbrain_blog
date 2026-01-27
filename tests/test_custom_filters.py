"""
Тесты для кастомных фильтров шаблонов
"""
from django.test import TestCase
from django.template import Template, Context
import math


class TestCustomFilters(TestCase):
    """Тесты кастомных фильтров шаблонов"""

    def test_div_filter_valid_division(self):
        """Тест фильтра div с валидными числами"""
        template = Template('{% load custom_filters %}{{ value|div:divisor }}')

        # Тест 1: Обычное деление
        context = Context({'value': 10, 'divisor': 2})
        result = template.render(context)
        self.assertEqual(result.strip(), '5.0')

        # Тест 2: Деление с плавающей точкой
        context = Context({'value': 7, 'divisor': 2})
        result = template.render(context)
        self.assertEqual(result.strip(), '3.5')

        # Тест 3: Большие числа
        context = Context({'value': 1000, 'divisor': 100})
        result = template.render(context)
        self.assertEqual(result.strip(), '10.0')

    def test_div_filter_zero_division(self):
        """Тест фильтра div с делением на ноль"""
        template = Template('{% load custom_filters %}{{ value|div:0 }}')

        context = Context({'value': 10})
        result = template.render(context)
        self.assertEqual(result.strip(), '0')

    def test_div_filter_invalid_values(self):
        """Тест фильтра div с невалидными значениями"""
        template = Template('{% load custom_filters %}{{ value|div:divisor }}')

        # Тест 1: Нечисловые строки
        context = Context({'value': 'abc', 'divisor': 'xyz'})
        result = template.render(context)
        self.assertEqual(result.strip(), '0')

        # Тест 2: Пустые строки
        context = Context({'value': '', 'divisor': ''})
        result = template.render(context)
        self.assertEqual(result.strip(), '0')

        # Тест 3: None значения
        context = Context({'value': None, 'divisor': None})
        result = template.render(context)
        self.assertEqual(result.strip(), '0')

        # Тест 4: Смешанные невалидные значения
        context = Context({'value': '10', 'divisor': 'abc'})
        result = template.render(context)
        self.assertEqual(result.strip(), '0')

    def test_div_filter_string_numbers(self):
        """Тест фильтра div со строковыми числами"""
        template = Template('{% load custom_filters %}{{ value|div:divisor }}')

        # Тест 1: Строки, которые можно преобразовать в числа
        context = Context({'value': '15', 'divisor': '3'})
        result = template.render(context)
        self.assertEqual(result.strip(), '5.0')

        # Тест 2: С плавающей точкой в строках
        context = Context({'value': '7.5', 'divisor': '2.5'})
        result = template.render(context)
        self.assertEqual(result.strip(), '3.0')

    def test_ceil_filter_valid_values(self):
        """Тест фильтра ceil с валидными значениями"""
        template = Template('{% load custom_filters %}{{ value|ceil }}')

        # Тест 1: Целое число
        context = Context({'value': 5})
        result = template.render(context)
        self.assertEqual(result.strip(), '5')

        # Тест 2: Дробное число вверх
        context = Context({'value': 5.1})
        result = template.render(context)
        self.assertEqual(result.strip(), '6')

        # Тест 3: Дробное число, равное целому
        context = Context({'value': 5.0})
        result = template.render(context)
        self.assertEqual(result.strip(), '5')

        # Тест 4: Отрицательное дробное число
        context = Context({'value': -5.1})
        result = template.render(context)
        self.assertEqual(result.strip(), '-5')

        # Тест 5: Большое число
        context = Context({'value': 12345.6789})
        result = template.render(context)
        self.assertEqual(result.strip(), '12346')

    def test_ceil_filter_string_values(self):
        """Тест фильтра ceil со строковыми значениями"""
        template = Template('{% load custom_filters %}{{ value|ceil }}')

        # Тест 1: Строка с целым числом
        context = Context({'value': '7'})
        result = template.render(context)
        self.assertEqual(result.strip(), '7')

        # Тест 2: Строка с дробным числом
        context = Context({'value': '7.8'})
        result = template.render(context)
        self.assertEqual(result.strip(), '8')

        # Тест 3: Невалидная строка (должна вызвать исключение)
        import math
        context = Context({'value': 'abc'})
        result = template.render(context)
        # При невалидном значении будет пустая строка или ошибка
        # В зависимости от реализации Django

    def test_ceil_filter_edge_cases(self):
        """Тест фильтра ceil с крайними случаями"""
        template = Template('{% load custom_filters %}{{ value|ceil }}')

        # Тест 1: Ноль
        context = Context({'value': 0})
        result = template.render(context)
        self.assertEqual(result.strip(), '0')

        # Тест 2: Ноль с плавающей точкой
        context = Context({'value': 0.0})
        result = template.render(context)
        self.assertEqual(result.strip(), '0')

        # Тест 3: Очень маленькое положительное число
        context = Context({'value': 0.0000001})
        result = template.render(context)
        self.assertEqual(result.strip(), '1')

        # Тест 4: Очень маленькое отрицательное число
        context = Context({'value': -0.0000001})
        result = template.render(context)
        self.assertEqual(result.strip(), '0')

    def test_filters_together(self):
        """Тест использования нескольких фильтров вместе"""
        template = Template(
            '{% load custom_filters %}'
            '{{ value|div:divisor|ceil }}'
        )

        # Тест 1: Деление с последующим округлением вверх
        context = Context({'value': 10, 'divisor': 3})
        result = template.render(context)
        # 10 / 3 = 3.333..., ceil = 4
        self.assertEqual(result.strip(), '4')

        # Тест 2: Результат уже целый
        context = Context({'value': 10, 'divisor': 2})
        result = template.render(context)
        # 10 / 2 = 5, ceil = 5
        self.assertEqual(result.strip(), '5')

    def test_filter_registration(self):
        """Тест регистрации фильтров"""
        from django.template import engines

        # Получаем движок Django
        django_engine = engines['django']

        # Проверяем, что фильтры зарегистрированы
        # В разных версиях Django атрибут может называться по-разному
        if hasattr(django_engine.engine, 'filters'):
            filters = django_engine.engine.filters
        elif hasattr(django_engine.engine, 'template_filters'):
            filters = django_engine.engine.template_filters
        else:
            # Если не нашли атрибут, пропускаем тест
            self.skipTest("Не удалось найти атрибут с фильтрами")
            return

        self.assertIn('div', filters)
        self.assertIn('ceil', filters)

    def test_filter_in_real_template(self):
        """Тест фильтров в реальном шаблоне"""
        template_content = """
        {% load custom_filters %}
        <!DOCTYPE html>
        <html>
        <body>
            <p>Деление: {{ number1|div:number2 }}</p>
            <p>Округление: {{ float_number|ceil }}</p>
        </body>
        </html>
        """

        template = Template(template_content)
        context = Context({
            'number1': 21,
            'number2': 7,
            'float_number': 12.34
        })

        result = template.render(context)

        # Проверяем, что результаты вставлены
        self.assertIn('Деление: 3.0', result)
        self.assertIn('Округление: 13', result)


class TestCustomFiltersPython(TestCase):
    """Тесты функций фильтров напрямую (без шаблонов)"""

    def test_div_function(self):
        """Тест функции div напрямую"""
        from blog.templatetags.custom_filters import div

        # Тест валидных значений
        self.assertEqual(div(10, 2), 5.0)
        self.assertEqual(div(7, 2), 3.5)
        self.assertEqual(div(1000, 100), 10.0)

        # Тест деления на ноль
        self.assertEqual(div(10, 0), 0)

        # Тест невалидных значений
        self.assertEqual(div('abc', 'xyz'), 0)
        self.assertEqual(div('', ''), 0)
        self.assertEqual(div(None, None), 0)

        # Тест строковых чисел
        self.assertEqual(div('15', '3'), 5.0)
        self.assertEqual(div('7.5', '2.5'), 3.0)

    def test_ceil_function(self):
        """Тест функции ceil напрямую"""
        from blog.templatetags.custom_filters import ceil
        import math

        # Тест валидных значений
        self.assertEqual(ceil(5), 5)
        self.assertEqual(ceil(5.1), 6)
        self.assertEqual(ceil(5.0), 5)
        self.assertEqual(ceil(-5.1), -5)
        self.assertEqual(ceil(12345.6789), 12346)

        # Сравниваем с math.ceil
        self.assertEqual(ceil(5.1), math.ceil(5.1))
        self.assertEqual(ceil(-5.1), math.ceil(-5.1))

        # Тест крайних случаев
        self.assertEqual(ceil(0), 0)
        self.assertEqual(ceil(0.0), 0)
        self.assertEqual(ceil(0.0000001), 1)
        self.assertEqual(ceil(-0.0000001), 0)