# -*- coding: utf-8 -*-
from dewloosh.core.typing.wrap import Wrapper
from axisvm.com.core.wrap import CollectionWrapper
from axisvm.com.core.utils import RMatrix3x3toNumPy, RMatrix2x2toNumPy
from axisvm.com.utils.surfaces import group_surfaces
import numpy as np
import pyvista as pv
try:
    from dewloosh.geom import PolyData
    __pdata__ = True
except ImportError:
    __pdata__ = False
    

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
            res = np.zeros((8, 8), dtype=float)
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
        if __pdata__:
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