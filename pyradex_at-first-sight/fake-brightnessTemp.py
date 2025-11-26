# for practiceee
# 那我它媽一開始直接設 brightness temperature 就他媽好了啊

import pyradex
import numpy as np
import matplotlib.pyplot as plt
datapath = "/home/aqing/pyradex/pyradex_data/"

# T_B set by me
'''
i said i want to use data(some) from the real data
but im still not sure the trandform code work well
因為我是瓠瓜啦哈哈py
'''
bTemp = np.array([0.0085, 0.51, 2.5, 0.11]).reshape(2, 2) # make 2d data
print(bTemp)

# Show the map
figg = plt.figure(figsize=(10, 8))
fake_map = figg.add_subplot() # one of the subplots, 此處應有 projection
fake_map.set_title('Fake map (T_B)')

obj = fake_map.imshow(bTemp) # imshow() 好文明
# mpl 的物件會不會有點太它媽多了
figg.colorbar(obj)


'''
他媽的反推的方法就是算爆然後找最小差距喔真的假的
難怪要 chi-square fitting

'''


# radexxxxx
bTemp_fitting = []
temp = np.linspace(10, 100, num=20) # min>0, no equal, ValueError: Must have kinetic temperature > 0 and < 10^4 K
dens = np.linspace(10, 1e10, num=20)
column = np.linspace(1e10, 1e20, num=20)

for T, n, N in zip(temp, dens, column):
    R = pyradex.Radex(
        species='co',
        collider_densities={'H2': n},
        column=N,
        temperature=T,
        datapath=datapath
    )
    output = R()
    bTemp_fitting.append(output['T_B'][0])  # brightness Temp, [0] -> (J=1-0)


print('brightness temp of each pixel:')
print(bTemp_fitting)

plt.show()
'''
我覺得寫到這邊他媽的我明天應該接的下去
'''