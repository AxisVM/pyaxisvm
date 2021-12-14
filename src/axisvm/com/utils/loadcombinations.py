# -*- coding: utf-8 -*-
from dewloosh.core.tools import issequence


def get_loadcombinations(Model = None, *args, **kwargs):
    as_dict = kwargs.pop('as_dict', False)
    kwargs['as_dict'] = False
    IDs = get_loadcombinationIDs(Model, *args, **kwargs)
    assert issequence(IDs)

    key = kwargs.pop('key', 'ID')
    if key == 'ID':
        ID_to_key = {ID: ID for ID in IDs}
    elif key == 'name':
        ID_to_key = get_names_of_loadcombinations_by_ID(Model,
                                                        loadcombinationIDs=IDs, as_dict=True)

    res = []
    for ID in IDs:
        factors, loadcaseIDs, _ = Model.LoadCombinations.GetCombination(ID)
        res.append((factors, loadcaseIDs))
    if as_dict:
        dres = {}
        for ID, (factors, loadcaseIDs) in zip(IDs, res):
            dres[ID_to_key[ID]] = {
                'factors': factors, 'loadcaseIDs': loadcaseIDs}
        return dres
    else:
        return res


def get_ALL_loadcombinations(Model = None, *args, **kwargs):
    return get_loadcombinations(Model, 'allloadcombinations', **kwargs)


def get_loadcombinationIDs(Model = None, *args, **kwargs):
    """
        Returns loadcombinationIDs for specified load combinations. It can be used to turn \
    an arbitrary specification of loadcombinationIDs in an embedded situation \
    into an iterable of loadcombinationIDs. For that reason it includes \
    trivial keys. Individual items can be specified, but the result is always iterable.
        ---
    Possible args:
        'allloadcombinations' : return a list containing all loadcaseIDs in the model
        Possible keys and values
                loadcombinationID : a single loadcombinationID, returns [loadcombinationID] (trivial)
                loadcombinationIDs : a list of loadcombinationIDs, returns loadcombinationIDs (trivial)
                loadcombinationname : str, name of a single loadcombination
                loadcombinationnames : [str], a list of names of multiple loadcombinations
        """
    try:
        IDs = None
        if 'allloadcombinations' in args:
            IDs = [i for i in range(1, Model.LoadCombinations.Count+1)]
        elif 'loadcombinationID' in kwargs:
            IDs = [kwargs.pop('loadcombinationID')]
        elif 'loadcombinationIDs' in kwargs:
            IDs = kwargs.pop('loadcombinationIDs')
        elif 'loadcombinationname' in kwargs:
            IDs = get_IDs_of_loadcombinations_by_name(Model, **kwargs)
        elif 'loadcombinationnames' in kwargs:
            IDs = get_IDs_of_loadcombinations_by_name(Model, **kwargs)
        return IDs
    except:
        raise "Ivalid specification of loadcombinations!"


def get_names_of_loadcombinations_by_ID(Model = None, *args, **kwargs):
    IDs = get_loadcombinationIDs(Model, *args, **kwargs)
    if kwargs.get('as_dict', False):
        return {ID: Model.LoadCombinations.Name[ID] for ID in IDs}
    else:
        return [Model.LoadCombinations.Name[ID] for ID in IDs]


def get_names_of_ALL_loadcombinations(Model = None, as_dict=False):
    return get_names_of_loadcombinations_by_ID(Model, 'allloadcombinations', as_dict=as_dict)


def get_IDs_of_loadcombinations_by_name(Model = None, **kwargs):
    try:
        allnames = get_names_of_ALL_loadcombinations(Model)
        name_to_ID = {name: ID for ID, name in enumerate(allnames)}
        if 'loadcombinationname' in kwargs:
            names = [kwargs.pop('loadcombinationname')]
        elif 'loadcombinationnames' in kwargs:
            names = kwargs.pop('loadcombinationnames')
        if kwargs.get('as_dict', False):
            return {name: name_to_ID[name] for name in names}
        else:
            return [name_to_ID[name] for name in names]
    except Exception:
        raise "Ivalid specification of loadcombinations!"
