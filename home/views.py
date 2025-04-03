from django.shortcuts import render

def index(request):
    template_data = {}
    template_data['title'] = 'Sole Mate Home'
    return render(request, 'home/index.html', {'template_data': template_data})

def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {'template_data': template_data})

def news(request):
    template_data = {}
    template_data['title'] = 'News'
    return render(request, 'home/news.html', {'template_data': template_data})