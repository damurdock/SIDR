# SIDR - Sequence Identification with Decision tRees

SIDR (pronounced: cider) is a tool to filter Next Generation Sequencing (NGS) data based on a chosen target organism. SIDR uses data fron BLAST (or similar classifiers) to train a decision tree model to classify sequence data as either belonging to the target organism, or belonging to something else. This classification can be used to filter the data for later assembly.

### Note: SIDR is pre-release software. Features are currently incomplete and subject to major change.

## Installation

To install SIDR, clone this repository and run setup.py.

    git clone 
    cd SIDR
    python setup.py install
    # or for development
    pip install --editable .

See the [documentation](https://sidr.readthedocs.io) for more details.

## Usage

Currently, only the default mode of SIDR–which computes variables from raw data–is implemented. It can be run like so:

    sidr default -d [taxdump path] -b [bamfile] -f [assembly FASTA] -r [BLAST results] -m model.dot -k tokeep.contigids -x toremove.contigids -t [target phylum] 

See the [documentation](https://sidr.readthedocs.io) for more details.

## TODO

- Fix and finish runfile mode

- More complete documentation

- More unit tests

- Redo docstrings post-restructure