'''radex-pipelind_runRadex.py
This script is intended to serve as a smaller-scale workflow version of `radex_pipeline.py`, from Eltha.

準確來說是我改過的 radex-pipeline_lite.py 的中間1/3部分
因為一次全部跑完的話有點懸, 所以就分成三部分了。
'''
# Module
import numpy as np
import os
import time
from joblib import Parallel, delayed
from pathlib import Path # for finding file, path

start_time = time.time()

# Path
projectRoot = Path(__file__).resolve().parents[1] # .../line-modeling_Circinus, no slash at the end
dataPath = f'{projectRoot}/data/radex_io'
productPath = f'{projectRoot}/products/from_radex-pipeline'

# Variable
cores = 20 # number of threads to use for multi-processing
linewidth = 15 # km/s
mole_0 = 'co'
mole_1 = '13co'
mole_2 = 'c18o'
'''# 冷知識: molecule是名詞, molecular是形容詞
小寫因為 mole_1 之後會寫到 .inp file裡面
第一行會呼叫要使用的 .dat file
需要一些統一的檔名
mole_n 和 molecule(list) 應該是互相可取代的關係
先寫一個簡單的，反正能跑再說
'''

# Physical Conditions Grid
step_Nco_exp = 0.2
step_Tkin_exp = 0.1
Nco_exp = np.arange(15., 20.1, step_Nco_exp)
Tkin_exp = np.arange(1., 2.8, step_Tkin_exp)
nH2_exp = np.arange(2., 5.1, step_Nco_exp) # step size for Nco and nH2 should be the same
X1213 = np.arange(20, 205, 10)
X1318 = np.arange(2, 21, 1)

# Pre-processing
round_Nco, round_Tkin = 1, 1  # 取的小數位數, 好像是 show in file name 用的？
Nco_coe = np.round(10**np.arange(0., 1., step_Nco_exp))   # columnDensity: A*10^B, A:*_coe; B:*_exp
Tkin_coe = np.round(10**np.arange(0., 1., step_Tkin_exp))

X1213_inv = 1. / X1213 # 真的不知道為什麽會有倒數
X1318_inv = 1. / X1318

num_Nco_exp = Nco_exp.shape[0] # len() works, too
num_Nco_coe = len(Nco_coe)
num_Tkin_exp = len(Tkin_exp)   # 並不確定這些是不是有要裝進變數的必要...
num_Tkin_coe = len(Tkin_coe)   # num_系列是跑回圈的時候會用到吧
num_nH2_exp = len(nH2_exp)
num_X1213 = len(X1213)
num_X1318 = len(X1318)

# def runRADEX_m*():
'''
這邊依然是製作檔名, 因為是要調用所以可預期的, 
檔名必須與 writeInput() 系列一致

我在想說為什麼不能就把 runRADEX_m*() 和 writeInput() 寫在一起...?
因為要進行平行處理嗎？
'''
def runRADEX_m0(i, j, k): # for (i, j, k) in range (num_Tkin, num_nH2, num_Nco)
    # _coe_here & _exp_here, 用 _here 是因為有些名字已經被佔用了, 避免分歧啦
    Tkin_coe_here = Tkin_coe[i%num_Tkin_coe]
    Tkin_exp_here = i//num_Tkin_coe + int(Tkin_exp[0])
    nH2_coe_here  = Nco_coe[j%num_Nco_coe]
    nH2_exp_here  = j//num_Nco_coe + int(nH2_exp[0])
    Nco_coe_here  = Nco_coe[k%num_Nco_coe]
    Nco_exp_here  = k//num_Nco_coe + int(Nco_exp[0])
    # _fn for fileName, spaces for beauty :)
    Tkin_fn = f'{round(Tkin_coe_here, round_Tkin)}e{round(Tkin_exp_here, round_Tkin)}'
    nH2_fn  = f'{round(nH2_coe_here, round_Nco)}e{nH2_exp_here}' 
    Nco_fn  = f'{round(Nco_coe_here, round_Nco)}e{Nco_exp_here}'
    fileName = f'Tkin-{Tkin_fn}_nH2-{nH2_fn}_Nco-{Nco_fn}'

    radexOut = os.system(f'radex < {dataPath}/input_{mole_0}/{fileName}.inp')
    return radexOut

