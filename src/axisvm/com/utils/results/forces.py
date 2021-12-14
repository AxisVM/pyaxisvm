import numpy as np
from pyoneer.tools.typing import issequence
from pyoneer.core import NestedDefaultDict
from collections import OrderedDict
from collections import Iterable
from pyoneer.Qt.scripting.AxisVM.results.envelope import get_envelopeIDs
from pyoneer.Qt.scripting.AxisVM.surfaces import get_nodes_of_surfaces, \
	get_surfaces
from pyoneer.Qt.scripting.AxisVM.nodes import get_connected_surfaceIDs, \
	get_nodes, get_nodeIDs
from pyoneer.interface.axisvm import AxisVMModel

def get_surface_forces(Model : AxisVMModel, *args, loadCaseIDs : Iterable = None,**kwargs):
	"""
	Returns forces for the specified surfaces and load cases as a numpy
	array with shape (nLoadCase, nSurface, 4, 8),where 4 and 8 refer to
	the 4 corners and 8 internal force components.
	If loadCaseIDs are not provided, nLoadCase equals to Model.LoadCases.Count.
	If surfaceIDs are not provided, nSurface equals to Model.Surfaces.Count.
	For the details of specification of surfaces see the documentation 
	of function : get_surfaces.
	----
	Possible kwargs:
		- surface specifiers
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""
	forces = Model.Results.Forces
	surfaces = get_surfaces(Model,*args,**kwargs)
	surfaceIDs = [Model.Surfaces.IndexOfUID(s.UID) for s in surfaces] 
	assert issequence(surfaceIDs)
	nSurf = len(surfaceIDs)
	def getforces():
		nonlocal forces, surfaceIDs
		return [forces.SurfaceForcesByLoadCaseId(id)[0] for id in surfaceIDs]

	if loadCaseIDs is None:
		nLoadCase = Model.LoadCases.Count
		loadCaseIDs = [i for i in range(1,nLoadCase+1)]
	else:
		nLoadCase = len(loadCaseIDs)
	nPoint,nComp = 4,8
	dtype = kwargs.get('dtype',np.float32)
	result = np.zeros((nLoadCase,nSurf,nPoint,nComp),dtype = dtype)

	comps = ['Nx','Ny','Nxy','Mx','My','Mxy','Vxz','Vyz']
	svfcomps = ['sfv' + comp for comp in comps]
	svfpoints = ['sfvContourPoint' + str(i) for i in range(1,5)]
	for i,LoadCaseID in enumerate(loadCaseIDs):
		forces.LoadCaseId = LoadCaseID
		RSurfaceForcesA = getforces()
		for j,RSurfaceForces in enumerate(RSurfaceForcesA):
			RSurfaceForceValuesA = [getattr(RSurfaceForces,p) for p in svfpoints]
			for k,RSurfaceForceValues in enumerate(RSurfaceForceValuesA):
				f = [getattr(RSurfaceForceValues,sfvcomp) for sfvcomp in svfcomps]
				result[i,j,k,:] = np.array(f,dtype = np.float32)

	if kwargs.get('as_dict',False):
		res = dict()
		for i,lcID in enumerate(loadCaseIDs):
			res[lcID] = dict()
			for j,sID in enumerate(surfaceIDs):
				res[lcID][sID] = result[i,j,:,:]
		return res
	else:
		return result

def get_ALL_surface_forces(Model : AxisVMModel, *args, loadCaseIDs : Iterable = None,**kwargs):
	"""
	Returns surface forces for all surfaces and specified load cases
	as a numpy array with shape (nLoadCase, nSurface, 4, 8),where 4
	and 8 refer to the 4 corners and 8 internal force components.
	If loadCaseIDs are not provided, nLoadCase equals to Model.Model.LoadCases.Count.
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""
	return get_surface_forces(Model, 'all', *args, loadCaseIDs = loadCaseIDs,**kwargs)

