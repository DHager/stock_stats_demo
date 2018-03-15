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
            "WIKI/AAPL": "Apple Inc (AAPL) Prices, Dividends, Splits and Trading Volume"
        }
        with self.assertRaises(SystemExit) as ecm:
            with captured_output() as (out, err):
                raw_args = ["symbols", "--key", self.apikey]
                args = self.parser.parse_args(raw_args)
                main(args)
        actual_entries = json.loads(out.getvalue().strip())
        self._assertDictSubset(expected_entries, actual_entries)

    @unittest.skip("Incomplete")
    def testSimpleStats(self):
        with self.assertRaises(SystemExit) as ecm:
            with captured_output() as (out, err):
                raw_args = ["stats", "--key", self.apikey, "2001-01", "2020-01","AAPL"]
                args = self.parser.parse_args(raw_args)
                main(args)
        x = out.getvalue().strip()
        self.fail("Incomplete test")


if __name__ == '__main__':
    unittest.main()
