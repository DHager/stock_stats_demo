import csv
import json
from collections import OrderedDict
from datetime import date
from io import TextIOWrapper
from typing import Dict, List, Union, Any
from zipfile import BadZipfile, LargeZipFile, ZipFile

from .http import HttpClient, HttpException


class StockException(Exception):
    """
    General purpose exception indicating something has gone wrong in the stock-
    statistic application.    
    """
    pass


class StockClient(object):
    DEFAULT_BASE_URL = 'https://www.quandl.com/api'
    HEADER_CONTENT_TYPE = 'Content-Type'
    CONTENT_TYPE_ZIP = 'application/zip'

    PARAM_KEY = 'api_key'
    PARAM_START = 'start_date'
    PARAM_END = 'end_date'
    PARAM_GROUP = 'collapse'
    PARAM_COMBINE = 'transform'

    COL_DATE = 'Date'
    COL_OPEN = 'Open'
    COL_CLOSE = 'Close'
    COL_ADJ_OPEN = 'Adj. Open'
    COL_ADJ_CLOSE = 'Adj. Close'
    COL_LOW = 'Low'
    COL_HIGH = 'High'
    COL_ADJ_LOW = 'Adj. Low'
    COL_ADJ_HIGH = 'Adj. High'

    def __init__(self, http_client: HttpClient, api_key: str,
                 base_url: str = None):
        """
        :param api_key: The API key
        :param base_url: The base URL to use, such as https://www.quandl.com/api
        """
        if base_url is None:
            base_url = self.DEFAULT_BASE_URL

        base_url = base_url.rstrip("/")
        self.http = http_client
        self.base_url = base_url
        self.api_key = api_key

    def _headers_indicate_zipfile(self, headers: Dict[str, str]) -> bool:
        actual = headers.get(self.HEADER_CONTENT_TYPE, None)
        return actual == self.CONTENT_TYPE_ZIP

    def _parse_csv_file(self, temp_file: str, is_zip: bool = False) -> List[List]:
        """
        :param temp_file: Path to temporary file on disk
        :param is_zip: If true, indicates that the csv is packaged as the sole item inside a zip file.
        :return: Row-data
        """
        try:
            if is_zip:
                archive = ZipFile(temp_file, 'r')
                names = archive.namelist()
                if len(names) != 1:
                    raise StockException("Unexpectedly got multiple files from API in zip-file")
                csv_handle = archive.open(names[0])

                # Workaround for ZipFile.open() not supporting text-mode
                # Closing wrapper closes wrapped object as well
                csv_handle = TextIOWrapper(csv_handle)
            else:
                csv_handle = open(temp_file, "rt")
        except (BadZipfile, LargeZipFile) as e:
            raise StockException("Error extracting ZIP data") from e

        try:
            with csv_handle:
                reader = csv.reader(csv_handle, csv.excel)
                rows = list(reader)
            return rows
        except csv.Error as e:
            raise StockException("Error parsing CSV") from e

    def _convert_timeseries(self, dataset: Dict) -> List[Dict[str, Union[float, date]]]:
        headers = dataset['column_names']
        converted = []
        for row in dataset['data']:
            kv = dict(zip(headers, row))
            parts = [int(s) for s in kv[self.COL_DATE].split("-")]
            kv[self.COL_DATE] = date(*parts)
            # Convert from a string to date-object
            converted.append(kv)

        # Shouldn't need to sort, server already returns our rows in reverse-
        # chronological order

        return converted

    def _group_by_month(self, days: List[Dict]) -> Dict[str, Dict]:
        by_month = {}
        for row in days:
            key = row[self.COL_DATE].strftime('%Y-%m')
            if key not in by_month:
                by_month[key] = []
            by_month[key].append(row)
        return by_month

    def get_symbols(self) -> Dict[str, str]:
        """
        :return: Retrieves a dictionary of stock symbols and descriptions.
        :raises StockException: On error, including network errors
        """
        try:
            params = {
                'api_key': self.api_key
            }
            url = "%s/v3/databases/WIKI/codes" % (self.base_url,)
            temp_file, headers = self.http.download(url, params)
            is_zip = self._headers_indicate_zipfile(headers)
            rows = self._parse_csv_file(temp_file, is_zip)

            result = OrderedDict()
            for (symbol, desc) in rows:
                # Intitial output seems to be in form DATABASE/DATASET, so we
                # want to strip the WIKI/ part out.
                short_name = symbol.split("/")[1]
                result[short_name] = desc

            return result
        except HttpException as e:
            raise StockException("Network error") from e

    def get_monthly_averages(self, symbol: str, start_date: date,
                             end_date: date, adjusted: bool
                             ) -> Dict[str, Dict[str, float]]:
        days = self._get_standard_timeseries(end_date, start_date, symbol)
        by_month = self._group_by_month(days)

        if adjusted:
            open_column = self.COL_ADJ_OPEN
            close_column = self.COL_ADJ_CLOSE
        else:
            open_column = self.COL_OPEN
            close_column = self.COL_CLOSE

        results = {}  # Keyed by month
        for key, days in by_month.items():
            open_total = 0.0
            close_total = 0.0
            day_count = 0.0
            assert len(days) > 0
            for day in days:
                open_total += day[open_column]
                close_total += day[close_column]
                day_count += 1
            results[key] = {
                'average_open':  open_total / day_count,
                'average_close': close_total / day_count,
            }
        return results

    def _get_standard_timeseries(self, end_date, start_date, symbol):
        url = "%s/v3/datasets/WIKI/%s/data.json" % (self.base_url, symbol)
        params = {
            self.PARAM_KEY:   self.api_key,
            self.PARAM_START: start_date.isoformat(),
            self.PARAM_END:   end_date.isoformat(),

            # Note: We can't ask the server to sum up the stats for us, because
            # there may be gaps in days when market is closed, so we won't know
            # how much to divide.
        }
        try:
            body, headers = self.http.get(url, params)
            json_body = json.loads(body)
            days = self._convert_timeseries(json_body['dataset_data'])
        except HttpException as e:
            raise StockException("Network error") from e
        except json.decoder.JSONDecodeError as e:
            raise StockException("Data encoding error") from e
        return days

    def get_best_days(self, symbol: str, start_date: date,
                      end_date: date, adjusted: bool
                      ) -> Dict[str, Any]:

        days = self._get_standard_timeseries(end_date, start_date, symbol)

        if adjusted:
            lo_column = self.COL_LOW
            hi_column = self.COL_HIGH
        else:
            lo_column = self.COL_ADJ_LOW
            hi_column = self.COL_ADJ_HIGH

        best_spread = 0.0
        best_day = None

        for day in days:
            spread = day[hi_column] - day[lo_column]
            if spread > best_spread:
                best_spread = spread
                best_day = day

        return {
            "date":   best_day[self.COL_DATE],
            "spread": best_spread
        }
