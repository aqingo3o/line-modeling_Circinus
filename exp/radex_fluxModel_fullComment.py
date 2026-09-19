# Script for feifei or blackhole.
# Put this script under {projectRoot}, (i.e. /home/aqing/Documents/line-modleing_Circiuns/)
# Remaining dependency paths will be created automatically.
'''
I think something unexcepted happend in Eltha's code (? maybe not)
so I write another script for RADEX model grid.

Though this version of script isn't appear in early stage of my work
(so mature folder system has been built)
但為了後續復現的方便 && 這隻程式高度資料夾路徑依賴
為了防止程式開始跑了才發現很多東西不存在, 我保留了自動建立檔案結構的部分。

然後靠北我根本不知道這是不是對的, 幹

ref: Eltha's radex_pipeline.py from her github repo.

Current version remove two *Abudance Ratio* as member of model grid.
Because I'm not sure if we need abudance ratio for science purpose or not.
Fewer fitting parameters may led to something good?

update: 2026-09-01, Just can't believe it is September now...
                    Fix the file name issue like 6309600000000000.0 etc.
        2026-09-09, Slightly extend Tk range (up to 794 K),
                    and HCO+ into model grid.
        2026-09-11, add `flagrow` in getMfllux(), due to radex.out of 
                    CO-family and HCO+ have different formation.
        2026-09-17, Add an option `addHCOp (bool)` in ln78 to control 
                    whether HCO+ lines are included in the model grid or not.
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
#'''
print('Start creating folder structure for radex_fluxModel.py ...')
projectRoot = Path(__file__).resolve().parents[0] # line-modeling_Circinus, no slash
# First-level
projectRoot_member = ['data', 'docs', 'products', 'scripts']
for i in projectRoot_member:
    projectRoot_sub = f'{projectRoot}/{i}'
    if not os.path.exists(projectRoot_sub):
        os.makedirs(projectRoot_sub)
# Second-level
print('Strat building second & third-level subfolders under projectRoot...')
under_data = ['radex_io', 'model_resolved', 'model_with-hco+',
                          'result_resolved', 'result_with-hco+']
for i in under_data:
    dataPath_sub = f'{projectRoot}/data/{i}'
    if not os.path.exists(dataPath_sub):
        os.makedirs(dataPath_sub)
# Third-level
under_radexio = ['input_co',  'input_13co',  'input_c18o',  'input_hco+',
                 'output_co', 'output_13co', 'output_c18o', 'output_hco+']
for i in under_radexio:
    ioPath_sub = f'{projectRoot}/data/radex_io/{i}' # radex_io/ is a hard-coding
    if not os.path.exists(ioPath_sub):
        os.makedirs(ioPath_sub)
print('Dependency folder strucrure is now OK :D')
print()
#'''

# -------------------------- Path Variables -------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus'
radexioPath = f'{projectRoot}/data/radex_io' # a VAST number of files

start_time = time.time()
# ------------------------- Basic Variables ------------------------- #
num_cores = 20  # joblib
linewidth = 25 # km/s, from mom2.

addHCOp = False # bool
# part of keys of model_grid
if addHCOp:
    mole_species = ['co', '13co', 'hco+',]
    phy_para = ['Kinetic Temperature', 'Number Density', '12CO Column Density', 
                'HCO+ Abundance',] 
    X12co = 3e-4 # CO-to-H2 abundance, Eltha(2022)
    npyPath = f'{projectRoot}/data/model_with-hco+' # extracted flux model
else:
    mole_species = ['co', '13co']
    phy_para = ['Kinetic Temperature', 'Number Density', '12CO Column Density',] 
    npyPath = f'{projectRoot}/data/model_resolved' # extracted flux model

# Abundance
X1213 = 40 # Abundance ratio, Hitschfeld(2008)
X1318 = 8  # ?

# Change the frequency range in ln174 !!
transis = ['10', '21', '32', '43', '54', '65'] 

# -------------------- def: Scientific notation -------------------- #
'''
This formatting function is used only for styling filenames.
the exact values used in calculations should remain unaffected.
BUT, this scripts use the filename of .out to rebuild physical conditions array
(saved as `phy_plain-model_Tk-nH2-Nco.npy`).
Thefore, don't use too coarse digit value to make sure model works.
'''
def sciFmt (val, digit=4):
    if isinstance(val, str):
        return 'nan'
    else: # 有點不嚴謹但不管啦, 給我自己用的
        coee, expp = f'{val:.{digit}e}'.split('e')
        expp = int(expp)
        if '.' in coee:
            coee = coee.rstrip('0').rstrip('.')
        return f'{coee}e{expp}'

