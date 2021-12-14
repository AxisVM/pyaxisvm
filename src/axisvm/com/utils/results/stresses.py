import numpy as np
from pyoneer.tools.typing import issequence
from pyoneer.core import NestedDefaultDict
from collections import Iterable, OrderedDict
from pyoneer.interface.axisvm import AxisVMModel
from pyoneer.Qt.scripting.AxisVM.results import get_surface_forces
from pyoneer.Qt.scripting.AxisVM.results import get_nodal_surface_forces, \
	get_critical_nodal_surface_forces, get_critical_nodal_surface_forces2
from pyoneer.mechanics.model.metashell import PreShell

def get_surface_stresses(Model : AxisVMModel = None,\
	loadCaseIDs : Iterable = None, surfaceIDs = None,**kwargs):
	"""
	Returns surface stresses for the specified surfaces and load cases as a numpy array
	with shape (nLoadCase, nSurface, 4, 1, 3, 5),where 4, 1, 3 and 8 refer to the 4 corners,
	1 layer, 3 points through the thickness and 5 internal stress components at each of these.
	If loadCaseIDs are not provided, nLoadCase equals to Model.Model.LoadCases.Count.
	If surfaceIDs are not provided, nSurface equals to Model.Model.Surfaces.Count.
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""
	#Model._init_modules()
	stresses = Model.Results.Stresses
	if surfaceIDs is None:
		nSurf = Model.Surfaces.Count
		surfaceIDs = [i for i in range(1,nSurf+1)]
		def getstresses():
			nonlocal stresses
			RSurfaceStressValuesA, _ = stresses.AllSurfaceStressesByLoadCaseId()
			return RSurfaceStressValuesA
	else:
		assert issequence(surfaceIDs)
		nSurf = len(surfaceIDs)
		def getstresses():
			nonlocal stresses, surfaceIDs
			return [stresses.SurfaceStressesByLoadCaseId(id)[0] for id in surfaceIDs]

	if loadCaseIDs is None:
		nLoadCase = Model.LoadCases.Count
		loadCaseIDs = [i for i in range(1,nLoadCase+1)]
	else:
		nLoadCase = len(loadCaseIDs)
	nPoint,nLayer,nPointz,nComp = 4,1,3,5
	dtype = kwargs.get('dtype',np.float32)
	result = np.zeros((nLoadCase,nSurf,nPoint,nLayer,nPointz,nComp),dtype = dtype)

	comps = ['Sxx','Syy','Sxy','Sxz','Syz']
	ssvcomps = ['ssv' + comp for comp in comps]
	ssvtmbpoints = ['ssvtmbContourPoint' + str(i) for i in range(1,5)]
	ssvtmbpointsz = ['ssv' + str(i) for i in ['Top','Middle','Bottom']]
	for i,LoadCaseID in enumerate(loadCaseIDs):
		stresses.LoadCaseId = LoadCaseID
		RSurfaceStressesA = getstresses()
		for j,RSurfaceStresses in enumerate(RSurfaceStressesA):
			RSurfaceStressValuesTMBA = [getattr(RSurfaceStresses,p) for p in ssvtmbpoints]
			for k,RSurfaceStressValuesTMB in enumerate(RSurfaceStressValuesTMBA):
				RSurfaceStressValuesA = [getattr(RSurfaceStressValuesTMB,p) for p in ssvtmbpointsz]
				for l,RSurfaceStressValues in enumerate(RSurfaceStressValuesA):
					f = [getattr(RSurfaceStressValues,ssvcomp) for ssvcomp in ssvcomps]
					result[i,j,k,0,l,:] = np.array(f,dtype = np.float32)

	if kwargs.get('as_dict',False):
		res = NestedDefaultDict()
		for i,lid in enumerate(loadCaseIDs):
			for j,sid in enumerate(surfaceIDs):
				res[lid][sid] = result[i,j,:,:,:]
		return res
	else:
		return result

def calculate_surface_stresses(axModel : AxisVMModel = None, Model : PreShell = None, \
	loadCaseIDs : Iterable = None, surfaceIDs = None,**kwargs):
	"""
	Returns surface stresses for the specified surfaces and load cases as a numpy array
	with shape (nLoadCase, nSurface, 4, nLayer, 3, 5),where 4, 3 and 5 refer to the 4
	corners, 3 points through the thickness of a layer and 5 stress components at each.
	The stresses are calculated from the internal forces of the domain.
	If loadCaseIDs are not provided, nLoadCase equals to axModel.LoadCases.Count.
	If surfaceIDs are not provided, nSurface equals to axModel.Surfaces.Count.
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""
	assert axModel is not None
	assert Model is not None

	if surfaceIDs is None:
		nSurf = axModel.Surfaces.Count
		surfaceIDs = [i for i in range(1,nSurf+1)]
	else:
		assert issequence(surfaceIDs)
		nSurf = len(surfaceIDs)

	try:
		as_dict = kwargs.pop('as_dict',False)
	except:
		as_dict = False
	surface_forces = get_surface_forces(axModel, \
		loadCaseIDs = loadCaseIDs, surfaceIDs = surfaceIDs,**kwargs)

	if loadCaseIDs is None:
		nLoadCase = axModel.LoadCases.Count
		loadCaseIDs = [i for i in range(1,nLoadCase+1)]
	else:
		nLoadCase = len(loadCaseIDs)

	nPoint,nPointz,nComp = 4,3,5
	nLayer = Model.numLayers
	dtype = kwargs.get('dtype',np.float32)
	result = np.zeros((nLoadCase,nSurf,nPoint,nLayer,nPointz,nComp),dtype = dtype)

	for i in range(nLoadCase):
		for j in range(nSurf):
			for k in range(nPoint):
				f = surface_forces[i,j,k,:]
				result[i,j,k,:,:,:] = Model.stresses_from_forces(f,dtype = dtype)

	if as_dict:
		res = NestedDefaultDict()
		for i,lid in enumerate(loadCaseIDs):
			for j,sid in enumerate(surfaceIDs):
				res[lid][sid] = result[i,j,:,:,:,:]
		return res
	else:
		return result

