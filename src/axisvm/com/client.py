# -*- coding: utf-8 -*-
from comtypes.client import CreateObject, GetActiveObject
from time import sleep
from axisvm.com.axapp import AxApp


__all__ = ['start_AxisVM']


def start_AxisVM(*args, join=False, visible=None, 
                 daemon=False, wrap=True, **kwargs):
    """Returns an interface to a new, or an existing AxisVM application. 
    
    If the argument `join` is True, an attempt is made to connect to an \n
    already running instance. If there is a running instance but `join` \n
    is False, that instance gets destroyed and a new one will be created.
    
    If the first argument is a valid path to an AxisVM model file, it gets
    opened.

    Parameters
    ----------
    join : boolean, optional \n
        Controls what to do if there is an already running instance \n
        to connect to. Default is False.
        
        This is only available from X6r2. For versions prior to this, \n
        `join=True` has no effect and a new instance is created every time.

    visible : boolean or None, optional \n
        Sets the visibility of the AxisVM application, while a None\n
        value takes no effect. Default is None.

    daemon : boolean, optional \n
        Controls the behaviour of the COM interface. Default is False. \n

        Assuming that `axapp` is a COM interface to an AxisVM application,\n
        `daemon=True` is equivalent to

        >>> from axisvm.com.tlb import acEnableNoWarning, lbFalse, lbTrue
        >>> axapp.CloseOnLastReleased = lbTrue
        >>> axapp.AskCloseOnLastReleased = lbFalse
        >>> axapp.AskSaveOnLastReleased = lbFalse
        >>> axapp.ApplicationClose = acEnableNoWarning
        
    wrap : boolean, optional \n
        Wraps the returning object if True, returns the raw object otherwise. \n
        Default is True.

    Returns
    -------
    axisvm.axapp.AxApp
        A python wrapper around an IAxisVMApplication instance.
        
    Examples
    --------
    >>> from axisvm.com.client import start_AxisVM
    >>> axvm = start_AxisVM(visible=True, daemon=True)
    """
    axapp = _find_AxisVM()
    if axapp is not None and not join:
        try:
            axapp.Quit()
            del axapp
        except Exception:
            pass
        finally:
            axapp = None
    if axapp is None:
        axapp = CreateObject("AxisVM.AxisVMApplication")
    if axapp is not None:
        _init_AxisVM(axapp, daemon=daemon, visible=visible, **kwargs)
    
    if wrap:
        res = AxApp(wrap=axapp) 
        if len(args) > 0 and isinstance(args[0], str):
            res.model = args[0]
        return res
    else:
        if len(args) > 0 and isinstance(args[0], str):
            _from_file(axapp, args[0])
        return axapp


def _init_AxisVM(axapp, *args, visible=None, daemon=False, **kwargs):
    while not axapp.Loaded:
        sleep(0.1)
    if isinstance(visible, bool):
        axapp.Visible = 1 if visible else 0
    _init_daemon(axapp) if daemon else None


def _init_daemon(axapp, *args, **kwargs):
    from axisvm.com.tlb import lbTrue as true, lbFalse as false, \
        acEnableNoWarning
    axapp.CloseOnLastReleased = true
    axapp.AskCloseOnLastReleased = false
    axapp.AskSaveOnLastReleased = false
    axapp.ApplicationClose = acEnableNoWarning
    

def _from_file(axapp, path):
    try:
        model = axapp.Models.New()
        model.LoadFromFile(path)
    except Exception as e:
        raise e


def _find_AxisVM():
    try:
        return GetActiveObject('AxisVM.AxisVMApplication')
    except Exception:
        return None
    
    
if __name__ == '__main__':
    from axisvm.com.client import start_AxisVM
    axapp = start_AxisVM(visible=True, daemon=True)