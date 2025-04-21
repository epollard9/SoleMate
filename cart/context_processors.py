from .models import CartItem

def cart_item_count(request):
    if request.user.is_authenticated:
        count = sum(item.quantity for item in CartItem.objects.filter(user=request.user))
    else:
        cart = request.session.get('cart', {})
        count = sum(cart.values())
    return {
        'cart_item_count': count
    }
