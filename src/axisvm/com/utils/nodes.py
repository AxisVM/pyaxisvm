# -*- coding: utf-8 -*-
from collections import OrderedDict
import numpy as np


def get_nodes(Model, *args, interactive=False, **kwargs):
    """
    Returns a list of nodes, which can be specified by keyword
    arguments. It can be used to turn an arbitrary specification
    of nodes in an embedded situation into a list of nodes.
    For that reason it includes trivial keys. Individual elements
    can be specified, but the result is always a list. If there are
    no valid specifiers, then
        (1) if argument 'all' is provided, all of the nodes of the
            model are returned
        (2) if interactive == True, function either gets the selected
            nodes from AxisVM, or if there is none, a selection \
            dialog shows up in AxisVM and the function is called again \
            with valid specifiers emerging from any of these scenarios.
    ---
    Possible keys and values
        node : a single domain, returns [node]
        nodes : a list of nodes, returns nodes
        ID : int, a single nodeID
        IDs : [int], a sequence of nodeIDs
        UID : int, a single nodeUID
        UIDs : [int], a sequence of nodeUIDs
    ---
    For example
        nodes = get_nodes(Model,**kwargs)
    or simply
        nodes = get_nodes(Model)
    to get nodes from a selection in AxisVM.
    """
    nodes = None
    try:
        if 'node' in kwargs:
            nodes = [kwargs.pop('node')]
        elif 'nodes' in kwargs:
            nodes = kwargs.pop('nodes')
        elif 'nodeID' in kwargs:
            nodes = [Model.Nodes.GetNode(kwargs.pop('nodeID'))[0]]
        elif 'nodeIDs' in kwargs:
            nodes = [Model.Nodes.GetNode(ID)[0]
                     for ID in kwargs.pop('nodeIDs')]
        elif 'nodeUID' in kwargs:
            ID = Model.Nodes.IndexOfUID(kwargs.pop('nodeUID'))
            nodes = [Model.Nodes.GetNode(ID)[0]]
        elif 'nodeUIDs' in kwargs:
            IDs = [Model.Nodes.IndexOfUID(UID)
                   for UID in kwargs.pop('nodeUIDs')]
            nodes = [Model.Nodes.GetNode(ID)[0] for ID in IDs]
    except Exception:
        raise "Ivalid specification of nodes!"
    finally:
        if nodes is None:
            nodes = get_selected_nodes(Model, interactive=interactive)
            if nodes is None and 'allnodes' in args:
                nNode = Model.Nodes.Count
                nodeIDs = [i for i in range(1, nNode+1)]
                nodes = get_nodes(Model, IDs=nodeIDs,
                                  interactive=False)
        return nodes


def select_nodes(Model, message: str = None):
    """
    Shows up a selectiondialog for nodes in AxisVM and returns the selected
    nodes if succesful.
    """
    if message is None:
        message = 'Select one or more nodes!'
    Model.StartModalSelection(message, Model.tlb.lbTrue, 'seltNode')
    return get_selected_nodes(Model, interactive=False)


def get_selected_nodes(Model, interactive=False):
    """
    Returns a dictionary of nodes mapping nodeIDs to Nodes.
    """
    try:
        nIDs = Model.Nodes.GetSelectedItemIds()[0]
        return [Model.Nodes.GetNode(nID)[0] for nID in nIDs]
    except Exception:
        if interactive:
            return select_nodes(Model, message='Select one or more nodes!')
        else:
            return None


