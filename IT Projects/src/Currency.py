import requests

class Currency:
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

    def convert_to(self, target_currency):
        url = f"https://api.exchangerate-api.com/v4/latest/{self._currency_type}"
        response = requests.get(url)
        data = response.json()
        if target_currency in data['rates']:
            rate = data['rates'][target_currency]
            converted_amount = self._amount * rate
            return Currency(converted_amount, target_currency)
        else:
            raise ValueError(f"Conversion rate for {target_currency} not found.")

