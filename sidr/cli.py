#!/usr/bin/python
import click
import os

from sidr import default
from sidr import runfile

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def validate_taxdump(value, method):
    if (os.path.isfile("%s/%s" % (value, "names.dmp")) and
        os.path.isfile("%s/%s" % (value, "nodes.dmp")) and
        os.path.isfile("%s/%s" % (value, "merged.dmp")) and
        os.path.isfile("%s/%s" % (value, "delnodes.dmp"))):
        return value
    else:
        with click.Context(method) as ctx:
            click.echo(ctx.get_help())
            raise click.BadParameter("Could not find names.dmp in taxdump, specify a value or make sure the files are present")


@click.group()
def cli():
    """
    Analyzes genomic data and attempts to classify contigs using a machine learning framework.

    SIDR uses data fron BLAST (or similar classifiers)to train a Decision Tree model to classify sequence data as either belonging to a target organism, or belonging to something else. This classification can be used to filter the data for later assembly.

    To use SIDR, you will need to construct a preliminary assembly, align your reads back to that assembly, then use BLAST to classify the assembly contigs.
    """
    pass


@cli.command(name="default", context_settings=CONTEXT_SETTINGS)
@click.option('--bam', '-b', type=click.Path(exists=True), help="Alignment of reads to preliminary assembly, in BAM format.")
@click.option('--fasta', '-f', type=click.Path(exists=True), help="Preliminary assembly, in FASTA format.")
@click.option('--blastresults', '-r', type=click.Path(exists=True), help="Classification of preliminary assembly from BLAST (or similar tools).")
@click.option('--taxdump', '-d', type=click.Path(), default=os.environ.get('BLASTDB'), help="Location of the NCBI Taxonomy dump. Default is $BLASTDB.")
@click.option('--model', '-m', type=click.Path(), default="", help="Location to save a graphical representation of the trained decision tree (optional). Output is in the form of a DOT file.")
@click.option('--output', '-o', type=click.Path(), default="%s/classifications.txt" % os.getcwd())
@click.option('--tokeep', '-k', type=click.Path(), default="", help="Location to save the contigs identified as the target organism(optional).")
@click.option('--toremove', '-x', type=click.Path(), default="", help="Location to save the contigs identified as not belonging to the target organism (optional).")
@click.option('--binary', is_flag=True, help="Use binary target/nontarget classification.")
@click.option('--target', '-t', help="The identity of the target organism at the chosen classification level. It is recommended to use the organism's phylum.")
@click.option('--level', '-l', default="phylum", help="The classification level to use when constructing the model. Default is 'phylum'.")
# @click.option('--verbose', '-v', count=True, help="Output more debugging options, repeat to increase verbosity (unimplemented).")
def default_runner(bam, fasta, blastresults, taxdump, modelOutput, output, tokeep, toremove, binary, target, level):
    """
    Runs the default analysis using raw preassembly data.
    """
    validate_taxdump(taxdump, runfile_runner)
    default.runAnalysis(bam, fasta, blastresults, taxdump, modelOutput, output, tokeep, toremove, binary, target, level)


@cli.command(name="runfile", context_settings=CONTEXT_SETTINGS)
@click.option('--infile', '-i', type=click.Path(exists=True), help="Tab-delimited input file.")
@click.option('--taxdump', '-d', type=click.Path(), default=os.environ.get('BLASTDB'), help="Location of the NCBI Taxonomy dump. Default is $BLASTDB.")
@click.option('--output', '-o', type=click.Path(), default="%s/classifications.txt" % os.getcwd())
@click.option('--model', '-m', type=click.Path(), default="", help="Location to save a graphical representation of the trained decision tree (optional). Output is in the form of a DOT file.")
@click.option('--tokeep', '-k', type=click.Path(), default="", help="Location to save the contigs identified as the target organism(optional).")
@click.option('--toremove', '-x', type=click.Path(), default="", help="Location to save the contigs identified as not belonging to the target organism (optional).")
@click.option('--target', '-t', help="The identity of the target organism at the chosen classification level. It is recommended to use the organism's phylum.")
@click.option('--binary', is_flag=True, help="Use binary target/nontarget classification.")
@click.option('--level', '-l', default="phylum", help="The classification level to use when constructing the model. Default is 'phylum'.")
def runfile_runner(infile, taxdump, output, modelOutput, tokeep, toremove, binary, target, level):
    """
    Runs a custom analysis using pre-computed data from BBMap or other sources.

    Input data will be read for all variables which will be used to construct a Decision Tree model.
    """
    validate_taxdump(taxdump, runfile_runner)
    runfile.runAnalysis(taxdump, infile, level, modelOutput, output, tokeep, toremove, binary, target)

""" WIP
@cli.command(name="filter", context_settings=CONTEXT_SETTINGS)
@click.option('--tokeep', '-k', type=click.Path(), default="", help="File containing list of contigs from the alignment to keep.")
@click.option('--bam', '-b', type=click.Path(exists=True), help="Alignment of reads to preliminary assembly, in BAM format.")
@click.option('-i1', type=click.Path(exists=True), help="Right read fastq to extract reads from.")
@click.option('-i2', type=click.Path(exists=True), help="Left read fastq to extract reads from.")
@click.option('-o1', type=click.Path(), help="Right read fastq to extract reads to.")
@click.option('-o2', type=click.Path(), help="Left read fastq to extract reads to.")
def filter_runner(tokeep, bam, i1, i2, o1, o2):
"""
#Filters reads aligning to the given contigs.
"""
    filterReads.runFilter(tokeep, bam, i1, i2, o1, o2)

if __name__ == "__main__":  # TODO Setuptools
    cli(prog_name="sidr")
""" 
