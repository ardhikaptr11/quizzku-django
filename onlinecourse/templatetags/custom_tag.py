from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def to_alphabet(value):
    return f"{chr(64 + value)})." if 1 <= value <= 26 else value