def get_nodeIDs(Model, *args, interactive=False, **kwargs):
    """
    Returns a list of integers, which can be specified by keyword
    arguments. It can be used to turn an arbitrary specification
    of nodeIDs in an embedded situation into a list of nodeIDs.
    For that reason it includes trivial keys. Individual elements
    can be specified, but the result is always a list. If there are
    no valid specifiers, the function either gets the selected nodes
    from AxisVM, or if there is none, a selection dialog shows up in
    AxisVM and the function is called again with valid specifiers
    emerging from any of these scenarios.
    ---
    Possible keys and values
        node : a single domain, returns [node]
        nodes : a list of nodes, returns nodes
        ID : int, a single nodeID
        IDs : [int], a sequence of nodeIDs
        UID : int, a single nodeUID
        UIDs : [int], a sequence of nodeUIDs
    ---
    For example
        nodeIDs = get_nodeIDs(Model,**kwargs)
    or simply
        nodeIDs = get_nodeIDs(Model)
    to get nodeIDs from a selection in AxisVM.
    """
    nodeIDs = None
    try:
        if 'node' in kwargs:
            n = kwargs['node']
            nodeIDs = [Model.Nodes.IndexOf(n.x, n.y, n.z, 1e-8, 1)]
        elif 'nodes' in kwargs:
            nodes = kwargs['nodes']
            nodeIDs = [Model.Nodes.IndexOf(n.x, n.y, n.z, 1e-8, 1)
                       for n in nodes]
        if 'nodeID' in kwargs:
            nodeIDs = [kwargs['nodeID']]
        elif 'nodeIDs' in kwargs:
            nodeIDs = kwargs['nodeIDs']
        elif 'nodeUID' in kwargs:
            nodeIDs = [Model.Nodes.IndexOfUID(kwargs['nodeUID'])]
        elif 'nodeUIDs' in kwargs:
            nodeIDs = [Model.Nodes.IndexOfUID(UID)
                       for UID in kwargs['nodeUIDs']]
    except Exception:
        raise "Ivalid specification of nodeIDs!"
    finally:
        if nodeIDs is None:
            nodeIDs = get_selected_nodeIDs(Model, interactive=interactive)
            if nodeIDs is None and 'allnodes' in args:
                nNode = Model.Nodes.Count
                nodeIDs = [i for i in range(1, nNode+1)]
        return nodeIDs


def select_nodeIDs(Model, message: str = None):
    """
    Shows up a selectiondialog for nodes in AxisVM and returns the selected
    nodeIDs if succesful.
    """
    if message is None:
        message = 'Select one or more nodes!'
    Model.StartModalSelection(message, Model.tlb.lbTrue, 'seltNode')
    return get_selected_nodeIDs(Model, interactive=False)


def get_selected_nodeIDs(Model, interactive=False):
    """
    Returns a list of nodeIDs. The result is always iterable,
    even if it contains only one item.
    """
    try:
        return Model.Nodes.GetSelectedItemIds()[0]
    except Exception:
        if interactive:
            return select_nodeIDs(Model, message='Select one or more nodes!')
        else:
            return None


def get_coordinates(Model = None, as_dict=False,
                    dtype=np.float32, **kwargs):
    """
    Returns coordinates of the specified nodes. For the details of
    specification of nodes see the documentation of function : get_nodeIDs.
    """
    nodeIDs = get_nodeIDs(Model, **kwargs)
    assert nodeIDs is not None, "Invalid specification of nodes!"
    RPoint3Ds, _ = Model.Nodes.BulkGetCoord(nodeIDs)
    if as_dict:
        return {nID: np.array([RPoint3D.x, RPoint3D.y, RPoint3D.z],
                              dtype=dtype) for nID, RPoint3D in
                zip(nodeIDs, RPoint3Ds)}
    return np.array([[RPoint3D.x, RPoint3D.y, RPoint3D.z]
                     for RPoint3D in RPoint3Ds], dtype=dtype)


def get_connected_surfaceIDs(Model = None, flatten=False,
                             as_dict=False, **kwargs):
    """
    Returns surfaces connected by the specified nodes. For the details of
    specification of nodes see the documentation of function : get_nodeIDs.
    If as_dict == True, result is a dictionary that maps nodeIDs to lists
    of surfaceIDs.
    """
    nodeIDs = get_nodeIDs(Model, **kwargs)
    assert nodeIDs is not None, "Invalid specification of nodes!"
    if as_dict:
        return OrderedDict({nID: Model.Nodes.GetConnectedSurfaces(nID)[0]
                            for nID in nodeIDs})
    if flatten:
        surfaces = set()
        for nID in nodeIDs:
            surfaces.update(Model.Nodes.GetConnectedSurfaces(nID)[0])
        return list(surfaces)
    return [Model.Nodes.GetConnectedSurfaces(nID)[0] for nID in nodeIDs]
