import unittest
import sys
from argparse import ArgumentParser
from stock_stats.command_line import create_parser


class TestArgumentParsing(unittest.TestCase):
    def setUp(self):
        parser = create_parser()
        self._neutralize_parser(parser)
        self.parser = parser

    def _neutralize_parser(self, parser: ArgumentParser) -> None:
        # This is kind of an ugly hack, but it seems ArgumentParser wasn't
        # designed to be very testable.
        #
        # Note that these overrides do NOT affect subparser objects for
        # individual commands, which would take some deeper monkey-patching.
        # This means there's still some STDERR junk when testing.

        def do_nothing(*args, **kwargs):
            pass
        parser._print_message = do_nothing

    def test_help(self):
        try:
            self.parser.parse_args(["-h"])
            self.fail("Expected to end")
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    def test_action_required(self):
        try:
            self.parser.parse_args(["-k", "mykey"])
            self.fail("Expected to end")
        except SystemExit as e:
            self.assertEqual(e.code, 2)

    def test_symbols(self):
        try:
            cmdline = ["symbols", "-k", "mykey"]
            args = self.parser.parse_args(cmdline)
            self.assertIsNotNone(args)
        except SystemExit as e:
            self.fail("Did not expect exit attempt with code %d" % e.code)

    def test_stats_basic(self):
        try:
            cmdline = ["stats", "-k", "mykey", "2001-01", "2020-01", "BUY", "N", "LARGE"]
            args = self.parser.parse_args(cmdline)
            self.assertIsNotNone(args)
        except SystemExit as e:
            self.fail("Did not expect exit attempt with code %d" % e.code)

    def test_missing_key(self):
        try:
            self.parser.parse_args(["symbols"])
            self.fail("Expected to end with error")
        except SystemExit as e:
            self.assertEqual(e.code, 2)

    def test_bad_date(self):
        try:
            cmdline = ["stats", "-k", "mykey", "2001-15", "2020-99", "BUY", "N", "LARGE"]
            args = self.parser.parse_args(cmdline)
            self.fail("Expected to end with error")
        except SystemExit as e:
            self.assertEqual(e.code, 2)

if __name__ == '__main__':
    unittest.main()