def calculate_nodal_surface_stresses(axModel : AxisVMModel = None, Model : PreShell = None, \
	loadCaseIDs : Iterable = None, nodeIDs = None,**kwargs):
	"""
	Returns nodal surface stresses for the specified nodes and load cases as a numpy array
	with shape (nLoadCase, nNode, nLayer, 3, 5), where 3 and 5 refer to the 3 points through
	the thickness of a layer and 5 stress components at each.
	The stresses are calculated from the nodal internal forces of the model.
	If loadCaseIDs are not provided, nLoadCase equals to Model.Model.LoadCases.Count.
	If nodeIDs are not provided, nNode equals to Model.Model.Nodes.Count.
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""

	assert axModel is not None
	assert Model is not None

	if nodeIDs is None:
		nNode = axModel.Nodes.Count
		nodeIDs = [i for i in range(1,nNode+1)]
	else:
		assert issequence(nodeIDs)
		nNode = len(nodeIDs)

	try:
		as_dict = kwargs.pop('as_dict',False)
	except:
		as_dict = False
	nsf = get_nodal_surface_forces(axModel, \
		loadCaseIDs = loadCaseIDs, nodeIDs = nodeIDs,**kwargs)
	nLoadCase, nNode, _ = nsf.shape

	if loadCaseIDs is None:
		loadCaseIDs = [i for i in range(1,nLoadCase+1)]

	nPointz,nComp = 3,5
	nLayer = Model.numLayers
	dtype = kwargs.get('dtype',np.float32)
	result = np.zeros((nLoadCase,nNode,nLayer,nPointz,nComp),dtype = dtype)

	for i in range(nLoadCase):
		for j in range(nNode):
			f = nsf[i,j,:]
			result[i,j,:,:,:] = Model.stresses_from_forces(f,dtype = dtype)

	if as_dict:
		res = NestedDefaultDict()
		for i,lID in enumerate(loadCaseIDs):
			for j,nID in enumerate(nodeIDs):
				res[lID][nID] = result[i,j,:,:,:]
		return res
	else:
		return result

def calculate_critical_nodal_surface_stresses(axModel: AxisVMModel = None, \
		Model : PreShell = None, component = None, minmax : str = None, \
			combType : int = None, nodeIDs = None,**kwargs):
	"""
	Returns critical nodal surface stresses for the specified nodes as a numpy array
	with shape (nNode, nLayer, 3, 5), where 3 and 5 refer to the 3 points through
	the thickness of a layer and 5 stress components at each.
	The stresses are calculated from the critical nodal internal forces of the model.
	If nodeIDs are not provided, nNode equals to Model.Model.Nodes.Count.
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""
	if kwargs.get('combinations',False):
		return calculate_critical_nodal_surface_stresses2(Model, component = component, \
			minmax = minmax, combType = combType, nodeIDs = nodeIDs,**kwargs)

	assert axModel is not None
	assert Model is not None

	if nodeIDs is None:
		nNode = axModel.Nodes.Count
		nodeIDs = [i for i in range(1,nNode+1)]
	else:
		assert issequence(nodeIDs)
		nNode = len(nodeIDs)

	try:
		as_dict = kwargs.pop('as_dict',False)
	except:
		as_dict = False

	#get forces for all possible surface forces
	fcomps = ['nx','ny','nxy','mx','my','mxy','vxz','vyz']
	scompIndex = {scomp : i for i,scomp in enumerate(['sxx','syy','sxy','sxz','syz'])}
	fminmax = ['min','max']
	cnsf = get_critical_nodal_surface_forces(axModel, component = fcomps,\
		minmax = fminmax, combType = combType, nodeIDs = nodeIDs,**kwargs)

	#calculate stresses for all cases
	dtype = kwargs.get('dtype',np.float32)
	nPointz,nComp = 3,5
	nLayer = Model.numLayers
	stresses = np.zeros((nNode,16,nLayer,nPointz,nComp),dtype = dtype)
	for i in range(nNode):
		c = 0
		for fcomp in fcomps:
			for fmin_or_fmax in fminmax:
				f = cnsf[fcomp][fmin_or_fmax][i,:]
				stresses[i,c,:,:,:] = Model.stresses_from_forces(f,dtype = dtype)
				c += 1

	#gather min and max for the specified stress components
	result = OrderedDict()
	for scomp in component:
		result[scomp] = OrderedDict()
		for smin_or_smax in minmax:
			result[scomp][smin_or_smax] = OrderedDict()
			subresult = np.zeros((nNode,nLayer,nPointz,nComp),dtype = dtype)
			for i in range(nNode):
				si = stresses[i,:,:,:,scompIndex[scomp]]
				if smin_or_smax == 'min':
					minmaxIndex,*_ = np.argwhere(np.asarray(si == si.min()))[0]
				else:
					minmaxIndex,*_ = np.argwhere(np.asarray(si == si.max()))[0]
				subresult[i,:,:,:] = stresses[i,minmaxIndex,:,:,:]

			if as_dict:
				result[scomp][smin_or_smax] = {nID : subresult[i,:,:,:] for i,nID \
					in enumerate(nodeIDs)}
			else:
				result[scomp][smin_or_smax] = subresult
	return result

