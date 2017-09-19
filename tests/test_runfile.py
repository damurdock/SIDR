import sidr
import pytest
import mock

from contextlib import closing
try:  # https://stackoverflow.com/questions/11914472/stringio-in-python3
    from StringIO import StringIO
except ImportError:
    from io import StringIO