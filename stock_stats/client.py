import csv
import json
from collections import OrderedDict
from datetime import date
from functools import reduce
from io import TextIOWrapper
from typing import Any, Dict, List, Union
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
    COL_VOLUME = 'Volume'
    COL_ADJ_VOLUME = 'Adj. Volume'

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

    def _parse_csv_file(self, path: str, is_zip: bool = False) -> List[List]:
        """
        :param path: Path to temporary file on disk
        :param is_zip: File is zip, expect single CSV inside
        :return: Row-data
        """
        try:
            if is_zip:
                archive = ZipFile(path, 'r')
                names = archive.namelist()
                if len(names) != 1:
                    raise StockException(
                        "Unexpectedly got multiple files from API in zip-file")
                csv_handle = archive.open(names[0])

                # Workaround for ZipFile.open() not supporting text-mode
                # Closing wrapper closes wrapped object as well
                csv_handle = TextIOWrapper(csv_handle)
            else:
                csv_handle = open(path, "rt")
        except (BadZipfile, LargeZipFile) as e:
            raise StockException("Error extracting ZIP data") from e

        try:
            with csv_handle:
                reader = csv.reader(csv_handle, csv.excel)
                rows = list(reader)
            return rows
        except csv.Error as e:
            raise StockException("Error parsing CSV") from e

    def _convert_timeseries(self, dataset: Dict) \
            -> List[Dict[str, Union[float, date]]]:

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

    def get_monthly_averages(self, timeseries, adjusted: bool) \
            -> Dict[str, Dict[str, float]]:

        by_month = self._group_by_month(timeseries)

        if adjusted:
            open_column = self.COL_ADJ_OPEN
            close_column = self.COL_ADJ_CLOSE
        else:
            open_column = self.COL_OPEN
            close_column = self.COL_CLOSE

        results = {}  # Keyed by month
        for key, timeseries in by_month.items():
            open_total = 0.0
            close_total = 0.0
            day_count = 0.0
            assert len(timeseries) > 0
            for day in timeseries:
                open_total += day[open_column]
                close_total += day[close_column]
                day_count += 1
            results[key] = {
                'average_open':  open_total / day_count,
                'average_close': close_total / day_count,
            }
        return results

    def get_standard_timeseries(self, symbol: str, start: date, end: date):
        url = "%s/v3/datasets/WIKI/%s/data.json" % (self.base_url, symbol)
        params = {
            self.PARAM_KEY:   self.api_key,
            self.PARAM_START: start.isoformat(),
            self.PARAM_END:   end.isoformat(),

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

    def get_top_variance_day(self, timeseries, adjusted: bool) \
            -> Dict[str, Any]:

        if adjusted:
            lo_column = self.COL_LOW
            hi_column = self.COL_HIGH
        else:
            lo_column = self.COL_ADJ_LOW
            hi_column = self.COL_ADJ_HIGH

        top_variance = 0.0
        top_day = None

        for day in timeseries:
            variance = day[hi_column] - day[lo_column]
            if variance > top_variance:
                top_variance = variance
                top_day = day

        return {
            "date":   top_day[self.COL_DATE],
            "variance": top_variance
        }

    def get_busy_days(self, timeseries, adjusted: bool) -> Dict[str, Any]:

        if adjusted:
            vol_column = self.COL_VOLUME
        else:
            vol_column = self.COL_ADJ_VOLUME

        total_volume = reduce(lambda a, b: a + b,
                              map(lambda d: d[vol_column], timeseries))
        mean_volume = total_volume / len(timeseries)
        threshold = mean_volume * 1.10
        busy_days = {}
        for day in timeseries:
            if day[vol_column] > threshold:
                busy_days[day[self.COL_DATE]] = day[vol_column]
        return {
            "average_volume": mean_volume,
            "busy_days":      busy_days
        }

    def get_losing_day_count(self, timeseries, adjusted: bool) -> int:

        if adjusted:
            open_column = self.COL_ADJ_OPEN
            close_column = self.COL_ADJ_CLOSE
        else:
            open_column = self.COL_OPEN
            close_column = self.COL_CLOSE

        # bad_days = len(list(filter(None,
        # map(lambda d: d[close_column] < d[open_column], timeseries)
        # ))
        bad_days = 0
        for day in timeseries:
            if day[close_column] < day[open_column]:
                bad_days += 1

        return bad_days
