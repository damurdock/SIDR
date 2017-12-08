import pysam
import click
import gc
import gzip

from sidr import common
from Bio.SeqUtils import GC  # for GC content
from Bio.SeqIO.FastaIO import FastaIterator


def readFasta(fastaFile):
    """
    Reads a FASTA file and parses contigs for GC content.

    Args:
        fastaFile: The path to the FASTA file.
    Returns:
        contigs A dictionary mapping contigIDs to sidr.common.Contig objects with GC content as a variable.
    """
    contigs = []
    if ".gz" in fastaFile: # should support .fa.gz files in a seamless (if slow) way
        openFunc = gzip.open
    else:
        openFunc = open
    with openFunc(fastaFile) as data:
        click.echo("Reading %s" % fastaFile)
        with click.progressbar(FastaIterator(data)) as fi:
            for record in fi:  # TODO: conditional formatting
                contigs.append(common.Contig(record.id.split(' ')[0], variables={"GC": GC(record.seq)}))
    if len(contigs) != len(set([x.contigid for x in contigs])): # exit if duplicate contigs, https://stackoverflow.com/questions/5278122/checking-if-all-elements-in-a-list-are-unique
        raise ValueError("Input FASTA contains duplicate contigIDs, exiting")
    return dict((x.contigid, x) for x in contigs)  # https://stackoverflow.com/questions/3070242/reduce-python-list-of-objects-to-dict-object-id-object


def readBAM(BAMFile, contigs):
    """
    Parses an aligned BAM file for coverage.

    Args:
        BAMFile: The BAM file to parse.
        contigs: List of sidr.common.Contigs taken from input FASTA.
    Returns:
        contigs: Input contigs updated with coverage, measured as an
                 average over the whole contig.
    """
    alignment = pysam.AlignmentFile(BAMFile, "rb")
    click.echo("Reading BAM file")
    with click.progressbar(contigs) as ci:
        for contig in ci:
            covArray = [] # coverage over contig = sum(coverage per base)/number of bases
            for pile in alignment.pileup(region=str(contig)):
                covArray.append(pile.nsegments)
            try:
                contigs[contig].variables["Coverage"] = (sum(covArray) / len(covArray))
            except ZeroDivisionError: # should only occur if 0 coverage recorded
                contigs[contig].variables["Coverage"] = 0
    return contigs


def readBLAST(classification, taxdump, classificationLevel, contigs):
    """
    Reads a BLAST result file and combines it with other known information about the contigs.

    Args:
        classification: A string containing the filename of the BLAST results. The BLAST
            results must be in the format -outfmt '6 qseqid staxids', additional information
            can be added but the first two fields must be qseqid and staxids.
        taxdump: The NCBI taxdump as processed by parseTaxdump()
        classificationLevel: The level of classification to save into the corpus. Defaults to phylum.
        contigs: List of sidr.common.Contigs taken from input FASTA
    Returns:
        contigs: Input list of contigs updated with classification form BLAST
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
                taxid = record[1].strip()
                taxonomy = common.taxidToLineage(taxid, taxdump, classificationLevel)
                taxonomy = taxonomy.lower()
                try:
                    if contig not in contigs.keys(): # assume that the first hit in blast output is best
                        contigs[contig].classification = taxonomy
                        if taxonomy not in classList:
                            classList.append(taxonomy)
                except IndexError:  # if a contig is in BLAST but not FASTA (should be impossible but)
                    continue
    for idx, className in enumerate(classList):
        classMap[className] = idx
    return contigs, classMap, classList


def runAnalysis(bam, fasta, blastresults, taxdump, modelOutput, output, tokeep, toremove, target, binary, level):
    taxdump, taxidDict = common.parseTaxdump(taxdump, False)
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
    corpus, testdata, features = common.constructCorpus(list(contigs.values()), classMap, binary, target)
    gc.collect()
    click.echo("Corpus constucted, %d contigs in corpus and %d contigs in test data" % (len(corpus), len(testdata)))
    classifier = common.constructModel(corpus, classList, features, modelOutput)
    result = common.classifyData(classifier, testdata, classMap)
    common.generateOutput(tokeep, toremove, result, corpus, target, output)
