Running With Raw Input
======================

By default, SIDR will analyse your data and construct a Decision Tree model based on the GC content and average coverage of your contigs. Before running SIDR, you will need to prepare some data based on your input. This is described here: :ref:`dataprep`

To run SIDR with the default settings on raw data, enter a command like::
    
    sidr default -d [taxdump path] \
    -b [bamfile] \
    -f [assembly FASTA] \
    -r [BLAST results] \
    -m model.dot \
    -k tokeep.contigids \
    -x toremove.contigids \
    -t [target phylum]