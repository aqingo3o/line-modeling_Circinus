# Try to use pyradex with hand-made fake data
'''
先做了一個三維的 physical condition grid, 
然後送進radex(via pyradex) 裡面進行運算，得到 brightness temperature.
並且把 brightnessTemp 畫成一個 map (像是mom0那樣的, 但非常少格)
'''


import pyradex
import numpy as np
import matplotlib.pyplot as plt
datapath = "/home/aqing/pyradex/pyradex_data/"

# (fake) physical condition array(4種值)
# 這邊應該是要製作一整個範圍，但是簡單一點先算4個值就好)
temp = [10, 20, 40, 80]           # kineticTemp, K
dens = [1e3, 1e4, 1e5, 1e6]       # h2(collasper)'s denity, cm^-3
column = [1e13, 1e14, 1e15, 1e16] # column density, cm^-2

pixelFlux = []
for T, n, N in zip(temp, dens, column): # zip() 有點類似矩陣製造器, 就是將三個串列對應起來
    R = pyradex.Radex(                  # 用到 pyradex 的地方
        species='co',
        collider_densities={'H2': n},
        column=N,
        temperature=T,
        datapath=datapath
    )
    output = R()
    pixelFlux.append(output['T_B'][0])    # brightness Temp, [0] -> (J=1-0)
    
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

# ------------------------------ COMMENTs ------------------------------ #
''' ### 這邊主要的問題是他媽的我不習慣使用物件
為什麼 這樣可以
```
output = R()
results.append(output['T_B'][0])
```

這樣不行 (object is not subscriptable)
```
print(R['T_B'])
```
喔喔就是一定要裝載一個東西裡面才可以導出的意思？  
好我等下還活著我就去看物件導向
'''

''' ### 久遠前的評論
感覺很有希望，除了 pyradx 還找到了本家的論文  
雖然說光用看得就要懂真的太抽象，但是很後面的附件有提供倆腳本？  
雖然說 2007 的 python 該不會是 python2.7 吧  
但論文裡設置變數的部分依然值得參考
'''