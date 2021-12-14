# -*- coding: utf-8 -*-


__all__ = ['Wrapper', 'wrapper', 'customwrapper', 'wrap']


NoneType = type(None)


class Wrapper(object):
    """
    Wrapper base class that
        (a) wraps an existing object at object creation provided as a keyword
            argument with wrapkey
        (b) wraps an existing object at object creation if it is a positional
            argument and an instance of wraptype
        (b) wraps the object wraptype(*args, **kwargs)
    """
    wrapkey = 'wrap'
    wraptype = NoneType

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._wrapped = kwargs.get(self.wrapkey, None)

        if self._wrapped is None and self.wraptype is not NoneType:
            for arg in args:
                if isinstance(arg, self.wraptype):
                    self._wrapped = arg
                    break

            if self._wrapped is None:
                try:
                    if self.wraptype is not NoneType:
                        self._wrapped = self.wraptype(*args, **kwargs)
                except Exception:
                    raise ValueError("Wrapped class '{}' cannot be "
                                     "initiated with these "
                                     "arguments".format(
                                         self.wraptype.__name__))
        else:
            if self.wraptype is not NoneType:
                assert isinstance(self._wrapped, self.wraptype), \
                    "Wrong type, unable to wrap object : {}". \
                    format(self._wrapped)
                    
    def wrap(self, obj):
        if self.wraptype is not NoneType:
            if isinstance(obj, self.wraptype):
                self._wrapped = obj
        else:
            self._wrapped = obj

    def wraps(self):
        return self._wrapped is not None

    def __hasattr__(self,attr):
        return any([attr in self.__dict__, attr in self._wrapped.__dict__])

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        try:
            return getattr(self._wrapped, attr)
        except Exception:
            raise AttributeError("'{}' object has no attribute \
                called {}".format(self.__class__.__name__, attr))

    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except Exception:
            try:
                return self._wrapped.__getitem__(index)
            except Exception:
                raise TypeError("'{}' object is not "
                                "subscriptable".format(
                                    self.__class__.__name__))

    def __setitem__(self, index, value):
        try:
            return super().__setitem__(index,value)
        except Exception:
            try:
                return self._wrapped.__setitem__(index,value)
            except Exception:
                raise TypeError("'{}' object does not support "
                                "item assignment".format(
                                    self.__class__.__name__))


class AxWrapper(Wrapper):

    __itemcls__ = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self._wrapped, 'Item'):
            self.__itemcls__ = None
            
    @property
    def Item(self):
        if self.__itemcls__:
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
               
               
def customwrapper(*args, wrapkey='wrap', wraptype=NoneType, **kwargs):
    """
    Returns a class decorator turning a class type into a wrapper type, that
        (a) wraps an existing object at object creation provided as a keyword
            argument with wrapkey
        (b) wraps an existing object at object creation if it is a positional
            argument and an instance of wraptype
        (b) wraps the object wraptype(*args, **kwargs)
    """
    class BaseWrapperType(Wrapper): ...
    BaseWrapperType.wrapkey = wrapkey
    BaseWrapperType.wraptype = wraptype    
    def wrapper(BaseType):   
        class WrapperType(BaseWrapperType, BaseType):
            basetype = BaseType    
        return WrapperType
    return wrapper


def wrapper(BaseType : type):
    """
    Simple class decorator that turns a type into a wrapper with default
    behaviour.
    """
    class WrapperType(Wrapper, BaseType):
        basetype = BaseType     
    return WrapperType


def wrap(obj : object) -> Wrapper:
    """
    Wraps an object and returns the wrapper.
    """
    return Wrapper(wrap=obj)


if __name__ == '__main__' :
    
    class Wrapped:

        def foo(self):
            print('foo in object to be wrapped')

        def boo(self):
            print('boo in object to be wrapped')

    @customwrapper(wrapkey='wrapkey', wraptype=Wrapped)
    class CustomWrapper:

        def boo(self):
            print('boo in custom wrapper')
            
    @wrapper
    class DefaultWrapper:

        def boo(self):
            print('boo in default wrapper')
            
    
    class DefaultWrapper2(Wrapper):

        def boo(self):
            print('boo in default wrapper')

    cw = CustomWrapper(wrapkey=Wrapped())
    cw.foo()
    cw.boo()
    
    dw = DefaultWrapper(wrap=Wrapped())
    dw.foo()
    dw.boo()
    
    dw2 = DefaultWrapper(wrap=Wrapped())
    dw2.foo()
    dw2.boo()
    
    w = wrap(Wrapped())
    w.foo()
    w.boo()
