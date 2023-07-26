# Author: Izaak Neutelings (July 2023)
import os, shutil

def ensureDirectory(*dirnames,**kwargs):
  """Make directory if it does not exist.
  If more than one path is given, it is joined into one."""
  dirname   = os.path.join(*dirnames)
  empty     = kwargs.get('empty', False)
  verbosity = kwargs.get('verb',  0    )
  if not dirname:
    pass
  elif not os.path.exists(dirname):
    os.makedirs(dirname)
    if verbosity>=1:
      print(">>> Made directory %r"%(dirname))
    if not os.path.exists(dirname):
      print(">>> Failed to make directory %r"%(dirname))
  elif empty:
    for filename in os.listdir(dirname):
      filepath = os.path.join(dirname,filename)
      if os.path.isfile(filepath) or os.path.islink(filepath):
        os.unlink(filepath)
      elif os.path.isdir(filepath):
        shutil.rmtree(filepath)
  return dirname

