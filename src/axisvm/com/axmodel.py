# -*- coding: utf-8 -*-
from dewloosh.core.typing.wrap import Wrapper
from axisvm.com.core.wrap import CollectionWrapper
from axisvm.com.axdomain import AxDomains
import numpy as np


__all__ = ['AxModels', 'AxModel', 'AxDomains', 'AxDomain']


class AxModel(Wrapper):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wdir = None
        
    def set_working_directory(self, path : str):
        self.wdir = path
        
    def coords(self, nIDs=None):
        if nIDs is None:
            nIDs = [i+1 for i in range(self._wrapped.Nodes.Count)]
        coords = self._wrapped.Nodes.BulkGetCoord(nIDs)[0]
        return np.array([[n.x, n.y, n.z] for n in coords])
            
    def plot(self):
        raise NotImplementedError
    
    @property
    def Domains(self):
        return AxDomains(model=self, wrap=self._wrapped.Domains)
    
    @property
    def Lines(self):
        return AxLines(model=self, wrap=self._wrapped.Lines)


class AxModels(CollectionWrapper):
    
    __itemcls__ = AxModel
    
    def __init__(self, *args, app=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        
class AxLine(Wrapper):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AxLines(CollectionWrapper):
    
    __itemcls__ = AxLine
    
    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model