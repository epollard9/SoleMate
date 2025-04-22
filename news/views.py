from django.shortcuts import render
from shop.models import Shoe
from datetime import datetime


def news_view(request):
    upcoming_shoes = Shoe.objects.filter(release_date__gte=datetime.today()).order_by('release_date')

    subscribed_shoes = []
    if request.user.is_authenticated:
        subscribed_shoes = request.user.subscribed_shoes.all()

    return render(request, "news/news.html", {
        "shoes": upcoming_shoes,
        "subscribed_shoes": subscribed_shoes,
    })