def get_envelope_surface_forces(Model : AxisVMModel, *args, component = None, \
	minmax : str = None,**kwargs):

	"""
	if kwargs.get('combinations',False):
		return get_critical_surface_forces2(Model, *args, component = component, minmax = minmax, \
			combType = combType,**kwargs)
	"""
	forces = Model.Results.Forces

	#get surfaces
	surfaces = get_surfaces(Model,*args,**kwargs)
	surfaceIDs = [Model.Surfaces.IndexOfUID(s.UID) for s in surfaces] 	
	assert issequence(surfaceIDs)
	nSurf = len(surfaceIDs)
	def getforces():
		nonlocal forces, surfaceIDs
		return [forces.EnvelopeSurfaceForces(id)[0] for id in surfaceIDs]

	#component
	if issequence(component):
		res = NestedDefaultDict()
		for comp in component:
			res[comp] = get_envelope_surface_forces(Model, \
				component = comp, minmax = minmax, \
				surfaceIDs = surfaceIDs,\
					**kwargs)
		return res
	else:
		components = ['nx','ny','nxy','mx','my','mxy','vxz','vyz']
		if isinstance(component,str):
			compIndex = components.index(component.lower())
		elif isinstance(component,int):
			compIndex = component
		forces.SurfaceForceComponent = Model.tlb.ESurfaceForce(compIndex)
	
	#minmax type
	if issequence(minmax):
		res = NestedDefaultDict()
		for mtype in minmax:
			res[mtype] = get_critical_surface_forces(Model, \
				component = component, minmax = mtype, \
				IDs = surfaceIDs,\
					**kwargs)
		return res
	else:
		minmaxIndex = 0 if minmax.lower() == 'min' else 1
		forces.MinMaxType = Model.tlb.EMinMaxType(minmaxIndex)

	eIDs = get_envelopeIDs(Model,*args,**kwargs)
	nEnvelope = len(eIDs)
	nPoint,nComp = 4,8
	dtype = kwargs.get('dtype',np.float32)
	result = np.zeros((nEnvelope,nSurf,nPoint,nComp),dtype = dtype)

	for i,eID in enumerate(eIDs):
		eUID = Model.Envelopes.EnvelopeUID[eID]
		forces.EnvelopeUID = eUID
		RSurfaceForcesA = getforces()
		svfpoints = ['sfvContourPoint' + str(i) for i in range(1,5)]
		comps = ['Nx','Ny','Nxy','Mx','My','Mxy','Vxz','Vyz']
		svfcomps = ['sfv' + comp for comp in comps]
		for j,RSurfaceForces in enumerate(RSurfaceForcesA):
			RSurfaceForceValuesA = [getattr(RSurfaceForces,p) for p in svfpoints]
			for k,RSurfaceForceValues in enumerate(RSurfaceForceValuesA):
				f = [getattr(RSurfaceForceValues,sfvcomp) for sfvcomp in svfcomps]
				result[i,j,k,:] = np.array(f,dtype = np.float32)

	if kwargs.get('as_dict',False):
		res = NestedDefaultDict()
		for i,eID in enumerate(eIDs):
			for j,sid in enumerate(surfaceIDs):
				res[eID][sid] = result[j,:,:]
		return res
	else:
		return result

