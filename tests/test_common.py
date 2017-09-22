import sidr
import pytest
import mock

from contextlib import closing
try:  # https://stackoverflow.com/questions/11914472/stringio-in-python3
    from StringIO import StringIO
except ImportError:
    from io import StringIO


# TODO: handle initial newline in csv
test_names = """1 |   root    |       |   scientific name |
2 |   phy    |       |   scientific name |
3 |   mergephy    |       |   scientific name |
"""
test_nodes = """1 |   1   |   no rank |       |   0   |   0   |   0   |   0   |   0   |   0   |   0   |   0   |
2 |   1   |   phylum |       |   0   |   0   |   0   |   0   |   0   |   0   |   0   |   0   |
3 |   1   |   phylum |       |   0   |   0   |   0   |   0   |   0   |   0   |   0   |   0   |
"""
test_deleted = "4 |"
test_merged = "5   |   3   |"
test_taxfiles = [test_names, test_nodes, test_merged, test_deleted]
test_taxdump = {'3': ['mergephy', '1', 'phylum'], '2': ['phy', '1', 'phylum'], '4': ['deleted'], '5': ['merged', '3'], '1': ['root', '1', 'no rank']}
test_gc = {"1": 50.0}

# some helpful sites
# https://stackoverflow.com/questions/1289894/how-do-i-mock-an-open-used-in-a-with-statement-using-the-mock-framework-in-pyth
# https://docs.python.org/dev/library/unittest.mock.html#mock-open
# http://boris-42.me/the-simplest-way-in-python-to-mock-open-during-unittest/
# https://gist.github.com/vpetro/1174019
# https://code.activestate.com/recipes/576650-with-statement-for-stringio/

def filegenerator(filestrings):
    for f in filestrings:
        yield closing(StringIO(f))


def test_parseTaxdump():
    with mock.patch('sidr.common.open', mock.mock_open()) as m:
        m.side_effect = filegenerator(test_taxfiles)
        assert sidr.common.parseTaxdump("test", False)[0] == test_taxdump


def test_taxidToLineage():
    assert sidr.common.taxidToLineage("2", test_taxdump, "phylum") == "phy"
    assert sidr.common.taxidToLineage("5", test_taxdump, "phylum") == "mergephy"
    with pytest.raises(Exception) as excinfo:
        sidr.common.taxidToLineage("4", test_taxdump, "phylum")
    assert "ERROR: Taxon id 4 has been deleted from the NCBI DB." in str(excinfo.value)

def test_constructCorpus():
    return