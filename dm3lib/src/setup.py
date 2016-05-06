#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from setuptools import setup, Extension

setup(
    author = 'Pierre-Ivan Raynal',
    description = 'Python module for parsing GATAN DM3 (DigitalMicrograph) files.',
    py_modules = ['DM3lib'],
    name = 'DM3lib',
    requires = (
        'python',
        'numpy',
        'pillow',
        'scipy'
        ),
    version = '1.1',
)
