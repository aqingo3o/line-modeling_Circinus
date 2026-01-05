''' # .inp file form template
.inp file 是一個各行數是固定格式的東西, 所以做了這樣一個格式參考
ref: RADEX off-line version, section"Running Radex"
link: https://sronpersonalpages.nl/~vdtak/radex/index.shtml

This piece ofcode is aim to make sure if .inp file can be create and write in the data to do the modeling.
This can also serve as a template of .inp file  when writing other RADEX-related script.
'''

import os

# open() 可以開啟不存在的東西？ 就像 mkdir -p 一樣嗎？
file = open('test.inp', 'w') # FLAG'w': 允許寫入
# ---------------------- 以下按照格式寫入，尾巴要加換行符 ----------------------
file.write('hco+.dat\n')  # 是什麼 mole 就填什麼啊
file.write('test.out\n')
file.write('50 500'+'\n') # output frequency range (GHz, 0 0 means unlimited)
file.write('20.0\n')      # kinetic temperature (K)
file.write('1\n')         # number of collision partners (或許通常就一個？)
file.write('H2\n')        # first collision partner
file.write('1e4\n')       # density of first collision partner (cm^-3)
'''# 沒有第二個撞擊夥伴的話可以不寫這兩行
file.write('e\n')         # second collision partner
file.write('1\n')         # density of second collision partner (cm^-3)
'''
file.write('2.73'+'\n')   # temperature of background radiation (K, 好像都設 2.73)
file.write('1e13\n')      # molecular column density (cm^-2)
file.write('1\n')         # line width (km/s)
file.write('0\n')         # run another calculation (or not, y/n = 1/0)
file.close()              # aftercare

'''# 以上應等價於:
with open('tt.inp', 'w') as file: # 但是和 with 的用法不太熟
    file.write()
'''