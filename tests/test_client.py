import unittest
import os
from stock_stats import StockClient, StockException, HttpClient
from .shared import MockHttpClient
from datetime import date


class TestStockClient(unittest.TestCase):
    """
    This set of tests uses canned HTTP responses to check the behavior of StockClient
    """
    def get_data(self, filename: str) -> str:
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        fpath = os.path.join(data_dir, filename)
        with open(fpath, 'rb') as f:
            return f.read()

    def setUp(self):
        self.http_client = MockHttpClient()
        self.stock_client = StockClient(self.http_client, "KEY", "http://example.com/")

    def tearDown(self):
        self.http_client.cleanup()

    def test_csv_parsing(self):
        self.http_client.responses['http://example.com/v3/databases/WIKI/codes?api_key=KEY'] = (
            self.get_data('symbols.csv'),
            {}
        )
        symbols = self.stock_client.get_symbols()
        expected = {
            'AAPL': 'Apple Inc (AAPL) Prices, Dividends, Splits and Trading Volume',
            'ABC': 'AmerisourceBergen Corp. (ABC) Prices, Dividends, Splits and Trading Volume',
            'AA': 'Alcoa Inc. (AA) Prices, Dividends, Splits and Trading Volume',
        }
        self.assertEqual(expected, symbols)

    def test_zip_extraction(self):
        self.http_client.responses['http://example.com/v3/databases/WIKI/codes?api_key=KEY'] = (
            self.get_data('symbols.zip'),
            {StockClient.HEADER_CONTENT_TYPE: StockClient.CONTENT_TYPE_ZIP}
        )
        symbols = self.stock_client.get_symbols()
        expected = {
            'AAPL': 'Apple Inc (AAPL) Prices, Dividends, Splits and Trading Volume',
            'ABC': 'AmerisourceBergen Corp. (ABC) Prices, Dividends, Splits and Trading Volume',
            'AA': 'Alcoa Inc. (AA) Prices, Dividends, Splits and Trading Volume',
        }
        self.assertEqual(expected, symbols)

    def test_bad_zip_data(self):
        url = 'http://example.com/v3/databases/WIKI/codes?api_key=KEY'
        with self.assertRaises(StockException):
            self.http_client.responses[url] = (
                self.get_data('corrupt.zip'),
                {StockClient.HEADER_CONTENT_TYPE: StockClient.CONTENT_TYPE_ZIP}
            )
            self.stock_client.get_symbols()

    @unittest.skip("Incomplete")
    def test_monthly_averages(self):
        url = 'http://example.com/v3/datasets/WIKI/GOOGL/data.json?api_key=KEY&collapse=monthly&end_date=2017-06-01&start_date=2017-01-01&transform=cumul'
        self.http_client.responses[url] = (self.get_data('averages1.json'), {})

        data = self.stock_client.get_monthly_averages('GOOGL', date(2017, 1, 1), date(2017, 6, 1))


if __name__ == '__main__':
    unittest.main()
