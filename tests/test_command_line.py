import unittest
import sys
from argparse import ArgumentParser
from stock_stats.command_line import create_parser
from tests import captured_output


class TestArgumentParsing(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()

    def test_help(self):
        try:
            with captured_output() as (out, err):
                self.parser.parse_args(["-h"])
            self.fail("Expected to end")
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    def test_action_required(self):
        try:
            with captured_output() as (out, err):
                self.parser.parse_args(["--key", "mykey"])
            self.fail("Expected to end")
        except SystemExit as e:
            self.assertEqual(e.code, 2)

    def test_symbols(self):
        try:
            cmdline = ["symbols", "--key", "mykey"]
            with captured_output() as (out, err):
                args = self.parser.parse_args(cmdline)
            self.assertIsNotNone(args)
        except SystemExit as e:
            self.fail("Did not expect exit attempt with code %d" % e.code)

    def test_stats_basic(self):
        try:
            cmdline = ["stats", "--key", "mykey", "2001-01", "2020-01", "BUY", "N", "LARGE"]
            with captured_output() as (out, err):
                args = self.parser.parse_args(cmdline)
            self.assertIsNotNone(args)
        except SystemExit as e:
            self.fail("Did not expect exit attempt with code %d" % e.code)

    def test_missing_key(self):
        try:
            with captured_output() as (out, err):
                self.parser.parse_args(["symbols"])
            self.fail("Expected to end with error")
        except SystemExit as e:
            self.assertEqual(e.code, 2)

    def test_bad_date(self):
        try:
            cmdline = ["stats", "--key", "mykey", "2001-15", "2020-99", "BUY", "N", "LARGE"]
            with captured_output() as (out, err):
                args = self.parser.parse_args(cmdline)
            self.fail("Expected to end with error")
        except SystemExit as e:
            self.assertEqual(e.code, 2)

if __name__ == '__main__':
    unittest.main()