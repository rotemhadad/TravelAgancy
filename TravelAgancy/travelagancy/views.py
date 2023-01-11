from audioop import reverse
import datetime
from operator import attrgetter
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Permission, User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .classes import IncomeMetric, Order
from .forms import PassengerInfoForm, UserForm
from .models import Flight,Seat,Passenger,Credit
from django.db.models import Max 
from django.core.mail import send_mail
from django.core.mail import EmailMessage, EmailMultiAlternatives
import socket

ADMIN_ID = 1

def index(request):
    now = datetime.date.today()
    return render(request, 'travelagancy/index.html', {'now' : str(now)})


def base_choose_func(request,context):
    if request.user.id == ADMIN_ID:  
        context['template_name'] = "travelagancy/admin_base.html"
    else:
        context['template_name'] = "travelagancy/ccust_base.html"


def admin_finance(request):
    all_flights = Flight.objects.all()
    all_seats = Seat.objects.all()
    all_flights = sorted(all_flights,key=attrgetter('leave_time')) 

    # order
    passengers = User.objects.exclude(pk=1)
    order_set = set()
    for p in passengers:
        flights = Flight.objects.filter(user=p)
        for f in flights:
            route = f.leave_city + ' → ' + f.arrive_city
            order = Order(p.username, f.name, route, f.leave_time, f.price)
            order_set.add(order)

    context = {
        'order_set': order_set,
        'all_seats' : all_seats,
        'username': request.user.username
    }
    return context




# info customer order
# flight info+managmant
def user_info(request):

    if request.user.is_authenticated:
        if request.user.id == ADMIN_ID:  #admin : show admin stuff
            context = admin_finance(request)
            return render(request, 'travelagancy/admin_finance.html', context)
        else: #customer user
            booked_flights = Flight.objects.filter(user=request.user)  #all the user flights reservetion
            #booked_seats = Seat.objects.filter(user=request.user)
            booked_seats = []
            psg = Passenger.objects.filter(user=request.user, isPay = True)
            for x in psg:
                seats = x.seat.all().distinct()
                flights = x.flight.all()
                booked_seats.append([list(seats), list(flights)])

            Npsg = Passenger.objects.filter(user=request.user, isPay = False)
            for i in Npsg:
                i.delete()


            
            # booked_seats = []
            # #psg = Passenger.objects.filter(user=request.user)
            
            # for x in psg:
            #     booked_seats.append([list(x.seat.all().distinct('row','seat_letter')), list(x.flight.all())])
            current_time = datetime.date.today()
            now = current_time.strftime('%b. %d, %Y')

            context = { #data for views
                'booked_flights': booked_flights,
                'booked_seats' : booked_seats,
                'now' : str(now),
                'username': request.user.username, 
                
            }
            return render(request, 'travelagancy/user_info.html', context)
    return render(request, 'travelagancy/login.html')



@csrf_exempt 
def book_ticket(request, flight_id):
    if not request.user.is_authenticated:
        return render(request, 'travelagancy/login.html')
    else:
        flight = Flight.objects.get(pk=flight_id)
        seats = Seat.objects.filter(flight=flight)

        if flight.capacity==0:
            context={
                'username': request.user.username
            }
            return render(request, 'travelagancy/book_conflict.html',context)


        # if request.method == 'POST':
        #     # if flight.capacity > 0 and request.user.id != ADMIN_ID:
        #     #     # flight.book_sum += 1 #how many ordered
        #     #     # flight.capacity -= 1 #-1 seats left
        #     #     # flight.income += flight.price
        #     #     # flight.user.add(request.user)
        #     #     # flight.save()  

        if request.user.id == ADMIN_ID:  #admin : show admin stuff
            admin=True
        else:
            admin=False

        context = {
            'flight': flight, 
            'username': request.user.username, 
            'seats':seats,
            'isAdmin': admin,

            }
        return render(request, 'travelagancy/book_flight.html', context)



def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'travelagancy/login.html', context)



def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        user = authenticate(username=username, password=password)
        if user is not None: 
            if user.is_active:  
                login(request, user)
                context = {'username': request.user.username}
                if user.id == ADMIN_ID:
                    context = admin_finance(request)  
                    return render(request, 'travelagancy/admin_finance.html',
                                  context)
                else:
                    return render(request, 'travelagancy/result.html', context)
            else:
                return render(
                    request, 'travelagancy/login.html',
                    {'error_message': 'Your account has been disabled'})
        else: 
            return render(request, 'travelagancy/login.html',
                          {'error_message': 'Invalid login'})
    return render(request, 'travelagancy/login.html')



