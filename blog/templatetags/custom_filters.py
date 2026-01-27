from django import template

register = template.Library()

@register.filter
def div(value, arg):
    """Деление value на arg"""
    try:
        if value is None or arg is None:
            return 0
        # Пробуем преобразовать в float для поддержки десятичных
        numerator = float(value) if str(value).strip() != '' else 0
        denominator = float(arg) if str(arg).strip() != '' else 1
        if denominator == 0:
            return 0
        return numerator / denominator
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def ceil(value):
    """Округление вверх"""
    import math
    try:
        # Пытаемся преобразовать к числу
        if value is None:
            return 0
        return math.ceil(float(value))
    except (ValueError, TypeError):
        return 0