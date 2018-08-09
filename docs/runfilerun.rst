.. _runfilerun:

Running With a Runfile
======================

SIDR can take a "runfile" with pre-computed variables as input. The runfile should be a comma delimited file starting with a header row. A column named "ID" which contains the contigID must exist, along with an "Origin" column with the name of the organism identified by BLAST for contigs where one was found. All other columns are used as variables for the decision tree, except any titled "Covered_bases", "Plus_reads", or "Minus_reads" as those are present in BBMap default output yet should not contribute to model construction.

To run SIDR in runfile mode, enter a command like: ::
   
    sidr runfile -d [taxdump path] \
    -i [runfile path] \
    -k tokeep.contigids \
    -x toremove.contigids \
    -t [target phylum]
