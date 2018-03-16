from urllib import request, response, parse
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

    def _get_final_url(self, url: str, extra_params: Dict = None) -> str:
        if extra_params is None:
            extra_params = {}

        url_components = list(parse.urlparse(url))

        original_params = dict(parse.parse_qsl(url_components[4]))
        original_params.update(extra_params)
        url_components[4] = parse.urlencode(original_params)

        return parse.urlunparse(url_components)

    def get(self, url: str, extra_params: Dict = None) -> Tuple[bytes, Dict[str, str]]:
        final_url = self._get_final_url(url, extra_params)
        with request.urlopen(final_url) as result:
            return result.read(), dict(result.info())

    def download(self, url: str, extra_params: Dict = None) -> Tuple[str, Dict[str, str]]:
        """        
        Behaves similarly to urllib.request.urlretrieve()
        :param url: URL to GET
        :param extra_params: Key-values to append to URL
        :return: The temp-file where the content has been downloaded, and a dictionary of HTTP response headers. 
        """
        final_url = self._get_final_url(url, extra_params)
        try:

            temp_file, headers = request.urlretrieve(final_url)  # API may be deprecated in future
            return temp_file, headers
        except (HTTPError, URLError, ContentTooShortError) as e:
            raise HttpException from e

    def cleanup(self):
        request.urlcleanup()
