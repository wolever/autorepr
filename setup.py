#!/usr/bin/env python

import os
import sys

from setuptools import setup

os.chdir(os.path.dirname(sys.argv[0]) or ".")

try:
    long_description = open("README.rst", "U").read()
except IOError:
    long_description = "See https://github.com/wolever/autorepr"

setup(
    name="autorepr",
    version="0.2.0",
    url="https://github.com/wolever/autorepr",
    author="David Wolever",
    author_email="david@wolever.net",
    description="Makes civilized __repr__, __str__, and __unicode__ methods",
    long_description=long_description,
    py_modules=["autorepr"],
    install_requires=[],
    license="BSD",
    classifiers=[ x.strip() for x in """
        Development Status :: 3 - Alpha
        Environment :: Console
        Intended Audience :: Developers
        License :: OSI Approved :: BSD License
        Natural Language :: English
        Operating System :: OS Independent
        Programming Language :: Python
        Topic :: Software Development
        Topic :: Utilities
    """.split("\n") if x.strip() ],
)
