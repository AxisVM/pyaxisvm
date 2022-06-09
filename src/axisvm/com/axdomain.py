# -*- coding: utf-8 -*-
from axisvm.com.core.wrap import AxWrapper
from axisvm.com.core.utils import RMatrix3x3toNumPy, \
    RMatrix2x2toNumPy
import numpy as np


class AxDomain(AxWrapper):

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

    @property
    def model(self):
        return self.parent.model

    def ABDS(self, *args, compose=True, **kwargs):
        A, B, D, S, *_ = self._wrapped.GetCustomStiffnessMatrix()
        A, B, D = [RMatrix3x3toNumPy(x) for x in (A, B, D)]
        S = RMatrix2x2toNumPy(S)
        if compose:
            res = np.zeros((8, 8), dtype=float)
            res[0:3, 0:3] = A
            res[0:3, 3:6] = B
            res[3:6, 0:3] = B
            res[3:6, 3:6] = D
            res[6:8, 6:8] = S
            return res
        else:
            return A, B, D, S


class AxDomains(AxWrapper):

    __itemcls__ = AxDomain

    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model