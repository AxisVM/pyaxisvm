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

    
    def GenerateMesh(self, *args, **kwargs):
        """
        Generates a mesh for the domain. If successful, returns the 
        domain index, otherwise returns an error code (errDatabaseNotReady 
        or other negative numbers [in this case see ErrorCodes, ErrorPoints, 
        ErrorLines for more information]).
        
        Notes
        -----
        Currently the `comtypes` package throws an error for SafeArrays of zero
        length (which is the case here if there is no error during meshing). 
        This problem is reported, the bug is fixed and a pull request is made towards
        the maintainers of `comtypes`. Until the next release of `comtypes`,
        the call to the tlb is wrapped in a try-except block.
            
            UPDATE : The pull request and the included bugfix is accepted and
                     will be included in comtypes v1.10.11. (2022.01.28)
        """
        return self._wrapped.GenerateMesh(*args, **kwargs)
        #try:
        #    return self._wrapped.GenerateMesh(*args, **kwargs)
        #except IndexError:
        #    pass


class AxDomains(AxWrapper):

    __itemcls__ = AxDomain

    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