# ----------------- Set Physical Conditions Range ------------------- #
# Grid steps
expstep_Tk = 0.1
expstep_nH2 = 0.2
expstep_Nco = expstep_nH2 # step size for Nco and nH2 should be the same (idky)

if addHCOp :
    model_grid = {
        "Kinetic Temperature": {
            "fracExp": np.arange(0.7, 3.0,  step=expstep_Tk),  # fracExp 代表在指數部分含有小數
        },
        "Number Density": {
            "fracExp": np.arange(2.,  5.1,  step=expstep_nH2), # 多的那 .1 due to arange() stop before the end.
        },
        "12CO Column Density": {
            "fracExp": np.arange(15., 20.1, step=expstep_Nco),
        },
        "HCO+ Abundance": {
            "fracExp": np.arange(-9., -8., step=0.1),
        },
    }
else:
    model_grid = {
        "Kinetic Temperature": {"fracExp": np.arange(0.7, 3.0,  step=expstep_Tk)},
        "Number Density":      {"fracExp": np.arange(2.,  5.1,  step=expstep_nH2)},
        "12CO Column Density": {"fracExp": np.arange(15., 20.1, step=expstep_Nco)},
        }

# ------------------------- Pre-processing ------------------------- #
# Generate model grid
for paraname in phy_para:
    aeb = []
    for fexp in model_grid[paraname]["fracExp"]:
        coe = 10 ** (fexp - int(fexp)) # frac-part of fexp will turn into pre(coe)
        aeb.append(float(f'{round(coe, 4)}e{int(fexp)}')) # float(string) -> number :)
    model_grid[paraname]["AeB"] = np.array(aeb)

# Gain 13CO and C18O column density from abundance ratios and 12CO column density
N12co_aeb = model_grid["12CO Column Density"]["AeB"]
model_grid["13CO Column Density"] = {"AeB": N12co_aeb / X1213}
model_grid["C18O Column Density"] = {"AeB": N12co_aeb / (X1213 * X1318)}

# 有 HCO+ 才要做這個
if addHCOp:
    # Gain HCO+ column density from HCO+ abundance and 12CO column density
    Nhcop_aeb = []
    for i in model_grid["HCO+ Abundance"]["AeB"]:
        Nhcop_aeb.append(i * N12co_aeb / X12co)
    model_grid["HCO+ Column Density"] = {"AeB": np.array(Nhcop_aeb)}
    #print(np.array(Nhcop_aeb).shape) # >> (10, 26) where (Xhcop, N12co)

#print(model_grid.keys())

# ------------------------- writeInputs(): ------------------------- #
def writeInput(molesp, Tk, nH2, Ncolu, Xhcop='default no X_HCO^+'):
    physet = f'{sciFmt(Tk)}_{sciFmt(nH2)}_{sciFmt(Ncolu)}_{sciFmt(Xhcop)}' # use scientific notation

    file = open(f'{radexioPath}/input_{molesp}/{physet}.inp', 'w')
    file.write(f'{molesp}.dat\n')
    file.write(f'{radexioPath}/output_{molesp}/{physet}.out\n')
    file.write('80 700\n') # frequency range (GHz), hco+-10: 89.1GHz; co-65: 691GHz
    file.write(f'{Tk}\n')
    file.write('1\n')
    file.write('H2\n')
    file.write(f'{nH2}\n')
    file.write('2.73'+'\n')
    file.write(f'{Ncolu}\n')
    file.write(f'{linewidth}\n')
    file.write('0\n')
    file.close()

### Just CO family ###
for molesp in mole_species:
    if molesp == 'co':
        ColumnDensityGrid = model_grid["12CO Column Density"]["AeB"]
    elif molesp == '13co':
        ColumnDensityGrid = model_grid["13CO Column Density"]["AeB"]
    elif molesp =='c18o':
        ColumnDensityGrid = model_grid["C18O Column Density"]["AeB"]
    else: 
        continue
    print(f'Writing .inp files for {molesp}...')
    Parallel(n_jobs=num_cores)(
        delayed(writeInput)(molesp, Tk ,nH2, Ncolu)
        for Ncolu in ColumnDensityGrid
        for nH2 in model_grid["Number Density"]["AeB"]
        for Tk in model_grid["Kinetic Temperature"]["AeB"]
    )

