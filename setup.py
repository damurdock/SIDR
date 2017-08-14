import os
from setuptools import setup

_LONG_DESCRIPTION = """

"""

setup(
    name="SIDR",
    version="0.0.1",
    author="Duncan Murdock",
    author_email="me@duncanmurdock.name",
    description=("Sequence Idenification using Decision tRees; a tool to classify DNA reads using machine learning models."),
    license="MIT",
    keywords="console tool bioinformatics",
    url="https://github.com/damurdock/SIDR",
    packages=['sidr', 'tests'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Environment :: Console',
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Environment :: Console",
    ],
    install_requires=["NumPy", "SciPy", "pysam", "BioPython", "scikit-learn", "click", "pandas"],
    long_description=_LONG_DESCRIPTION,
    entry_points={
        'console_scripts': [
            'sidr = sidr.cli:cli',
        ],
    })