def calculate_critical_nodal_surface_stresses2(Model: AxisVMModel = None, \
		axModel : PreShell = None, component = None, minmax : str = None, \
			combType : int = None, nodeIDs = None,**kwargs):
	"""
	Returns critical nodal surface stresses for the specified nodes as a numpy array
	with shape (nNode, nLayer, 3, 5), where 3 and 5 refer to the 3 points through
	the thickness of a layer and 5 stress components at each.
	The stresses are calculated from the critical nodal internal forces of the model.
	If nodeIDs are not provided, nNode equals to Model.Model.Nodes.Count.
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""
	assert Model is not None
	assert axModel is not None

	if nodeIDs is None:
		nNode = axModel.Nodes.Count
		nodeIDs = [i for i in range(1,nNode+1)]
	else:
		assert issequence(nodeIDs)
		nNode = len(nodeIDs)

	try:
		as_dict = kwargs.pop('as_dict',False)
	except:
		as_dict = False

	#get forces for all possible surface forces
	fcomps = ['nx','ny','nxy','mx','my','mxy','vxz','vyz']
	scompIndex = {scomp : i for i,scomp in enumerate(['sxx','syy','sxy','sxz','syz'])}
	fminmax = ['min','max']
	cnsf2 = kwargs.get('cnsf2',None)
	if cnsf2 is None:
		cnsf2 = get_critical_nodal_surface_forces2(axModel, component = fcomps,\
			minmax = fminmax, combType = combType, nodeIDs = nodeIDs,**kwargs)

	#collect stresses and combinations for all cases
	dtype = kwargs.get('dtype',np.float32)
	nPointz,nComp = 3,5
	nLayer = Model.numLayers
	stresses = np.zeros((nNode,16,nLayer,nPointz,nComp),dtype = dtype)
	combinations = {nID : [] for nID in nodeIDs}
	for i,nID in enumerate(nodeIDs):
		c = 0
		for fcomp in fcomps:
			for fmin_or_fmax in fminmax:
				f = cnsf2[fcomp][fmin_or_fmax][0][i,:]
				stresses[i,c,:,:,:] = Model.stresses_from_forces(f,dtype = dtype)
				comb = cnsf2[fcomp][fmin_or_fmax][1][nID]
				combinations[nID].append(comb)
				c += 1

	#gather min and max and combination for the specified stress components
	result = OrderedDict()
	for scomp in component:
		result[scomp] = OrderedDict()
		for smin_or_smax in minmax:
			result[scomp][smin_or_smax] = [OrderedDict(),OrderedDict()]
			subresult = np.zeros((nNode,nLayer,nPointz,nComp),dtype = dtype)
			for i,nID in enumerate(nodeIDs):
				si = stresses[i,:,:,:,scompIndex[scomp]]
				if smin_or_smax == 'min':
					minmaxIndex,*_ = np.argwhere(np.asarray(si == si.min()))[0]
				else:
					minmaxIndex,*_ = np.argwhere(np.asarray(si == si.max()))[0]
				subresult[i,:,:,:] = stresses[i,minmaxIndex,:,:,:]
				result[scomp][smin_or_smax][1][nID] = combinations[nID][minmaxIndex]

			if as_dict:
				result[scomp][smin_or_smax][0] = {nID : subresult[i,:,:,:] for i,nID \
					in enumerate(nodeIDs)}
			else:
				result[scomp][smin_or_smax][0] = subresult
	return result




