from django.shortcuts import render
from shop.models import Shoe
from .models import CalendarEntry
from datetime import datetime, timedelta


def news_view(request):
    upcoming_shoes = Shoe.objects.filter(release_date__gte=datetime.today()).order_by('release_date')

    subscribed_shoes = []
    calendar_entries = []
    if request.user.is_authenticated:
        subscribed_shoes = request.user.subscribed_shoes.all()
        time = datetime.today() - timedelta(days=3)
        subscribed_shoes = request.user.subscribed_shoes.filter(last_edit__gte=time)
        calendar_entries = CalendarEntry.objects.all().order_by('date')

    return render(request, "news/news.html", {
        "shoes": upcoming_shoes,
        "subscribed_shoes": subscribed_shoes,
        "calendar_entries": calendar_entries,
    })
