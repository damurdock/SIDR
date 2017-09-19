import sidr
import pytest
import mock

from contextlib import closing
try:  # https://stackoverflow.com/questions/11914472/stringio-in-python3
    from StringIO import StringIO
except ImportError:
    from io import StringIO

test_fasta = """>1
GCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATAT
GCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATAT
GCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATATGCGCATAT
"""

def filegenerator(filestrings):
    for f in filestrings:
        yield closing(StringIO(f))

def test_readFasta():
    with mock.patch('sidr.default.open', mock.mock_open()) as m:
        m.side_effect = filegenerator([test_fasta])
        fastaCheck = sidr.default.readFasta("test")
        assert list(fastaCheck.keys()) == ['1']
        assert list(fastaCheck.values())[0].variables["GC"] == 50

def test_readBAM():
    return


def test_readBLAST():
    return

