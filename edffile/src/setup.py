#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from setuptools import setup, Extension

setup(
    author = 'Alexandre Gobbo',
    description = 'Read EDF files.',
    py_modules = ['EdfFile'],
    name = 'edffile',
    requires = (
        'python',
        'numpy'
        ),
    version = '1.6',
)
