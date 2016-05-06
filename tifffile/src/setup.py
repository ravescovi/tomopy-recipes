#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from setuptools import setup, Extension
import numpy


ext_modules = [
    Extension(
        '_tifffile',
        ['tifffile.c'],
        include_dirs=[numpy.get_include()]
        )
    ]

setup(
    author = 'Christoph Gohlke',
    description = 'Read and write image data from and to TIFF files.',
    py_modules = ['tifffile'],
    ext_modules = ext_modules,
    name = 'tifffile',
    requires = (
        'python',
        'numpy',
        ),
    version = '2014.08.24',
)
