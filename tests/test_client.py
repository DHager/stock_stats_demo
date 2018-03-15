import unittest
import os
from stock_stats import StockClient, StockException, HttpClient
from .shared import MockHttpClient


class TestStockClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data_dir = os.path.join(os.path.dirname(__file__), "data")

    def get_data_path(self, filename: str) -> str:
        return os.path.join(self.__class__.data_dir, filename)

    def setUp(self):
        self.http_client = MockHttpClient()
        self.stock_client = StockClient(self.http_client, "NOKEY")

    def testCsvParsing(self):
        reader = self.stock_client._payload_to_csv(self.get_data_path('symbols.csv'), False)

        rows = list(reader)
        expected = [
            ['WIKI/AAPL', 'Apple Inc (AAPL) Prices, Dividends, Splits and Trading Volume'],
            ['WIKI/ABC', 'AmerisourceBergen Corp. (ABC) Prices, Dividends, Splits and Trading Volume'],
            ['WIKI/AA', 'Alcoa Inc. (AA) Prices, Dividends, Splits and Trading Volume']
        ]
        self.assertEqual(rows, expected)

    def testZipExtraction(self):
        reader = self.stock_client._payload_to_csv(self.get_data_path('symbols.zip'), True)

        rows = list(reader)
        expected = [
            ['WIKI/AAPL', 'Apple Inc (AAPL) Prices, Dividends, Splits and Trading Volume'],
            ['WIKI/ABC', 'AmerisourceBergen Corp. (ABC) Prices, Dividends, Splits and Trading Volume'],
            ['WIKI/AA', 'Alcoa Inc. (AA) Prices, Dividends, Splits and Trading Volume']
        ]
        self.assertEqual(rows, expected)

    def testBadZipException(self):
        with self.assertRaises(StockException):
            reader = self.stock_client._payload_to_csv(self.get_data_path('corrupt.zip'), True)
            data = list(reader)

if __name__ == '__main__':
    unittest.main()
