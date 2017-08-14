import click
import pandas
import common
import csv


def readRunfile(runfile, taxidDict, taxDump, classificationLevel):
    unnecessaryColumns = ["Length", "Covered_percent", "Covered_bases", "Plus_reads", "Minus_reads", "Read_GC"]
    contigs = []
    classList = []
    classMap = {}
    with open(runfile) as rf:
        runfile = pandas.read_csv(rf, index_col=False)
        print(runfile)
    for column in unnecessaryColumns:
        runfile.drop(column, axis=1, inplace=True)  # https://stackoverflow.com/questions/13411544/delete-column-from-pandas-dataframe for inplace
    runfile = runfile.fillna(value=False)
    for row in runfile.iterrows():
        row = row[1]
        contigid = row["ID"]
        row.drop("ID", inplace=True)
        if not "0" == row["Origin"]:
            taxid = taxidDict[row["Origin"]]
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
    return contigs, classMap, classList


def parseTaxids(blastdb):
    taxidDict = {}
    with open(blastdb + "/names.dmp") as names:
        click.echo("Reading names.dmp")
        namesReader = list(csv.reader(names, delimiter="|"))
        with click.progressbar(namesReader) as nr:
            for line in nr:
                taxidDict[line[1].strip()] = line[0].strip()
    return taxidDict



def runAnalysis(blastdb, runfile, classificationLevel):
    taxDump = common.parseTaxdump(blastdb)
    taxidDict = parseTaxids(blastdb)
    contigs, classMap, classList = readRunfile(runfile, taxidDict, taxDump, classificationLevel)
    corpus, testdata, features = common.constructCorpus(contigs, classMap)
    click.echo("Corpus constucted, %d contigs in corpus and %d contigs in test data" % (len(corpus), len(testdata)))
    classifier = common.constructModel(corpus, classList, features)
    result = common.classifyData(classifier, testdata, classMap)
    print(result)