def get_critical_surface_forces(Model : AxisVMModel, *args, component = None, \
	minmax : str = None, combType : int = None,**kwargs):
	"""
	Returns critical forces for the specified surfaces as a numpy
	array with the shape of (nSurfaces,4,8). 4 and 8 refer
	to the 4 corners and 8 internal force components.
	-----
	minmax : 'min' or 'max'
	component : any of ['nx','ny','nxy','mx','my','mxy','vxz','vyz'],
				or an integer (see the enumeration ESurfaceForce)
	combType : integer (see the enumeration ECombinationType)

	If combType is not provided, the combonent with the highest index
	is selected from all the possible values in the model
	(see the enumeration ECombinationType).
	If surfaceIDs are not provided, nSurface equals to Model.Model.Surfaces.Count.
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
		- combinations : if True, calls get_critical_surface_forces2()
	---
	author : Bence BALOGH
	"""
	if kwargs.get('combinations',False):
		return get_critical_surface_forces2(Model, *args, component = component, minmax = minmax, \
			combType = combType,**kwargs)
	
	forces = Model.Results.Forces

	#get surfaces
	surfaces = get_surfaces(Model,*args,**kwargs)
	surfaceIDs = [Model.Surfaces.IndexOfUID(s.UID) for s in surfaces] 	
	assert issequence(surfaceIDs)
	nSurf = len(surfaceIDs)
	def getforces():
		nonlocal forces, surfaceIDs
		return [forces.CriticalSurfaceForces(id)[0] for id in surfaceIDs]

	#component
	if issequence(component):
		res = NestedDefaultDict()
		for comp in component:
			res[comp] = get_critical_surface_forces(Model, \
				component = comp, minmax = minmax, \
				combType = combType,surfaceIDs = surfaceIDs,**kwargs)
		return res
	else:
		components = ['nx','ny','nxy','mx','my','mxy','vxz','vyz']
		if isinstance(component,str):
			compIndex = components.index(component.lower())
		elif isinstance(component,int):
			compIndex = component
		forces.SurfaceForceComponent = Model.tlb.ESurfaceForce(compIndex)

	#minmax type
	if issequence(minmax):
		res = NestedDefaultDict()
		for mtype in minmax:
			res[mtype] = get_critical_surface_forces(Model, \
				component = component, minmax = mtype, \
				combType = combType,surfaceIDs = surfaceIDs,**kwargs)
		return res
	else:
		minmaxIndex = 0 if minmax.lower() == 'min' else 1
		forces.MinMaxType = Model.tlb.EMinMaxType(minmaxIndex)

	#combinationtype
	if combType is None:
		validcombs = Model.valid_combination_types()
		combType = max(validcombs)
	else:
		assert isinstance(combType,int)
	forces.CombinationType = Model.tlb.ECombinationType(combType)

	nPoint,nComp = 4,8
	dtype = kwargs.get('dtype',np.float32)
	result = np.zeros((nSurf,nPoint,nComp),dtype = dtype)

	RSurfaceForcesA = getforces()
	svfpoints = ['sfvContourPoint' + str(i) for i in range(1,5)]
	comps = ['Nx','Ny','Nxy','Mx','My','Mxy','Vxz','Vyz']
	svfcomps = ['sfv' + comp for comp in comps]
	for j,RSurfaceForces in enumerate(RSurfaceForcesA):
		RSurfaceForceValuesA = [getattr(RSurfaceForces,p) for p in svfpoints]
		for k,RSurfaceForceValues in enumerate(RSurfaceForceValuesA):
			f = [getattr(RSurfaceForceValues,sfvcomp) for sfvcomp in svfcomps]
			result[j,k,:] = np.array(f,dtype = np.float32)

	if kwargs.get('as_dict',False):
		res = NestedDefaultDict()
		for j,sid in enumerate(surfaceIDs):
			res[sid] = result[j,:,:]
		return res
	else:
		return result

