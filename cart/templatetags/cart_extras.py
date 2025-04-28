# cart/templatetags/cart_extras.py

from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def mul(value, arg):
    """
    Multiply two values as Decimals so we can do:
      {{ quantity|mul:unit_price }}
    even if unit_price is a Decimal.
    """
    try:
        return Decimal(value) * Decimal(arg)
    except Exception:
        return Decimal('0.00')
