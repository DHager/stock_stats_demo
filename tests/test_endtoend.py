import unittest
import os
import json
from stock_stats.command_line import main, create_parser
from tests import captured_output
from typing import Dict


@unittest.skipIf(not os.path.isfile("apikey.txt"),
                 "Live tests, skip if no stored API key")
class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()
        self.apikey = open("apikey.txt", 'r').readline().strip()

    def _assertDictSubset(self, smaller: Dict, larger: Dict):
        """
        Replacement for deprecated TestCase.assertDictContainsSubset, not sure
        why the deprecation occurred and whether it indicates a fundamental
        pitfall.
        """
        self.assertTrue(set(smaller.items()).issubset(set(larger.items())))

    def testSymbols(self):
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
    def testSimpleStats(self):
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