def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                context = {'username': request.user.username}
                return render(request, 'travelagancy/result.html',
                              context)  
    context = {
        "form": form,
    }
    return render(request, 'travelagancy/register.html', context)



def result(request):
    max_price = Flight.objects.all().aggregate(Max('price'))['price__max']
    now = datetime.date.today()
    if request.method == 'POST':
        back_flights_by_downprice = []
        back_flights_by_price = []
        back_flights_by_rate = []
        back_flights_by_atime = []
        back_flights_by_ltime = []
        
        dis_search_head = 'block'
        dis_search_failure = 'none'
        back_dis_search_head = 'block'
        back_dis_search_failure = 'none'
        form = PassengerInfoForm(request.POST) 
        num_way= request.POST.get('gridRadios')
        if form.is_valid():
            passenger_lcity = form.cleaned_data.get('leave_city')
            passenger_acity = form.cleaned_data.get('arrive_city')
            passenger_ldate = form.cleaned_data.get('leave_date')
            passenger_ltime = datetime.datetime.combine(passenger_ldate,
                                                        datetime.time())
            usable_flights = []
            back_flights_list = []     
            all_flights = Flight.objects.filter(leave_city=passenger_lcity,
                                arrive_city=passenger_acity,leave_time__gte=now)                                       
            if num_way == "two_way":
                back_flights = Flight.objects.filter(leave_city=passenger_acity, arrive_city=passenger_lcity,leave_time__gte=now)
                for flight in back_flights:  
                    flight.leave_time = flight.leave_time.replace(tzinfo=None)
                    if flight.leave_time.date() >= passenger_ltime.date():
                        back_flights_list.append(flight)

            for flight in all_flights:  
                flight.leave_time = flight.leave_time.replace(tzinfo=None)
                if flight.leave_time.date() == passenger_ltime.date():
                    usable_flights.append(flight)
            if 'want_price_range' in request.POST:
                want_price_range(request,usable_flights,back_flights_list)
            usable_flights_by_ltime = sorted(usable_flights, key=attrgetter('leave_time')) 
            usable_flights_by_atime = sorted(usable_flights, key=attrgetter('arrive_time'))
            usable_flights_by_price = sorted(usable_flights, key=attrgetter('price'))
            usable_flights_by_rate = sorted(usable_flights, key=attrgetter('book_sum'), reverse=True)
            usable_flights_by_downprice = sorted(usable_flights, key=attrgetter('price'), reverse=True)
            
            if (back_flights_list != []):
                back_flights_by_ltime = sorted(back_flights_list, key=attrgetter('leave_time')) 
                back_flights_by_atime = sorted(back_flights_list, key=attrgetter('arrive_time'))
                back_flights_by_price = sorted(back_flights_list, key=attrgetter('price'))
                back_flights_by_rate = sorted(back_flights_list, key=attrgetter('book_sum'), reverse=True)
                back_flights_by_downprice = sorted(back_flights_list, key=attrgetter('price'), reverse=True)

            if len(usable_flights_by_price) == 0:
                dis_search_head = 'none'
                dis_search_failure = 'block'
            if len(back_flights_by_price) == 0 and num_way == "two_way" :
                back_dis_search_head = 'none'
                back_dis_search_failure = 'block'
            context = {
                'is_two_way' : num_way == "two_way",
                'leave_city': passenger_lcity,
                'arrive_city': passenger_acity,
                'leave_date': str(passenger_ldate),
                'usable_flights_by_ltime': usable_flights_by_ltime,
                'usable_flights_by_atime': usable_flights_by_atime,
                'usable_flights_by_price': usable_flights_by_price,
                'usable_flights_by_rate' : usable_flights_by_rate,
                'dis_search_head': dis_search_head,
                'dis_search_failure': dis_search_failure,
                'back_dis_search_head': back_dis_search_head,
                'back_dis_search_failure': back_dis_search_failure,
                'now' : str(now),
                'usable_flights_by_pricedown': usable_flights_by_downprice,
                'back_flights_by_pricedown':back_flights_by_downprice,
                'back_flights_by_price' : back_flights_by_price,
                'back_flights_by_rate' :back_flights_by_rate,
                'back_flights_by_atime' : back_flights_by_atime,
                'back_flights_by_ltime' : back_flights_by_ltime,
                'max_price' : max_price
            }
            if request.user.is_authenticated:  # FIXME: django higher version 'bool' object is not callable
                context['username'] = request.user.username
            return render(request, 'travelagancy/result.html',context)  


        else: #at least one of the fields is empty
            passenger_ldate = form.cleaned_data.get('leave_date')
            leave_city = form.cleaned_data.get('leave_city')
            arrive_city = form.cleaned_data.get('arrive_city')
            all_flights = None
            usable_flights = []
            back_flights_list = []

            if passenger_ldate == None:
                if (leave_city != None):
                    if (arrive_city != None): #leave and arrive
                        if num_way == "two_way": #only if the user wrote arrive and leave city
                            back_flights = Flight.objects.filter(leave_city=arrive_city,arrive_city=leave_city)
                            for flight in back_flights:  
                                flight.leave_time = flight.leave_time.replace(tzinfo=None)
                                if flight.leave_time.date() >= now:
                                    back_flights_list.append(flight)
                            if 'want_price_range' in request.POST:
                                want_price_range(request,usable_flights,back_flights_list)
                            if (back_flights_list != []):
                                back_flights_by_ltime = sorted(back_flights_list, key=attrgetter('leave_time')) 
                                back_flights_by_atime = sorted(back_flights_list, key=attrgetter('arrive_time'))
                                back_flights_by_price = sorted(back_flights_list, key=attrgetter('price'))
                                back_flights_by_rate = sorted(back_flights_list, key=attrgetter('book_sum') ,reverse=True)
                                back_flights_by_downprice = sorted(back_flights_list, key=attrgetter('price'), reverse=True)
                        all_flights = Flight.objects.filter(arrive_city=arrive_city, leave_city=leave_city,leave_time__gte=now)
                    else: #only leave city
                        all_flights = Flight.objects.filter(leave_city=leave_city,leave_time__gte=now)
                else: #only arrive_city
                    all_flights = Flight.objects.filter(arrive_city=arrive_city,leave_time__gte=now)
                if (all_flights != None):
                    for flight in all_flights:
                        usable_flights.append(flight)  
            else: #at least one of the city is empty and passenger_ldate!=None
                passenger_ltime = datetime.datetime.combine(passenger_ldate,datetime.time())
                if (leave_city == None and arrive_city == None):
                    for flight in Flight.objects.all():
                        if flight.leave_time.date() == passenger_ltime.date():
                            usable_flights.append(flight)
                else:
                    if (leave_city != None): #arrive city is None, passenger_ldate is not None
                        all_flights = Flight.objects.filter(leave_city=leave_city)
                    elif (arrive_city != None):
                        all_flights = Flight.objects.filter(arrive_city=arrive_city)
                    for flight in all_flights:  
                        flight.leave_time = flight.leave_time.replace(tzinfo=None)
                        if flight.leave_time.date() == passenger_ltime.date():
                            print(flight.leave_time.date(), passenger_ltime.date())
                            usable_flights.append(flight)
            if (arrive_city == None and leave_city == None and passenger_ldate == None and 'want_price_range' in request.POST):
                all_flights = Flight.objects.filter(leave_time__gte=now)
                if (all_flights != None):
                    for flight in all_flights:
                        usable_flights.append(flight)  
                want_price_range(request,usable_flights,back_flights_list)

            if 'want_price_range' in request.POST:
                want_price_range(request,usable_flights,back_flights_list)
            usable_flights_by_ltime = sorted(usable_flights, key=attrgetter('leave_time')) 
            usable_flights_by_atime = sorted(usable_flights, key=attrgetter('arrive_time'))
            usable_flights_by_price = sorted(usable_flights, key=attrgetter('price'))
            usable_flights_by_rate = sorted(usable_flights, key=attrgetter('book_sum'), reverse=True)
            usable_flights_by_downprice = sorted(usable_flights, key=attrgetter('price'), reverse=True)

            if len(back_flights_by_price) == 0 and num_way == "two_way" :
                back_dis_search_head = 'none'
                back_dis_search_failure = 'block'
            if len(usable_flights_by_price) == 0:
                dis_search_head = 'none'
                dis_search_failure = 'block'

            context = {
                'is_two_way' : num_way == "two_way",
                'leave_city': leave_city,
                'arrive_city': arrive_city,
                'leave_date': str(passenger_ldate),
                'usable_flights_by_ltime': usable_flights_by_ltime,
                'usable_flights_by_atime': usable_flights_by_atime,
                'usable_flights_by_price': usable_flights_by_price,
                'usable_flights_by_rate' : usable_flights_by_rate,
                'dis_search_head': dis_search_head,
                'dis_search_failure': dis_search_failure,
                'back_dis_search_head': back_dis_search_head,
                'back_dis_search_failure': back_dis_search_failure,
                'now' : str(now),
                'usable_flights_by_pricedown': usable_flights_by_downprice,
                'back_flights_by_pricedown':back_flights_by_downprice,
                'back_flights_by_price' : back_flights_by_price,
                'back_flights_by_rate' : back_flights_by_rate,
                'back_flights_by_atime' : back_flights_by_atime,
                'back_flights_by_ltime' : back_flights_by_ltime,
                'max_price' : max_price
            }
            if request.user.is_authenticated:  # FIXME: django higher version 'bool' object is not callable
                context['username'] = request.user.username
            return render(request, 'travelagancy/result.html',context)  

    else:
        context = {
        'dis_search_head': 'none',
        'dis_search_failure': 'none',
        'back_dis_search_head': 'none',
        'back_dis_search_failure': 'none',
        'now': str(now),
        'max_price' : max_price
        }
       
    return render(request, 'travelagancy/result.html', context)

