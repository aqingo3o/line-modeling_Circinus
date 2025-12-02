'''
因為就是我想要試試看傳入東西
但我沒有 inp 檔
所以就想說做一個
反正之後也是需要做的吧

巨量的參考 Eltha 女士的碼

然後我就先做到能寫出 .inp 為止
'''

import os
import numpy as np
from joblib import Parallel, delayed # 反正是用不到 feifei 身上, 在 LabMachine 上有裝了哈哈屁眼
import time


# 直接看 write input 啊
model = '5d_coarse2' # 粗略的模型的意思?
molecule_0 = 'co'
linewidth = 15 # (km/s)?
round_dens = 1
round_temp = 1 # 這些是什麼？
num_cores = 20 # joblib 的東西, 就是可以用的 cpu 的核心的數量
# 源碼裡面的一坨東西有些沒有貼在這裡

Nco = np.arange(15., 20.1, 0.2) # column density
Tkin = np.arange(1., 2.8, 0.1)  # kinetic 
nH2 = np.arange(2., 5.1, 0.2)   # h2 的密度或是之類的東西
X_13co = np.arange(10, 205, 10) # X 應該是 conversion factor?
X_c18o = np.arange(2, 21, 1)    # 對這樣是 5d, 第六個維度應該是 beam filling factor (\Phi)
'''
那和我做得很像啊！我上次做的那些東西
欸但他有 4E6 種組合，超你嗎多，大概要從今天開始跑
'''

# Pre-processing
incr_dens = round(Nco[1] - Nco[0], 1) # round() 會取四捨五入
incr_temp = round(Tkin[1] - Tkin[0], 1)
'''
# incr 是 incresement(增量)
incr 是上面那個 np.arange 的步長，稍微取一點四捨五入
可能用這種算法比較節省變數吧

# round() 可以對整個陣列作用
換成低效的寫法就是
results = []
for x in listt:
    results.append(round(x))
'''

# dex 是 10 的指數的意思，這邊是在產生 10^n, n 用 np.arange() 產生
co_dex = np.round(10**np.arange(0., 1., incr_dens), 4)
Tk_dex = np.round(10**np.arange(0.,1.,incr_temp), 4)

# shaoe v.s. len()
num_Nco = Nco.shape[0]
num_Tk = Tkin.shape[0]
num_nH2 = nH2.shape[0]
'''
num_ 是建立的 grid 的邊長，可以這麼說，像是 len() 但可能 numpy 要用 shape 吧？
欸沒有， len() works, too
# 但可能是本人很喜歡 len()
我也使寫過
for i in range(len(listt)):
    print(listt[i])
這種屁股程式的人呢
'''

# 不知道為什麼有倒數
factors_13co = 1./ X_13co  
factors_c18o = 1./ X_c18o
cycle_dens = co_dex.shape[0] # 也許是循環的次數，但依然是 len()
cycle_temp = Tk_dex.shape[0]
num_X12to13 = X_13co.shape[0]
num_X13to18 = X_c18o.shape[0]
diff_Tk = Tkin[1] - Tkin[0] # 為什麼是這個

# ------------------------------------------------------------------------------------ #
# functionnnnn
def write_inputs_m0(i,j,k): # 用 i, j, k 解碼真的是頭腦十分清楚了
    powi = str(i//cycle_temp + int(Tkin[0]))
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    powj = j//cycle_dens + int(nH2[0])
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    prei = str(Tk_dex[i%cycle_temp])
    prej = str(co_dex[j%cycle_dens])
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    prek = str(co_dex[k%cycle_dens])
    codex = str(round(co_dex[k%cycle_dens], round_dens))
    # .inp 是要輸進 RADEX 的材料
    file = open('input_'+model+'_'+molecule_0+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'.inp', 'w')
    file.write(molecule_0+'.dat\n') # 寫入的是字面意思上的 'mole0.dat'
    file.write('output_'+model+'_'+molecule_0+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'.out\n')
    file.write('100'+' '+'400'+'\n')
    file.write(prei+'e'+powi+'\n')
    file.write('1\n')
    file.write('H2\n')
    file.write(prej+'e'+n_h2+'\n')
    file.write('2.73'+'\n')
    file.write(prek+'e'+N_co+'\n')
    file.write(str(linewidth)+'\n')
    file.write('0\n')
    file.close()  


"""
def run_radex_m0(i,j,k):
    powj = j//cycle_dens + int(nH2[0])
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    codex = str(round(co_dex[k%cycle_dens], round_dens))
    run = os.system('radex < input_'+model+'_'+molecule_0+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'.inp') # 直接進行一個大傳入
    return run

def radex_flux(i,j,k,m,n):
    powj = j//cycle_dens + int(nH2[0])
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))   
    x13co = str(X_13co[m])
    xc18o = str(X_c18o[n])
    codex = str(round(co_dex[k%cycle_dens], round_dens))
    
    # .out 的話是 radex 的產物，下面有一個黨名後綴小整理
    outfile_0 = 'output_'+model+'_'+molecule_0+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'.out'
  
    # Extract reliable flux predictions (avoid those with convergence issues)
    if np.loadtxt(outfile_0,skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_0 = np.full((3,), np.nan)
    else:
        flux_0 = np.genfromtxt(outfile_0, skip_header=13)[:, 11]
    
    return k, i, j, m, n, flux_0
"""


# 因為寫成一行我就是他媽讀不出來, 所以進行了一些寫成兩坨的動作
print('Writing input files...')
task_m0 = (
    delayed(write_inputs_m0)(i, j, k)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )
Parallel(n_jobs=num_cores)(task_m0)

"""
print('Running RADEX with inputs...')
task_m0 = ( # 直接進行一個變數循環利用
    delayed(run_radex_m0)(i, j, k)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )
Parallel(n_jobs=num_cores, verbose=5)(task_m0)  

print('Constructing flux model grids...') # 不知道是不是有寫一些別的東西進去
result_m0 = (
    delayed(radex_flux)(i,j,k,m,n)
    for n in range(0,num_X13to18)
    for m in range(0,num_X12to13)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )
results = Parallel(n_jobs=num_cores, verbose=5)(result_m0)
"""

