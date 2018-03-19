import os
import unittest
from datetime import date

from stock_stats.client import StockClient, StockException
from .shared import MockHttpClient


class TestStockClient(unittest.TestCase):
    """
    This set of tests uses canned HTTP responses to check the behavior of
    StockClient with canned HTTP responses.
    """
    def _get_data(self, filename: str) -> bytes:
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        file_path = os.path.join(data_dir, filename)
        with open(file_path, 'rb') as f:
            return f.read()

    def setUp(self):
        self.http_client = MockHttpClient()
        self.stock_client = StockClient(self.http_client, "KEY", "http://example.com/")

    def tearDown(self):
        self.http_client.cleanup()

    def test_csv_parsing(self):
        url = 'http://example.com/v3/databases/WIKI/codes?api_key=KEY'
        self.http_client.responses[url] = (
            self._get_data('symbols.csv'),
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
        url = 'http://example.com/v3/databases/WIKI/codes?api_key=KEY'
        self.http_client.responses[url] = (
            self._get_data('symbols.zip'),
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
                self._get_data('corrupt.zip'),
                {StockClient.HEADER_CONTENT_TYPE: StockClient.CONTENT_TYPE_ZIP}
            )
            self.stock_client.get_symbols()

    def test_monthly_averages(self):
        url = 'http://example.com/v3/datasets/WIKI/GOOGL/data.json' \
              '?api_key=KEY&end_date=2017-06-01&start_date=2017-01-01'
        self.http_client.responses[url] = (self._get_data('averages1.json'), {})

        series = self.stock_client.get_standard_timeseries(
            'GOOGL',
            date(2017, 1, 1),
            date(2017, 6, 1)
        )
        data = self.stock_client.get_monthly_averages(series, adjusted=False)

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

    def test_best_days(self):
        url = 'http://example.com/v3/datasets/WIKI/GOOGL/data.json' \
              '?api_key=KEY&end_date=2017-06-01&start_date=2017-01-01'
        self.http_client.responses[url] = (self._get_data('averages1.json'), {})

        series = self.stock_client.get_standard_timeseries(
            'GOOGL',
            date(2017, 1, 1),
            date(2017, 6, 1)
        )
        data = self.stock_client.get_best_day(series, adjusted=False)

        # Manually calculated
        expected_date = date(2017, 6, 9)
        expected_variance = 52.13

        self.assertEqual(data['date'], expected_date)
        self.assertAlmostEqual(data['variance'], expected_variance)

    def test_busy_days(self):
        url = 'http://example.com/v3/datasets/WIKI/GOOGL/data.json' \
              '?api_key=KEY&end_date=2017-06-01&start_date=2017-01-01'
        self.http_client.responses[url] = (self._get_data('averages1.json'), {})

        series = self.stock_client.get_standard_timeseries(
            'GOOGL',
            date(2017, 1, 1),
            date(2017, 6, 1)
        )
        data = self.stock_client.get_busy_days(series, adjusted=False)

        expected_average = 1632363.696
        expected_days = [
            (date(2017, 6, 30), 2185444),
            (date(2017, 6, 29), 3182331),
            (date(2017, 6, 28), 2713366),
            (date(2017, 6, 27), 2428048),
            (date(2017, 6, 16), 2484914),
            (date(2017, 6, 15), 2349212),
            (date(2017, 6, 13), 1992456),
            (date(2017, 6, 12), 4167184),
            (date(2017, 6, 9), 3613964),
            (date(2017, 5, 25), 1951402),
            (date(2017, 5, 17), 2414323),
            (date(2017, 5, 8), 1863198),
            (date(2017, 5, 4), 1934652),
            (date(2017, 5, 1), 2294856),
            (date(2017, 4, 28), 3753169),
            (date(2017, 4, 27), 1817740),
            (date(2017, 4, 25), 2020460),
            (date(2017, 4, 5), 1855153),
            (date(2017, 4, 3), 1969402),
            (date(2017, 3, 27), 1935211),
            (date(2017, 3, 24), 2105682),
            (date(2017, 3, 23), 3287669),
            (date(2017, 3, 21), 2537978),
            (date(2017, 3, 17), 1868252),
            (date(2017, 3, 1), 1818671),
            (date(2017, 2, 1), 2251047),
            (date(2017, 1, 31), 2020180),
            (date(2017, 1, 30), 3516933),
            (date(2017, 1, 27), 3752497),
            (date(2017, 1, 26), 3493251),
            (date(2017, 1, 23), 2457377),
            (date(2017, 1, 6), 2017097),
            (date(2017, 1, 3), 1959033),

        ]
        self.assertAlmostEqual(data['average_volume'], expected_average)
        self.assertEqual(len(data['busy_days']), len(expected_days))
        for exp_day, exp_vol in expected_days:
            self.assertIn(exp_day, data['busy_days'])
            self.assertEqual(exp_vol, data['busy_days'][exp_day])

    def test_bad_days(self):
        url = 'http://example.com/v3/datasets/WIKI/GOOGL/data.json' \
              '?api_key=KEY&end_date=2017-06-01&start_date=2017-01-01'
        self.http_client.responses[url] = (self._get_data('averages1.json'), {})

        series = self.stock_client.get_standard_timeseries(
            'GOOGL',
            date(2017, 1, 1),
            date(2017, 6, 1)
        )
        count = self.stock_client.get_losing_day_count(series, adjusted=False)

        expected_count = 52
        self.assertEqual(count, expected_count)


if __name__ == '__main__':
    unittest.main()
