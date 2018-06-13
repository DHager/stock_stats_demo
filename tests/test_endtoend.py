import json
import os
import unittest
from typing import Dict

from stock_stats.client import StockException
from stock_stats.command_line import create_parser, main
from tests.shared import captured_output


@unittest.skipUnless(
    os.path.isfile(os.path.join(os.path.dirname(__file__), "..", "apikey.txt")),
    "Live tests, skip if no stored API key")
class TestEndToEnd(unittest.TestCase):
    """
    These live tests approximate command-line input and check STDOUT, and are
    primarily used to help in active development and debugging.
    """

    def setUp(self):
        self.parser = create_parser()
        key_path = os.path.join(os.path.dirname(__file__), "..", "apikey.txt")
        with open(key_path, 'r') as fh:
            self.apikey = fh.readline().strip()

    def _assertDictSubset(self, smaller: Dict, larger: Dict):
        """
        Replacement for deprecated TestCase.assertDictContainsSubset, not sure
        why the deprecation occurred and whether it indicates a fundamental
        pitfall.
        """
        self.assertTrue(set(smaller.items()).issubset(set(larger.items())))

    def test_list_symbols(self):
        expected_entries = {
            "AAPL": "Apple Inc (AAPL) Prices, Dividends, Splits and Trading Volume"
        }

        with captured_output() as (out, err):
            raw_args = ["list-symbols", "--key", self.apikey]
            args = self.parser.parse_args(raw_args)
            code = main(args)
            self.assertEqual(code, 0)
        actual_entries = json.loads(out.getvalue().strip())
        self._assertDictSubset(expected_entries, actual_entries)

    def test_month_averages(self):
        with captured_output() as (out, err):
            raw_args = ["month-averages", "--key", self.apikey,
                        "2017-01", "2017-06", "GOOGL", 'MSFT']
            args = self.parser.parse_args(raw_args)
            code = main(args)
            self.assertEqual(code, 0)
        text = out.getvalue().strip()
        data = json.loads(text)
        self.assertIn("GOOGL", data)
        self.assertIn("MSFT", data)
        actual_googl_open = data['GOOGL']['2017-01']['average_open']
        self.assertAlmostEqual(actual_googl_open, 829.854)

    def test_error_invalid_symbol(self):
        with self.assertRaises(StockException):
            with captured_output():
                raw_args = ["month-averages", "--key", self.apikey,
                            "2017-01", "2017-01", "WEYLANDYUTANI"]
                args = self.parser.parse_args(raw_args)
                main(args)

    def test_error_swapped_months(self):
        with self.assertRaises(StockException):
            with captured_output():
                raw_args = ["month-averages", "--key", self.apikey,
                            "2017-02", "2017-01", "GOOGL"]
                args = self.parser.parse_args(raw_args)
                main(args)

    def test_top_variance_days(self):
        with captured_output() as (out, err):
            raw_args = ["top-variance-days", "--key", self.apikey,
                        "2017-01", "2017-06", "GOOGL", 'MSFT']
            args = self.parser.parse_args(raw_args)
            code = main(args)
            self.assertEqual(code, 0)
        text = out.getvalue().strip()
        data = json.loads(text)
        self.assertIn("GOOGL", data)
        self.assertIn("MSFT", data)
        actual_googl_variance = data['GOOGL']['variance']
        self.assertAlmostEqual(actual_googl_variance, 52.13)

    def test_busy_days(self):
        with captured_output() as (out, err):
            raw_args = ["busy-days", "--key", self.apikey,
                        "2017-01", "2017-06", "GOOGL", 'MSFT']
            args = self.parser.parse_args(raw_args)
            code = main(args)
            self.assertEqual(code, 0)
        text = out.getvalue().strip()
        data = json.loads(text)
        self.assertIn("GOOGL", data)
        self.assertIn("MSFT", data)
        sample_busy_day = data['GOOGL']['busy_days']['2017-01-03']
        self.assertEqual(sample_busy_day, 1959033)

    def test_bad_days(self):
        with captured_output() as (out, err):
            raw_args = ["biggest-loser", "--key", self.apikey,
                        "2017-01", "2017-06", "GOOGL", 'MSFT']
            args = self.parser.parse_args(raw_args)
            code = main(args)
            self.assertEqual(code, 0)
        text = out.getvalue().strip()
        data = json.loads(text)
        self.assertIn("symbols", data)
        self.assertIn("days", data)
        self.assertIn('MSFT', data['symbols'])


if __name__ == '__main__':
    unittest.main()
