# for practiceee

import pyradex
import numpy as np
from astropy.io import fits # maybe matplotlib can handle it...?
import matplotlib.pyplot as plt
datapath = "/home/aqing/pyradex/pyradex_data/"


# phisical condition set by ME
temp = [10, 20, 40, 80]  # K
dens = [1e3, 1e4, 1e5, 1e6] # collider_densities, cm^-3
column = [1e13, 1e14, 1e15, 1e16] # column density, cm^-2

# radexxxxx
pixelFlux = []
for T, n, N in zip(temp, dens, column):
    R = pyradex.Radex(
        species='co',
        collider_densities={'H2': n},
        column=N,
        temperature=T,
        datapath=datapath
    )
    output = R()
    pixelFlux.append(output['T_B'][0])  # brightness Temp, [0] -> (J=1-0)


print('brightness temp of each pixel:')
print(pixelFlux)

'''
因為他的計算速度太牛逼了以至於我沒注意到它已經解了輻射傳輸方程
'''

# to make a 'map'
map_data = np.array(pixelFlux).reshape(2, 2) # make 2d data

figg = plt.figure(figsize=(10, 8))
fake_map = figg.add_subplot() # one of the subplots, 此處應有 projection
fake_map.set_title('Fake map (T_B)')

obj = fake_map.imshow(map_data) # imshow() 好文明
# mpl 的物件會不會有點太它媽多了
figg.colorbar(obj)


plt.show()