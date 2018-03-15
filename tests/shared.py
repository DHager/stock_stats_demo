import sys
import os
from tempfile import mkstemp
from contextlib import contextmanager
from io import StringIO
from stock_stats import HttpClient
from typing import Tuple, Dict


@contextmanager
def captured_output():
    """
    Temporarily redirects STDOUT and STDERR for capture.    
    """
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class MockHttpClient(HttpClient):
    def __init__(self):
        # Maps specific URLs to outputs
        self.responses = {}  # type: Dict[str, Tuple[str, Dict[str, str]]]
        self.tempfiles = []  # type: List[str]

    def get(self, url: str) -> Tuple[bytes, Dict[str, str]]:
        content, headers = self.responses.get(url, (None, None))

        if content is None:
            raise Exception("No preset response for URL '%s'" % url)
        if isinstance(content, str):
            content = bytes(content)

        return content, headers

    def download(self, url: str) -> Tuple[str, Dict[str, str]]:
        content, headers = self.get(url)

        # In this context callers expect a temp file result
        (fd, fpath) = mkstemp()
        self.tempfiles.append(fpath)
        with os.fdopen(fd, 'wb') as fh:
            fh.write(content)

        return fpath, headers

    def cleanup(self):
        for fpath in self.tempfiles:
            os.unlink(fpath)
