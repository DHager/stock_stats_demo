import unittest
import os
from stock_stats import StockClient, StockException


class TestStockClient(unittest.TestCase):
    """
    Attempts to test the features of the client that do not require a valid API
    key or network access.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data_dir = os.path.join(os.path.dirname(__file__), "data")

    def setUp(self):
        self.client = StockClient("NOKEY")

    def testCsvParsing(self):
        file_name = os.path.join(self.__class__.data_dir, "symbols.csv")
        reader = self.client._payload_to_csv(file_name, False)

        rows = list(reader)
        expected = [
            ['WIKI/AAPL', 'Apple Inc (AAPL) Prices, Dividends, Splits and Trading Volume'],
            ['WIKI/ABC', 'AmerisourceBergen Corp. (ABC) Prices, Dividends, Splits and Trading Volume'],
            ['WIKI/AA', 'Alcoa Inc. (AA) Prices, Dividends, Splits and Trading Volume']
        ]
        self.assertEqual(rows, expected)

    def testZipExtraction(self):
        file_name = os.path.join(self.__class__.data_dir, "symbols.zip")
        reader = self.client._payload_to_csv(file_name, True)

        rows = list(reader)
        expected = [
            ['WIKI/AAPL', 'Apple Inc (AAPL) Prices, Dividends, Splits and Trading Volume'],
            ['WIKI/ABC', 'AmerisourceBergen Corp. (ABC) Prices, Dividends, Splits and Trading Volume'],
            ['WIKI/AA', 'Alcoa Inc. (AA) Prices, Dividends, Splits and Trading Volume']
        ]
        self.assertEqual(rows, expected)

    def testBadZipException(self):
        with self.assertRaises(StockException):
            file_name = os.path.join(self.__class__.data_dir, "corrupt.zip")
            reader = self.client._payload_to_csv(file_name, True)
            data = list(reader)

if __name__ == '__main__':
    unittest.main()
