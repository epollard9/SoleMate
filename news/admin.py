from django.contrib import admin
from .models import CalendarEntry

# Register your models here.
@admin.register(CalendarEntry)
class CalendarEntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    search_fields = ('name','date')
