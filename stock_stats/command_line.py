from typing import Any
import re
import argparse
import sys
import json
from datetime import date
from stock_stats import HttpClient, StockClient
from typing import List
from dateutil.relativedelta import relativedelta


def _parse_month_begin(val: str) -> date:
    return _parse_month(val, False)


def _parse_month_end(val: str) -> date:
    return _parse_month(val, True)


def _parse_month(val: str, ending: bool = True) -> date:
    m = re.match(r"^(\d{4})-(\d{2})$", val)
    if m is None:
        raise argparse.ArgumentTypeError("Invalid year-month")
    try:
        d = date(int(m.group(1)), int(m.group(2)), 1)
        if ending:
            # Last day of same month. Not the first day of the next month,
            # because the API we work against uses inclusive date ranges.
            d = d + relativedelta(months=1, days=-1)
        return d
    except ValueError as e:
        raise argparse.ArgumentTypeError("Invalid year-month") from e


def _add_parser_global_args(parsers: List[argparse.ArgumentParser]) -> None:
    # The -h/--help options should already be generated for us unless the
    # (sub)parser has used add_help=False in its constructor.

    for parser in parsers:
        # Named group as workaround for https://bugs.python.org/issue9694
        required_group = parser.add_argument_group('required arguments')

        required_group.add_argument('--key', required=True, metavar='API_KEY',
                                    help="Quandl API key")
        parser.add_argument('--pretty', action='store_true',
                            help="Use pretty-printing in JSON output")


def _add_parser_analysis_args(parsers: List[argparse.ArgumentParser]) -> None:
    for parser in parsers:
        parser.add_argument('start_month', type=_parse_month_begin, help="Start month inclusive. Ex: 2017-01")
        parser.add_argument('end_month', type=_parse_month_end, help="End month inclusive. Ex: 2017-06")
        parser.add_argument('symbol', nargs='+', help="Stock symbol. Ex: GOOGL")


def create_parser() -> argparse.ArgumentParser:
    #
    # I've been having a bunch of problems with creating the two-tiered control
    # scheme that I want.
    #
    # In some arrangements, the -h options (from add_help=True) cause a
    # collision when using parent/child relationships, and turning them
    # off makes it work but removes the contextual help.
    #
    # So instead of using "parent" relationships, I'm using helper methods
    # to duplicate configuration across the subparsers.

    main_parser = argparse.ArgumentParser(description='Demos access and analysis of stock data.')

    # Enable two-tiered command structure
    subparsers = main_parser.add_subparsers(title="Sub-commands", dest='action')
    subparsers.required = True  # Workaround for http://bugs.python.org/issue9253#msg186387

    # Individual actions
    listing = subparsers.add_parser(
        'list-symbols',
        help="List all ticker-symbols with descriptions."
    )

    month_average = subparsers.add_parser(
        'month-averages',
        help="Calculates average statistics for a month-to-month span."
    )

    best_days = subparsers.add_parser(
        'best-days',
        help="For each symbol, determines which day offered the highest profit from a single purchase and sale."
    )

    busy_days = subparsers.add_parser(
        'busy-days',
        help="For each symbol, determine which days had trade-volume of >10%% its average."
    )

    biggest_loser = subparsers.add_parser(
        'biggest-loser',
        help="Determine which symbol had the most days where closing was lower than opening."
    )
    _add_parser_global_args([
        listing,
        month_average,
        best_days,
        busy_days,
        biggest_loser
    ])

    _add_parser_analysis_args([
        month_average,
        best_days,
        busy_days,
        biggest_loser
    ])

    return main_parser


def print_json(data: Any, pretty=False):
    if pretty:
        out = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        out = json.dumps(data)
    print(out)


def action_symbols(client: StockClient, pretty: bool = False) -> int:
    symbols = client.get_symbols()
    print_json(symbols, pretty)
    return 0


def action_month_averages(client: StockClient, symbols: List[str],
                          start_date: date, end_date: date,
                          pretty: bool = False
                          ) -> int:
    results = {}
    for symbol in symbols:
        results[symbol] = client.get_monthly_averages(symbol, start_date, end_date)
    print_json(results, pretty)
    return 0


def main(args: Any) -> int:
    http_client = HttpClient()
    client = StockClient(http_client, args.key)

    if args.action == 'list-symbols':
        # No additional arguments needed for this command
        return action_symbols(client, args.pretty)
    elif args.action == 'month-averages':
        return action_month_averages(client, args.symbol, args.start_month, args.end_month, args.pretty)
    elif args.action == 'best-days':
        raise Exception("Not yet implemented")
    elif args.action == 'busy-days':
        raise Exception("Not yet implemented")
    elif args.action == 'biggest-loser':
        raise Exception("Not yet implemented")

    return 4  # Nothing matched


def shell_entry():
    main_parser = create_parser()
    args = main_parser.parse_args()

    if args is None:
        exit(1)

    code = main(args)
    sys.exit(code)


if __name__ == "__main__":
    shell_entry()
