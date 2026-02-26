from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    # Si el diccionario está vacío o no existe, devolvemos None sin que se rompa
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)