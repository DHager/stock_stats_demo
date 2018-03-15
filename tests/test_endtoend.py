import unittest
import os
import json
from stock_stats.command_line import main, create_parser
from tests import captured_output


@unittest.skipIf(not os.path.isfile("apikey.txt"),
                 "Live tests, skip if no stored API key")
class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()
        self.apikey = open("apikey.txt", 'r').readline().strip()

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
        self.assertDictContainsSubset(expected_entries, actual_entries)


if __name__ == '__main__':
    unittest.main()
