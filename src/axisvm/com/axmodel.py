# -*- coding: utf-8 -*-
from axisvm.com.core.wrap import Wrapper, CollectionWrapper
from axisvm.com.utils import RMatrix3x3toNumPy, RMatrix2x2toNumPy
import numpy as np
from numba import njit
import pyvista as pv
try:
    from dewloosh.geom import PolyData
    __pnr__ = True
except ImportError:
    __pnr__ = False


__all__ = ['AxModels', 'AxModel', 'AxDomains', 'AxDomain']


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
            keyT3 : np.zeros((count[dID][keyT3], 3), dtype=dIDs.dtype), 
            keyQ4 : np.zeros((count[dID][keyQ4], 4), dtype=dIDs.dtype)
                }
    return res, inds


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


class AxDomain(Wrapper):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                        
    def coords(self, *args, **kwargs):
        raise NotImplementedError
    
    def plot(self, *args, isolate=True, proj='2d', backend='mpl', **kwargs):
        raise NotImplementedError
        
    def ABDS(self, compose=True):
        A, B, D, S, *_ = self._wrapped.GetCustomStiffnessMatrix()
        A, B, D = [RMatrix3x3toNumPy(x) for x in (A, B, D)]
        S = RMatrix2x2toNumPy(S)
        if compose:
            res = np.zeros((8, 8))
            res[0:3, 0:3] = A
            res[0:3, 3:6] = B
            res[3:6, 0:3] = B
            res[3:6, 3:6] = D
            res[6:8, 6:8] = S
            return res
        else:
            return A, B, D, S
        

class AxDomains(CollectionWrapper):
    
    __itemcls__ = AxDomain
    
    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
                        
    def coords(self, *args, **kwargs):
        raise NotImplementedError
    
    def topology(self):
        axm = self.model
        nS = axm.Surfaces.Count
        sIDs = [i+1 for i in range(nS)]
        surfaces = axm.Surfaces.BulkGetSurfaces(sIDs)[0]
        dIDs = np.array(list(map(lambda x : x.DomainIndex, surfaces))).astype(np.int64)
        scoords = axm.Surfaces.GetAllCoordinatesOfSurfaces(sIDs)[0]
        lengths = np.array(list(map(lambda x : x.ContourPointCount, scoords)))
        polydata, inds = group_surfaces(lengths, dIDs)
        def getter(i):    
            if lengths[i] == 3:
                polydata[dIDs[i]]['T3'][inds[i], 0] = scoords[i].ContourPoint1Id - 1
                polydata[dIDs[i]]['T3'][inds[i], 1] = scoords[i].ContourPoint2Id - 1
                polydata[dIDs[i]]['T3'][inds[i], 2] = scoords[i].ContourPoint3Id - 1
            elif lengths[i] == 4:
                polydata[dIDs[i]]['Q4'][inds[i], 0] = scoords[i].ContourPoint1Id - 1
                polydata[dIDs[i]]['Q4'][inds[i], 1] = scoords[i].ContourPoint2Id - 1
                polydata[dIDs[i]]['Q4'][inds[i], 2] = scoords[i].ContourPoint3Id - 1
                polydata[dIDs[i]]['Q4'][inds[i], 3] = scoords[i].ContourPoint4Id - 1
            return None
        list(map(getter, range(nS)))
        return polydata
    
    def to_polydata(self):
        if __pnr__:
            coords = self.model.coords()
            polydata = self.topology()
            mesh = PolyData(coords=coords)
            for key in polydata:
                for subkey in polydata[key]:
                    mesh[key][subkey] = PolyData(topo=polydata[key][subkey])
            return mesh
        else:
            raise NotImplementedError
        
    def to_vtk(self, deepcopy=True):
        return self.to_polydata().to_vtk(deepcopy)
        
    def to_pyvista(self, deepcopy=True):
        return pv.wrap(self.to_vtk(deepcopy))
    
    def plot(self, *args, theme='document', deepcopy=True, \
        jupyter_backend='pythreejs', show_edges=True, \
            notebook=False, **kwargs): 
        if theme is not None:
            pv.set_plot_theme(theme)
        if notebook:
            return pv.wrap(self.to_vtk(deepcopy)).plot(*args, \
                jupyter_backend=jupyter_backend, show_edges=show_edges, \
                    notebook=notebook, **kwargs)
        else:
            pv.wrap(self.to_vtk(deepcopy)).plot(*args, \
                show_edges=show_edges, notebook=notebook, \
                    **kwargs)
                      
        
class AxLine(Wrapper):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AxLines(CollectionWrapper):
    
    __itemcls__ = AxLine
    
    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model