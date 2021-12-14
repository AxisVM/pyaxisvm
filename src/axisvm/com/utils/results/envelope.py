from pyoneer.interface.axisvm import AxisVMModel

def get_envelopeIDs(Model : AxisVMModel,*args,**kwargs):
    eIDs = None
    try:
        if 'envelopename' in kwargs:
            eIDs =  [index_of_envelope(Model, envelope = kwargs.pop('envelopename'))]
        elif 'envelopenames' in kwargs:
            eIDs =  [index_of_envelope(Model, envelope = n) for n in kwargs.pop('envelopenames')]
        elif 'envelopeID' in kwargs:
            eIDs = [kwargs.pop('envelopeID')]
        elif 'envelopeIDs' in kwargs:
            eIDs = [kwargs.pop('envelopeIDs')]
        elif 'envelopeUID' in kwargs:
            eIDs = [Model.Envelopes.IndexOfUID(kwargs.pop('envelopeUID'))]
        elif 'envelopeUIDs' in kwargs:
            eIDs = [Model.Envelopes.IndexOfUID(UID) for UID in kwargs.pop('envelopeUIDs')] 
    except:
        raise "Ivalid specification of nodes!"
    finally:
        return eIDs

def index_of_envelope(Model : AxisVMModel, envelope : str):
    envelope = envelope.lower()
    if envelope in ['all uls','all uls ','all_uls','uls all','uls all ','uls_all']:
        envelope = 'All ULS '
    return Model.Envelopes.IndexOfName(envelope), envelope

def possible_envelope_names(Model : AxisVMModel):
    return [Model.Envelopes.Name[i] for i in range(Model.Envelopes.Count)]