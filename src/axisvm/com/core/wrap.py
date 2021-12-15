# -*- coding: utf-8 -*-
from dewloosh.core.typing.wrap import Wrapper
from typing import Callable


__all__ = ['AxWrapper']


NoneType = type(None)


class AxItemCollection(list):
    
    def __getattribute__(self, attr):
        if hasattr(self[0], attr):
            _attr = getattr(self[0], attr)
            if isinstance(_attr, Callable):
                getter = lambda i : getattr(i, attr)
                funcs = map(getter, self)
                def inner(*args, **kwargs):
                    return list(map(lambda f : f(*args, **kwargs), funcs)) 
                return inner
            else:
                return list(map(lambda i : getattr(i, attr), self)) 
        else:
            return super().__getattribute__(attr)  


class AxWrapper(Wrapper):

    __itemcls__ = None
    
    def __init__(self, *args, **kwargs):
        self.__has_items = False
        super().__init__(*args, **kwargs)
            
    def wrap(self, obj=None):
        if obj is not None:
            if hasattr(obj, 'Item'):
                self.__has_items = True
            else:
                self.__has_items = False
                self.__itemcls__ = None
        super().wrap(obj)
            
    @property
    def Item(self):
        if self.__has_items:
            return self
        else:
            raise AttributeError("Object {} has no attribute 'Item'.".format(self))
            
    def __getitem__(self, ind):
        if self.__has_items:
            cls = AxWrapper if self.__itemcls__ is None else self.__itemcls__
            if isinstance(ind, int):
                return cls(wrap=self._wrapped.Item[ind])
            elif isinstance(ind, slice):
                axobj = self._wrapped
                item = lambda i : cls(wrap=axobj.Item[i])
                start, stop, step = ind.start, ind.stop, ind.step
                start = 1 if start == None else start
                stop = axobj.Count + 1 if stop == None else stop
                step = 1 if step == None else step
                res = [item(i) for i in range(start, stop, step)]
                if len(res) == 1:
                    return res[0]
                if self.__itemcls__ is not None:
                    return AxItemCollection(res)
                else:
                    return res
            else:
                raise NotImplementedError
        else:            
            try:
                return super().__getitem__(ind)
            except Exception:
                try:
                    return self._wrapped.__getitem__(ind)
                except Exception:
                    raise TypeError("'{}' object is not "
                                    "subscriptable".format(
                                        self.__class__.__name__))



               
            
