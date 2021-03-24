from django import template

register = template.Library()


@register.filter
def percentage(value):
    """
    Formate un nombre en pourcentage.

    :param value: valeur
    :return: valeur formatée
    """

    return format(value, ".0%")


@register.filter
def add_one(value):
    """
    Ajoute 1 à la valeur donnée.

    :param value: valeur
    :return: valeur + 1
    """
    return value + 1
