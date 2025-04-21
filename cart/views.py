from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Shoe
from django.http import JsonResponse
from .models import CartItem

def add_to_cart(request):
    shoe_id = request.POST.get('shoe_id')
    quantity = int(request.POST.get('quantity', 1))
    shoe = get_object_or_404(Shoe, pk=shoe_id)

    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(user=request.user, shoe=shoe)
        cart_item.quantity += quantity
        cart_item.save()
        count = sum(item.quantity for item in CartItem.objects.filter(user=request.user))
    else:
        cart = request.session.get('cart', {})
        if shoe_id in cart:
            cart[shoe_id] += quantity
        else:
            cart[shoe_id] = quantity
        request.session['cart'] = cart
        count = sum(cart.values())

    return JsonResponse({'success': True, 'cartCount': count})


def remove_from_cart(request, shoe_id):
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user, shoe_id=shoe_id).delete()
    else:
        cart = request.session.get('cart', {})
        if shoe_id in cart:
            del cart[shoe_id]
        request.session['cart'] = cart

    return redirect('cart:view_cart')


def view_cart(request):
    cart_items = []
    total = 0

    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user)
        for item in items:
            subtotal = item.shoe.price * item.quantity
            total += subtotal
            cart_items.append({'shoe': item.shoe, 'quantity': item.quantity, 'subtotal': subtotal})
    else:
        cart = request.session.get('cart', {})
        for shoe_id, qty in cart.items():
            shoe = get_object_or_404(Shoe, pk=shoe_id)
            subtotal = shoe.price * qty
            total += subtotal
            cart_items.append({'shoe': shoe, 'quantity': qty, 'subtotal': subtotal})

    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total': total})


def update_cart_quantity(request):
    shoe_id = request.POST.get('shoe_id')
    quantity = int(request.POST.get('quantity'))

    if request.user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(user=request.user, shoe_id=shoe_id)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
        except CartItem.DoesNotExist:
            pass
    else:
        cart = request.session.get('cart', {})
        if quantity > 0:
            cart[shoe_id] = quantity
        else:
            cart.pop(shoe_id, None)
        request.session['cart'] = cart

    return JsonResponse({'success': True})
