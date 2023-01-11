"""FlightTicket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include

from . import views

app_name = 'travelagancy'  

urlpatterns = [
    url(r'^register/$', views.register, name='register'), 
    url(r'^login_user/$', views.login_user, name='login_user'),  
    url(r'^login_user/add_flight/$', views.add_flight, name='add_flight'), 
    #url(r'^login_user/countries_management/$', views.countries_management, name='countries_management'), 
    url(r'^logout_user/$', views.logout_user, name='logout_user'),  
    url(r'^showall/$', views.showall, name='showall'), 


    url(r'^$', views.index, name='index'), 
    url(r'^result/$', views.result, name='result'),  
    url(r'^user_info/$', views.user_info, name='user_info'),  
    url(r'^book/flight/(?P<flight_id>[0-9]+)/$', views.book_ticket, name='book_ticket'),
    url(r'^refund_ticket/flight/(?P<seat_id>[0-9]+)/$', views.refund_ticket, name='refund_ticket'), 
    url(r'^delete_flight/flight/(?P<flight_id>[0-9]+)/$', views.delete_flight, name='delete_flight'), 
    url(r'^change_flight/flight/(?P<flight_id>[0-9]+)/$', views.change_flight, name='change_flight'),
    url(r'^pay/flight/(?P<flight_id>[0-9]+)/(?P<amount_of_seats>[0-9]+)/$', views.pay, name='pay'),
    url(r'^proceed/flight/(?P<flight_id>[0-9]+)/(?P<amount_of_seats>[0-9]+)/$', views.proceed, name='proceed'),
    url(r'^procces_pay/flight/(?P<flight_id>[0-9]+)/(?P<amount_of_seats>[0-9]+)/$', views.procces_pay, name='procces_pay'),
    url(r'^pay_success/flight/$', views.pay_success, name='pay_success'),

]