def want_price_range(request,usable_flights,back_flights):
    price_range = request.POST.get('rangeInput')
    print(usable_flights)
    new_us = []
    new_bc = []
    if usable_flights != [] :
        for i in usable_flights:
            if i.price <= int(price_range):
                new_us.append(i)
    usable_flights.clear()
    for i in new_us:
        usable_flights.append(i)

    if back_flights != [] :
        for i in back_flights:
            if i.price <= int(price_range):
                new_bc.append(i)
    back_flights.clear()
    for i in new_bc:
        back_flights.append(i)



def add_flight(request):
    if request.method == 'POST':
        name= request.POST.get('name')
        leave_city = request.POST.get('leave_city')
        arrive_city = request.POST.get('arrive_city')
        arrive_airport = request.POST.get('arrive_airport')
        leave_airport = request.POST.get('leave_airport')
        leave_time = request.POST.get('leave_time')
        arrive_time = request.POST.get('arrive_time')
        num_of_rows =  request.POST.get('num_of_rows')
        seats_in_row =  request.POST.get('seats_in_row')
        capacity = int(num_of_rows)*int(seats_in_row)
        price = request.POST.get('price')
        book_sum = 0
        income = 0
        user = None
        flight= Flight(name=name,leave_city=leave_city,arrive_city=arrive_city,arrive_airport=arrive_airport,
        leave_airport=leave_airport,leave_time=leave_time,arrive_time=arrive_time,capacity=capacity,price=price,
        book_sum=book_sum,income=income,num_of_rows=num_of_rows,seats_in_row=seats_in_row)
        flight.save()

        arr=list(map(chr, range(65, 65+int(seats_in_row))))
        user = None
        busy = False
        for i in range(1,int(num_of_rows)+1): #all the rows
            for j in range(0,int(seats_in_row)): #letter of the seat from arr
                row = i
                seat_letter = arr[j]
                seat = Seat(row=row,seat_letter=seat_letter,busy=busy)
                seat.save()
                seat.flight.add(flight)
                seat.save()
                
        return render(request, 'travelagancy/add_flight.html') #####

    else:
        now = datetime.datetime.now()
        print(str(now.strftime("%Y-%m-%d %H:%M:%S")))
        return render(request, 'travelagancy/add_flight.html', {'now': str(now.strftime("%Y-%m-%d %H:%M:%S"))})

