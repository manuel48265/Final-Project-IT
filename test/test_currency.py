import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from src.Currency import Currency

class TestCurrency(unittest.TestCase):
    def test_get_set_amount(self):
        currency = Currency(100, 'USD')
        self.assertEqual(currency.get_amount(), 100)
        currency.set_amount(200)
        self.assertEqual(currency.get_amount(), 200)

    def test_get_set_currency_type(self):
        currency = Currency(100, 'USD')
        self.assertEqual(currency.get_currency_type(), 'USD')
        currency.set_currency_type('EUR')
        self.assertEqual(currency.get_currency_type(), 'EUR')

    def test_str(self):
        currency = Currency(100, 'USD')
        self.assertEqual(str(currency), 'USD')

    def setUp(self):
        Currency.current_currency = 'USD'
        Currency.rates = {'USD': 1.0, 'EUR': 0.5}
        Currency.last_update = datetime.now()

    @patch('src.Currency.requests.get')
    def test_convert_to_current_currency(self, mock_get):
        # 100 EUR at 0.5 EUR per USD are 200 USD, the current currency.
        self.assertEqual(Currency(100, 'EUR').convert(), 200)
        mock_get.assert_not_called()

    @patch('src.Currency.requests.get')
    def test_rates_are_refreshed_when_stale(self, mock_get):
        mock_get.return_value.json.return_value = {'rates': {'USD': 1.0, 'EUR': 0.25}}
        Currency.last_update = datetime.now() - Currency.time_delta - timedelta(seconds=1)
        self.assertEqual(Currency(100, 'EUR').convert(), 400)
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main()