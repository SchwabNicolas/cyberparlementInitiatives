from django import template

register = template.Library()


@register.filter
def percentage(value):
    return format(value, ".0%")


@register.filter
def add_one(value):
    return value + 1
