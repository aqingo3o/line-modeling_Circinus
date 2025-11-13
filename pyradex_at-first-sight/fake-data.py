# for practiceee

import pyradex
import numpy as np
datapath = "/home/aqing/pyradex/pyradex_data/"


# fake pixel arrayyyy
temp = [10, 20, 40, 80]  # K
dens = [1e3, 1e4, 1e5, 1e6] # cm^-3
column = [1e13, 1e14, 1e15, 1e16] # cm^-2

results = []
for T, n, N in zip(temp, dens, column):
    R = pyradex.Radex(
        species='co',
        collider_densities={'H2': n},
        column=N,
        temperature=T,
        datapath=datapath
    )
    output = R()
    results.append(output['T_B'][0])  # maybe brightness temp?


print('can be here')
print(results)

'''aqing 20151113
okayy, the result can be printed so the code can work
but i am not sure about the unit i've used
and the data structure of the object "R"

and i have to make sure how zip() actually work

(for next time ) i want to use the data from my fits
pick out some pixels and di the "modeling" 
'''