from django.shortcuts import render, redirect
from shop.models import Shoe

def add_to_cart(request, id):
    cart = request.session.get('cart', [])
    if id not in cart:
        cart.append(id)
    request.session['cart'] = cart
    return redirect('shop.index')

def remove_from_cart(request, id):
    cart = request.session.get('cart', [])
    if id in cart:
        cart.remove(id)
    request.session['cart'] = cart
    return redirect('cart.view_cart')

def view_cart(request):
    cart = request.session.get('cart', [])
    shoes = Shoe.objects.all()
    cart_items = [shoe for shoe in shoes if shoe in cart]
    return render(request, 'cart/cart.html', {'cart_items': cart_items})
