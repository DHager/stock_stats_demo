import unittest
import os
from stock_stats import StockClient, StockException, HttpClient
from .shared import MockHttpClient


class TestStockClient(unittest.TestCase):
    def get_data(self, filename: str) -> str:
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        fpath =  os.path.join(data_dir, filename)
        with open(fpath,'rb') as f:
            return f.read()

    def setUp(self):
        self.http_client = MockHttpClient()
        self.stock_client = StockClient(self.http_client, "KEY", "http://example.com/")

    def tearDown(self):
        self.http_client.cleanup()

    def testCsvParsing(self):
        self.http_client.responses['http://example.com/codes?api_key=KEY'] = (
            self.get_data('symbols.csv'),
            {}
        )
        symbols = self.stock_client.get_symbols()
        expected = {
            'WIKI/AAPL': 'Apple Inc (AAPL) Prices, Dividends, Splits and Trading Volume',
            'WIKI/ABC': 'AmerisourceBergen Corp. (ABC) Prices, Dividends, Splits and Trading Volume',
            'WIKI/AA': 'Alcoa Inc. (AA) Prices, Dividends, Splits and Trading Volume',
        }
        self.assertEqual(expected, symbols)

    def testZipExtraction(self):
        self.http_client.responses['http://example.com/codes?api_key=KEY'] = (
            self.get_data('symbols.zip'),
            {StockClient.HEADER_CONTENT_TYPE : StockClient.CONTENT_TYPE_ZIP}
        )
        symbols = self.stock_client.get_symbols()
        expected = {
            'WIKI/AAPL': 'Apple Inc (AAPL) Prices, Dividends, Splits and Trading Volume',
            'WIKI/ABC': 'AmerisourceBergen Corp. (ABC) Prices, Dividends, Splits and Trading Volume',
            'WIKI/AA': 'Alcoa Inc. (AA) Prices, Dividends, Splits and Trading Volume',
        }
        self.assertEqual(expected, symbols)

    def testBadZipException(self):
        with self.assertRaises(StockException):
            self.http_client.responses[
                'http://example.com/codes?api_key=KEY'] = (
                self.get_data('corrupt.zip'),
                {StockClient.HEADER_CONTENT_TYPE: StockClient.CONTENT_TYPE_ZIP}
            )
            self.stock_client.get_symbols()

if __name__ == '__main__':
    unittest.main()
