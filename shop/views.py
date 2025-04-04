from django.shortcuts import render
from .models import Shoe
# Create your views here.
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Shoe.objects.filter(name__icontains=search_term)
    else:
        movies = Shoe.objects.all()
    template_data = {}
    template_data['title'] = 'Shoes'
    template_data['shoes'] = movies
    return render(request, 'shop/index.html',
                  {'template_data': template_data})

def show(request, id):
    shoe = Shoe.objects.get(shoe_number=id)
    template_data = {}
    template_data['title'] = shoe.name
    template_data['shoe'] = shoe
    return render(request, 'shop/show.html',
                  {'template_data': template_data})