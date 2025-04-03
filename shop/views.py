from django.shortcuts import render

# Create your views here.
shoes = [
    {'id': 1, 'name': 'Sneaker', 'price': 35, 'description': 'Casual every day shoes'},
    {'id': 2, 'name': 'Crocs', 'price': 40, 'description': ' Great to impress the ladies'},
    {'id': 3, 'name': 'Running Shoes', 'price': 40,'description': 'For when you want to loose the stomach'},
    {'id': 4, 'name': 'Nike', 'price': 50,'description': 'Just do it.'},
]
def index(request):
    template_data = {}
    template_data['title'] = 'Shoes'
    template_data['shoes'] = shoes
    return render(request, 'shop/index.html',
                  {'template_data': template_data})

def show(request, id):
    shoe = shoes[id - 1]
    template_data = {}
    template_data['title'] = shoe['name']
    template_data['shoe'] = shoe
    return render(request, 'shop/show.html',
                  {'template_data': template_data})