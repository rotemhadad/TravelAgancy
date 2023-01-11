
class IncomeMetric:
    metric = '00'  
    flight_sum = 0
    income = 0

    def __init__(self, metric, flight_sum, income):
        self.metric = metric
        self.flight_sum = flight_sum
        self.income = income



class Order:
    passenger_name = ''
    flight_name = ''
    flight_route = ''
    flight_ltime = ''
    flight_price = ''

    def __init__(self, pname, fname, froute, fltime, fprice):
        self.passenger_name = pname
        self.flight_name = fname
        self.flight_route = froute
        self.flight_ltime = fltime
        self.flight_price = fprice
