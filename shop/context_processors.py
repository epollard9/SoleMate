from .models import Shoe
from datetime import datetime, timedelta

def subscribed(request):
    count = 0
    time = datetime.today() - timedelta(days=3)
    subscribed_shoes = request.user.subscribed_shoes.filter(last_edit__gte=time)
    for shoe in subscribed_shoes:
        count += 1
    return {'subscribed': count}