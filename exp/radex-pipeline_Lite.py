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
#from joblib import Parallel, delayed
from pathlib import Path # for finding file, path

start_time = time.time()

# Path
projectRoot = Path(__file__).resolve().parents[1] # .../line-modeling_Circinus, no slash at the end
dataPath = f'{projectRoot}/data/radex_io/'

# Variable
cores = 20 # number of threads to use for multi-processing
linewidth = 15 # km/s
molecule = ['co', '13co', 'c18o'] # 冷知識: molecule是名詞, molecular是形容詞
'''
我提出的問題是
Eltha 是事先知道他要用那六種線進行建模，所以才這麼寫的
那我他媽現在還不知道我有沒有這麼多線，我還要這樣寫嗎？
'''

mole_1 = 'co' 
'''
小寫因為 mole_1 之後會寫到 .inp file裡面
第一行會呼叫要使用的 .dat file
需要一些統一的檔名
mole_n 和 molecule(list) 應該是互相可取代的關係
先寫一個簡單的，反正能跑再說
處理環境相依問題真的是最白癡的吧
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

num_Nco_exp = Nco_exp.shape[0] # len() works, too
num_Nco_coe = len(Nco_coe)
num_Tkin_exp = len(Tkin_exp)   # 並不確定這些是不是有要裝進變數的必要...
num_Tkin_coe = len(Tkin_coe)
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

參考 make-a-inp.py 裡的 .inp file 格式可能就不會有那麼多欸幹這是三小
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
def runRADEX_m0(i, j, k):
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

def runRADEX_m1(i, j, k, m):
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


def runRADEX_m2(i, j, k, m, n):
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
    
