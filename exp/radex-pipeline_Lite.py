'''radex-pipeline_lite.py
This script is intended to serve as a smaller-scale workflow version of `radex_pipeline.py`, from Eltha.

# Note: 
- This script should be placed under the `scripts/` directory.
- This script is expected to run on the Lab machine, not on feifei,
- due to differences in directory structure. (雖然盡量寫的通用了...)
'''

import numpy as np
import os
import time
#from joblib import Parallel, delayed
from pathlib import Path # for finding file, path

# Path
projectRoot = Path(__file__).resolve().parents[1] # .../line-modeling_Circinus, no slash at the end
dataPath = f'{projectRoot}/data/radexProcessing/'

# Variable
molecule = ['co', '13co', 'c18o'] # 冷知識: molecule是名詞, molecular是形容詞
'''
我提出的問題是
Eltha 是事先知道他要用那六種線進行建模，所以才這麼寫的
那我他媽現在還不知道我有沒有這麼多線，我還要這樣寫嗎？
'''

mole_1 = 'CO' 
'''
大寫因為我覺得我很多檔案都是大寫的，真是醜陋的習慣
當然如果要他自動 import 檔案的話我那個狗啃檔名真的會需要改一下欸
mole_n 和 molecule(list) 應該是互相可取代的關係
先寫一個簡單的，反正能跑再說
處理環境相依問題真的是最白癡的吧
'''
num_cores = 20 # joblib-related
linewidth = 15 # km/s

# Physical Conditions Grid
