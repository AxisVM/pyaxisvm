# -*- coding: utf-8 -*-
import numpy as np


def RMatrix2x2toNumPy(RMatrix):
    res = np.zeros((2, 2))
    res[0, 0] = RMatrix.e11
    res[0, 1] = RMatrix.e12
    res[1, 0] = RMatrix.e21
    res[1, 1] = RMatrix.e22
    return res


def RMatrix3x3toNumPy(RMatrix):
    res = np.zeros((3, 3))
    res[0, 0] = RMatrix.e11
    res[0, 1] = RMatrix.e12
    res[0, 2] = RMatrix.e13
    res[1, 0] = RMatrix.e21
    res[1, 1] = RMatrix.e22
    res[1, 2] = RMatrix.e23
    res[2, 0] = RMatrix.e31
    res[2, 1] = RMatrix.e32
    res[2, 2] = RMatrix.e33
    return res