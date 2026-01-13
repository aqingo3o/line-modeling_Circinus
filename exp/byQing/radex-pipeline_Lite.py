'''radex-pipeline_lite.py
This script is intended to serve as a smaller-scale workflow version of `radex_pipeline.py`, from Eltha.

# Note: 
- This script should be placed under the `scripts/` directory.
- This script is expected to run on the Lab machine, not on feifei,
- due to differences in directory structure. (雖然盡量寫的通用了...)
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

# def radexFlux():
# 不知道這是幹啥的
def radex_flux(i,j,k,m,n):
    # 檔名這邊和前面一樣
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

    fileName_0 = f'Tkin-{Tkin_fn}_nH2-{nH2_fn}_Nco-{Nco_fn}'
    outfile_0 = f'{dataPath}/output_{mole_0}/{fileName_0}.out'
    outfile_1 = f'{dataPath}/output_{mole_1}/{fileName_0}_X1213-{X1213[m]}.out'
    outfile_2 = f'{dataPath}/output_{mole_2}/{fileName_0}_X1213-{X1213[m]}_X1318-{X1318[n]}.out'
    
    # Extract reliable flux predictions (avoid those with convergence issues)
    # 以下全部都不知道在做什麼
    if np.loadtxt(outfile_0,skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_0 = np.full((3,), np.nan)
    else:
        flux_0 = np.genfromtxt(outfile_0, skip_header=13)[:, 11]

    if np.loadtxt(outfile_1,skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_1 = np.full((3,), np.nan)
    else:    
        flux_1 = np.genfromtxt(outfile_1, skip_header=13)[:, 11]

    if np.loadtxt(outfile_2,skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_2 = np.full((3,), np.nan)
    else:    
        flux_2 = np.genfromtxt(outfile_2, skip_header=13)[:, 11]
    
    return k, i, j, m, n, flux_0, flux_1, flux_2

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
writeInp_time = time.time()
print(f'It took {(writeInp_time - start_time):.5f} seconds to write all .inp files.') # 519

# Use the functions_------ wi verbose
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
print(f'It took {(runRadex_time - writeInp_time):.5f} seconds to finish running RADEX.')

# ---------------------------- IDK why she do that ------------------------------ #
# Construct 3D - 5D flux models
flux_results = Parallel(n_jobs=cores)(
    delayed(radex_flux)(i,j,k,m,n)    
    for n in range(0, num_X1318)
    for m in range(0, num_X1213)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
)

flux_co_10 =  np.full((num_Nco_exp, num_Tkin_exp, num_nH2_exp), np.nan)
flux_co_21 = np.full((num_Nco_exp, num_Tkin_exp, num_nH2_exp), np.nan)
flux_13co_21 = np.full((num_Nco_exp, num_Tkin_exp, num_nH2_exp, num_X1213), np.nan)
flux_13co_32 = np.full((num_Nco_exp, num_Tkin_exp, num_nH2_exp, num_X1213), np.nan)
flux_c18o_21 = np.full((num_Nco_exp, num_Tkin_exp, num_nH2_exp, num_X1213,num_X1318), np.nan)
flux_c18o_32 = np.full((num_Nco_exp, num_Tkin_exp, num_nH2_exp, num_X1213,num_X1318), np.nan)

for result in flux_results:
    k, i, j, m, n, flux_0, flux_1, flux_2 = result
    flux_co_10[k,i,j] = flux_0[0]
    flux_co_21[k,i,j] = flux_0[1]
    flux_13co_21[k,i,j,m] = flux_1[0]
    flux_13co_32[k,i,j,m] = flux_1[1]
    flux_c18o_21[k,i,j,m,n] = flux_2[0]
    flux_c18o_32[k,i,j,m,n] = flux_2[1]

# Save Flux files: {projectRoot}/products/from_radex-pipeline/flux_{mole}-{transition}.npy
np.save(f'{productPath}/flux_co-10.npy', flux_co_10)
np.save(f'{productPath}/flux_co-21.npy', flux_co_21)
np.save(f'{productPath}/flux_13co-21.npy', flux_13co_21)
np.save(f'{productPath}/flux_13co-32.npy', flux_13co_32)
np.save(f'{productPath}/flux_c18o-21.npy', flux_c18o_21)
np.save(f'{productPath}/flux_c18o-32.npy', flux_c18o_32) 

# Construct 5D ratio models
temp = np.repeat(flux_co_21[:, :, :, np.newaxis], num_X1213, axis=3)
co21_5d = np.repeat(temp[:, :, :, :, np.newaxis], num_X1318, axis=4)
temp2 = np.repeat(flux_co_10[:, :, :, np.newaxis], num_X1213, axis=3)
co10_5d = np.repeat(temp2[:, :, :, :, np.newaxis], num_X1318, axis=4)
c13o_21_5d = np.repeat(flux_13co_21[:, :, :, :, np.newaxis], num_X1318, axis=4)
c13o_32_5d = np.repeat(flux_13co_32[:, :, :, :, np.newaxis], num_X1318, axis=4) 

# 變數命名裡莫名其妙的 2 原來是 to 的意思
ratio_co           = co21_5d      / co10_5d
ratio_13co         = c13o_32_5d   / c13o_21_5d
ratio_c18o         = flux_c18o_32 / flux_c18o_21
ratio_co213co      = co21_5d      / c13o_21_5d
ratio_co2c18o      = co21_5d      / flux_c18o_21
ratio_13co2c18o_21 = c13o_21_5d   / flux_c18o_21
ratio_13co2c18o_32 = c13o_32_5d   / flux_c18o_32

# Save Ratio files: {projectRoot}/products/from_radex-pipeline/ratio_{mole-a}-{a-transi}_over_{mole-b}-{b-transi}.npy
np.save(f'{productPath}/ratio_co-21_over_co_10.npy',     ratio_co)
np.save(f'{productPath}/ratio_13co-32-to-21.npy',        ratio_13co)
np.save(f'{productPath}/ratio_c18o-32_over_c18o-21.npy', ratio_c18o)
np.save(f'{productPath}/ratio_co-21_over_c13o-21.npy',   ratio_co213co)
np.save(f'{productPath}/ratio_co-21_over_c18o-21.npy',   ratio_co2c18o)
np.save(f'{productPath}/ratio_13co-21_over_c18o-21.npy', ratio_13co2c18o_21)
np.save(f'{productPath}/ratio_13co-32_over_c18o-32.npy', ratio_13co2c18o_32)
print('Ratio models saved.')

endall_time = time.time()
print(f'It took {(endall_time - start_time):.5f} seconds to do all above.')
