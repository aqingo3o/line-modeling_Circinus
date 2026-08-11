# Script for feifei or blackhole.
# Put this script under {projectRoot}, (i.e. /home/aqing/Documents/line-modleing_Circiuns/)
# Remaining dependency paths will be created automatically.
'''
因為一些發現, 總之要自己寫這個程式了, 不知道是大事很妙還是大事不妙
雖然這個程式並非出現在工作的前期 (也就是我已經擁有熟成的檔案結構)
但為了後續復現的方便 && 這隻程式高度資料夾路徑依賴
為了防止程式開始跑了才發現很多東西不存在, 我保留了自動建立檔案結構的部分。

程式湯底來自 Eltha 女士的 radex_pipeline.py, flux_model_6d.py

目前的版本刪掉了 Abudance ratio
因為不知道可拿這些做蛇麼, 少點參數我還可以算 reduce chi2
----------------------------------------------------------------------------------
然後這支程式真的狗幹長, 所以提供了[目錄]
- Import Module
- Build Folder Structure
- Path Variables

### RADEX pipeline
- Basic Variables
- Physical Conditions Grid
- Pre-processing
- def write_inputs_m*():
- def run_radex_m*():
- Use Functions write_inputs_m*() for molecules0,1,2
- Run RADEX for molecules 0,1,2 

### Save Models into .npy Files
- def radex_flux(): **from bayes repo**
- Run radex_flux():
- Containers for File Saving
- Construct 3D - 5D flux models (initial shape)
- Construct 5D Flux Models
- Construct 6D Flux Models

### Write Time Records
'''

# -------------------------- Import Module --------------------------- #
from joblib import Parallel, delayed
import numpy as np
import os
from pathlib import Path
import subprocess
import tempfile
import time

# ---------------------- Build Folder Structure ---------------------- #
'''
print('Start creating folder structure for radex_fluxModel.py ...')
projectRoot = Path(__file__).resolve().parents[0] # line-modeling_Circinus, no slash
# First-level
projectRoot_member = ['data', 'docs', 'exp', 'products', 'scripts'] 
for i in projectRoot_member:
    projectRoot_sub = f'{projectRoot}/{i}'
    if not os.path.exists(projectRoot_sub):
        os.makedirs(projectRoot_sub)
# Second-level
print('Strat building second & third-level subfolders under projectRoot...')
under_data = ['radex_io', 'model_npy'] 
for i in under_data:
    dataPath_sub = f'{projectRoot}/data/{i}'
    if not os.path.exists(dataPath_sub):
        os.makedirs(dataPath_sub)
# Third-level
under_radexio = ['input_co',  'input_13co',  'input_c18o', 
                 'output_co', 'output_13co', 'output_c18o'] 
for i in under_radexio:
    ioPath_sub = f'{projectRoot}/data/radex_io/{i}' # radex_io/ is a hard-coding
    if not os.path.exists(ioPath_sub):
        os.makedirs(ioPath_sub)
print('Dependency folder strucrure is now OK :D')
print()
'''

# -------------------------- Path Variables -------------------------- #
projectRoot = '/home/aqing/Documents/line-modeling_Circinus' # blackhole
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
radexioPath = f'{projectRoot}/data/radex_io' # a VAST number of files
npyPath = f'{projectRoot}/data/model_npy'    # extracted flux model
d_with_bf = '4d' # model's dimensiom with beam filling factor

### ------------------------ RADEX Pipeline ------------------------ ###
start_time = time.time()
# ------------------------- Basic Variables ------------------------- #
num_cores = 20 # joblib
linewidth = 300 # km/s
phy_para = ['Kinetic Temperature', 'Number Density', 'Column Density'] # keys of model_grid
molesp = ['co', 
          #'13co', 'c18o'
          ]
transis = ['10', '21', '32', '43'] # (i think) model grids should cover everything

# ----------------- Set Physical Conditions Range ------------------- #
expstep_Tk = 0.1
expstep_nH2 = 0.2
expstep_Nco = expstep_nH2 # step size for Nco and nH2 should be the same (idky)
'''
stepex_*: 指數部分的 step
i.e. Tkin -> 10^1, 10^1.1, 10^1.2, ... 10^2.7
'''
model_grid = { 
    "Kinetic Temperature": {
        "fracExp": np.arange(0.7, 2.9,  step=expstep_Tk),  # fracExp 代表在指數部分含有小數
    },
    "Number Density": {
        "fracExp": np.arange(2.,  6.1,  step=expstep_nH2), # 多的那 .1 是因為 arange() 會在終點前停下
    },
    "Column Density": {
        "fracExp": np.arange(15., 20.1, step=expstep_Nco),
    },
}

