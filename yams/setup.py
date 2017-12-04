#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 16:26:08 2017

@author: ania
"""

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy # to get includes
import scipy

# extensions = [Extension("*", ["yamsx/*.pyx"])]

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("GenRBall", ["GenRBall.pyx"], )],
    include_dirs = [numpy.get_include(),scipy.get_include(),],
)