def showall(request):
    now = datetime.date.today() 
    print(now)
    flights=Flight.objects.filter(leave_time__gte=now)
    if request.user.id == ADMIN_ID:  #admin : show admin stuff
        admin=True
    else:
        admin=False
    context = {
                'flights': flights,
                'isAdmin': admin,
                'username': request.user.username
            }
    return render(request, 'travelagancy/showall.html',context) 


def delete_flight(request,flight_id):
    ##delete from db the flight
    flight=Flight.objects.get(pk=flight_id)
    users = flight.user.all()
    mails = []
    for i in users:
        mails.append(str(i.email))
    flight.delete()
    if mails != []:

        subject = 'Flight Cancel!'
        body = 'Hi, sorry for the inconvenient, The flight you have orderd has been canceled.'
        to = mails
        from_email = 'skyairlineadm@hotmail.com'

        email = EmailMessage(subject, body, to=to, from_email=from_email)
        try:
            email.send()
        except Exception as e:
            # handle the exception
            print(e)

    return HttpResponseRedirect('/travelagancy/showall')


def change_flight(request,flight_id):
    ##change flight stuff in db by admin
    if request.method == 'POST': ##change country
        price = request.POST.get('price')
        flight=Flight.objects.get(pk=flight_id)
        flight.price= price
        flight.save()
        return HttpResponseRedirect('/travelagancy/showall')
    else:
        flight = Flight.objects.get(pk=flight_id)
        return render(request,'travelagancy/change_flight.html', {'flight':flight})



