from django.shortcuts import render
from shop.models import Shoe
from datetime import datetime


def news_view(request):
    a = 5
    upcoming_shoes = Shoe.objects.filter(release_date__gte=datetime.today()).order_by('release_date')

    return render(request, "news/news.html", {
        "shoes": upcoming_shoes
    })
