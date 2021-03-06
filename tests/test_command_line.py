import unittest

from stock_stats.command_line import create_parser
from tests.shared import captured_output


# We suppress these inspections because Pycharm seems to misunderstand the
# context-manager blocks.
#
# noinspection PyUnusedLocal,PyUnreachableCode
class TestArgumentParsing(unittest.TestCase):
    """
    This set of tests exercises the code that changes command-line arguments
    into a python data-structure.
    """
    def setUp(self):
        self.parser = create_parser()

    def test_help(self):
        cmdline = ["-h"]
        with self.assertRaises(SystemExit) as ecm:
            with captured_output() as (out, err):
                self.parser.parse_args(cmdline)
                self.fail("Expected to end")
        self.assertEqual(ecm.exception.code, 0)

    def test_action_required(self):
        cmdline = ["--key", "mykey"]
        with self.assertRaises(SystemExit) as ecm:
            with captured_output() as (out, err):
                self.parser.parse_args(cmdline)
                self.fail("Expected to end")
        self.assertEqual(ecm.exception.code, 2)

    def test_symbols(self):
        cmdline = ["list-symbols", "--key", "mykey"]
        with captured_output() as (out, err):
            args = self.parser.parse_args(cmdline)
        self.assertIsNotNone(args)

    def test_stats_basic(self):
        cmdline = ["month-averages", "--key", "mykey",
                   "2017-01", "2017-02",
                   "BUY", "N", "LARGE"
                   ]
        with captured_output() as (out, err):
            args = self.parser.parse_args(cmdline)
            self.assertIsNotNone(args)

    def test_missing_key(self):
        with self.assertRaises(SystemExit) as ecm:
            with captured_output() as (out, err):
                self.parser.parse_args(["symbols"])
                self.fail("Expected to end with error")
        self.assertEqual(ecm.exception.code, 2)

    def test_bad_date(self):
        cmdline = ["stats", "--key", "mykey",
                   "2001-15", "2020-99",
                   "BUY", "N", "LARGE"
                   ]
        with self.assertRaises(SystemExit) as ecm:
            with captured_output() as (out, err):
                args = self.parser.parse_args(cmdline)
                self.fail("Expected to end with error")
        self.assertEqual(ecm.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
