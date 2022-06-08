# -*- coding: utf-8 -*-
from axisvm.com.core.wrap import AxWrapper
from axisvm.com.axmodel import AxModel, AxModels
import os


class AxApp(AxWrapper):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self._model = AxModel(wrap=self._wrapped.Models.Item[1])
        except Exception:
            self.new_model()
            
    @property
    def app(self):
        return self._wrapped
    
    @property
    def Models(self):
        return AxModels(app=self, wrap=self._wrapped.Models)
    
    @property    
    def model(self):
        return self._model
    
    @model.setter    
    def model(self, value):
        if isinstance(value, int):
            self._model = AxModel(wrap=self._wrapped.Models.Item[value])
        elif isinstance(value, str):
            if os.path.exists(value):
                if self._model is None:
                    self.new_model()
                self._model.LoadFromFile(value)
            else:
                raise FileNotFoundError("File {} not found!".format(value))
        else:
            raise RuntimeError("Invalid input : {}!".format(value))
        
    def new_model(self):
        self.model = self._wrapped.Models.New()
        return self._model
    
    def Quit(self, *args, unload_client=True, **kwargs):
        if unload_client:
            self._wrapped.UnLoadCOMClients()
        self._wrapped.Quit()
        self._wrapped = None