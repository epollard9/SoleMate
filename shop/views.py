from django.shortcuts import render, redirect, get_object_or_404
from .models import Shoe, Size, Review
from django.contrib.auth.decorators import login_required

# Create your views here.
import urllib.request
import urllib.parse
import json

YOUTUBE_API_KEY = "AIzaSyC8BMdwgocDFD_qQwakjHqBn7_myYWpZiA"

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
    if search_term:
        shoes = Shoe.objects.filter(name__icontains=search_term)
    else:
        shoes = Shoe.objects.all()
    template_data = {}
    template_data['title'] = 'Shoes'
    template_data['shoes'] = shoes
    template_data['sizes'] = Size.objects.all()
    return render(request, 'shop/index.html',
                  {'template_data': template_data})

def show(request, id):
    shoe = get_object_or_404(Shoe, shoe_number=id)
    reviews = Review.objects.filter(shoe=shoe)


    video_url = get_youtube_review_video(shoe.name)

    template_data = {
        'title': shoe.name,
        'shoe': shoe,
        'sizes': Size.objects.all(),
        'reviews': reviews,
        'youtube_video_url': video_url,
    }
    return render(request, 'shop/show.html', {'template_data': template_data})



@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        shoe = Shoe.objects.get(shoe_number=id)
        review = Review()
        review.comment = request.POST['comment']
        review.shoe = shoe
        review.user = request.user
        review.rating = 2
        review.save()
        return redirect('shop.show', shoe_number=id)
    else:
        return redirect('shop.show', shoe_number=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, shoe_number=review_id)
    if request.user != review.user:
        return redirect('shop.show', shoe_number=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'shop/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(shoe_number=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('shop.show', shoe_number=id)
    else:
        return redirect('shop.show', shoe_number=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('shop.show', id=id)