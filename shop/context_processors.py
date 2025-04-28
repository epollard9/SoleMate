from .models import Shoe
from datetime import datetime, timedelta

def subscribed(request):
    if request.user.is_authenticated:
        count = 0
        time = datetime.today() - timedelta(days=3)
        subscribed_shoes = request.user.subscribed_shoes.filter(last_edit__gte=time)
        for shoe in subscribed_shoes:
            count += 1
    else:
        count = 0
    return {'subscribed': count}