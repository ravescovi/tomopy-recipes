#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from setuptools import setup, Extension

setup(
    author = 'Stuart B. Wilkins',
    description = 'Read SPE files.',
    py_modules = ['spefile'],
    name = 'spefile',
    requires = (
        'python',
        ),
    version = '1.6',
)
