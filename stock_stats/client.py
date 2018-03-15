from .http import HttpClient, HttpException
from zipfile import ZipFile, BadZipfile, LargeZipFile
from io import TextIOWrapper
import json
import csv
from typing import List, Dict


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
        :return: Retrieves a list of stock symbols and descriptions.
        :raises StockException: On error, including network errors
        """
        try:
            url = "%s/v3/databases/WIKI/codes?api_key=%s" % (self.base_url, self.api_key)
            temp_file, headers = self.http.download(url)
            is_zip = self._headers_indicate_zipfile(headers)
            reader = self._payload_to_csv(temp_file, is_zip)
            result = {symbol: desc for (symbol, desc) in reader}
            return result
        except HttpException as e:
            raise StockException("Network error") from e
