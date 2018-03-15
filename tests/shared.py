import sys
from contextlib import contextmanager
from io import StringIO


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
