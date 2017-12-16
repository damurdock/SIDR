Welcome to SIDR's documentation!
================================

SIDR (Sequence Identification with Decision tRees, pronounced *cider*) is a tool to filter Next Generation Sequencing (NGS) data based on a chosen target organism. SIDR uses data fron BLAST (or similar classifiers) to train a Decision Tree model to classify sequence data as either belonging to the target organism, or belonging to something else. This classification can be used to filter the data for later assembly.

There are two ways to run SIDR. The first, or default, method takes a number of bioinformatics files as input and calculates relevant statistics from them. The second, or custom, method takes a specifically formatted tab-delimited file with your chosen statistics and uses that directly to train the model.


Documentation
-------------

.. toctree::
   :maxdepth: 2

   install
   dataprep
   rundefault
   runfilerun
   runfileexample
