# -*- coding: utf-8 -*-
import numpy as np


def get_domains(Model, *args, interactive=False, **kwargs):
    """
    Returns a list of domains, which can be specified by keyword
    arguments. It can be used to turn an arbitrary specification
    of domains in an embedded situation into a list of domains.
    For that reason it includes trivial keys. Individual elements
    can be specified, but the result is always a list. If there are
    no valid specifiers, the function either gets the selected domains
    from AxisVM, or if there is none, a selection dialog shows up in
    AxisVM and the function is called again with valid specifiers
    emerging from any of these scenarios.

    Possible keys and values
    ------------------------
    
        'domain' : a single domain, returns [domain]
        
        'domains' : a list of domains, returns domains
        
        'ID' : int, a single domainID
        
        'IDs' : [int], a sequence of domainIDs
        
        'UID' : int, a single domainUID
        
        'UIDs' : [int], a sequence of domainUIDs
        
    Parameters
    ----------    
        interactive : bool, optional
            Dafault is False.
    
    Returns
    -------
    list
        A list of AxisVM domains.
    
    Examples
    --------
    Assuming that we have an interface to an AxisVM model as the\n 
    variable `model`:

    >>> from axisvm.com.utils import get_domains
    >>> get_domains(model, ID=10)
    >>> get_domains(model, IDs=[1, 10, 5])
    
    """
    domains = None
    try:
        if 'domain' in kwargs:
            domains = [kwargs.pop('domain')]
        elif 'domains' in kwargs:
            domains = kwargs.pop('domains')
        elif 'domainID' in kwargs:
            domains = [Model.Domains.Item[kwargs.pop('domainID')]]
        elif 'domainIDs' in kwargs:
            domains = [Model.Domains.Item[ID]
                       for ID in kwargs.pop('domainIDs')]
        elif 'domainUID' in kwargs:
            ID = Model.Domains.IndexOfUID(kwargs.pop('domainUID'))
            domains = [Model.Domains.Item[ID]]
        elif 'domainUIDs' in kwargs:
            IDs = [Model.Domains.IndexOfUID(UID)
                   for UID in kwargs.pop('domainUIDs')]
            domains = [Model.Domains.Item[ID] for ID in IDs]
    except Exception:
        raise "Ivalid specification of domains!"
    finally:
        if domains is None:
            domains = get_selected_domains(Model, interactive=interactive)
            if domains is None and 'alldomains' in args:
                nDomain = Model.Domains.Count
                dIDs = [i for i in range(1, nDomain+1)]
                domains = get_domains(Model, domainIDs=dIDs,
                                      interactive=False)
        return domains


def select_domains(Model, message: str = None):
    """
    Shows up a selectiondialog for domains in AxisVM and returns the selected
    domains if succesful.
    """
    if message is None:
        message = 'Select one or more domains!'
    Model.StartModalSelection(message, Model.tlb.lbTrue, 'seltDomains')
    return get_selected_domains(Model, interactive=False)


def get_selected_domains(Model, interactive=False):
    """
    Returns a list of domains. The result is always iterable,
    even if it contains only one item.
    """
    try:
        dIDs = Model.Domains.GetSelectedItemIds()[0]
        return get_domains(Model, domainIDs=dIDs)
    except Exception:
        if interactive:
            return select_domains(Model,
                                  message='Select one or more domains!')
        else:
            return None


def get_selected_domainIDs(Model, interactive=False):
    """
    Returns a list of domainIDs. The result is always iterable,
    even if it contains only one item.
    """
    try:
        return Model.Domains.GetSelectedItemIds()[0]
    except Exception:
        domains = get_selected_domains(Model, interactive)
        if domains is None:
            return None
        dUIDs = [d.UID for d in domains]
        dIDs = [Model.Domains.IndexOfUID[dUID] for dUID in dUIDs]
        return dIDs


def get_surfaces_of_domains(Model, *args, flatten=False,
                            as_dict=False, **kwargs):
    """
    Returns a list of surfaces belonging to the    specified domains.
    If there are no domains specified, a selection dialog shows up in AxisVM.
    If as_dict = True, result is provided as a dictionary, where domainIDs
    are mapped to lists of surfaces.
    """
    domains = get_domains(Model, *args, **kwargs)
    assert domains is not None, "Invalid specification of domains!"
    if not as_dict:
        surfaces = []
        for domain in domains:
            if domain.MeshExists:
                IDs = domain.MeshSurfaceIds
                if flatten:
                    surfaces.extend([Model.Surfaces.Item(ID) for ID in IDs])
                else:
                    surfaces.append([Model.Surfaces.Item(ID) for ID in IDs])
        return surfaces
    else:
        dID_to_sIDs = {}
        for domain in domains:
            if domain.MeshExists:
                dID = Model.Domains.IndexOfUID[domain.UID]
                IDs = domain.MeshSurfaceIds
                dID_to_sIDs[dID] = [Model.Surfaces.Item(ID) for ID in IDs]
        return dID_to_sIDs


def get_surfaces_of_selected_domains(Model, flatten=False,
                                     empty=True, as_dict=False):
    """
    Returns a list of surfaces belonging to the    selected domains in AxisVM.
    If there are no domains selected, a selection dialog shows up in AxisVM.
    If empty is True, all domains of the model are deselected before before
    showing the selection dialog.
    """
    if empty:
        Model.SelectAll(Model.tlb.lbFalse)
    return get_surfaces_of_domains(Model, flatten=flatten, as_dict=as_dict)


def set_custom_stiffness_matrix(Model, *args,
                                A: np.ndarray = None, B: np.ndarray = None,
                                D: np.ndarray = None, S: np.ndarray = None,
                                ABDS: np.ndarray = None, **kwargs):
    """
    Set a custom stiffness matrix to the specified domains. For the details
    of specification of domains see the documentation of function :
    get_domains. Stiffness matrix can be specified by either providing ABDS
    or the submatrices. Specification of the matrix B is optional, its
    abscence means no plate-membrane coupling.
    """
    domains = get_domains(Model, *args, **kwargs)
    assert domains is not None, "Invalid specification of domains!"
    RMatrix2x2 = Model.tlb.RMatrix2x2
    RMatrix3x3 = Model.tlb.RMatrix3x3
    try:
        if ABDS is not None:
            A = RMatrix3x3(*ABDS[0:3, 0:3].flatten())
            B = RMatrix3x3(*ABDS[0:3, 3:6].flatten())
            D = RMatrix3x3(*ABDS[3:6, 3:6].flatten())
            S = RMatrix2x2(*ABDS[6:8, 6:8].flatten())
        else:
            # membrane
            assert A is not None, "Matrix A must be provided!"
            A = RMatrix3x3(*A.flatten())
            # membrane-plate coupling
            if B is None:
                B = np.zeros(9)
            B = RMatrix3x3(*B.flatten())
            # bending
            assert D is not None, "Matrix D must be provided!"
            D = RMatrix3x3(*D.flatten())
            # shear
            assert S is not None, "Matrix S must be provided!"
            S = RMatrix2x2(*S.flatten())

        Model.BeginUpdate()
        for d in domains:
            d.SetCustomStiffnessMatrix(A, B, D, S)
        Model.EndUpdate()
    except Exception:
        raise 'Assignment failed!'
