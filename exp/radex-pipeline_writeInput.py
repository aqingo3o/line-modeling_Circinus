'''radex-pipeline_writeInput.py
This script is intended to serve as a smaller-scale workflow version of `radex_pipeline.py`, from Eltha.

準確來說是我改過的 radex-pipeline_lite.py 的前半部分
因為一次全部跑完的話有點懸，所以就分成兩部分了。
'''
# Module
import numpy as np
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

# def writeInput_m*():
'''
因為要做平行處理所以才會需要一樣的東西分三行寫對吧？
Eltha 使用了聰明人才看得懂的超複雜引數，
因為我是智障所以我將會把所有東西都大展開

基本上的東西是 file = open('xxx.inp', 'w')
但是檔名要用迴圈所以會有一堆str, 
不過個人偏向於使用 f-string

參考 make-a-inp.py 裡的 .inp file 格式
'''
def writeInput_m0(i, j, k): # for (i, j, k) in range (num_Tkin, num_nH2, num_Nco)
    # _coe_here & _exp_here, 用 _here 是因為有些名字已經被佔用了, 避免分歧啦
    Tkin_coe_here = Tkin_coe[i%num_Tkin_coe]
    Tkin_exp_here = i//num_Tkin_coe + int(Tkin_exp[0])
    nH2_coe_here  = Nco_coe[j%num_Nco_coe] # Nco_coe 數字上等於 nH2_coe, 因為 nH2 & Nco's step相等 (more: note, 巨醜def()幹了什麼, 20260105)
    nH2_exp_here  = j//num_Nco_coe + int(nH2_exp[0])
    Nco_coe_here  = Nco_coe[k%num_Nco_coe]
    Nco_exp_here  = k//num_Nco_coe + int(Nco_exp[0])
    # 大家的計算方式很對稱啊

    # _fn for fileName, spaces for beauty :)
    Tkin_fn = f'{round(Tkin_coe_here, round_Tkin)}e{round(Tkin_exp_here, round_Tkin)}'
    nH2_fn  = f'{round(nH2_coe_here, round_Nco)}e{nH2_exp_here}' 
    Nco_fn  = f'{round(Nco_coe_here, round_Nco)}e{Nco_exp_here}'
    fileName = f'Tkin-{Tkin_fn}_nH2-{nH2_fn}_Nco-{Nco_fn}' 
    # .inp and .out 就差在後綴所以就打包了, 這邊的順序用的和 Eltha 一樣, 但加上標籤了

    # write info into .inp file
    file = open(f'{dataPath}/input_{mole_0}/{fileName}.inp', 'w') ### data/input_co/
    file.write(f'{mole_0}.dat\n')                    ### co.dat, here is writeInput_m1()
    file.write(f'{dataPath}/output_{mole_0}/{fileName}.out\n')    ### data/output_co/
    file.write('100 400'+'\n')                       ### output frequency range (GHz)
    file.write(f'{Tkin_coe_here}e{Tkin_exp_here}\n') ### kinetic temperature (K)
    file.write('1\n')                                #   number of collision partners (或許通常就一個？)
    file.write('H2\n')                               #   first collision partner
    file.write(f'{nH2_coe_here}e{nH2_exp_here}\n')   ### density of first collision partner (cm^-3)
    file.write('2.73'+'\n')                          #   temperature of background radiation (K, 好像都設 2.73)
    file.write(f'{Nco_coe_here}e{Nco_exp_here}\n')   ### molecular column density (cm^-2)
    file.write(f'{linewidth}\n')                     #   line width (km/s)
    file.write('0\n')                                #   run another calculation (or not, y/n = 1/0)
    file.close() # aftercare

