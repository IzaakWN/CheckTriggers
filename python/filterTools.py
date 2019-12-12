# Author: Izaak Neutelings (November, 2019)
# Description: Tools to check triggers and their filters in nanoAOD
# Source:
#   https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py
#   https://cms-nanoaod-integration.web.cern.ch/integration/master-106X/mc106X_doc.html#TrigObj
import os, sys, yaml #, json
import numpy as np
objectids   = { 'Electron': 11, 'Muon': 13, 'Tau': 15, } 
collections = { 1: 'Jet', 6: 'FatJet', 2: 'MET', 3: 'HT', 4: 'MHT',
                11: 'Electron', 13: 'Muon', 15: 'Tau', 22: 'Photon', } 



def loadTriggersFromJSON(filename,verbose=False):
    """Help function to load trigger path and object information from a JSON file.
    The format is as follows:
      'year'
         -> year
      'filterbits'
         -> object type ('Electron', 'Muon', 'Tau', ...)
           -> shorthand for filters patterns in nanoAOD
             -> bits (powers of 2)
      'hltcombs'
         -> data type ('data' or 'mc')
           -> tau trigger type (e.g. 'etau', 'mutau', 'ditau', 'SingleMuon', ...)
             -> list of recommended HLT paths
      'hltpaths'
         -> HLT path ("HLT_*")
           -> 'runrange':     in case this path was only available in some data runs (optional)
           -> 'filter':       last filter associated with this trigger path ("hlt*")
           -> object type ('Electron', 'Muon', 'Tau', ...)
             -> 'ptmin':      offline cut on pt 
             -> 'etamax':     offline cut on eta (optional)
             -> 'filterbits': list of shorthands for filter patterns
    """
    if verbose:
      print ">>> loadTriggersFromJSON: loading '%s'"%(filename)
    filters         = [ ]
    filterpairs     = [ ]
    bitdict         = { }
    triggers        = { }
    
    # OPEN JSON
    with open(filename,'r') as file:
      #data = json.load(file)
      data = yaml.safe_load(file)
    for key in ['filterbits','hltpaths']:
      assert key in data, "Did not find '%s' key in JSON file '%s'"%(key,filename)
    objects = data['filterbits'].keys() # e.g. ['ele','mu','tau']
    
    # LOAD FILTER BIT DEFINITIONS
    for obj in objects:
      id = objectids[obj]
      bitdict[obj] = { }
      for filterbit, bit in data['filterbits'][obj].iteritems():
        bitdict[obj][filterbit] = bit
        filter = TriggerFilter(id,filterbit,bit=bit)
        filters.append(filter)
    
    # COMBINATIONS OF HLT PATHS
    if 'hltcombs' in data:
      for datatype in data['hltcombs']:
        triggers[datatype] = { }
        for channel, hltcomb in data['hltcombs'][datatype].iteritems():
          # TODO: load run range from data['hltpaths']
          triggers[datatype][channel] = Trigger(hltcomb)
    
    # HLT PATHS with corresponding filter bits, pt, eta cut
    for hltpath, trigdict in data['hltpaths'].iteritems():
      runrange     = trigdict.get('runrange',None)
      hltfilters   = [ ]
      for obj in objects:
        if obj not in trigdict: continue
        id         = objectids[obj]
        ptmin      = trigdict[obj].get('ptmin', 0.0)
        etamax     = trigdict[obj].get('etamax',6.0)
        filterbits = trigdict[obj]['filterbits']
        filter     = TriggerFilter(id,filterbits,hltpath,ptmin,etamax,runrange=runrange)
        filter.setbits(bitdict[obj])
        #if len(filterbits)==1 and any(id==f.id and filterbits[0]==f.name for f in filters):
        #  continue # avoid duplicates
        filters.append(filter)
        hltfilters.append(filter)
      assert len(hltfilters)>0, "Did not find any valid filters for '%s' in %s"%(hltpath,trigdict)
      if len(hltfilters)>1:
        filterpair   = FilterPair(hltpath,*hltfilters)
        filterpairs.append(filterpair)
    filters.sort(key=lambda f: (f.id,-int(f.name in data['filterbits'][f.collection]),f.trigpath,f.bits,f.ptmin))
    
    # PRINT
    if verbose:
      if 'hltcombs' in data:
        for datatype in data['hltcombs']:
          print ">>> %s trigger requirements:"%datatype
          for channel, hltcombs in data['hltcombs'][datatype].iteritems():
            print ">>> %7s:  "%channel + ' || '.join(hltcombs)
      print ">>> hlt with pair of filters:"
      for pair in filterpairs:
        print ">>>   %s (%s)"%(pair.name,pair.channel)
        print ">>>     %3s leg: %s"%(pair.filter1.collection,pair.filter1.name)
        print ">>>     %3s leg: %s"%(pair.filter2.collection,pair.filter2.name)
      for obj, id in objectids.iteritems():
        print ">>> %s filter bits:"%obj
        for filter in filters:
          if filter.id!=id: continue
          path = filter.trigpath
          print ">>> %6d: %s"%(filter.bits,filter.name)+(" (%s)"%path if path else "")
    
    return filters, filterpairs, triggers
    