### For HCO+ ###
if addHCOp:
    for molesp in mole_species:
        if molesp != 'hco+':
            continue
        ColumnDensityGrid = model_grid["HCO+ Column Density"]["AeB"]
        print(f'Writing .inp files for {molesp}...')
        Parallel(n_jobs=num_cores)(
            delayed(writeInput)(molesp, Tk, nH2, Ncolu, Xhcop)
            for Xhcop, the_Nhcop in zip(model_grid["HCO+ Abundance"]["AeB"],     # More explain to this zip(),
                                        model_grid["HCO+ Column Density"]["AeB"])# plz go to itoya!
            for Ncolu in the_Nhcop
            for nH2 in model_grid["Number Density"]["AeB"]
            for Tk in model_grid["Kinetic Temperature"]["AeB"]
        )

input_time = time.time()
print(f'It took {(input_time - start_time):.2f} seconds to write all .inp files.')
print()

# --------------------------- runRADEX(): -------------------------- #
def runRADEX(molesp, Tk ,nH2, Nco, Xhcop='default no X_HCO^+'):
    inpPath = f'{radexioPath}/input_{molesp}/{sciFmt(Tk)}_{sciFmt(nH2)}_{sciFmt(Nco)}_{sciFmt(Xhcop)}.inp'
    # create tempoary indep-folder for each caculation, avoiding "Error open radex.log"
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

### For CO family ###
for molesp in mole_species:
    if molesp == 'co':
        ColumnDensityGrid = model_grid["12CO Column Density"]["AeB"]
    elif molesp == '13co':
        ColumnDensityGrid = model_grid["13CO Column Density"]["AeB"]
    elif molesp =='c18o':
        ColumnDensityGrid = model_grid["C18O Column Density"]["AeB"]
    else:
        continue
    print(f'Start RADEXing for {molesp} ...')
    Parallel(n_jobs=num_cores)(
        delayed(runRADEX)(molesp, Tk ,nH2, Ncolu)
        for Ncolu in ColumnDensityGrid
        for nH2 in model_grid["Number Density"]["AeB"]
        for Tk in model_grid["Kinetic Temperature"]["AeB"]
    )

### Only HCO+ ###
if addHCOp:
    for molesp in mole_species:
        if molesp != 'hco+':
            continue
        ColumnDensityGrid = model_grid["HCO+ Column Density"]["AeB"]
        print(f'Start RADEXing for {molesp} ...')
        Parallel(n_jobs=num_cores)(
            delayed(runRADEX)(molesp, Tk, nH2, Ncolu, Xhcop)
            for Xhcop, the_Nhcop in zip(model_grid["HCO+ Abundance"]["AeB"],
                                        model_grid["HCO+ Column Density"]["AeB"])
            for Ncolu in the_Nhcop
            for nH2 in model_grid["Number Density"]["AeB"]
            for Tk in model_grid["Kinetic Temperature"]["AeB"]
        )

radex_time = time.time()
print(f'It took {(radex_time - input_time):.2f} seconds to finish running RADEX.')
print()

# --------------- Get Model Flux into dict: `flux_model` --------------- #
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
所以這樣取出的串列就會是長度為 n 個 transision 的陣列, 
n 取決於填入 .inp 的頻率範圍, 應該要與這隻程式中設定的 transis 一樣多
(這邊因為都是 CO 系列的, 所以可以套用同樣的範圍, 
別的品種可能要注意一下, 
總之就是讓所有的物種都剛好算出**同樣數量**的 transisioins)

