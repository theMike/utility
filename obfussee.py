#!/bin/python

import string
import random
import zlib
import base64
import sys

"""
  Q & D text obfuscation and unobfuscation 
"""

def padit(minrange=6, maxrange=6, chars=string.ascii_uppercase+string.digits):
  rndsize = random.randint(minrange,maxrange)
  return str(rndsize)+''.join(random.choice(chars) for _ in range(rndsize))

def obfuscateit(targetpad,targetstring):
  workingstr = targetpad+":"+targetstring
  endstring = base64.b64encode(zlib.compress(workingstr))
  return endstring

def illumit(targetstring):
  expandedstr=zlib.decompress(base64.b64decode(targetstring))
  saltindx = expandedstr.split(':',1)
  return saltindx[1]
  

if __name__ == '__main__':

  if sys.argv[1] == '1':
    print obfuscateit(padit(minrange=2),''.join(sys.argv[2:]))
  
  if sys.argv[1] == '2':   
    print illumit(''.join(sys.argv[2:]))
  


