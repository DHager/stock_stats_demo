import unittest
import sys
from argparse import ArgumentParser
from stock_stats.command_line import create_parser
from tests import captured_output


class TestArgumentParsing(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()

    def test_help(self):
        cmd = ["-h"]
        with self.assertRaises(SystemExit) as ecm:
            with captured_output() as (out, err):
                self.parser.parse_args(cmd)
                self.fail("Expected to end")
        self.assertEqual(ecm.exception.code, 0)

    def test_action_required(self):
        cmd = ["--key", "mykey"]
        with self.assertRaises(SystemExit) as ecm:
            with captured_output() as (out, err):
                self.parser.parse_args(cmd)
                self.fail("Expected to end")
        self.assertEqual(ecm.exception.code, 2)

    def test_symbols(self):
        cmdline = ["list-symbols", "--key", "mykey"]
        with captured_output() as (out, err):
            args = self.parser.parse_args(cmdline)
        self.assertIsNotNone(args)

    def test_stats_basic(self):
        cmdline = ["month-averages", "--key", "mykey",
                   "2001-01", "2020-01",
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
        with self.assertRaises(SystemExit) as ecm:
            cmdline = ["stats", "--key", "mykey",
                       "2001-15", "2020-99",
                       "BUY", "N", "LARGE"
                       ]
            with captured_output() as (out, err):
                args = self.parser.parse_args(cmdline)
            self.fail("Expected to end with error")
        self.assertEqual(ecm.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
