import unittest
import os
from stock_stats import StockClient, StockException, HttpClient
from .shared import MockHttpClient
from datetime import date


class TestStockClient(unittest.TestCase):
    """
    This set of tests uses canned HTTP responses to check the behavior of StockClient
    """
    def get_data(self, filename: str) -> bytes:
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

    def test_monthly_averages(self):
        url = 'http://example.com/v3/datasets/WIKI/GOOGL/data.json' \
              '?api_key=KEY&end_date=2017-06-01&start_date=2017-01-01'
        self.http_client.responses[url] = (self._get_data('averages1.json'), {})

        data = self.stock_client.get_monthly_averages(
            'GOOGL',
            date(2017, 1, 1),
            date(2017, 6, 1)
        )

        # Test results calculated independently from CSV output
        expectations = {
            # Month : (open, close)
            '2017-01': (829.854, 830.2495),
            '2017-02': (836.151052631579, 836.754736842105),
            '2017-03': (853.858260869566, 853.789782608696),
            '2017-04': (860.076578947368, 861.377631578947),
            '2017-05': (959.595909090909, 961.654545454545),
            '2017-06': (975.781818181818, 973.372727272728),
        }
        self.assertEqual(data.keys(), expectations.keys())
        for k, actuals in data.items():
            self.assertAlmostEqual(actuals['average_open'], expectations[k][0])
            self.assertAlmostEqual(actuals['average_close'], expectations[k][1])


if __name__ == '__main__':
    unittest.main()
