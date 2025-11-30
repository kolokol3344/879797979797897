from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """
    Розділяє рядок по роздільнику
    Використання: {{ product.sizes|split:"," }}
    """
    if value:
        return value.split(arg)
    return []

@register.filter(name='trim')
def trim(value):
    """
    Видаляє пробіли на початку та в кінці рядка
    Використання: {{ text|trim }}
    """
    if value:
        return value.strip()
    return value