def get_critical_surface_forces2(Model : AxisVMModel, *args, component = None, \
		minmax : str = None, combType : int = None,**kwargs):
	"""
	Returns critical forces for the	specified surfaces as a numpy array 
	with the shape of (nSurfaces,4,8) and a dictionary about the critical 
	combination. 
	4 and 8 refer to the 4 corners and 8 internal force components.
	-----
	minmax : 'min' or 'max'
	component : any of ['nx','ny','nxy','mx','my','mxy','vxz','vyz'],
				or an integer (see the enumeration ESurfaceForce)
	combType : integer (see the enumeration ECombinationType)

	If combType is not provided, the combonent with the highest index
	is selected from all the possible values in the model
	(see the enumeration ECombinationType).
	If surfaceIDs are not provided, nSurface equals to Model.Model.Surfaces.Count.
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""
	forces = Model.Results.Forces
	sfType = Model.tlb.ESurfaceVertexType(0) #surface polygon vertex

	#surfaces
	surfaces = get_surfaces(Model,*args,**kwargs)
	surfaceIDs = [Model.Surfaces.IndexOfUID(s.UID) for s in surfaces] 	
	assert issequence(surfaceIDs)
	nSurf = len(surfaceIDs)
	sIDs_to_nIDs = get_nodes_of_surfaces(Model, surfaceIDs = surfaceIDs)
			
	#component
	if issequence(component):
		res = {}
		for comp in component:
			res[comp] = get_critical_surface_forces2(Model, \
				component = comp, minmax = minmax, \
				combType = combType,surfaceIDs = surfaceIDs,**kwargs)
		return res
	else:
		components = ['nx','ny','nxy','mx','my','mxy','vxz','vyz']
		if isinstance(component,str):
			compIndex = components.index(component.lower())
		elif isinstance(component,int):
			compIndex = component
		forces.SurfaceForceComponent = Model.tlb.ESurfaceForce(compIndex)

	#minmax type
	if issequence(minmax):
		res = {}
		for mtype in minmax:
			res[mtype] = get_critical_surface_forces2(Model, \
				component = component, minmax = mtype, \
				combType = combType,surfaceIDs = surfaceIDs,**kwargs)
		return res
	else:
		minmaxIndex = 0 if minmax.lower() == 'min' else 1
		forces.MinMaxType = Model.tlb.EMinMaxType(minmaxIndex)

	#combinationtype
	if combType is None:
		validcombs = Model.valid_combination_types()
		combType = max(validcombs)
	else:
		assert isinstance(combType,int)
	forces.CombinationType = Model.tlb.ECombinationType(combType)

	nPoint,nComp = 4,8
	dtype = kwargs.get('dtype',np.float32)
	result = np.zeros((nSurf,nPoint,nComp),dtype = dtype)
	result_comb = OrderedDict()
	comps = ['Nx','Ny','Nxy','Mx','My','Mxy','Vxz','Vyz']
	svfcomps = ['sfv' + comp for comp in comps]
	for i, sID in enumerate(sIDs_to_nIDs):
		result_comb[sID] = OrderedDict()
		for j,nID in enumerate(sIDs_to_nIDs[sID]):
			RSurfaceForceValues,combtype,factors,lcIDs,_ = \
				forces.CriticalSurfaceForce2(sID,sfType,nID)
			f = [getattr(RSurfaceForceValues,sfvcomp) \
				for sfvcomp in svfcomps]
			combination = OrderedDict({lcID : factor for lcID,factor in zip(lcIDs,factors)})
			result[i,j,:] = np.array(f,dtype = dtype)
			result_comb[sID][nID] = {
				'CriticalCombination' : combination,
				'CriticalCombinationType' : combtype
			}

	if kwargs.get('as_dict',False):
		res_d = OrderedDict()
		for i, sID in enumerate(sIDs_to_nIDs):
			res_d[sID] = OrderedDict()
			for j,nID in enumerate(sIDs_to_nIDs[sID]):
				res_d[sID][nID] = result[i,j,:]
		return res_d, result_comb
	else:
		return result, result_comb

def get_ALL_critical_surface_forces(Model : AxisVMModel, *args, component = None, \
		minmax : str = None, combType : int = None,**kwargs):
	"""
	Returns critical forces for all surfaces as a numpy array
	with the shape of (nSurfaces,4,8). 4 and 8 refer to the 4 corners
	and 8 internal force components.
	-----
	minmax : 'min' or 'max'
	component : any of ['nx','ny','nxy','mx','my','mxy','vxz','vyz'],
				or an integer (see the enumeration ESurfaceForce)
	combType : integer (see the enumeration ECombinationType)

	If combType is not provided, the combonent with the highest index
	is selected from all the possible values in the model
	(see the enumeration ECombinationType).
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""
	return get_critical_surface_forces(Model, 'all', *args, component = component, \
		minmax = minmax,combType = combType,**kwargs)