class Trigger:
    """Container class for trigger."""
    def __init__(self,paths,**kwargs):
      if isinstance(paths,str): paths = [paths]
      self.name  = ' || '.join(paths)
      self.paths = paths
      if paths:
        pathcomb   =  "e."+" or e.".join(paths)
        exec ("self.fired = lambda e: "+pathcomb) in locals()
        #self.fired = lambda e: any(e.p for p in self.paths)
      else:
        self.fired = lambda e: True
    


class TriggerFilter:
    """Container class for trigger filter(s)."""
    
    def __init__(self,id,filters,trigpaths=[],ptmin=0.0,etamax=6.0,**kwargs):
        if isinstance(filters,str):   filters   = [filters]
        if isinstance(trigpaths,str): trigpaths = [trigpaths]
        self.filters    = filters
        self.name       = '_'.join(filters)
        self.trigpath   = ' || '.join(trigpaths)
        self.trigpaths  = trigpaths
        self.trigger    = Trigger(trigpaths)
        self.id         = id
        self.collection = collections.get(id,None) # NanoAOD object
        self.ptmin      = ptmin
        self.etamax     = etamax
        self.bits       = kwargs.get('bit',0)
        self.runrange   = kwargs.get('runrange',None)
        self.channel    = self.collection
        self.channel    = ('etau'  if any('HLT_Ele' in f for f in trigpaths) else
                           'mutau' if any('HLT_IsoMu' in f for f in trigpaths) else
                           'ditau' if any('HLT_Double' in f for f in trigpaths) else
                           self.channel) if any('PFTau' in f for f in filters) else (
                           'Double'+self.channel if any('Double' in f for f in trigpaths) else 'Single'+self.channel)
        self.channel    = kwargs.get('channel',self.channel)
        if 'bitdict' in kwargs:
          self.setbits(kwargs['bitdict'])
        
    def __repr__(self):
        """Returns string representation of TriggerFilter object."""
        return '<%s("%s",%s) at %s>'%(self.__class__.__name__,self.name,self.bits,hex(id(self)))
        
    def setbits(self,bitdict):
        """Compute bits for all filters using some given filter bit dictionary."""
        self.bits = 0
        for filter in self.filters:
          assert filter in bitdict, "Could not find filter '%s' in bitdict = %s"%(filter,bitdict)
          self.bits += bitdict[filter] #.get(filter,0)
        return self.bits
        
    def hasbits(self,bits):
        """Check if a given set of bits contain this filter's set of bits,
        using the bitwise 'and' operator, '&'."""
        return self.bits & bits == self.bits
        
    def match(self,trigObj,recoObj,dR=0.2):
        #if isinstance(recoObj,'TrigObj'): trigObj, recoObj = recoObj, trigObj
        return trigObj.DeltaR(recoObj)<dR and recoObj.pt>self.pt_min and abs(recoObj).eta<self.eta_max
    


class FilterPair:
    """Container class for filters of triggers with two objects (e.g. mutau triggers)."""
    def __init__(self,trigpath,*filters,**kwargs):
        filter1, filter2 = filters[:2] if len(filters)>=2 else (filters[0],filters[0])
        if filter1.id>filter2.id: filter1, filter2 = filter2, filter1
        self.name     = trigpath
        self.trigpath = trigpath
        self.trigger  = Trigger(trigpath)
        self.filter1  = filter1
        self.filter2  = filter2
        self.runrange = kwargs.get('runrange',None)
        self.channel  = ('etau'  if filter1.id==11 else
                         'mutau' if filter1.id==13 else
                         'ditau' if filter1.id==15 else None) if filter2.id==15 else (
                         'Double'+self.filter1.collection if filter1.id==filter2.id else "")
        self.channel  = kwargs.get('channel',self.channel)
    


#def getBits(x):
#  """Decompose integer into list of bits (powers of 2)."""
#  powers = [ ]
#  i = 1
#  while i <= x:
#    if i & x: powers.append(i)
#    i <<= 1
#  return powers
  

