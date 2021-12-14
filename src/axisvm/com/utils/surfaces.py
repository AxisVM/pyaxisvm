# -*- coding: utf-8 -*-
from collections import OrderedDict
import numpy as np
from numba import njit


@njit(nogil=True, cache=True)
def count_surfaces(lengths : np.ndarray, dIDs : np.ndarray):
    nS = len(lengths)
    inds = np.zeros(nS, dtype=lengths.dtype)
    keyT3 = 'T3'
    keyQ4 = 'Q4'
    count = {dID : {keyT3 : 0, keyQ4 : 0} for dID in dIDs}
    for i in range(nS):
        li = lengths[i]
        if li == 3:
            inds[i] = count[dIDs[i]][keyT3]
            count[dIDs[i]][keyT3] += 1
        elif li == 4:
            inds[i] = count[dIDs[i]][keyQ4]
            count[dIDs[i]][keyQ4] += 1
    return count, inds


@njit(nogil=True, cache=True)
def group_surfaces(lengths : np.ndarray, dIDs : np.ndarray):
    keyT3 = 'T3'
    keyQ4 = 'Q4'
    count, inds = count_surfaces(lengths, dIDs)
    res = {}
    for dID in count:
        res[dID] = {
            keyT3 : np.zeros((count[dID][keyT3], 3), 
                             dtype=dIDs.dtype), 
            keyQ4 : np.zeros((count[dID][keyQ4], 4), 
                             dtype=dIDs.dtype)
                }
    return res, inds


def get_surfaces(axmodel, *args, interactive = False, **kwargs):
    """
    Returns a list of surfaces, which can be specified by keyword
    arguments. It can be used to turn an arbitrary specification
    of surfaces in an embedded situation into a list of surfaces.
    For that reason it includes trivial keys. Individual elements
    can be specified, but the result is always a list. If there are
    no valid specifiers, then
        (1) if argument 'all' is provided, all of the surfaces of the
            model are returned
        (2) if interactive == True, function either gets the selected
            surfaces from AxisVM, or if there is none, a selection \
            dialog shows up in AxisVM and the function is called again \
            with valid specifiers emerging from any of these scenarios.
    ---
    Possible keys and values
        surface : a single domain, returns [surface]
        surfaces : a list of surfaces, returns surfaces
        ID : int, a single surfaceID
        IDs : [int], a sequence of surfaceIDs
        UID : int, a single surfaceUID
        UIDs : [int], a sequence of surfaceUIDs
    ---
    For example
        surfaces = get_surfaces(axmodel,**kwargs)
        all_surfaces = get_surfaces(axmodel,'all')
    or simply
        surfaces = get_surfaces(axmodel)
    to get surfaces from a selection in AxisVM.
    """
    surfaces = None
    try:
        if 'surface' in kwargs:
            surfaces = [kwargs.pop('surface')]
        elif 'surfaces' in kwargs:
            surfaces = kwargs.pop('surfaces')
        elif 'surfaceID' in kwargs:
            surfaces = [axmodel.Surfaces.Item[kwargs.pop('surfaceID')]]
        elif 'surfaceIDs' in kwargs:
            surfaces = [axmodel.Surfaces.Item[ID]
                        for ID in kwargs.pop('surfaceIDs')]
        elif 'surfaceUID' in kwargs:
            ID = axmodel.Surfaces.IndexOfUID(kwargs.pop('surfaceUID'))
            surfaces = [axmodel.Surfaces.Item[ID]]
        elif 'surfaceUIDs' in kwargs:
            IDs = [axmodel.Surfaces.IndexOfUID(UID)
                   for UID in kwargs.pop('surfaceUIDs')]
            surfaces = [axmodel.Surfaces.Item[ID] for ID in IDs]
    except Exception:
        raise "Ivalid specification of surfaces!"
    finally:
        if surfaces is None:
            surfaces = get_selected_surfaces(axmodel, interactive=interactive)
            if surfaces is None and 'allsurfaces' in args:
                nSurf = axmodel.Surfaces.Count
                SurfaceIDs = [i for i in range(1, nSurf+1)]
                surfaces = get_surfaces(axmodel, surfaceIDs = SurfaceIDs,
                                        interactive = False)
        return surfaces


def select_surfaces(axmodel, message : str = None):
    """
    Shows up a selectiondialog for surfaces in AxisVM and returns the selected
    surfaces if succesful.
    """
    if message is None:
        message = 'Select one or more surfaces!'
    axmodel.StartModalSelection(message, axmodel.tlb.lbTrue, 'seltAllSurfaces')
    return get_selected_surfaces(axmodel, interactive = False)


def get_selected_surfaces(axmodel, interactive = False):
    """
    Returns a list of surfaces. The result is always iterable,
    even if it contains only one item.
    """
    try:
        sIDs = axmodel.Surfaces.GetSelectedItemIds()[0]
        return get_surfaces(axmodel, surfaceIDs = sIDs)
    except Exception:
        if interactive:
            return select_surfaces(axmodel,
                                   message = 'Select one or more surfaces!')
        else:
            return None


def get_selected_surfaceIDs(axmodel, interactive = False):
    """
    Returns a list of surfaceIDs. The result is always iterable,
    even if it contains only one item.
    """
    try:
        return axmodel.Surfaces.GetSelectedItemIds()[0]
    except Exception:
        if interactive:
            surfaces = get_selected_surfaces(axmodel, interactive = True)
            if surfaces is not None:
                sUIDs = [s.UID for s in surfaces]
                sIDs = [axmodel.Surfaces.IndexOfUID[sUID] for sUID in sUIDs]
                return sIDs
        else:
            return None


def get_nodes_of_surfaces(axmodel = None, *args,**kwargs):
    """
    Returns a dictionary containing lists of nodeIDs to
    every surfaceID specified. If SurfaceIds == None, nodes
    are listed for all surfaces in the model.
    """
    interactive = 'all' not in args
    surfaces = get_surfaces(axmodel,*args,interactive = interactive,**kwargs)
    if surfaces is None and not interactive:
        nSurf = axmodel.Surfaces.Count
        SurfaceIDs = [i for i in range(1,nSurf+1)]
        surfaces = get_surfaces(axmodel,surfaceIDs = SurfaceIDs,
                                interactive = False)
    assert surfaces is not None, "Invalid specification of surfaces!"
    result = OrderedDict()
    for s in surfaces:
        nIDs = s.GetContourPoints()[0]
        sID = axmodel.Surfaces.IndexOfUID(s.UID)
        result[sID] = list(nIDs)
    return result

