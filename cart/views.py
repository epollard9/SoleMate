from decimal import Decimal
from django.shortcuts             import render, redirect, get_object_or_404
from django.http                  import JsonResponse
from django.db.models             import Sum
from django.urls                  import reverse
from .models                      import CartItem, Order, OrderItem
from shop.models                  import Shoe, Size
from django.contrib.auth.decorators import login_required

def detail(request):
    """
    Renders the cart page. Supports both authenticated users (DB-backed)
    and anonymous users (session-backed), discarding any malformed session keys.
    """
    if request.user.is_authenticated:
        items = list(CartItem.objects.filter(user=request.user))
    else:
        raw_cart = request.session.get('cart', {})
        valid_cart = {}
        for key, qty in raw_cart.items():
            if key.count(':') == 1:
                valid_cart[key] = qty
        request.session['cart'] = valid_cart

        items = []
        for key, qty in valid_cart.items():
            shoe_id, size_id = key.split(':')
            shoe = get_object_or_404(Shoe, pk=shoe_id)
            size = get_object_or_404(Size, pk=size_id)
            anon = CartItem(user=None, shoe=shoe, size=size, quantity=qty)
            items.append(anon)

    total = Decimal('0.00')
    for item in items:
        unit_price = (
            item.shoe.discounted_price
            if getattr(item.shoe, 'discount', 0) > 0
            else item.shoe.price
        )
        item.subtotal = unit_price * item.quantity
        total += item.subtotal

    return render(request, 'cart/cart.html', {
        'cart_items': items,
        'total': total,
    })


def add_to_cart(request):
    shoe_id  = request.POST.get('shoe_id')
    size_id  = request.POST.get('size_id')
    quantity = int(request.POST.get('quantity', 1))
    shoe     = get_object_or_404(Shoe, pk=shoe_id)
    size     = get_object_or_404(Size, pk=size_id)

    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            shoe=shoe,
            size=size,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        count = CartItem.objects.filter(user=request.user).aggregate(
            total=Sum('quantity')
        )['total'] or 0
    else:
        cart = request.session.get('cart', {})
        key  = f"{shoe_id}:{size_id}"
        cart[key] = cart.get(key, 0) + quantity
        request.session['cart'] = cart
        count = sum(cart.values())

    return JsonResponse({'success': True, 'count': count})


def update_quantity(request):
    shoe = get_object_or_404(Shoe, pk=request.POST['shoe_id'])
    size = get_object_or_404(Size, pk=request.POST['size_id'])
    qty  = int(request.POST['quantity'])

    if request.user.is_authenticated:
        ci = get_object_or_404(CartItem, user=request.user, shoe=shoe, size=size)
        ci.quantity = qty
        ci.save()
    else:
        cart = request.session.get('cart', {})
        cart[f"{shoe.pk}:{size.pk}"] = qty
        request.session['cart'] = cart

    return JsonResponse({'success': True})


def remove_from_cart(request, shoe_id, size_id):
    shoe = get_object_or_404(Shoe, pk=shoe_id)
    size = get_object_or_404(Size, pk=size_id)
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user, shoe=shoe, size=size).delete()
    else:
        cart = request.session.get('cart', {})
        cart.pop(f"{shoe_id}:{size_id}", None)
        request.session['cart'] = cart
    return redirect('cart:view_cart')


def checkout(request):
    """
    POST-only: for logged-in users creates an order and redirects to /completed/,
    for guests calculates total and shows the guest completion page.
    """
    if request.method != 'POST':
        return redirect('cart:view_cart')

    # First, collect cart items & compute total
    if request.user.is_authenticated:
        # logged-in flow
        discount_code = request.POST.get('discount_code', '').strip().upper()
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return redirect('cart:view_cart')

        order = Order.objects.create(user=request.user)
        for ci in cart_items:
            OrderItem.objects.create(
                order=order,
                shoe=ci.shoe,
                size=ci.size,
                quantity=ci.quantity,
                price=ci.shoe.price,
            )
        cart_items.delete()

        # build redirect with code if valid
        url = reverse('cart:completed', args=[order.id])
        if discount_code == 'SOLEMATE15':
            url += '?code=SOLEMATE15'
        return redirect(url)

    else:
        # guest flow
        raw_cart = request.session.get('cart', {})
        total = Decimal('0.00')
        for key, qty in raw_cart.items():
            shoe_id, size_id = key.split(':')
            shoe = get_object_or_404(Shoe, pk=shoe_id)
            # apply per‐item discount if any
            unit_price = (
                shoe.discounted_price
                if getattr(shoe, 'discount', 0) > 0
                else shoe.price
            )
            total += unit_price * qty

        # clear session cart
        request.session['cart'] = {}

        return render(request, 'cart/guest_completed.html', {
            'total': total,
        })


@login_required
def completed(request, order_id):
    """
    Renders the order completion page for authenticated users,
    applies per‐item discounts and a 15% promo if ?code=SOLEMATE15 was passed.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    total = Decimal('0.00')
    for item in order.items.select_related('shoe'):
        unit_price = (
            item.shoe.discounted_price
            if getattr(item.shoe, 'discount', 0) > 0
            else item.price
        )
        total += unit_price * item.quantity

    if request.GET.get('code') == 'SOLEMATE15':
        total = (total * Decimal('0.85')).quantize(Decimal('0.01'))

    discount_codes = ['SOLEMATE15']

    return render(request, 'cart/completed.html', {
        'order_id':       order_id,
        'total':          total,
        'discount_codes': discount_codes,
    })


@login_required
def history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .order_by('-created_at')
        .prefetch_related('items__shoe', 'items__size')
    )
    for order in orders:
        order.total = sum(
            (item.shoe.discounted_price if getattr(item.shoe, 'discount', 0) > 0 else item.price)
            * item.quantity
            for item in order.items.all()
        )
    return render(request, 'cart/history.html', {'orders': orders})