# -------------------------- Pre-processing -------------------------- #
for paraname in phy_para:
    aeb = []
    for fexp in model_grid[paraname]["fracExp"]:
        coe = 10 ** (fexp - int(fexp)) # fexp 的非整數部分會轉生成係數
        aeb.append(f'{round(coe, 4)}e{int(fexp)}') # (10^exp非整數部分)e(fexp整數部分)
        '''
        我知道有類似 f-string 的方法可以更優雅地完成這件事
        但是個人認為這個東西的可讀性比較高
        '''
    model_grid[paraname]["AeB"] = np.array(aeb) # 驚天超爛名字

# --------------------------- writeInputs(): --------------------------- #
def writeInputs(mole, Tk, nH2, Nco):
    file = open(f'{radexioPath}/input_{mole}/{Tk}_{nH2}_{Nco}.inp', 'w')
    file.write(f'{mole}.dat\n')
    file.write(f'{radexioPath}/output_{mole}/{Tk}_{nH2}_{Nco}.out\n')
    file.write('100 500\n')
    file.write(f'{Tk}\n')
    file.write('1\n')
    file.write('H2\n')
    file.write(f'{nH2}\n')
    file.write('2.73'+'\n')
    file.write(f'{Nco}\n')
    file.write(f'{linewidth}\n')
    file.write('0\n')
    file.close()

for mole in molesp:
    print(f'Writing .inp files for {mole} ...')
    Parallel(n_jobs=num_cores)(
        delayed(writeInputs)(mole, Tk ,nH2, Nco)
        for Nco in model_grid["Column Density"]["AeB"]
        for nH2 in model_grid["Number Density"]["AeB"]
        for Tk in model_grid["Kinetic Temperature"]["AeB"]
        )
input_time = time.time()
print(f'It took {(input_time - start_time):.2f} seconds to write all .inp files.')

# ---------------------------- runRADEX(): ---------------------------- #
def runRADEX(mole, Tk ,nH2, Nco):
    inpPath = f'{radexioPath}/input_{mole}/{Tk}_{nH2}_{Nco}.inp' # 因為 radexioPath 就是絕對路徑,
                                                                 # 所以可以直接用字串傳入
    # 為每個計算開闢獨立的臨時資料夾，避免 radex.log 互相衝突
    with tempfile.TemporaryDirectory() as temp_dir: # with 語法 (Context Manager): 是沙盒
        with open(inpPath, 'r') as inpFile: # 用 with open() 的方法讀取路徑為 inpPath 的檔案, 稱之為 inpFile
            subprocess.run( # subprocess: 聽說是 Python 官方推薦用來取代 os.system 的子進程管理工具
                            # 我覺得這是有說法的喔, 因為寫 os.system() 的時候, system 會被劃線劃掉, 聽説這代表函式過期
                ['radex'],  # 就是指令
                stdin=inpFile, # 相當於 Shell 的 < input.inp 重定向
                               # 喔我以為 < 是 radex 自己發明的椰
                               # stdin: 標準輸入串流, 聽說不需要經過 Shell 解析，執行效率比 os.system 更高且更安全
                cwd=temp_dir,               # cwd: current woking directory
                stdout=subprocess.DEVNULL,  # 終端資訊丟進 /dev/null
                stderr=subprocess.DEVNULL,
            )

for mole in molesp:
    print(f'Start RADEXing for {mole} ...')
    Parallel(n_jobs=num_cores)(
        delayed(runRADEX)(mole, Tk ,nH2, Nco)
        for Nco in model_grid["Column Density"]["AeB"]
        for nH2 in model_grid["Number Density"]["AeB"]
        for Tk in model_grid["Kinetic Temperature"]["AeB"]
        )
radex_time = time.time()
print(f'It took {(radex_time - input_time):.2f} seconds to finish running RADEX.')


