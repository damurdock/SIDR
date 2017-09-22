# SIDR - Sequence Identification with Decision tRees

[![Build Status](https://travis-ci.org/damurdock/SIDR.svg?branch=master)](https://travis-ci.org/damurdock/SIDR)

SIDR (pronounced: cider) is a tool to filter Next Generation Sequencing (NGS) data based on a chosen target organism. SIDR uses data fron BLAST (or similar classifiers) to train a decision tree model to classify sequence data as either belonging to the target organism, or belonging to something else. This classification can be used to filter the data for later assembly.

### Note: SIDR is pre-release software. Features are currently incomplete and subject to major change.

## Installation

To install SIDR, clone this repository and run setup.py.
    
    pip install git+https://github.com/damurdock/SIDR.git

See the [documentation](https://sidr.readthedocs.io) for more details.

## Usage

SIDR has two main modes. Default mode takes several bioinformatics files as input, and computes a decision tree based on percentage GC content and per-base sequencing coverage. To run it, use:

    sidr default -d [taxdump path] -b [bamfile] -f [assembly FASTA] -r [BLAST results] -m model.dot -k tokeep.contigids -x toremove.contigids -t [target phylum] 

Runfile mode takes a tab-delimited file of contigs, variables, and classification as input. To run it, use: 

    sidr runfile -i [runfile] -m model.dot -k tokeep.contigids -x toremove.contigids -t [target phylum] 

See the [documentation](https://sidr.readthedocs.io) for more details.

## TODO

- More complete documentation

- More unit tests

- Redo docstrings post-restructure