關於 np.genfromtxt(): 
skip_header=13: 跳過 13 列 >> 到達那個有寫躍遷和一堆計算結果的那邊
反正就是開一個 .out 出來看看就對了
'''

'''
Check exsiting .out file for the `flagrow`.
In general, it should be the line that recording calculation finished in how many iterations.
- CO   : 11 (default)
- 13CO : 11 (default)
- C18O : 11 (default)
- HCO+ : 9
'''
def getMflux(molesp, Tk, nH2, Ncolu, Xhcop='default no X_HCO^+', flagrow=11):
    physet = f'{sciFmt(Tk)}_{sciFmt(nH2)}_{sciFmt(Ncolu)}_{sciFmt(Xhcop)}'
    outFile = f'{radexioPath}/output_{molesp}/{physet}.out'
    # Extract reliable flux predictions (dispose those with convergence issues)
    if np.loadtxt(outFile, skiprows=flagrow-1, max_rows=1, dtype='str')[3] == '****':
        mflux = np.full(len(transis), np.nan)
        print(f"{molesp}'s {physet}.out has converage issue :(")
    else:
        mflux = np.genfromtxt(outFile, skip_header=flagrow+2)[:, 11]
    return physet, mflux

flux_model = {}
physical_condi = {}
### For CO family ###
for molesp in mole_species:
    if molesp == 'co':
        ColumnDensityGrid = model_grid["12CO Column Density"]["AeB"]
    elif molesp == '13co':
        ColumnDensityGrid = model_grid["13CO Column Density"]["AeB"]
    elif molesp =='c18o':
        ColumnDensityGrid = model_grid["C18O Column Density"]["AeB"]
    else:
        continue
    print(f"Extracting model flux from {molesp}'s output files...")
    resultset = Parallel(n_jobs=num_cores)( # `resultset` 裝 getMflux's return, resultset -> [physet, ]
                    delayed(getMflux)(molesp, Tk ,nH2, Ncolu)
                    for Ncolu in ColumnDensityGrid
                    for nH2 in model_grid["Number Density"]["AeB"]
                    for Tk in model_grid["Kinetic Temperature"]["AeB"]
                )
    '''
    到這邊, 就讀完一坨檔案了, 集成一個大 list
    所以我猜接下來不做平行處理也行?
    '''
    # Get model flux for each tansision
    for t_idx in range(len(transis)):
        mfluxArray = []
        for _, mflux in resultset:
            mfluxArray.append(mflux[t_idx])
        flux_model[f'{molesp}-{transis[t_idx]}'] = {"Original Flux Model": np.array(mfluxArray),}

    # Turn physical conditions value into array and save into `physical_condi`
    phyArray = []
    for physet, _ in resultset:
        phyArray_sub = []
        for phy in physet.split('_'):
            if phy == 'nan': # just for CO family, because there is only 3 有效 para for them.
                continue 
            phyArray_sub.append(float(phy)) # follow the order: Tk, nH2, Ncolu, (Xhco+, if have.)
        phyArray.append(phyArray_sub)
    physical_condi[f"Tk-nH2-N{molesp}"] = np.array(phyArray)

     
### Only HCO+ ###
if addHCOp: 
    for molesp in mole_species: 
        if molesp != 'hco+':
            continue
        ColumnDensityGrid = model_grid["HCO+ Column Density"]["AeB"]
        print(f"Extracting model flux from {molesp}'s output files...")
        resultset = Parallel(n_jobs=num_cores)( # `resultset` 裝 getMflux's return, resultset -> [physet, ]
                        delayed(getMflux)(molesp, Tk ,nH2, Ncolu, Xhcop, flagrow=9)
                        for Xhcop, the_Nhcop in zip(model_grid["HCO+ Abundance"]["AeB"],
                                                    model_grid["HCO+ Column Density"]["AeB"])
                        for Ncolu in the_Nhcop
                        for nH2 in model_grid["Number Density"]["AeB"]
                        for Tk in model_grid["Kinetic Temperature"]["AeB"]
                    )

        # Get model flux for each tansision
        for t_idx in range(len(transis)):
            mfluxArray = []
            for _, mflux in resultset:
                mfluxArray.append(mflux[t_idx])
            flux_model[f'{molesp}-{transis[t_idx]}'] = {"Original Flux Model": np.array(mfluxArray),}

        # Turn physical conditions value into array and save into `physical_condi`
        phyArray = []
        for physet, _ in resultset:
            phyArray_sub = []
            for phy in physet.split('_'):       # the string 'nan' work for float, too. 
                phyArray_sub.append(float(phy)) # follow the order: Tk, nH2, Ncolu, (Xhco+, if have.)
            phyArray.append(phyArray_sub)
        physical_condi[f"Tk-nH2-N{molesp}_Xhco+"] = np.array(phyArray)

# --------------- Save Physical Condition Array into .npy --------------- #
'''
In fact, we only need these four parameters: [Tk, nH2, N12co, Xhco+]
They're enough for us to drive the physical conditions from fitting results.

