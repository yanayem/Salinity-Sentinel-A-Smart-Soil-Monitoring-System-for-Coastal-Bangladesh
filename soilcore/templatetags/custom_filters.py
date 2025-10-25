# E:\SDP_200\soilcore\soilcore\templatetags\custom_filters.py
from django import template

register = template.Library()

# ----------------- GET DICTIONARY ITEM -----------------
@register.filter
def get_item(dictionary, key):
    """
    Returns value from dictionary by key.
    Usage in template: {{ my_dict|get_item:my_key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

# ----------------- pH ALERT CHECK -----------------
@register.filter
def ph_alert(ph):
    """
    Returns True if pH is out of safe range (6.0 - 7.5)
    """
    try:
        ph = float(ph)
        return ph < 6.0 or ph > 7.5
    except (TypeError, ValueError):
        return False

# ----------------- JOIN LIST OF CROPS -----------------
@register.filter
def join_crops(crops):
    if isinstance(crops, list):
        return ', '.join(str(c) for c in crops)
    return crops
