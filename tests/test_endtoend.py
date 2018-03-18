import unittest
import os
import json
from stock_stats.command_line import main, create_parser
from tests import captured_output
from typing import Dict


@unittest.skipUnless(
    os.path.isfile(os.path.join(__file__, "..", "..", "apikey.txt")),
    "Live tests, skip if no stored API key")
class TestEndToEnd(unittest.TestCase):
    """
    These live tests approximate command-line input and check STDOUT, and are
    primarily used to help in active development and debugging.
    """
    def setUp(self):
        self.parser = create_parser()
        key_path = os.path.join(__file__, "..", "..", "apikey.txt")
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

    @unittest.skip("Incomplete")
    def test_month_averages(self):
        with captured_output() as (out, err):
            raw_args = ["month-averages", "--key", self.apikey, "2017-01", "2017-06", "GOOGL"]
            args = self.parser.parse_args(raw_args)
            code = main(args)
            self.assertEqual(code, 0)
        text = out.getvalue().strip()
        data = json.loads(text)
        self.assertIn("GOOGL", data)


if __name__ == '__main__':
    unittest.main()
