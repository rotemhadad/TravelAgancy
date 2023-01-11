from django.contrib import admin

from .forms import FlightForm
from .models import Flight



class FlightAdmin(admin.ModelAdmin):
    list_display = ('name', 'leave_city', 'arrive_city', 'leave_airport',
                    'arrive_airport', 'leave_time', 'arrive_time', 'capacity',
                    'price', 'book_sum', 'income')
    form = FlightForm  


# Register your models here.
admin.site.register(Flight, FlightAdmin)
