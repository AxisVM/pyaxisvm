# -*- coding: utf-8 -*-
from dewloosh.core.typing.wrap import Wrapper


__all__ = ['AxWrapper', 'CollectionWrapper']


NoneType = type(None)


class AxWrapper(Wrapper):

    __itemcls__ = None
    
    def __init__(self, *args, **kwargs):
        self._iterable = False
        super().__init__(*args, **kwargs)
            
    def wrap(self, obj=None):
        if obj is not None:
            if hasattr(obj, 'Item'):
                self._iterable = True
            else:
                self._iterable = False
                self.__itemcls__ = None
        super().wrap(obj)
            
    @property
    def Item(self):
        if self._iterable:
            return self
        else:
            raise AttributeError("Object {} has not attribute 'Item'.".format(self))
    
    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        try:
            return getattr(self._wrapped, attr)
        except Exception:
            raise AttributeError("'{}' object has no attribute \
                called {}".format(self.__class__.__name__, attr))
        
    def __getitem__(self, ind):
        if self.__itemcls__:
            if isinstance(ind, int):
                return self.__itemcls__(wrap=self._wrapped.Item[ind])
            elif isinstance(ind, slice):
                axobj = self._wrapped
                item = lambda i : self.__itemcls__(wrap=axobj.Item[i])
                start, stop, step = ind.start, ind.stop, ind.step
                start = 1 if start == None else start
                stop = axobj.Count + 1 if stop == None else stop
                step = 1 if step == None else step
                res = [item(i) for i in range(start, stop, step)]
                if len(res) == 1:
                    return res[0]
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


class CollectionWrapper(Wrapper):

    __itemcls__ = None
         
    @property
    def Item(self):
        return self
        
    def __getitem__(self, ind):
        if isinstance(ind, int):
            return self.__itemcls__(wrap=self._wrapped.Item[ind])
        elif isinstance(ind, slice):
            axobj = self._wrapped
            item = lambda i : self.__itemcls__(wrap=axobj.Item[i])
            start, stop, step = ind.start, ind.stop, ind.step
            start = 1 if start == None else start
            stop = axobj.Count + 1 if stop == None else stop
            step = 1 if step == None else step
            res = [item(i) for i in range(start, stop, step)]
            if len(res) == 1:
                return res[0]
            return res
        else:
            raise NotImplementedError
               
            
