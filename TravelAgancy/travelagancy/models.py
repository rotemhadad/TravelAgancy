from django.contrib.auth.models import Permission, User
from django.db import models


# Create your models here.
class Flight(models.Model):
    user = models.ManyToManyField(User, default=None)
    name = models.CharField(max_length=100, null=True)
    leave_city = models.CharField(max_length=100, null=True)  
    arrive_city = models.CharField(max_length=100, null=True) 
    leave_airport = models.CharField(max_length=100, null=True)
    arrive_airport = models.CharField(max_length=100, null=True)
    leave_time = models.DateTimeField(null=True)
    arrive_time = models.DateTimeField(null=True)
    capacity = models.IntegerField(default=0, null=True)
    num_of_rows =  models.IntegerField(default=0, null=True)
    seats_in_row =  models.IntegerField(default=0, null=True)
    price = models.FloatField(default=0, null=True)
    book_sum = models.IntegerField(default=0, null=True)
    income = models.FloatField(default=0, null=True)

    def __str__(self):
        return f'Name: {self.name}, Price:{self.price}'


class Seat(models.Model):
    user = models.ManyToManyField(User, default=None) #buy this seat
    row = models.IntegerField(default=1, null=True)
    seat_letter = models.CharField(max_length=3,null=True)
    busy = models.BooleanField(default=False,null=True)
    flight = models.ManyToManyField(Flight, default=1)
    
    def __str__(self):
        return f'Row: {self.row}, Letter: {self.seat_letter}'


class Passenger(models.Model):
    user = models.ManyToManyField(User, default=None) #buy this seat
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    ps_id = models.IntegerField(default=1, null=True)
    ps_number = models.IntegerField(default=1, null=True)
    flight = models.ManyToManyField(Flight, default=1)
    seat = models.ManyToManyField(Seat, default=1)
    isPay = models.BooleanField(default=False,null=True)


    
class Credit(models.Model):
    user = models.ManyToManyField(User, default=None) 
    fullname = models.CharField(max_length=100, null=True)
    cardnum = models.CharField(max_length=100, null=True)
    userid = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f'full name: {self.fullname}, userid: {self.userid}'



    
    


