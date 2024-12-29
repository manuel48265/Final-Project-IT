import requests
from datetime import date, datetime, timedelta

class Currency:
    time_delta = timedelta(minutes=1)
    rates = None
    current_currency = 'PLN'
    last_update = None

    def __init__(self, amount, currency_type):
        self._amount = amount
        self._currency_type = currency_type

    def get_amount(self):
        return self._amount

    def set_amount(self, amount):
        self._amount = amount

    def get_currency_type(self):
        return self._currency_type

    def set_currency_type(self, currency_type):
        self._currency_type = currency_type

    def __str__(self):
        return f"{self._currency_type}"
    
    @staticmethod
    def update():
        if Currency.rates is None or Currency.last_update is None:
            Currency.last_update = datetime.now()
            url = f"https://api.exchangerate-api.com/v4/latest/{Currency.current_currency}"
            response = requests.get(url)
            Currency.rates = response.json()['rates']
        elif (datetime.now() - Currency.last_update).min > Currency.time_delta:
            Currency.last_update = datetime.now()
            url = f"https://api.exchangerate-api.com/v4/latest/{Currency.current_currency}"
            response = requests.get(url)
            Currency.rates = response.json()['rates']
        
        
    def convert(self):
        Currency.update()
        rate = Currency.rates[self._currency_type]
        converted_amount = self._amount / rate
        return converted_amount
        



