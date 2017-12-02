import click
import csv

from sklearn import tree
from sklearn import ensemble

try: # later versions of sklearn move the scoring tools
    from sklearn import model_selection as mscv
except ImportError:
    from sklearn import cross_validation as mscv


class Contig(object): # to store contigs for analysis
    def __init__(self, contigid, variables={}, classification=False):
        self.contigid = contigid
        self.variables = variables
        self.classification = classification


def parseTaxdump(blastdb, createDict):
    """
    Parses a local copy of the NCBI Taxonomy dump for use by later functions.

    Args:
        blastdb: A string containing the root directory for the NCBI taxdump.
        createDict: True to create taxon dictionary for runfile mode
    Returns:
        taxdump: A dictionary mapping NCBI taxon ids to a tuple containing the
            taxid of the parent taxon and the name of the current taxon.
        taxdict: A dictionary mapping human readable names to taxids
    """
    taxdump = {}
    taxidDict = {}
    with open(blastdb + "/names.dmp") as names:
        click.echo("Reading names.dmp")
        namesReader = list(csv.reader(names, delimiter="|"))
        with click.progressbar(namesReader) as nr: # human readable names
            for line in nr:
                if "scientific name" in line[3].strip():
                    taxdump[line[0].strip()] = line[1].strip() # {taxid: Name}
                if createDict:
                    taxidDict[line[1].strip()] = line[0].strip() # {Name: taxid}
    with open(blastdb + "/nodes.dmp") as nodes:
        click.echo("Reading nodes.dmp")
        nodesReader = list(csv.reader(nodes, delimiter="|"))
        with click.progressbar(nodesReader) as nr: # connection between taxids
            for line in nr:
                taxdump[line[0].strip()] = [taxdump[line[0].strip()], line[1].strip(), line[2].strip()]  # {taxid: [Name, Parent, Rank]}
    with open(blastdb + "/merged.dmp") as merged: # merged taxids are the same organism, effectively
        click.echo("Reading merged.dmp")
        mergedReader = list(csv.reader(merged, delimiter="|"))
        with click.progressbar(mergedReader) as mr:
            for line in mr:
                taxdump[line[0].strip()] = ["merged", line[1].strip()]
    with open(blastdb + "/delnodes.dmp") as delnodes: # if a taxid is deleted than the BLAST DB and taxdump are too far out of sync
        click.echo("Reading delnodes.dmp")
        delReader = list(csv.reader(delnodes, delimiter="|"))
        with click.progressbar(delReader) as dr:
            for line in dr:
                taxdump[line[0].strip()] = ["deleted"]
    return taxdump, taxidDict


def taxidToLineage(taxid, taxdump, classificationLevel):
    """
    Recursively converts an NCBI taxid to a full phylogenetic lineage.

    Args:
        taxid: The taxid to look up.
        taxdump: The NCBI taxonomy dump as parsed by parseTaxDump
        classificationLevel: The level of classification to save into the corpus.
    Returns:
        classification: A string containing the lineage at the chosen classification level.
    """
    taxid = taxid.split(";")[0]
    tax = taxdump[taxid]
    if "deleted" in tax: # taxid has been removed from NCBI db, indicates that taxdump and blastdb are out of sync
        raise Exception("ERROR: Taxon id %s has been deleted from the NCBI DB.\nPlease update your databases and re-run BLAST." % taxid)
    if "merged" in tax:
        merge = tax[1]
        return taxidToLineage(merge, taxdump, classificationLevel)
    try:
        if tax[2].lower() == classificationLevel.lower(): # final answer
            return tax[0]
        elif taxid != '1': # recursive call
            return taxidToLineage(tax[1], taxdump, classificationLevel)
        elif taxid == '1': # nohit
            return("nohit")
        else: # edge case
            raise Exception("Taxid %s has failed to resolve." % taxid)
    except KeyError:
        raise Exception("Taxon id %s was not found in the NCBI DB.\nPlease update your DB and try again." % taxid)


def constructCorpus(contigs, classMap, binary, target):
    """
    Construct a corpus, or body of training data for the decision tree, as well as the data under test.

    Args:
        contigs: A list of sidr.common.Contig objects with test variables.
        classMap: A dictionary mapping class names to their class id used by scikit-learn.
        binary: Set True to use "binary" (target/nontarget) classification for the model.
        target: The name of the target classification.
    Returns:
        corpus: A list of lists, containing the GC content, coverage, and class number.
        testdata: Data that was not classified by BLAST and will later be classified by the
            trained model.
        features: List of variables used by each contig.
    """
    corpus = []
    testdata = []
    features = []
    for contig in contigs:
        variableBuf = list(contig.variables.values())
        features = list(contig.variables.keys())
        if contig.classification:
            if binary:
                if contig.classification.lower() == target.lower():
                    variableBuf.append("target")
                    corpus.append(variableBuf)
                else:
                    variableBuf.append("nontarget")
                    corpus.append(variableBuf)
            else:
                variableBuf.append(contig.classification)
                corpus.append(variableBuf)
        else:
            variableBuf.insert(0, contig.contigid)
            testdata.append(variableBuf)
    return corpus, testdata, features


