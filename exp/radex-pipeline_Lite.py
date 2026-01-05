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
dataPath = f'{projectRoot}/data/radexProcessing/'

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



