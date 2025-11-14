import pyradex
import numpy as np

datapath = "/home/aqing/Documents/pyradexxxxx"
#datapath = "/home/pyradex/pyradex_data/"

R = pyradex.Radex(collider_densities={'oH2':900,'pH2':100},
                  column=1e16, species='co', temperature=20,
                  datapath=datapath
)

Tlvg = R(escapeProbGeom='lvg')
Tslab = R(escapeProbGeom='slab')
Tsphere = R(escapeProbGeom='sphere')
Tlvg[:3].pprint()
Tslab[:3].pprint()
Tsphere[:3].pprint()
