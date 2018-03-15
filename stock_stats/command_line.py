from typing import Any, Optional
import re
import argparse
import sys
from datetime import date
from stock_stats import StockClient

def parse_month(val: str) -> date:
    m = re.match(r"^(\d{4})-(\d{2})$", val)
    if m is None:
        raise argparse.ArgumentTypeError("Invalid year-month")
    try:
        d = date(int(m.group(1)), int(m.group(2)), 1)
        return d
    except ValueError as e:
        raise argparse.ArgumentTypeError("Invalid year-month") from e


def create_parser() -> argparse.ArgumentParser:
    main_parser = argparse.ArgumentParser(description='Demos access and analysis of stock data.')

    # Known issues:
    # 1. Can't make subcommand mandatory.
    # 2. Required -k option is listed under "optional" arguments in help.
    # 3. Unable to get both subcommands to share their -k configuration, so duplicating for now.

    subparsers = main_parser.add_subparsers(title="Sub-commands", dest='action')

    list_parser = subparsers.add_parser('symbols', help="List all ticker-symbols with descriptions.")
    list_parser.add_argument('--key',
                             metavar='API_KEY',
                             required=True,
                             help="Quandl API key")

    stats_parser = subparsers.add_parser('stats', help="Calculates statistics for a month-to-month span.")
    stats_parser.add_argument('--key',
                              metavar='API_KEY',
                              required=True,
                              help="Quandl API key")

    stats_parser.add_argument('start_month', type=parse_month, help="Start month inclusive. Ex: 2018-01")
    stats_parser.add_argument('end_month', type=parse_month, help="End month inclusive. Ex: 2018-12")
    stats_parser.add_argument('symbols', nargs='+', help="Stock symbols")
    stats_parser.add_argument('--max-daily-profit', action='store_true')
    stats_parser.add_argument('--busy-day', action='store_true')
    stats_parser.add_argument('--biggest-loser', action='store_true')

    return main_parser


def parse_commandline() -> Optional[Any]:
    main_parser = create_parser()
    args = main_parser.parse_args()
    return args


def main(args: Any):
    client = StockClient(args.key)

    if args.action == 'symbols':
        rows = client.get_symbols()
        for (symbol, desc) in rows:
            print("%s\t%s" % (symbol, desc))
    elif args.action == 'stats':
        raise Exception("Not Yet Implemented")  # TODO
    else:
        assert False
    sys.exit(0)


def shell_entry():
    args = parse_commandline()
    if args is None:
        exit(1)
    main(args)


if __name__ == "__main__":
    shell_entry()
