import click
import pandas
import csv

from sidr import common


def readRunfile(runfile, taxidDict, taxDump, classificationLevel):
    unnecessaryColumns = ["Covered_bases", "Plus_reads", "Minus_reads"] # TODO: different formatting?
    contigs = []
    classList = []
    classMap = {}
    with open(runfile) as rf:
        runfile = pandas.read_csv(rf, index_col=False)
    for column in unnecessaryColumns:
        runfile.drop(column, axis=1, inplace=True)  # https://stackoverflow.com/questions/13411544/delete-column-from-pandas-dataframe for inplace
    runfile = runfile.fillna(value=False) # replace all non-existent values with False for later processing
    for row in runfile.iterrows():
        row = row[1] # iterrows returns a tuple of (index, Series)
        contigid = row["ID"]
        row.drop("ID", inplace=True)
        if not "0" == row["Origin"]:
            taxid = taxidDict[row["Origin"]] # text to taxid, should give options here
            classification = common.taxidToLineage(taxid, taxDump, classificationLevel)
            if classification not in classList:
                classList.append(classification)
        else:
            classification = False
        row.drop("Origin", inplace=True)
        variables = row.to_dict()
        contigs.append(common.Contig(contigid, variables, classification))
        for idx, className in enumerate(classList):
            classMap[className] = idx
    if len(contigs) != len(set([x.contigid for x in contigs])): # exit if duplicate contigs, https://stackoverflow.com/questions/5278122/checking-if-all-elements-in-a-list-are-unique
        raise ValueError("Input runfile contains duplicate contigIDs, exiting")
    return contigs, classMap, classList


def runAnalysis(blastdb, runfile, classificationLevel, modelOutput, output, tokeep, toremove, binary, target):
    taxDump, taxidDict = common.parseTaxdump(blastdb, True)
    contigs, classMap, classList = readRunfile(runfile, taxidDict, taxDump, classificationLevel)
    corpus, testdata, features = common.constructCorpus(contigs, classMap, binary, target)
    click.echo("Corpus constucted, %d contigs in corpus and %d contigs in test data" % (len(corpus), len(testdata)))
    classifier = common.constructModel(corpus, classList, features, modelOutput)
    result = common.classifyData(classifier, testdata, classMap)
    common.generateOutput(tokeep, toremove, result, contigs, target, output)
