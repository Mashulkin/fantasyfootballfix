# -*- coding: utf-8 -*-
"""
Inserting an additional path into the environment
"""
import sys
import inspect
import os.path
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(1, parentdir)


__author__ = 'Vadim Arsenev'
__version__ = '1.0.0'
__data__ = '30.07.2021'
