from urllib import request
from urllib.error import HTTPError, URLError, ContentTooShortError
from zipfile import ZipFile, BadZipfile, LargeZipFile
from io import TextIOWrapper
import csv

from typing import List, Dict


class StockException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StockClient(object):
    CONTENT_TYPE_ZIP = 'application/zip'

    def __init__(self, api_key: str, base_url: str = None):
        """
        :param api_key: The API key
        :param base_url: The base URL to use, such as https://www.quandl.com/api/v3/databases/WIKI
        """
        if base_url is None:
            base_url = 'https://www.quandl.com/api/v3/databases/WIKI'

        base_url.rstrip("/")
        self.base_url = base_url
        self.api_key = api_key

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

    def get_symbols(self) -> List[List[str]]:
        """
        :return: Retrieves a list of stock symbols and descriptions.
        :raises StockException: On error, including network errors
        """
        try:
            url = "%s/codes?api_key=%s" % (self.base_url, self.api_key)
            temp_file, headers = request.urlretrieve(url)
            is_zip = headers['Content-Type'] == StockClient.CONTENT_TYPE_ZIP
            reader = self._payload_to_csv(temp_file, is_zip)
            return list(reader)
        except (HTTPError, URLError, ContentTooShortError) as e:
            raise StockException("Network error") from e
        finally:
            request.urlcleanup()
