.. _dataprep:

Data Preparation
================

In order to run SIDR, you will need to perform several analyses of your data. For the default analysis, you will need:

- A preliminary assembly

- An alignment back to that preliminary assembly

- A BLAST classification of that assembly

- A copy of the NCBI Taxonomy Dump

Alternatively, you can precalculate the data you wish to use to train the model, and save it in a specific format for input. This is explained here: :ref:`runfilerun`.

Assembly
--------

SIDR requires a preliminary assembly of your data built with standard *de novo* assembly techniques. The scaffolds from this assembly will be used as input for the machine learning model. During testing, the ABySS_ assembler was used to generate preliminary assemblies, however at this time no testing has been done as to the effect the preliminary assembler has on downstream assembly.

Regardless of the tools used, the final scaffold FASTA file will be used for input into SIDR.

.. _ABySS: http://www.bcgsc.ca/platform/bioinfo/software/abyss

Alignment
---------

The second piece of data required is an alignment of your raw reads to the preliminary assembly. The alignment can be constructed using any standard alignment tools, during testing GSNAP_ was used. Regardless of the tools used, the alignment must be in a sorted and indexed BAM file. These can be created from a SAM alignment using the following samtools_ commands::

    samtools view -Sb /path/to/alignment.sam -o /path/to/alignment.bam
    samtools sort /path/to/alignment.bam /path/to/alignment_sorted
    samtools index /path/to/alignment_sorted.bam

.. _samtools: http://www.htslib.org/
.. _GSNAP: http://research-pub.gene.com/gmap/

BLAST
-----

The last piece of data that must be precalculated is a BLAST_ classification of the preliminary assembly. This may be constructed with a tool besides command-line BLAST, so long as it is properly formatted. To make a properly-formatted BLAST result file, you can use the command::

    blastn \
	-task megablast \
	-query /path/to/FASTA \
	-db nt \
	-outfmt '6 qseqid staxids bitscore std sscinames sskingdoms stitle' \
	-culling_limit 5 \
	-num_threads 8 \
	-evalue 1e-25 \
	-out /path/to/output

Currently SIDR assumes that BLAST input will have the sequence ID in the first column, and the NCBI Taxonomy ID in the second column. Any alternative classification tool may be used so long as it can produce this output.

.. _BLAST: https://blast.ncbi.nlm.nih.gov/Blast.cgi

Taxonomy Dump
-------------

SIDR uses the NCBI Taxonomy to translate the BLAST results into the desired classification. The Taxonomy dump can be downloaded from::

    ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz

After downloading, extract it and note it's location. By default, SIDR checks the directory listed in $BLASTDB, however this can be changed at runtime.
