import pyradex
import numpy as np

datapath = "/home/aqing/pyradex/pyradex_data/"

R_co = pyradex.Radex(collider_densities={'oH2':900,'pH2':100},
                  column=1e16, species='co', temperature=20,
                  datapath=datapath
                )

Tlvg = R_co(escapeProbGeom='lvg')
Tslab = R_co(escapeProbGeom='slab')
Tsphere = R_co(escapeProbGeom='sphere')
Tlvg[:3].pprint()
Tslab[:3].pprint()
Tsphere[:3].pprint()
print()
print('---- HCO+ what everrrr ----')
print()

# not the real para
R_hco = pyradex.Radex(collider_densities={'oH2':900,'pH2':100},
                  column=1e16, species='hco+', temperature=20,
                  datapath=datapath
                )

Tlvg = R_hco(escapeProbGeom='lvg')
Tslab = R_hco(escapeProbGeom='slab')
Tsphere = R_hco(escapeProbGeom='sphere')
Tlvg[:3].pprint()
Tslab[:3].pprint()
Tsphere[:3].pprint()

'''
though these code is not the "Modeling" part 
, here is something worth warning:
the object R_xx because something i may seen from k's repo, 
it could only be occupied by 1 set of data.

so if need to do multi-modeling (any work that call the objects)
u have to work like this: 
(O): define obj -> print(end the usage of the first obj)
-> define new obj -> print (end the usage of the second obj)

(X): define all the obj at the same blockk and do the ""pprint"" in another block

i don't know y but just follow the instruction :)
'''
