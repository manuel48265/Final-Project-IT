import unittest
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

    def test_convert_to(self):
        currency = Currency(100, 'USD')
        converted_currency = currency.convert_to('EUR')
        self.assertEqual(converted_currency.get_currency_type(), 'EUR')
        self.assertTrue(converted_currency.get_amount() > 0)

if __name__ == '__main__':
    unittest.main()