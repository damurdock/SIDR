import pysam
import click
import gc

from sidr import common
from Bio.SeqUtils import GC  # for GC content
from Bio.SeqIO.FastaIO import FastaIterator


def readFasta(fastaFile):
    """
    Reads a FASTA file and parses contigs for GC content.

    Args:
        fastaFile: A string containing the location of the FASTA file
    Returns:
        contigsWithGC: A dictionary mapping contig ids to GC content.
    """
    contigs = []
    with open(fastaFile) as data:
        click.echo("Reading %s" % fastaFile)
        with click.progressbar(FastaIterator(data)) as fi:
            for record in fi:  # TODO: conditional formatting
                contigs.append(common.Contig(record.id.split(' ')[0], variables={"GC": GC(record.seq)}))
    return dict((x.contigid, x) for x in contigs)  # https://stackoverflow.com/questions/3070242/reduce-python-list-of-objects-to-dict-object-id-object


def readBAM(alignment, contigs):
    """
    Parses an aligned BAM file for coverage.

    Args:
        alignment: The BAM file to parse.
        contigsWithGC: A dictionary mapping contig ids to GC content
    Returns:
        contigsWithCov: A list where each line contains a contig id
            and that contig's average coverage.
    """
    alignment = pysam.AlignmentFile(alignment, "rb")
    click.echo("Reading BAM file")
    with click.progressbar(contigs) as ci:
        for contig in ci:
            covArray = []
            for pile in alignment.pileup(region=str(contig)):
                covArray.append(pile.nsegments)
            try:
                contigs[contig].variables["Coverage"] = (sum(covArray) / len(covArray))
            except ZeroDivisionError:
                contigs[contig].variables["Coverage"] = 0
    return contigs


def readBLAST(classification, taxdump, classificationLevel, contigs):
    """
    Reads a BLAST result file and combines it with other known information about the contigs.

    Args:
        classification: A string containing the filename of the BLAST results. The BLAST
            results must be in the format -outfmt '6 qseqid staxids', additional information
            can be added but the first two fields must be qseqid and staxids.
        contigsWithCov: A list where each line contains a contig id, that contig's GC content,
            and that contig's average coverage.
        taxdump: The names/nodes dict as provided by parseTaxDump().
        deletedTaxa: A list of taxids that have been deleted from the taxdump.
        mergedTaxa: A dictionary mapping merged taxa to their new equivalents.
        classificationLevel: The level of classification to save into the corpus. Defaults to phylum.
    Returns:
        contigsWithClass: A dictionary mapping contig ids to the chosen classification.
        classMap: A dictionary mapping class names to their class id used by scikit-learn.
        classList: A list of class names.
    """
    classList = []
    classMap = {}
    with open(classification) as data:
        click.echo("Reading %s" % classification)
        with click.progressbar(data) as dt:
            for line in dt:
                record = line.split("\t")
                contig = record[0]
                taxid = record[1]
                taxonomy = common.taxidToLineage(taxid, taxdump, classificationLevel)
                if taxonomy.lower() != "nematoda":  # TODO fix this
                    taxonomy = "other"
                else:
                    taxonomy = "nematoda"
                try:
                    if taxonomy not in classList:  # I love python
                        classList.append(taxonomy)
                    contigs[contig].classification = taxonomy
                except IndexError:  # again, I love python
                    continue
    for idx, className in enumerate(classList):
        classMap[className] = idx
    return contigs, classMap, classList


def runAnalysis(bam, fasta, blastresults, taxdump, model, output, tokeep, toremove, target, level):
    taxdump = common.parseTaxdump(taxdump)
    gc.collect()
    click.echo("Taxdump parsed, %d taxIDs loaded" % len(taxdump))
    contigs = readFasta(fasta)
    gc.collect()
    click.echo("FASTA loaded, %d contigs returned" % len(contigs))
    contigs = readBAM(bam, contigs)
    gc.collect()
    click.echo("BAM loaded")
    contigs, classMap, classList = readBLAST(blastresults,
                                             taxdump, level.lower(), contigs)
    gc.collect()
    click.echo("BLAST results loaded")
    corpus, testdata, features = common.constructCorpus(list(contigs.values()), classMap)
    gc.collect()
    click.echo("Corpus constucted, %d contigs in corpus and %d contigs in test data" % (len(corpus), len(testdata)))
    classifier = common.constructModel(corpus, classList, features)
    result = common.classifyData(classifier, testdata, classMap)
    common.generateOutput(tokeep, toremove, result, corpus, target, output)