Of course, [Tk, nH2, Nhco+, Xhco+] also work 
and recordinf these four would simplify this program.
However, deriving N12co from Nhco+, X12co (constant here) and Xhco+ require calculations,
which could lead to unexceptable errors in the subsequent code.

So I chose to record the original one,
by joining two physical arraies from the dict `physical_condi`.

For more coding detail, please refer to itoya 2026-09-11.
'''
phy3 = physical_condi["Tk-nH2-Nco"] # 3 for three physical parameters: [Tk, nH2, N12co]
if addHCOp:
    num_phy3 = phy3.shape[0] # phy3.shape >> (9568, 3), 3 for three para
    num_Xhcop = len(model_grid["HCO+ Abundance"]["AeB"])
    phy4 = np.zeros((num_phy3 * num_Xhcop, 4)) # 4 for four phyPara: [Tk, nH2, N12co, Xhco+]
                                            # except phy4.shape >> (95680, 4)
    for i, Xhcop in enumerate(model_grid["HCO+ Abundance"]["AeB"]):
        phy4[i*num_phy3 : (i+1)*num_phy3] = np.column_stack([phy3, np.full(num_phy3, Xhcop)])
    np.save(f'{npyPath}/phy_plain-model_Tk-nH2-Nco-Xhco+.npy', phy4)
else:
    phy4 = phy3 # for next section (if/else in ln408)
    np.save(f'{npyPath}/phy_plain-model_Tk-nH2-Nco.npy', phy3) # Save phyArray with just 3 paras.

# ------------------------ Align CO Flux Models ------------------------ #
'''
Because CO-family's flux model is like (9252, ) but HCO+ is (9568*num_Xhcop, ).
If CO-family and HCO+ lines need to be fit together,
these two kinds of flux model have to be in the same shape.

The approach of making the shapes identical needs to be coordinated 
with the method of creating `phy4`.
For more coding detail, please refer to itoya 2026-09-11.
'''
# Alignment
for molename in flux_model.keys():
    mflux_ori = flux_model[molename]["Original Flux Model"]
    if mflux_ori.shape[0] == phy4.shape[0]: # phy4.shape[0] >> (num_phy3 * num_Xhcop)
        flux_model[molename]["Aligned Flux Model"] = mflux_ori
    else:
        flux_model[molename]["Aligned Flux Model"] = np.tile(mflux_ori, num_Xhcop)

    np.save(f'{npyPath}/flux_plain-model_{len(phy_para)}para_{molename}.npy',
            flux_model[molename]["Aligned Flux Model"]) # Save all aligned model flux as .npy

# ------------- Add Beam Filling Factor to Model ------------- #
Phib = 10 ** np.arange(-1.3, 0.1, step=0.1)
np.save(f'{npyPath}/phy_plain-model_Phibf.npy', np.array(Phib)) # Save Phib array as .npy

for molename in flux_model.keys():
    scaledflux = np.outer(flux_model[molename]["Aligned Flux Model"], Phib) # scalar product!
    '''
    喔幹竟然是外積嗎?
    scaledflux.shape -> (12012, 14)
    scaledflux[a, b] = flux_model[a] * Phib[b], 還滿簡易的嘻嘻
    '''
    np.save(f'{npyPath}/flux_plain-model_{len(phy_para)+1}para_{molename}.npy',
            scaledflux) # scaledflux.shape -> (95680, 14), not that plain, actually

model_time = time.time()
print('Scaled flux models are saved.')
print()
# ----------------------- Write Time Records ----------------------- #
'''
timerec = open(f'{projectRoot}/docs/radex-pipeline_timeRecord.txt', 'w')
timerec.write(f'It took {(input_time - start_time):.2f} seconds to write all .inp files.\n')
timerec.write(f'It took {(radex_time - input_time):.2f} seconds to finish running RADEX.\n')
timerec.write(f'It took {(model_time - radex_time):.2f} seconds to add beam filling factor.\n')
timerec.close()
print()
'''
print('Sincere congratulations! This script arrived here without any obstacles. <3')