### ----------------------------- Save Models into .npy Files ------------------------------- ###
'''
哇這邊最有可能抽風了
'''
'''
aa = np.loadtxt(outFile, skiprows=10, max_rows=1, dtype='str')
print(aa)
>> ['Calculation' 'finished' 'in' '30' 'iterations'

喔所以 skiprow 不是從 0 開始, 
總之 .out 裡面寫說計算在多少次迭代中完成的是第11列,
然後根據前人的經驗, 
如果計算沒有收斂的話, 會在迭代次數, 也就是第11列的第4個字串(idx=3), 那顯示 fortran 的溢位符號
也就是 "****"

關於 np.loadtext():
skiprow=10: 跳過10列, 從第11列開始讀, 反正不知道的就 print 出來看看
max_rows=1: 最多只讀一列, 讀一列就停下來, 不會浪費時間
dtype='str': 將讀進來的資料以空白切割成字串陣列

///

print(np.genfromtxt(outFile, skip_header=13))
>> 
[[ 1.0000000e+00            nan  0.0000000e+00  5.5000000e+00
   1.1527120e+02  2.6007576e+03 -5.1301000e+01 -1.1610000e-01
   6.7660000e+00  7.1940000e-02  2.1530000e-02  2.1610000e+03
   4.2620000e-05]
 [ 2.0000000e+00            nan  1.0000000e+00  1.6600000e+01
   2.3053800e+02  1.3004037e+03 -1.2362500e+02 -2.1250000e-01
   3.0650000e+01  1.3110000e-01  7.1940000e-02  9.7880000e+03
   1.5440000e-03]
 [ 3.0000000e+00            nan  2.0000000e+00  3.3200000e+01
   3.4579600e+02  8.6696340e+02  2.5866600e+02  2.3130000e-01
   5.1700000e+01  1.7220000e-01  1.3110000e-01  1.6510000e+04
   8.7930000e-03]]

這邊用 genfromtxt 好像是因為有一些nan 還是什麼的
總之我記得他和 np.loadtxt() 的區別是這個比較寬鬆, 可以處理缺失值什麼的
印出來之後稍微對照一下, 發現每個第二層串列中的前三個是躍遷資訊
接下來的資訊是什麼就是對照著 .out 看就對了
發現第 11 個元素就是 flux (K km s-1) :D
關於 np.genfromtxt(): 
skip_header=13: 跳過 13 列 >> 到達那個有寫躍遷和一堆計算結果的那邊
反正就是開一個 .out 出來看看就對了
'''
# --------------------------------------- Run radex_flux(): ------------------------------------ #
def radex_flux(mole, Tk, nH2, Nco):
    physet = f'{Tk}_{nH2}_{Nco}'
    outFile = f'{radexioPath}/output_{mole}/{physet}.out'
    # Extract reliable flux predictions (avoid those with convergence issues)
    if np.loadtxt(outFile, skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux = np.full(len(transis), np.nan)
        print(f'{outFile} has converage issue :(') # 這邊像要做一個寫入啊哈, 但不是必要的
    else:
        flux = np.genfromtxt(outFile, skip_header=13)[:, 11]
    return flux
    
    #return k, i, j, m, n, flux (???)


'''
現在的困難比較偏向於世
我應該用什麼樣的資料結構去儲存老子的 flux
讀取一個檔案, 然後取出總共4個transision的flux

用字典嗎? 第一層先是 molecule sp,
第二層是是一大堆的鍵值, key is physet and value is flux array (4 member)
但不知道就是說痾這樣的東西還可以放平行處理嗎
key 也是儲存資料的一部分啊哈
而且用字典在存東西的話, 感覺運算速度會很慢
靠北之後還要從字典讀出來嗎
還是做成內外混合串列
但不行, 因為npy計算要快的話好像是要純數字的

但總之,radex flux model 的前半部分應該要先下去跑啊哈
'''
#print('Constructing flux model grids...')
#here i a paralle

"""
# ----------------------------- Containers for File Saving -------------------------------- #

mole_info = [  # molespiece, (initial flux array's shape)
    ('co',   (num_Nco, num_Tk, num_nH2)),
    ('13co', (num_Nco, num_Tk, num_nH2, num_X12to13)),
    ('c18o', (num_Nco, num_Tk, num_nH2, num_X12to13, num_X13to18)),
]
flux_model = {}

# ---------------------- Construct 3D - 5D flux models (initial shape) ---------------------------- #
for molesp, iniShape in mole_info: # Initialize flux array
    for t in transis:
        flux_model[f'{molesp}-{t}'] = {"flux": np.full(iniShape, np.nan)}

for result in results: # Get FluxxxxxX, by Function radex_flux()
    k, i, j, m, n, flux_co, flux_13co, flux_c18o = result
    
    flux_data = [flux_co, flux_13co, flux_c18o]
    mole_spiece = ['co', '13co', 'c18o'] # 這兩的 index 要對齊

    for m_idx, molesp in enumerate(mole_spiece):
        for t_idx, t in enumerate(transis):
            if molesp == 'co':
                flux_model[f'{molesp}-{t}']["flux"][k,i,j] = flux_data[m_idx][t_idx]
            elif molesp == '13co':
                flux_model[f'{molesp}-{t}']["flux"][k,i,j,m] = flux_data[m_idx][t_idx]
            elif molesp == 'c18o':
                flux_model[f'{molesp}-{t}']["flux"][k,i,j,m,n] = flux_data[m_idx][t_idx]
'''
保留這個東西 因為這個太他媽懸吊了
for result in results:
    k, i, j, m, n, flux_0, flux_1, flux_2 = result
    flux_co10[k,i,j] = flux_0[0]
    flux_co21[k,i,j] = flux_0[1]
    flux_co32[k,i,j] = flux_0[2]
    flux_13co10[k,i,j,m] = flux_1[0]
    flux_13co21[k,i,j,m] = flux_1[1]
    flux_13co32[k,i,j,m] = flux_1[2]
    flux_c18o10[k,i,j,m] =   flux_2[0] # 雞雞為什麼這個少一個
    flux_c18o21[k,i,j,m,n] = flux_2[1]
    flux_c18o32[k,i,j,m,n] = flux_2[2]
'''

for molename in flux_model.keys(): # Save "flux" into .npy
    np.save(f'{npyPath}/flux_nd-coarse2_{molename}.npy', flux_model[molename]["flux"]) # (filename) modi by qing (20260317)
fluxini_time = time.time()
print('Flux models saved.')

# ---------------------------------- Construct 5D Flux Models ---------------------------------- #
for molesp, _ in mole_info: # reshape the initial flux model to 5d
    for t in transis:
        theFlux = flux_model[f'{molesp}-{t}']["flux"]
        if molesp == 'co':
            cache = np.repeat(theFlux[:,:,:, np.newaxis], num_X12to13, axis=3) # used to be 'temp'
            theFlux_5d = np.repeat(cache[:,:,:,:, np.newaxis], num_X13to18, axis=4)
        elif molesp == '13co':
            theFlux_5d = np.repeat(theFlux[:,:,:,:, np.newaxis], num_X13to18, axis=4)
        elif molesp == 'c18o':
            theFlux_5d = theFlux
        flux_model[f'{molesp}-{t}']["flux_5d"] = theFlux_5d

for molename in flux_model.keys(): # Save "flux_5d" into .npy
    np.save(f'{npyPath}/flux_{molename}.npy', flux_model[molename]["flux_5d"]) # (filename) modi by qing (20260317)

ratio5d_time = time.time()

# ---------------------------------- Construct 6D Flux Models --------------------------------- #
'''
以下的部分不是 radex_pipeline.py 了
來自 flux_model_6d.py, Eltha
不知道為什麼 Eltha 女士要分開寫, 但是合在一起同樣能避免要再設一次一桶變數的問題
'''
beam_fill = 10 ** np.arange(-1.3, 0.1, 0.1)
beamFactor = beam_fill.reshape(1,1,1,1,1, beam_fill.shape[0]) # factor 是亂叫的

# Construct 6d-flux models from 5d by adding the beam filling factor dimension
for molesp, _ in mole_info:
    for t in transis:
        theFlux_5d = flux_model[f'{molesp}-{t}']["flux_5d"]
        theFlux_6d = theFlux_5d.reshape(num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18,1) * beamFactor
        flux_model[f'{molesp}-{t}']["flux_6d"] = theFlux_6d

for molename in flux_model.keys(): # Save "flux_6d" into .npy
    np.save(f'{npyPath}/flux_{d_with_bf}_{molename}.npy', flux_model[molename]["flux_6d"])
print('Flux_6d models saved.')
flux6d_time = time.time()

### ------------------------------- Write Time Records ------------------------------------ ###
timerec = open(f'{projectRoot}/docs/radex-pipeline_timeRecord_iset.txt', 'w') # made by qing (20260113)
timerec.write(f'It took {(input_time - start_time):.2f} seconds to write all .inp files.\n')
timerec.write(f'It took {(radex_time - input_time):.2f} seconds to finish running RADEX.\n')
timerec.write(f'It took {(fluxini_time - radex_time):.2f} seconds to save 3d, 4d, 5d flux models.\n')
timerec.write(f'It took {(ratio5d_time - fluxini_time):.2f} seconds to save 5d ratio models.\n')
timerec.write(f'It took {(flux6d_time - ratio5d_time):.2f} seconds to save 6d flux models.\n')
timerec.close()
"""
print('Sincere congratulations! This script arrived here without any obstacles. <3')