from typing import Any, Optional
import re
import argparse
import sys
import json
from datetime import date
from stock_stats import HttpClient, StockClient
import os
import shutil


def pick_storage_folder():
    # Not sure which OSes this doesn't work on
    return os.path.expanduser(os.path.join("~", ".stock_stats"))


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
    subparsers.required = True  # Workaround for http://bugs.python.org/issue9253#msg186387

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

    clean_parser = subparsers.add_parser('clean', help="Cleans caches")

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


def do_clean(storage_folder: str) -> int:
    if not os.path.isdir(storage_folder):
        print("Nothing to clean, %s does not exist" % storage_folder)
        return 0
    entry = input("Deleting %s, type 'confirm' to proceed: " % storage_folder)
    if entry == 'confirm':
        shutil.rmtree(storage_folder)
        return 0
    else:
        print("Clean canceled.")
        return 1


def main(args: Any) -> int:
    storage_folder = pick_storage_folder()

    if args.action == 'clean':
        return do_clean(storage_folder)

    http_client = HttpClient()
    client = StockClient(http_client, args.key)

    if args.action == 'symbols':
        symbols = client.get_symbols()
        print(json.dumps(symbols, sort_keys=True, indent=4, separators=(',', ': ')))
    elif args.action == 'stats':
        raise Exception("Not Yet Implemented")  # TODO
    else:
        return 255
    return 0


def shell_entry():
    args = parse_commandline()
    if args is None:
        exit(1)
    code = main(args)
    sys.exit(code)


if __name__ == "__main__":
    shell_entry()
