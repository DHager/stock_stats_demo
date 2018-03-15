from urllib import request, response
from urllib.error import HTTPError, URLError, ContentTooShortError
from typing import Tuple, Dict


class HttpException(Exception):
    pass


class HttpClient(object):
    """
    Exists primarily to encapsulate urllib and to allow for convenient 
    unit-testing.
    
    There are other methods to monkey-patch urllib or to install custom
    "openers", but adding this layer of indirection seemed cleaner.
    """

    def __init__(self):
        pass

    def get(self, url: str) -> Tuple[bytes, Dict[str, str]]:
        with request.urlopen(url) as result:
            return result.read(), dict(result.info())

    def download(self, url: str) -> Tuple[str, Dict[str, str]]:
        """        
        Behaves similarly to urllib.request.urlretrieve()
        :param url: URL to GET
        :return: The temp-file where the content has been downloaded, and a dictionary of HTTP response headers. 
        """
        try:
            temp_file, headers = request.urlretrieve(url)  # API may be deprecated in future
            return temp_file, headers
        except (HTTPError, URLError, ContentTooShortError) as e:
            raise HttpException from e

    def cleanup(self):
        request.urlcleanup()
