from .http import HttpClient, HttpException
from zipfile import ZipFile, BadZipfile, LargeZipFile
from io import TextIOWrapper
import json
import csv
from collections import OrderedDict
from datetime import date
from typing import List, Dict, Tuple


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

    GROUP_MONTH = 'monthly'
    COMBINE_TOTAL = 'cumul'

    def __init__(self, http_client: HttpClient, api_key: str, base_url: str = None):
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

    def _payload_to_csv(self, temp_file: str, is_zip: bool = False) -> csv.reader:
        """
        :param temp_file: Path to temporary file on disk
        :param is_zip: If true, indicates that the csv is packaged as the sole item inside a zip file.
        :return: A CSV reader object.
        """
        try:
            if is_zip:
                archive = ZipFile(temp_file, 'r')
                names = archive.namelist()
                if len(names) != 1:
                    raise StockException("Unexpectedly got multiple files from API in zip-file")
                csv_handle = archive.open(names[0])

                # Workaround for ZipFile.open() not supporting text-mode
                csv_handle = TextIOWrapper(csv_handle)
            else:
                csv_handle = open(temp_file, "rt")
            return csv.reader(csv_handle, csv.excel)
        except csv.Error as e:
            raise StockException("Error parsing CSV") from e
        except (BadZipfile, LargeZipFile) as e:
            raise StockException("Error extracting ZIP data") from e

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
            reader = self._payload_to_csv(temp_file, is_zip)

            result = OrderedDict()
            for (symbol, desc) in reader:
                # Intitial output seems to be in form DATABASE/DATASET, so we
                # want to strip the WIKI/ part out.
                short_name = symbol.split("/")[1]
                result[short_name] = desc

            return result
        except HttpException as e:
            raise StockException("Network error") from e

    def get_monthly_averages(self, symbol: str, start_date: date, end_date: date) -> Dict:
        url = "%s/v3/datasets/WIKI/%s/data.json" % (self.base_url, symbol)
        params = {
            self.PARAM_KEY: self.api_key,
            self.PARAM_START: start_date.isoformat(),
            self.PARAM_END: end_date.isoformat(),
            self.PARAM_GROUP: self.GROUP_MONTH,
            self.PARAM_COMBINE: self.COMBINE_TOTAL,  # No average? We'll do the division ourselves.
        }
        try:
            """
            column_index=4
            """
            content, headers = self.http.get(url, params)
            d = json.loads(content)
            return d
        except HttpException as e:
            raise StockException("Network error") from e
