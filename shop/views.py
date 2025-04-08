from django.shortcuts import render, redirect, get_object_or_404
from .models import Shoe, Size, Review
from django.contrib.auth.decorators import login_required
# Create your views here.
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
    shoe = Shoe.objects.get(shoe_number=id)
    reviews = Review.objects.filter(shoe=shoe)
    template_data = {}
    template_data['title'] = shoe.name
    template_data['shoe'] = shoe
    template_data['sizes'] = Size.objects.all()
    template_data['reviews'] = reviews
    return render(request, 'shop/show.html',
                  {'template_data': template_data})


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