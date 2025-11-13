# for practiceee

import pyradex
import numpy as np

# 建立一個假 pixel 陣列：4 pixels，各自有不同條件
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
        datapath='/path/to/pyradex/data'  # 要改成你的路徑
    )
    output = R()
    results.append(output['T_B'][0])  # 取出第一條線的亮度溫度
