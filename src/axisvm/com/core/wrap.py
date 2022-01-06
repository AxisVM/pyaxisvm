# -*- coding: utf-8 -*-
from dewloosh.core.typing.wrap import Wrapper
from typing import Callable, Iterable, Any


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
        
    def __repr__(self) -> str:
        return self._wrapped.__repr__()
        
    def __len__(self):
        if hasattr(self._wrapped, 'Count'):
            return self._wrapped.Count
        else:
            raise AttributeError("Object {} has no concept of length.".format(self._wrapped)) 
    
    def __iter__(self):
        for i in range(1, self.Count + 1):
            yield self[i]
    
    def __getattr__(self, attr):
        res = super().__getattr__(attr)
        if hasattr(res, 'Item'):
            return AxWrapper(wrap=res)
        return res
    
    def __setattr__(self, __name: str, __value: Any) -> None:
        if '_wrapped' in self.__dict__:
            if self._wrapped is not None and hasattr(self._wrapped, __name):
                return setattr(self._wrapped, __name, __value)
        return super().__setattr__(__name, __value)

    def __getitem__(self, ind):
        if self.__has_items:
            cls = AxWrapper if self.__itemcls__ is None else self.__itemcls__
            if isinstance(ind, int):
                if ind < 0:
                    ind = self._wrapped.Count + 1 + ind
                return cls(wrap=self._wrapped.Item[ind])
            elif isinstance(ind, slice):
                axobj = self._wrapped
                item = lambda i : cls(wrap=axobj.Item[i], parent=self)
                start, stop, step = ind.start, ind.stop, ind.step
                start = 1 if start == None else start
                stop = axobj.Count + 1 if stop == None else stop
                step = 1 if step == None else step
                inds = list(range(start, stop, step))
                if min(inds) < 0:
                    N = self._wrapped.Count + 1
                    foo = lambda i : i if i > 0 else N + i
                    inds = map(foo, inds)
                res = list(map(item, inds))
                if len(res) == 1:
                    return res[0]
                return AxItemCollection(res)
            elif isinstance(ind, Iterable):
                axobj = self._wrapped
                item = lambda i : cls(wrap=axobj.Item[i], parent=self)
                res = [item(i) for i in ind]
                if len(res) == 1:
                    return res[0]
                return AxItemCollection(res)
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



               
            