def writeInput_m1(i, j, k, m): # for (i, j, k, m) in range (num_Tkin, num_nH2, num_Nco, num_X1213)
    # _coe_here & _exp_here
    Tkin_coe_here = Tkin_coe[i%num_Tkin_coe]
    Tkin_exp_here = i//num_Tkin_coe + int(Tkin_exp[0])
    nH2_coe_here  = Nco_coe[j%num_Nco_coe]
    nH2_exp_here  = j//num_Nco_coe + int(nH2_exp[0])
    Nco_coe_here  = Nco_coe[k%num_Nco_coe]
    Nco_exp_here  = k//num_Nco_coe + int(Nco_exp[0])
    N13co_coe_here = X1213_inv[m] * Nco_coe_here # 這邊不一樣, 並且我有點看不懂

    # _fn for fileName
    Tkin_fn = f'{round(Tkin_coe_here, round_Tkin)}e{round(Tkin_exp_here, round_Tkin)}'
    nH2_fn  = f'{round(nH2_coe_here, round_Nco)}e{nH2_exp_here}' 
    Nco_fn  = f'{round(Nco_coe_here, round_Nco)}e{Nco_exp_here}'
    fileName = f'Tkin-{Tkin_fn}_nH2-{nH2_fn}_Nco-{Nco_fn}_X1213-{X1213[m]}' # X1213_fn 就直接寫了

    # write info into .inp file, almost the same as writeInput_m0()
    file = open(f'{dataPath}/input_{mole_1}/{fileName}.inp', 'w')
    file.write(f'{mole_1}.dat\n') ### 13co.dat, here is writeInput_m1()
    file.write(f'{dataPath}/output_{mole_1}/{fileName}.out\n')
    file.write('100 400'+'\n')
    file.write(f'{Tkin_coe_here}e{Tkin_exp_here}\n')
    file.write('1\n')
    file.write('H2\n')
    file.write(f'{nH2_coe_here}e{nH2_exp_here}\n')
    file.write('2.73'+'\n')
    file.write(f'{round(N13co_coe_here, 4)}e{Nco_exp_here}\n') ### column density of 13co, exp的話co和13co是相通的
    file.write(f'{linewidth}\n')
    file.write('0\n')
    file.close() # aftercare

def writeInput_m2(i, j, k, m, n): # for (i, j, k, m, n) in range (num_Tkin, num_nH2, num_Nco, num_X1213, num_X1318)
    # _coe_here & _exp_here
    Tkin_coe_here = Tkin_coe[i%num_Tkin_coe]
    Tkin_exp_here = i//num_Tkin_coe + int(Tkin_exp[0])
    nH2_coe_here  = Nco_coe[j%num_Nco_coe]
    nH2_exp_here  = j//num_Nco_coe + int(nH2_exp[0])
    Nco_coe_here  = Nco_coe[k%num_Nco_coe]
    Nco_exp_here  = k//num_Nco_coe + int(Nco_exp[0])
    N18co_coe_here = X1318_inv[n] * X1213_inv[m] * Nco_coe_here # 這邊不一樣, 並且我有點看不懂

    # _fn for fileName
    Tkin_fn = f'{round(Tkin_coe_here, round_Tkin)}e{round(Tkin_exp_here, round_Tkin)}'
    nH2_fn  = f'{round(nH2_coe_here, round_Nco)}e{nH2_exp_here}' 
    Nco_fn  = f'{round(Nco_coe_here, round_Nco)}e{Nco_exp_here}'
    fileName = f'Tkin-{Tkin_fn}_nH2-{nH2_fn}_Nco-{Nco_fn}_X1213-{X1213[m]}_X1318-{X1318[n]}' # X**_fn 就直接寫了

    # write info into .inp file, almost the same as writeInput_m0()
    file = open(f'{dataPath}/input_{mole_2}/{fileName}.inp', 'w')
    file.write(f'{mole_2}.dat\n') ### c18o.dat, here is writeInput_m1()
    file.write(f'{dataPath}/output_{mole_2}/{fileName}.out\n')
    file.write('100 400'+'\n')
    file.write(f'{Tkin_coe_here}e{Tkin_exp_here}\n')
    file.write('1\n')
    file.write('H2\n')
    file.write(f'{nH2_coe_here}e{nH2_exp_here}\n')
    file.write('2.73'+'\n')
    file.write(f'{round(N18co_coe_here, 4)}e{Nco_exp_here}\n') ### column density of c18o? exp的話co-iso們是互通的
    file.write(f'{linewidth}\n')
    file.write('0\n')
    file.close() # aftercare

# Use the functions_writeInput_m*()
# 我就是要把它展開來寫啊
print('Writing .inp files...')
Parallel(n_jobs=cores)(
    delayed(writeInput_m0)(i, j, k)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )
Parallel(n_jobs=cores)(
    delayed(writeInput_m1)(i, j, k, m)
    for m in range(0, num_X1213)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )
Parallel(n_jobs=cores)(
    delayed(writeInput_m2)(i, j, k, m, n)
    for n in range(0, num_X1318)
    for m in range(0, num_X1213)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )

print('Completed writing.')
writeInp_time = time.time()
print(f'It took {(writeInp_time - start_time):.5f} seconds to write all .inp files.') # 519

'''# 檔案數量
input_co/  : 4992    四千九百九十二
input_13co/: 94848   九萬四千八百四十八個
input_c18o/: 1368269 一百三十六萬八千兩百六十九

feifei 做的還比較快?
'''