# -*- coding: utf-8 -*-


def get_loadcaseIDs(Model = None, *args, **kwargs):
    """
        Returns loadcaseIDs for specified load cases. It can be used to turn \
    an arbitrary specification of loadcaseIDs in an embedded situation \
    into an iterable of loadcaseIDs. For that reason it includes \
    trivial keys. Individual items can be specified, but the result is always iterable. 
        ---
    Possible args:
        'allloadcases' : return a list containing all loadcaseIDs in the model
        Possible keys and values
                loadcaseID : a single loadcaseID, returns [loadcaseID] (trivial)
                loadcaseIDs : a list of loadcaseIDs, returns loadcaseIDs (trivial)
                loadcasename : str, name of a single loadcase
                loadcasenames : [str], a list of names of multiple loadcases
        """
    try:
        IDs = None
        if 'allloadcases' in args:
            IDs = [i for i in range(1, Model.LoadCases.Count+1)]
        elif 'loadcaseID' in kwargs:
            IDs = [kwargs.pop('loadcaseID')]
        elif 'loadcaseIDs' in kwargs:
            IDs = kwargs.pop('loadcaseIDs')
        elif 'loadcasename' in kwargs:
            IDs = get_IDs_of_loadcases_by_name(Model, **kwargs)
        elif 'loadcasenames' in kwargs:
            IDs = get_IDs_of_loadcases_by_name(Model, **kwargs)
        return IDs
    except:
        raise "Ivalid specification of loadcases!"


def get_names_of_loadcases_by_ID(Model, *args, **kwargs):
    IDs = get_loadcaseIDs(Model, *args, **kwargs)
    if kwargs.get('as_dict', False):
        return {ID: Model.LoadCases.Name[ID] for ID in IDs}
    else:
        return [Model.LoadCases.Name[ID] for ID in IDs]


def get_names_of_ALL_loadcases(Model, as_dict=False):
    return get_names_of_loadcases_by_ID(Model, 'allloadcases', as_dict=as_dict)


def get_IDs_of_loadcases_by_name(Model, **kwargs):
    try:
        allnames = get_names_of_ALL_loadcases(Model)
        def get_ID(name): return allnames.index(name)
        if 'loadcasename' in kwargs:
            names = [kwargs.pop('loadcasename')]
        elif 'loadcasenames' in kwargs:
            names = kwargs.pop('loadcasenames')
        if kwargs.get('as_dict', False):
            return {name: get_ID(name) for name in names}
        else:
            return [get_ID(name) for name in names]
    except Exception:
        raise "Ivalid specification of loadcases!"