def runRADEX_m1(i, j, k, m): # for (i, j, k, m) in range (num_Tkin, num_nH2, num_Nco, num_X1213)
    # _coe_here & _exp_here
    Tkin_coe_here = Tkin_coe[i%num_Tkin_coe]
    Tkin_exp_here = i//num_Tkin_coe + int(Tkin_exp[0])
    nH2_coe_here  = Nco_coe[j%num_Nco_coe]
    nH2_exp_here  = j//num_Nco_coe + int(nH2_exp[0])
    Nco_coe_here  = Nco_coe[k%num_Nco_coe]
    Nco_exp_here  = k//num_Nco_coe + int(Nco_exp[0])
    # _fn for fileName
    Tkin_fn = f'{round(Tkin_coe_here, round_Tkin)}e{round(Tkin_exp_here, round_Tkin)}'
    nH2_fn  = f'{round(nH2_coe_here, round_Nco)}e{nH2_exp_here}' 
    Nco_fn  = f'{round(Nco_coe_here, round_Nco)}e{Nco_exp_here}'
    fileName = f'Tkin-{Tkin_fn}_nH2-{nH2_fn}_Nco-{Nco_fn}_X1213-{X1213[m]}' # X1213_fn 就直接寫了
    radexOut = os.system(f'radex < {dataPath}/input_{mole_1}/{fileName}.inp')
    return radexOut

def runRADEX_m2(i, j, k, m, n): # for (i, j, k, m, n) in range (num_Tkin, num_nH2, num_Nco, num_X1213, num_X1318)
    # _coe_here & _exp_here
    Tkin_coe_here = Tkin_coe[i%num_Tkin_coe]
    Tkin_exp_here = i//num_Tkin_coe + int(Tkin_exp[0])
    nH2_coe_here  = Nco_coe[j%num_Nco_coe]
    nH2_exp_here  = j//num_Nco_coe + int(nH2_exp[0])
    Nco_coe_here  = Nco_coe[k%num_Nco_coe]
    Nco_exp_here  = k//num_Nco_coe + int(Nco_exp[0])
    # _fn for fileName
    Tkin_fn = f'{round(Tkin_coe_here, round_Tkin)}e{round(Tkin_exp_here, round_Tkin)}'
    nH2_fn  = f'{round(nH2_coe_here, round_Nco)}e{nH2_exp_here}' 
    Nco_fn  = f'{round(Nco_coe_here, round_Nco)}e{Nco_exp_here}'
    fileName = f'Tkin-{Tkin_fn}_nH2-{nH2_fn}_Nco-{Nco_fn}_X1213-{X1213[m]}_X1318-{X1318[n]}' # X**_fn 就直接寫了
    radexOut = os.system(f'radex < {dataPath}/input_{mole_2}/{fileName}.inp')
    return radexOut

# Use the functions_------ wi verbose
# 我就是要把它展開來寫啊
print('Running RADEX with .inp files...')
Parallel(n_jobs=cores, verbose=5)(
    delayed(runRADEX_m0)(i, j, k)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )
Parallel(n_jobs=cores, verbose=5)(
    delayed(runRADEX_m1)(i, j, k, m)
    for m in range(0, num_X1213)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )
Parallel(n_jobs=cores, verbose=5)(
    delayed(runRADEX_m2)(i, j, k, m, n)
    for n in range(0, num_X1318)
    for m in range(0, num_X1213)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )
runRadex_time = time.time() 
print(f'It took {(runRadex_time - start_time):.5f} seconds to finish running RADEX.')