def get_nodal_surface_forces(Model : AxisVMModel, *args, loadCaseIDs : Iterable = None,\
		**kwargs):
	"""
	Returns forces for the specified nodes and load cases as a numpy
	array with shape (nLoadCase, nNode,  8), where 8 refers to
	the 8 internal force components.
	If loadCaseIDs are not provided, nLoadCase equals to Model.Model.LoadCases.Count.
	If nodeIDs are not provided, nNode equals to Model.Model.Nodes.Count.
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""
	nIDs = get_nodeIDs(Model,*args,**kwargs)
	assert issequence(nIDs)
	nNode = len(nIDs)
	nID_to_sIDs = get_connected_surfaceIDs(Model, nodeIDs = nIDs, as_dict = True)
	sIDs = list(set(np.concatenate(list(nID_to_sIDs.values())).flatten()))
	sID_to_nIDs = get_nodes_of_surfaces(Model, surfaceIDs = sIDs)

	try:
		as_dict = kwargs.pop('as_dict',False)
	except:
		as_dict = False
	
	if loadCaseIDs is None:
		nLoadCase = Model.LoadCases.Count
		loadCaseIDs = [i for i in range(1,nLoadCase+1)]
	else:
		assert issequence(loadCaseIDs)
		nLoadCase = len(loadCaseIDs)
	sf_d = get_surface_forces(Model, loadCaseIDs = loadCaseIDs, \
		surfaceIDs = sIDs, as_dict = True)

	dtype = kwargs.get('dtype',np.float32)
	result = np.zeros((nLoadCase,nNode,8),dtype = dtype)
	for i,lcID in enumerate(loadCaseIDs):
		for j,nID in enumerate(nIDs):
			nodalforces = []
			for sID in nID_to_sIDs[nID]:
				nIndex = sID_to_nIDs[sID].index(nID)
				nodalforces.append(sf_d[lcID][sID][nIndex,:])
			result[i,j,:] = np.average(nodalforces,axis = 0)

	if as_dict:
		res = NestedDefaultDict()
		for i,lcID in enumerate(loadCaseIDs):
			for j,nID in enumerate(nIDs):
				res[lcID][nID] = result[i,j,:]
		return res
	else:
		return result

def get_ALL_nodal_surface_forces(Model : AxisVMModel, *args, loadCaseIDs : Iterable = None,\
		**kwargs):
		"""
		Returns forces for all the nodes and specified load cases as a numpy
		array with shape (nLoadCase, nNode,  8),where 8 refers to
		the 8 internal force components.
		If loadCaseIDs are not provided, nLoadCase equals to Model.Model.LoadCases.Count.
		nNode equals to Model.Model.Nodes.Count.
		----
		Possible kwargs:
			- dtype : as in numpy, applies to the result
			- as_dict : returns the values in the form of a dictionary
		---
		author : Bence BALOGH
		"""
		return get_nodal_surface_forces(Model, 'all', *args, loadCaseIDs = loadCaseIDs,**kwargs)

def get_critical_nodal_surface_forces(Model : AxisVMModel, *args, component = None, \
		minmax : str = None, combType : int = None,**kwargs):
	"""
	Returns critical forces for the specified nodes as a numpy
	array with shape (nNode,  8), where 8 refers to	the 8 internal force components.
	If nodeIDs are not provided, nNode equals to Model.Model.Nodes.Count.
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""
	if kwargs.get('combinations',False):
		return get_critical_nodal_surface_forces2(Model, *args, component = component, minmax = minmax, \
			combType = combType, **kwargs)

	nodeIDs = get_nodeIDs(Model,*args,**kwargs)
	assert issequence(nodeIDs)
	sIDs = get_connected_surfaceIDs(Model, nodeIDs = nodeIDs, flatten = True)
	nNode = len(nodeIDs)
	sIDs_to_nIDs = get_nodes_of_surfaces(Model, surfaceIDs = sIDs)
	nIDs = list(set(np.concatenate(list(sIDs_to_nIDs.values())).flatten()))

	try:
		as_dict = kwargs.pop('as_dict',False)
	except:
		as_dict = False
	if not issequence(component):
		component = [component]
	if not issequence(minmax):
		minmax = [minmax]
	csf_fcomp_minmax = get_critical_surface_forces(Model, *args, component = component,\
		minmax = minmax, combType = combType, surfaceIDs = sIDs,**kwargs)

	comps = ['nx','ny','nxy','mx','my','mxy','vxz','vyz']
	nComp = 8
	dtype = kwargs.get('dtype',np.float32)
	result = NestedDefaultDict()
	for fcomp in component:
		fcompIndex = comps.index(fcomp)
		for min_or_max in minmax:
			csf = csf_fcomp_minmax[fcomp][min_or_max]
			nodalforces = {nID : [] for nID in nIDs}
			for i,sID in enumerate(sIDs_to_nIDs.keys()):
				for j,nID in enumerate(sIDs_to_nIDs[sID]):
					nodalforces[nID].append(csf[i,j,:])

			subresult = np.zeros((nNode,nComp),dtype = dtype)
			for i,nID in enumerate(nodeIDs):		
				nodalforces[nID] = np.vstack(nodalforces[nID])
				if min_or_max == 'min':
					minmaxIndex = np.argmin(nodalforces[nID][:,fcompIndex])
				else:
					minmaxIndex = np.argmax(nodalforces[nID][:,fcompIndex])
				subresult[i,:] = nodalforces[nID][minmaxIndex,:]

			if as_dict:
				result[fcomp][min_or_max] = {nID : subresult[i,:] for i,nID in enumerate(nodeIDs)}
			else:
				result[fcomp][min_or_max] = subresult

	return result

