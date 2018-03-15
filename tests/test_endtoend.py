import unittest
from stock_stats.command_line import main, create_parser
from tests import captured_output


@unittest.skip("Used only for manual debugging")
class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()
        self.apikey = open("apikey.txt", 'r').readline().strip()

    def testSymbols(self):
        expected_first_line = "WIKI/AAPL" + "\t" + "Apple Inc (AAPL) Prices, Dividends, Splits and Trading Volume"
        with self.assertRaises(SystemExit) as ecm:
            with captured_output() as (out, err):
                raw_args = ["symbols", "--key", self.apikey]
                args = self.parser.parse_args(raw_args)
                main(args)
        self.assertEqual(ecm.exception.code, 0)
        actual_first_line = out.getvalue().strip().split("\n")[0]
        self.assertEqual(expected_first_line, actual_first_line)


if __name__ == '__main__':
    unittest.main()
