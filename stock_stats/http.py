from collections import OrderedDict
from typing import Dict, Tuple
from urllib import parse, request
from urllib.error import ContentTooShortError, HTTPError, URLError


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

        # We alphabetize the extra parameters for unit-testing purposes.
        # Doing so gives us a consistent repeatable final URL.
        ordered_params = OrderedDict(sorted(
            extra_params.items(),
            key=lambda tup: tup[0]
        ))

        url_components = list(parse.urlparse(url))

        original_params = OrderedDict(parse.parse_qsl(url_components[4]))
        original_params.update(ordered_params)
        url_components[4] = parse.urlencode(original_params)

        return parse.urlunparse(url_components)

    def get(self, url: str, extra_params: Dict = None) \
            -> Tuple[bytes, Dict[str, str]]:

        final_url = self._get_final_url(url, extra_params)
        try:
            with request.urlopen(final_url) as result:
                return result.read(), dict(result.info())
        except (HTTPError, URLError, ContentTooShortError) as e:
            raise HttpException from e

    def download(self, url: str, extra_params: Dict = None) \
            -> Tuple[str, Dict[str, str]]:
        """        
        Behaves similarly to urllib.request.urlretrieve()
        :param url: URL to GET
        :param extra_params: Key-values to append to URL
        :return: File path and HTTP headers
        """
        final_url = self._get_final_url(url, extra_params)
        try:
            # Docs suggest urlretrieve API may be deprecated in future
            temp_file, headers = request.urlretrieve(final_url)
            return temp_file, headers
        except (HTTPError, URLError, ContentTooShortError) as e:
            raise HttpException from e

    def cleanup(self):
        request.urlcleanup()
