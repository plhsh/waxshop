from django import template

register = template.Library ()


# @register.filter (name='is_in_cart')
# def is_in_cart(product, cart):
#     keys = cart.keys ()
#     for id in keys:
#         if int (id) == product.id:
#             return True
#     return False;


@register.filter()
def cart_quantity(product, cart):
    return cart.get(str(product.id), '0')