def constructModel(corpus, classList, features, modelOutput):
    """
    Trains a Decision Tree model on the test corpus.

    Args:
        corpus: A list of lists, containing the GC content, coverage, and class number.
        classList: A list of class names.
        features: List of variables used by each contig.
        modelOutput: Location to save model as GraphViz DOT, or False to save no model.
    Returns:
        classifier: A DecisionTreeClassifier object that has been trained on the test corpus.
    """
    corpus.sort()  # just in case
    X = []
    Y = []
    for item in corpus:
        X.append(item[:-1]) # all but the last item
        Y.append(item[-1]) # only the last item
    X_train, X_test, Y_train, Y_test = mscv.train_test_split(X, Y, test_size=0.3, random_state=0)
    # TODO: implement classifier testing and comparison, now only treeClassifier is used
    treeClassifier = tree.DecisionTreeClassifier()
    treeClassifier = treeClassifier.fit(X_train, Y_train)
    click.echo("Decision tree classifier built, score is %s out of 1.00" % treeClassifier.score(X_test, Y_test))
    baggingClassifier = ensemble.BaggingClassifier()
    baggingClassifier = baggingClassifier.fit(X_train, Y_train)
    click.echo("Bagging classifier built, score is %s out of 1.00" % baggingClassifier.score(X_test, Y_test))
    forestClassifier = ensemble.RandomForestClassifier(n_estimators=10)
    forestClassifier = forestClassifier.fit(X_train, Y_train)
    click.echo("Random forest classifier built, score is %s out of 1.00" % forestClassifier.score(X_test, Y_test))
    adaClassifier = ensemble.AdaBoostClassifier(n_estimators=100)
    adaClassifier = adaClassifier.fit(X_train, Y_train)
    click.echo("AdaBoost classifier built, score is %s out of 1.00" % adaClassifier.score(X_test, Y_test))
    gradientClassifier = ensemble.GradientBoostingClassifier(n_estimators=100)
    gradientClassifier = gradientClassifier.fit(X_train, Y_train)
    click.echo("Gradient tree boosting classifier built, score is %s out of 1.00" % gradientClassifier.score(X_test, Y_test))
    if modelOutput:
        with open(modelOutput, 'w') as dotfile:
            tree.export_graphviz(treeClassifier, out_file=dotfile, feature_names=features,
                                 class_names=classList, filled=True, rounded=True, special_characters=True)
    return treeClassifier


def classifyData(classifier, testdata, classMap):
    """
    Classifies data based on the previously trained model.

    Args:
        classifier: A classifier object that has been trained on the test corpus.
        testdata: A dataset to classify based on reads.
        classMap: A dictionary mapping class names to their class id used by scikit-learn.
    Returns:
        result: Test data as classified by the model.
    """
    testdata.sort()
    X = []
    # testdata = [[contigID, variable1, variable2, ...], ...]
    for item in testdata:
        X.append(item[1::]) # all but the first item
    Y = classifier.predict(X)
    # Step one: transpose the testdata matrix and extract all contigIDs
    contigIDs = list(zip(*testdata))[0]  # https://stackoverflow.com/questions/4937491/matrix-transpose-in-python
    # Step two: combine the contigIDs with the results from the classifier
    result = list(zip(contigIDs, Y))
    return result

def generateOutput(tokeep, toremove, result, contigs, target, output):
    """
    Generates output files for completed runs.

    Args:
        tokeep: File-like object to output target contigs to.
        toremove: File-like object to output non-target contigs to.
        result: Classified data from sidr.common.classifyData().
        contigs: List of sidr.common.Contig objects from input.
        target: Target classification.
        output: File-like object to save complete results to.
    """
    targetContigIDs = []
    nontargetContigIDs = []
    outputLines = []
    for contig in contigs:
        if contig.classification:
            if target == contig.classification:
                targetContigIDs.append(contig.contigid)
            else:
                nontargetContigIDs.append(contig.contigid)
            outputLines.append([contig.contigid, contig.classification, "input"])
    for contig in result:
        if target == contig[1]:
            targetContigIDs.append(contig[0])
        else:
            nontargetContigIDs.append(contig[0])
        outputLines.append([contig[0], contig[1], "dt"])
    with open(output, "w+") as f:
        f.write("contigid, classification, source\n")
        for ln in outputLines:
            f.write("%s, %s, %s\n" % (ln[0], ln[1], ln[2]))  # https://stackoverflow.com/questions/899103/writing-a-list-to-a-file-with-python for %s\n suggestion
    if tokeep:
        with open(tokeep, "w+") as f:
            for i in targetContigIDs:
                f.write("%s\n" % i )
    if toremove:
        with open(toremove, "w+") as f:
            for i in nontargetContigIDs:
                f.write("%s\n" % i)

