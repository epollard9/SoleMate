from django.shortcuts import render, redirect, get_object_or_404
from .models import Shoe, Size, Review
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localdate
# Create your views here.
import urllib.request
import urllib.parse
import json

YOUTUBE_API_KEY = "AIzaSyCSOLAiDxAsl6Xqe1AHoN9WU9pPf4GIXn0"

def get_youtube_review_video(shoe_name):
    query = urllib.parse.quote(f"{shoe_name} review")
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={query}&key={YOUTUBE_API_KEY}&type=video"

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if data.get("items"):
                video_id = data["items"][0]["id"]["videoId"]
                return f"https://www.youtube.com/embed/{video_id}"
    except Exception as e:
        print(f"Error fetching YouTube video: {e}")
    return None

def index(request):
    search_term = request.GET.get('search')
    size_term = request.GET.get('sizeFilter')
    brand_term = request.GET.get('brandFilter')
    price_term = request.GET.get('priceFilter')
    shoes = Shoe.objects.all()
    if search_term:
        shoes = shoes.filter(name__icontains=search_term)
    if size_term:
        shoes = shoes.filter(sizes__size_code=size_term)
    if brand_term:
        shoes = shoes.filter(brand__icontains=brand_term)
    if price_term:
        shoes = shoes.filter(price__lte=price_term)

    template_data = {}
    template_data['title'] = 'Shoes'
    template_data['shoes'] = shoes
    template_data['sizes'] = Size.objects.all()
    template_data['brands'] = Shoe.objects.all().values_list("brand", flat=True).distinct()
    return render(request, 'shop/index.html',
                  {'template_data': template_data})

def seller(request):
    template_data = {}
    shoes = Shoe.objects.filter(brand__icontains="Sneaker Enthusiast")
    template_data['title'] = 'Shoes'
    template_data['shoes'] = shoes
    template_data['sizes'] = Size.objects.all()
    return render(request, 'shop/seller.html',{'template_data': template_data})

def sell(request):
    template_data = {}
    template_data['title'] = 'Shoes'
    template_data['sizes'] = Size.objects.all()
    return render(request, 'shop/sell.html',{'template_data': template_data})

def show(request, id):
    shoe = get_object_or_404(Shoe, shoe_number=id)
    reviews = Review.objects.filter(shoe=shoe)
    seller = False
    if shoe.seller == request.user.username:
        seller = True

    video_url = get_youtube_review_video(shoe.name)

    template_data = {
        'title': shoe.name,
        'shoe': shoe,
        'sizes': Size.objects.all(),
        'reviews': reviews,
        'youtube_video_url': video_url,
        'seller': seller,
    }
    return render(request, 'shop/show.html', {'template_data': template_data})

def my_listings(request):
    template_data={}
    name = request.user.username
    template_data['shoes'] = Shoe.objects.filter(seller__icontains =name)
    return render(request, 'shop/my_listings.html', {'template_data': template_data})

def edit_shoe(request, id):
    shoe = get_object_or_404(Shoe, shoe_number=id)
    template_data = {
        'title': shoe.name,
        'shoe': shoe,
        'sizes': Size.objects.all(),
    }
    return render(request, 'shop/edit_shoe.html', {'template_data': template_data})

def edit_shoe_entry(request, id):
    shoe = get_object_or_404(Shoe, shoe_number=id)

    if request.method == 'POST':
        shoe.name = request.POST['shoe_name']
        shoe.price = request.POST['shoe_price']
        shoe.description = request.POST['shoe_description']
        shoe.image = request.FILES['imageUpload']
        shoe.last_edit = localdate()
        shoe.brand = request.POST['shoe_brand']
        shoe.save()
        for key, values in request.POST.lists():
            if key == "sizes":
                for value in values:
                    shoe.sizes.add(value)
                    shoe.save()
        return redirect('shop.index')
    else:
        return redirect('shop.index')


@login_required
def create_shoe(request):
    max = 0
    for shoe in Shoe.objects.all():
        if int(shoe.shoe_number) > max:
            max = int(shoe.shoe_number)
    if request.method == 'POST':
        shoe = Shoe()
        shoe.name = request.POST['shoe_name']
        shoe.seller = request.user.username
        shoe.brand = request.POST['shoe_brand']
        shoe.price = request.POST['shoe_price']
        shoe.description = request.POST['shoe_description']
        shoe.image = request.FILES['imageUpload']
        shoe.shoe_number = str(max+1)
        shoe.release_date = localdate()
        shoe.last_edit = localdate()
        shoe.save()
        for key, values in request.POST.lists():
            if key == "sizes":
                for value in values:
                    shoe.sizes.add(value)
                    shoe.save()
        return redirect('shop.index')
    else:
        return redirect('shop.index')

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '' and request.POST['star']:
        shoe = Shoe.objects.get(shoe_number=id)
        review = Review()
        review.comment = request.POST['comment']
        review.shoe = shoe
        review.user = request.user
        review.rating = request.POST['star']
        review.save()
        return redirect('shop.show', id=id)
    else:
        return redirect('shop.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, shoe_id=review_id, user=request.user)
    if request.user != review.user:
        return redirect('shop.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'shop/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('shop.show', id=id)
    else:
        return redirect('shop.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('shop.show', id=id)

@login_required
def subscribe_shoe(request, shoe_id):
    shoe = get_object_or_404(Shoe, pk=shoe_id)
    request.user.subscribed_shoes.add(shoe)
    return redirect('news')  # or wherever you want to redirect after subscribing