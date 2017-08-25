import click
import csv

from sklearn import tree

try:
    from sklearn import model_selection as mscv
except ImportError:
    from sklearn import cross_validation as mscv


class Contig(object):
    def __init__(self, contigid, variables={}, classification=False):
        self.contigid = contigid
        self.variables = variables
        self.classification = classification


def parseTaxdump(blastdb):
    """
    Parses a local copy of the NCBI Taxonomy dump for use by later functions.

    Args:
        blastdb: A string containing the root directory for the NCBI taxdump.
    Returns:
        taxdump: A dictionary mapping NCBI taxon ids to a tuple containing the
            taxid of the parent taxon and the name of the current taxon.
    """
    taxdump = {}
    with open(blastdb + "/names.dmp") as names:
        click.echo("Reading names.dmp")
        namesReader = list(csv.reader(names, delimiter="|"))
        with click.progressbar(namesReader) as nr:
            for line in nr:
                if "scientific name" in line[3].strip():
                    taxdump[line[0].strip()] = line[1].strip()
    with open(blastdb + "/nodes.dmp") as nodes:
        click.echo("Reading nodes.dmp")
        nodesReader = list(csv.reader(nodes, delimiter="|"))
        with click.progressbar(nodesReader) as nr:
            for line in nr:
                taxdump[line[0].strip()] = [taxdump[line[0].strip()], line[1].strip(), line[2].strip()]  # {sseqid: (Name, Parent, Rank)}
    with open(blastdb + "/merged.dmp") as merged:
        click.echo("Reading merged.dmp")
        mergedReader = list(csv.reader(merged, delimiter="|"))
        with click.progressbar(mergedReader) as mr:
            for line in mr:
                taxdump[line[0].strip()] = ["merged", line[1].strip()]
    with open(blastdb + "/delnodes.dmp") as delnodes:
        click.echo("Reading delnodes.dmp")
        delReader = list(csv.reader(delnodes, delimiter="|"))
        with click.progressbar(delReader) as dr:
            for line in dr:
                taxdump[line[0].strip()] = ["deleted"]
    return taxdump


def taxidToLineage(taxid, taxdump, classificationLevel):
    """
    Recursively converts an NCBI taxid to a full phylogenetic lineage.

    Args:
        taxid: The taxid to look up.
        taxdump: The names/nodes dict as provided by parseTaxDump().
        deletedTaxa: A list of taxids that have been deleted from the taxdump.
        mergedTaxa: A dictionary mapping merged taxa to their new equivalents.
        classificationLevel: The level of classification to save into the corpus. Defaults to phylum.
    Returns:
        retval: A string containing the lineage at the chosen classification level.
    """
    taxid = taxid.split(";")[0]
    tax = taxdump[taxid]
    if "deleted" in tax:
        raise Exception("ERROR: Taxon id %s has been deleted from the NCBI DB.\nPlease update your databases and re-run BLAST." % taxid)
    if "merged" in tax:
        merge = tax[1]
        return taxidToLineage(merge, taxdump, classificationLevel)
    try:
        if tax[2].lower() == classificationLevel.lower():
            return tax[0]
        elif taxid != '1':
            return taxidToLineage(tax[1], taxdump, classificationLevel)
        elif taxid == '1':
            return("nohit")
        else:
            raise Exception("Taxid %s has failed to resolve." % taxid)
    except KeyError:
        raise Exception("Taxon id %s was not found in the NCBI DB.\nPlease update your DB and try again." % taxid)


def constructCorpus(contigs, classMap):
    """
    Construct a corpus for scikit-learn to learn from.

    Args:
        contigsWithClass: A dictionary mapping contig ids to the chosen classification.
        contigsWithCov: A list where each line contains a contig id, that contig's GC content,
            and that contig's average coverage.
        classMap: A dictionary mapping class names to their class id used by scikit-learn.
    Returns:
        corpus: A list of lists, containing the GC content, coverage, and class number.
        testdata: Data that was not classified by BLAST and will later be classified by the
            trained model.
    """
    corpus = []
    testdata = []
    features = []
    for contig in contigs:
        variableBuf = list(contig.variables.values())
        features = list(contig.variables.keys())
        if contig.classification:
            variableBuf.append(contig.classification)
            corpus.append(variableBuf)
        else:
            variableBuf.insert(0, contig.contigid)
            testdata.append(variableBuf)
    return corpus, testdata, features


def constructModel(corpus, classList, features):
    """
    Trains a Decision Tree model on the test corpus.

    Args:
        corpus: A list of lists, containing the GC content, coverage, and class number.
        classList: A list of class names.
    Returns:
        classifier: A DecisionTreeClassifier object that has been trained on the test corpus.
    """
    corpus.sort()  # just in case
    X = []
    Y = []
    for item in corpus:
        X.append([item[0], item[1]])
        Y.append(item[2])
    X_train, X_test, Y_train, Y_test = mscv.train_test_split(X, Y, test_size=0.3, random_state=0)

    classifier = tree.DecisionTreeClassifier()
    classifier = classifier.fit(X_train, Y_train)
    click.echo("Classifier built, score is %s out of 1.00" % classifier.score(X_test, Y_test))
    with open("model.dot", 'w') as dotfile:
        tree.export_graphviz(classifier, out_file=dotfile, feature_names=features,
                             class_names=classList, filled=True, rounded=True, special_characters=True)
    return classifier


def classifyData(classifier, testdata, classMap):
    """
    Classifies data based on the previously trained model.

    Args:
        classifier: A DecisionTreeClassifier object that has been trained on the test corpus.
        testdata: A dataset to classify based on reads.
    """
    testdata.sort()
    X = []
    for item in testdata:
        X.append([item[1], item[2]])
    Y = classifier.predict(X)
    contigIDs = list(zip(*testdata))[0]  # https://stackoverflow.com/questions/4937491/matrix-transpose-in-python
    result = list(zip(contigIDs, Y))
    return result
