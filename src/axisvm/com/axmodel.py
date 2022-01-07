# -*- coding: utf-8 -*-
from axisvm.com.core.wrap import AxWrapper
from axisvm.com.axdomain import AxDomains


__all__ = ['AxModels', 'AxModel', 'AxDomains', 'AxDomain']


class AxModel(AxWrapper):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                            
    @property
    def Domains(self):
        return AxDomains(model=self, wrap=self._wrapped.Domains)
    
    @property
    def Lines(self):
        return AxLines(model=self, wrap=self._wrapped.Lines)
    
    def __enter__(self):
        if self._wrapped is not None:
            self._wrapped.BeginUpdate()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self._wrapped is not None:
            self._wrapped.EndUpdate()
            
   
class AxModels(AxWrapper):
    
    __itemcls__ = AxModel
    
    def __init__(self, *args, app=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        
class AxLine(AxWrapper):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AxLines(AxWrapper):
    
    __itemcls__ = AxLine
    
    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model