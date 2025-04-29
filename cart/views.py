from decimal import Decimal
from django.shortcuts              import render, redirect, get_object_or_404
from django.http                   import JsonResponse
from django.db.models              import Sum
from django.urls                   import reverse
from django.contrib.auth.decorators import login_required

from .models                       import CartItem, Order, OrderItem
from shop.models                   import Shoe, Size, Discount

def detail(request):
    """Show cart for both logged-in users and guests."""
    if request.user.is_authenticated:
        items = list(CartItem.objects.filter(user=request.user))
    else:
        raw = request.session.get('cart', {})
        valid = {k: v for k, v in raw.items() if k.count(':') == 1}
        request.session['cart'] = valid
        items = []
        for key, qty in valid.items():
            shoe_id, size_id = key.split(':')
            shoe = get_object_or_404(Shoe, pk=shoe_id)
            size = get_object_or_404(Size, pk=size_id)
            items.append(CartItem(user=None, shoe=shoe, size=size, quantity=qty))

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
        'total':      total,
    })


def add_to_cart(request):
    """AJAX add-to-cart."""
    shoe_id  = request.POST['shoe_id']
    size_id  = request.POST['size_id']
    quantity = int(request.POST.get('quantity', 1))
    shoe     = get_object_or_404(Shoe, pk=shoe_id)
    size     = get_object_or_404(Size, pk=size_id)

    if request.user.is_authenticated:
        ci, created = CartItem.objects.get_or_create(
            user=request.user,
            shoe=shoe,
            size=size,
            defaults={'quantity': quantity}
        )
        if not created:
            ci.quantity += quantity
            ci.save()
        count = CartItem.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
    else:
        cart = request.session.get('cart', {})
        key  = f"{shoe_id}:{size_id}"
        cart[key] = cart.get(key, 0) + quantity
        request.session['cart'] = cart
        count = sum(cart.values())

    return JsonResponse({'success': True, 'count': count})


def update_quantity(request):
    """AJAX update quantity."""
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
    """Remove one line from cart."""
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
    POST-only:
    - Logged-in: create Order (+ items), record discount, redirect to completed.
    - Guest: compute total, clear session → guest_completed.
    """
    if request.method != 'POST':
        return redirect('cart:view_cart')

    # --- Logged-in checkout ---
    if request.user.is_authenticated:
        code       = request.POST.get('discount_code', '').strip().upper()
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return redirect('cart:view_cart')

        # create order + items
        order = Order.objects.create(
            user=request.user,
            discount_code=(code if code not in Discount.objects.all().values() else None)
        )
        for ci in cart_items:
            OrderItem.objects.create(
                order=order,
                shoe=ci.shoe,
                size=ci.size,
                quantity=ci.quantity,
                price=ci.shoe.price,
            )
        cart_items.delete()

        # redirect w/ no GET-param (we read from order.discount_code)
        return redirect('cart:completed', order_id=order.id)

    # --- Guest checkout ---
    raw_cart = request.session.get('cart', {})
    total    = Decimal('0.00')
    for key, qty in raw_cart.items():
        shoe_id, _ = key.split(':')
        shoe = get_object_or_404(Shoe, pk=shoe_id)
        unit_price = (
            shoe.discounted_price
            if getattr(shoe, 'discount', 0) > 0
            else shoe.price
        )
        total += unit_price * qty

    request.session['cart'] = {}
    return render(request, 'cart/guest_completed.html', {
        'total': total,
    })


# cart/views.py
from decimal import Decimal
from django.shortcuts              import render, redirect, get_object_or_404
from django.http                   import JsonResponse
from django.db.models              import Sum
from django.urls                   import reverse
from django.contrib.auth.decorators import login_required

from .models                       import CartItem, Order, OrderItem
from shop.models                   import Shoe, Size

@login_required
def completed(request, order_id):
    """
    Renders the order completion page for authenticated users,
    showing original total, discount applied, and final total.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # 1) compute the raw (per-item) total
    raw_total = Decimal('0.00')
    for item in order.items.select_related('shoe'):
        unit_price = (
            item.shoe.discounted_price
            if getattr(item.shoe, 'discount', 0) > 0
            else item.price
        )
        raw_total += unit_price * item.quantity

    # 2) figure discount amount & final total
    discount_amount = Decimal('0.00')
    discount = Discount.objects.filter(discount_code__icontains=order.discount_code)
    if (discount):
        discount = discount.values_list('discount_percent', flat=True)[0]
    else:
        discount= Decimal('0.00')
    discount_amount = (raw_total * discount).quantize(Decimal('.01'))
    final_total = (raw_total - discount_amount).quantize(Decimal('0.01'))

    # 3) pass into template
    return render(request, 'cart/completed.html', {
        'order_id':       order.id,
        'raw_total':      raw_total,
        'discount_amount': discount_amount,
        'total':          final_total,
        'discount_codes': ['SOLEMATE15'],  # for the “Your available codes” box
    })


@login_required
def history(request):
    """
    List all past orders for the user, showing for each:
    - original total
    - discount (if any)
    - final total
    """
    orders = (
        Order.objects.filter(user=request.user)
        .order_by('-created_at')
        .prefetch_related('items__shoe', 'items__size')
    )

    for order in orders:
        # raw total
        raw = sum(
            (item.shoe.discounted_price if getattr(item.shoe, 'discount', 0) > 0 else item.price)
            * item.quantity
            for item in order.items.all()
        )
        # discount
        if (order.discount_code):
            discount = Discount.objects.filter(discount_code__icontains=order.discount_code)
            if (discount):
                discount = discount.values_list('discount_percent', flat=True)[0]
                order.discount_amount = (raw * discount).quantize(Decimal('0.01'))
            else:
                discount = Decimal('0.00')
                order.discount_amount = Decimal('0.00')
        else:
            order.discount_amount = Decimal('0.00')
        # final
        order.raw_total = raw
        order.total     = (raw - order.discount_amount).quantize(Decimal('0.01'))

    return render(request, 'cart/history.html', {'orders': orders})