def get_critical_nodal_surface_forces2(Model : AxisVMModel, *args, component = None, \
		minmax : str = None, combType : int = None,**kwargs):
	"""
	Returns critical forces and combination data for the specified nodes as a numpy
	array with shape (nNode,  8) and a dyctionary, where 8 refers to the 8 internal 
	force components.
	If nodeIDs are not provided, nNode equals to Model.Model.Nodes.Count.
	----
	Possible kwargs:
		- dtype : as in numpy, applies to the result
		- as_dict : returns the values in the form of a dictionary
	---
	author : Bence BALOGH
	"""
	nodeIDs = get_nodeIDs(Model,*args,**kwargs)
	assert issequence(nodeIDs)
	sIDs = get_connected_surfaceIDs(Model, nodeIDs = nodeIDs, flatten = True)
	nNode = len(nodeIDs)
	sIDs_to_nIDs = get_nodes_of_surfaces(Model, surfaceIDs = sIDs)
	nIDs = list(set(np.concatenate(list(sIDs_to_nIDs.values())).flatten()))

	try:
		as_dict = kwargs.pop('as_dict',False)
	except:
		as_dict = False
	if not issequence(component):
		component = [component]
	if not issequence(minmax):
		minmax = [minmax]
	csf2 = get_critical_surface_forces2(Model, *args, component = component,\
		minmax = minmax, combType = combType, surfaceIDs = sIDs,**kwargs)

	comps = ['nx','ny','nxy','mx','my','mxy','vxz','vyz']
	nComp = 8
	dtype = kwargs.get('dtype',np.float32)
	result = OrderedDict()
	for fcomp in component:
		result[fcomp] = OrderedDict()
		fcompIndex = comps.index(fcomp)
		for min_or_max in minmax:
			result[fcomp][min_or_max] = [OrderedDict(),OrderedDict()]
			csf_val = csf2[fcomp][min_or_max][0]
			csf_comb = csf2[fcomp][min_or_max][1]
			nodalforces = {nID : [] for nID in nIDs}
			nodalcombs = {nID : [] for nID in nIDs}
			for i,sID in enumerate(sIDs_to_nIDs.keys()):
				for j,nID in enumerate(sIDs_to_nIDs[sID]):
					nodalforces[nID].append(csf_val[i,j,:])
					nodalcombs[nID].append(csf_comb[sID][nID])

			subresult = np.zeros((nNode,nComp),dtype = dtype)
			for i,nID in enumerate(nodeIDs):		
				nodalforces[nID] = np.vstack(nodalforces[nID])
				if min_or_max == 'min':
					minmaxIndex = np.argmin(nodalforces[nID][:,fcompIndex])
				else:
					minmaxIndex = np.argmax(nodalforces[nID][:,fcompIndex])
				subresult[i,:] = nodalforces[nID][minmaxIndex,:]
				result[fcomp][min_or_max][1][nID] = nodalcombs[nID][minmaxIndex]

			if as_dict:
				result[fcomp][min_or_max][0] = {nID : subresult[i,:] for i,nID \
					in enumerate(nodeIDs)}
			else:
				result[fcomp][min_or_max][0] = subresult

	return result