# def countries_management(request):
#     if request.method == 'POST': ##add country
#         name = request.POST.get('city')
#         new_city= Country(name=name)
#         new_city.save()
#         return render(request, 'travelagancy/countries_management.html') 

#     else:
#         c_list= Country.objects.all()
#         return render(request, 'travelagancy/countries_management.html',{'c_list': c_list})




def proceed(request,flight_id, amount_of_seats):
    flight = Flight.objects.get(pk=flight_id)
    amount_of_seats = amount_of_seats
    seats = Seat.objects.filter(flight=flight)
    # if request.method=='POST':
    #     seat_chosen = request.POST.getlist('chosen')
    #     print(seat_chosen)
    context={
        'flight': flight,
        'amount_of_seats': amount_of_seats,
        'seats' : seats
    }
    return render(request, 'travelagancy/proceed.html',context)


def pay(request,flight_id,amount_of_seats):
    now = datetime.date.today()
    flight = Flight.objects.get(pk=flight_id)
    #seat = Seat.objects.get(pk=seat_id)
    seats = request.POST.getlist('chosen')
    firstnames= request.POST.getlist('first_name')
    lastnames= request.POST.getlist('last_name')
    idspas= request.POST.getlist('ID')
    ps_nums= request.POST.getlist('ps_num')
    price = int(amount_of_seats)*flight.price
    psg_list = []
    if request.method == 'POST' and flight.capacity > 0:
        for i in range(0,int(amount_of_seats)):
            s = Seat.objects.get(pk=seats[i])
            s.save()
            psg = Passenger(isPay = False,ps_number=int(ps_nums[i]),ps_id=int(idspas[i]),last_name=lastnames[i],first_name=firstnames[i])
            psg.save()
            psg.flight.add(flight)
            psg.save()
            psg.seat.add(s) ########################
            psg.save() 
            psg.user.add(request.user)
            psg.save()
            psg_list.append(psg)
        c = Credit.objects.filter(user=request.user).first() # check if this user saved his card
        print(c)
        save = False
        userid = None
        fullname = None
        cardnum = None
        if c is not None :
            save = True
            userid = c.userid
            fullname = c.fullname
            cardnum = c.cardnum
        context = {
            'flight' : flight,
            'seats' : seats,
            'amount_of_seats' : amount_of_seats,
            'price' : price,
            'psg_list' : psg_list,
            'now' : str(now),
            'save' : save,
            'cardnum' : cardnum,
            'fullname' : fullname,
            'userid' :userid
        }
        return render(request, 'travelagancy/pay.html',context)


def procces_pay(request,flight_id,amount_of_seats):
    save_card = 'checkbox' in request.POST
    flight = Flight.objects.get(pk=flight_id)
    if flight.capacity > 0 and request.user.id != ADMIN_ID:
        flight.book_sum += int(amount_of_seats) #how many ordered
        flight.capacity -= int(amount_of_seats) #-1 seats left
        flight.income += flight.price*int(amount_of_seats)
        flight.user.add(request.user)
        flight.save()

    if save_card:
        userid =request.POST.get('userid', False)
        cardnum="4580040112341278"
        fullname=request.POST.get('fullname', False)
        cr = Credit(userid=userid,cardnum=cardnum,fullname=fullname)
        cr.save()
        cr.user.add(request.user)
        cr.save()
    psgs = Passenger.objects.filter(user=request.user,flight=flight)

    seats =[]


    for i in psgs:
        i.isPay = True
        i.save()
        for j in  i.seat.all():
            j.busy = True
            j.save()
            j.user.add(request.user)
            j.save()
            j.flight.add(flight)
            j.save()
            print(j)
            seats.append(j)

    context = {
        'flight' : flight,
        'amount_of_seats' : amount_of_seats,
        'psgs' : psgs,
        'username' : request.user.username,
        'seats' : seats
    }
    return render(request, 'travelagancy/pay_success.html',context)


def pay_success(request):
    return render(request, 'travelagancy/pay_success.html')


def refund_ticket(request,seat_id):
    seat = Seat.objects.get(pk=seat_id)
    flight = seat.flight.first()
    psg = Passenger.objects.filter(user=request.user)
    for x in psg:
        seats = x.seat.all().distinct()
        for i in seats:
            if i == seat:
                x.delete()       

    
    flight.book_sum = flight.book_sum-1
    flight.capacity = flight.capacity+1
    flight.income = flight.income-flight.price
    seat.user.remove(request.user)
    seat.busy = False
    seat.save()
    flight.save()

    s = Seat.objects.filter(user=request.user,flight=flight)
    if not s.exists():
        flight.user.remove(request.user)
            
    return HttpResponseRedirect('/travelagancy/user_info')


