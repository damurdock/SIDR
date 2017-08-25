Installing SIDR
===============

SIDR can be installed either using pip–the python package manager–or manually using the included setup.py file.

Dependencies
------------

SIDR is able to install all of its dependencies from PyPI automatically. This should work in most cases. If you are installing under Python 3, you may need to manually install Cython with::

    pip install cython

If you have a locally installed version of HTSLib, you can include it by using the commands::
    
    export HTSLIB_LIBRARY_DIR=/usr/local/lib
    export HTSLIB_INCLUDE_DIR=/usr/local/include

before installing SIDR.

Using a Virtualenv
------------------

Some cluster users may need to setup a Python virtualenv due to the nature of working with a cluster environment. A virtualenv can be setup with the commands::

    virtualenv venv
    . venv/bin/activate

If necessary, virtualenv can be installed in the user's home directory (~/.local/bin must be in $PATH) with the following command::

    pip install --user virtualenv

Installing from PyPI
--------------------

.. warning:: SIDR is not yet published on PyPI

Installing from PyPI is the easiest method, and thus the recommended one. To install SIDR::

    pip install SIDR

Installing from Source with pip
-------------------------------

.. note:: When installing from source, setuptools will attempt to contact PyPI to install dependencies. If this is not an option then dependencies will need to be manually installed.

If PyPI is not an option, SIDR can be installed by running the following command::

    pip install git+https://github.com/damurdock/SIDR.git

If you're installing SIDR in order to develop it, download the source from GitHub_ and install it by running the following command in the unzipped source directory::

    pip install --editable .

.. _GitHub: https://github.com/damurdock/SIDR.git

Installing from Source with Setup.py
------------------------------------

If for some reason pip is completely unavailable, SIDR can be installed by downloading the source from GitHub_ and running the following command command in the unzipped source directory::

    python setup.py install

.. _GitHub: https://github.com/damurdock/SIDR.git
