# Can be run on Lab machine(ubuntu) or feifei(macOS)
# Auto set the folder structure
# You MUST put this script under your project root (i.e. ~/line-modeling_Circinus/thisScript.py)
# 對如果要把這個腳本放進 projectRoot/scripts/ 的話, 請跑完之後再放, 雖然很怪洨但先這樣吧?
# radex_fluxModel.py 的變數重新命名版
'''For user
radex_fluxModel.py 的程式湯底來自 Eltha 女士的 radex_pipeline.py and flux_model_6d.py, 
對標寒假的工作算是 radex-pipeline_setFolder-modiPath-add6d.py, 
盡量的改變了檔案命名的方式, 但因為牽涉到平行處理, 有些地方我不敢亂動
果然不是親自寫的程式用起來多半有點不安心...

這份程式進行了新的變數命名, 不過整個主要的架構依然不是我想出來的
改命名只是方便我改變建立的 physical conditions grid 的參數
因為直接用別人的 grid fit Circinus 很明顯他媽的不行

最前面的部分包含了設定整個工作空間的資料夾結構 (make_projectRoot.py && make_folders.py)
因為 radex-pipeline 系列的工作會有很多寫入檔案的機會, 所以對於相同命名的環境要求有點多
因此, 就算還沒有開始處理 cube, moment maps, 也可以先跑這支程式喔
'''
# ---------------------------- Table of contents ----------------------------- #
'''這支程式真的狗幹長, 所以提供了[目錄]
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
# ------------------------------ Testing Result ------------------------------- #
'''Run on Lab Server, blackhole, IP: 140.117.30.85
'''

# ------------------------------- Import Module ------------------------------- #
from joblib import Parallel, delayed
import numpy as np
import os
from pathlib import Path
import time

# -------------------------- Build Folder Structure ---------------------------- #
print('Start building suitable folder structure for radex pipeline...')
projectRoot = Path(__file__).resolve().parents[0] # line-modeling_Circinus, no slash
projectRoot_member = ['data', 'docs', 'exp', 'products', 'scripts', 'src'] # first-level
print('Strat building projectRoot and the top-level subfolders...')
for i in projectRoot_member: # first-level
    projectRoot_sub = f'{projectRoot}/{i}'
    if not os.path.exists(projectRoot_sub):
        os.makedirs(projectRoot_sub)

print('Strat building second & third-level subfolders under projectRoot...')
under_data = ['radex_io', 'model_npy'] # second-level
under_radexio = ['input_5d-coarse2_co', 'input_5d-coarse2_13co', 'input_5d-coarse2_c18o', 
                  'output_5d-coarse2_co', 'output_5d-coarse2_13co', 'output_5d-coarse2_c18o'] # third-level
for i in under_data: # second-level
    dataPath_sub = f'{projectRoot}/data/{i}'
    if not os.path.exists(dataPath_sub):
        os.makedirs(dataPath_sub)
for i in under_radexio: # third-level
    ioPath_sub = f'{projectRoot}/data/radex_io/{i}' # here's a hard-coding
    if not os.path.exists(ioPath_sub):
        os.makedirs(ioPath_sub)
print('Folder structure is ok :)')
print()

# ------------------------------- Path Variables ---------------------------------- #
projectRoot = '1'
radexioPath = f'{projectRoot}/data/radex_io' # 巨幅檔案數目的那個
npyPath = f'{projectRoot}/data/model_npy'    # extract flux 的那些

model_5d = '5d-coarse2' # level3 那邊相依的, 至今未知用途...
model_6d = '6d-coarse2'


### ------------------------------ RADEX Pipeline ------------------------------- ###
start_time = time.time()
# -------------------------------- Basic Variables -------------------------------- #
num_cores = 20  # for joblib
linewidth = 300 # km/s
mole_0 = 'co'
mole_1 = '13co'
mole_2 = 'c18o'
round_Nco, round_Tkin = 1, 1 # 檔名命名用的, f-string, 避免呈現一坨小數

# ------------------------- Set Physical Conditions Grid -------------------------- #
step_Tkin_exp = 0.1
step_Nco_exp = 0.2
'''
step_*_exp: 指數部分的 step
i.e. Tkin -> 10^1, 10^1.1, 10^1.2, ... 10^2.7
'''
Tkin_exp = np.arange(1.,  2.8,  step_Tkin_exp) # 必須從整數開始哈! 
nH2_exp  = np.arange(2.,  5.1,  step_Nco_exp) # (from E's Github) step size for Nco and nH2 should be the same
Nco_exp  = np.arange(15., 20.1, step_Nco_exp)
X1213 = np.arange(20, 205, 10) 
X1318 = np.arange(2,  21,  1)

# ----------------------- Generate Physical Conditions Grid ----------------------- #
Tkin_coe = np.round(10 ** np.arange(0., 1., step_Tkin_exp), 4) # columnDensity: A*10^B, A:*_coe; B:*_exp
Nco_coe  = np.round(10 ** np.arange(0., 1., step_Nco_exp),  4) # 與 *_exp 共用 step_ *
'''
原本這邊的 step 應該是 incr_
由以下程式碼產生
incr_dens = round(Nco_exp[1] - Nco_exp[0],  1)
incr_temp = round(Tkin_exp[1] - Tkin_exp[0],1)
'''

X1213_inv = 1. / X1213 # 真的不知道為什麽會有倒數
X1318_inv = 1. / X1318

# Lenght of Each Array
num_Nco_exp =  Nco_exp.shape[0] # len() works, too
num_Nco_coe =  len(Nco_coe)
num_Tkin_exp = len(Tkin_exp)   # 並不確定這些是不是有要裝進變數的必要...
num_Tkin_coe = len(Tkin_coe)   # num_系列是跑回圈的時候會用到吧
num_nH2_exp =  len(nH2_exp)
num_X1213 = len(X1213)
num_X1318 = len(X1318)
"""
# Source code
diff_Tk = Tkin[1] - Tkin[0]#
co_dex = np.round(10**np.arange(0.,1.,incr_dens), 4)#
Tk_dex = np.round(10**np.arange(0.,1.,incr_temp), 4)#
factors_13co = 1./X_13co  
factors_c18o = 1./X_c18o
num_Nco = Nco.shape[0]#
num_Tk = Tkin.shape[0]#
num_nH2 = nH2.shape[0]#
cycle_dens = co_dex.shape[0]#
cycle_temp = Tk_dex.shape[0]#
num_X1213 = X_13co.shape[0]#
num_X1318 = X_c18o.shape[0]#
"""
#print(num_Nco_exp, num_Nco_coe, num_Tkin_exp, num_Tkin_coe, num_nH2_exp, num_X1213, num_X1318)
# 會和 best_set 的 shape 有某些相似...?

# ------------------------------- def writeInputs_m*(): ------------------------------ #
def writeInputs_m0(i, j, k): # for (i, j, k) in range (num_Tkin_exp, num_nH2_exp, num_Nco_exp)
    # value in .inp
    # _coe_here & _exp_here, 用 _here 是因為有些名字已經被佔用了, 避免分歧啦
    Tkin_coe_here = Tkin_coe[i % num_Tkin_coe]
    Tkin_exp_here = i//num_Tkin_coe + int(Tkin_exp[0])
    nH2_coe_here  = Nco_coe[j % num_Nco_coe] # Nco_coe 數字上等於 nH2_coe, 因為 nH2 & Nco's step相等
    nH2_exp_here  = j//num_Nco_coe + int(nH2_exp[0])
    Nco_coe_here  = Nco_coe[k % num_Nco_coe]
    Nco_exp_here  = k//num_Nco_coe + int(Nco_exp[0])
    # 大家的計算方式很對稱啊

    # _fn for fileName, round() used :)
    Tkin_fn = f'{round(step_Tkin_exp * i + int(Tkin_exp[0]), round_Tkin)}'
    nH2_fn  = f'{round(nH2_coe_here, round_Nco)}e{nH2_exp_here}' 
    Nco_fn  = f'{round(Nco_coe_here, round_Nco)}e{Nco_exp_here}'
    # .inp and .out 就差在後綴所以就打包了, 這邊的順序用的和 Eltha 一樣, 但加上標籤了

    # write info into .inp file 
    file = open(f'{radexioPath}/input_{model_5d}_{mole_0}/{Tkin_fn}_{nH2_fn}_{Nco_fn}.inp', 'w')
    file.write(f'{mole_0}.dat\n')
    file.write(f'{radexioPath}/output_{model_5d}_{mole_0}/{Tkin_fn}_{nH2_fn}_{Nco_fn}.out\n')
    # 因為平行處理所以就不設 'filename' 這種多個函式會共用的變數了哈

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

def writeInputs_m1(i, j, k, m):
    # value in .inp
    Tkin_coe_here = Tkin_coe[i % num_Tkin_coe]
    Tkin_exp_here = i//num_Tkin_coe + int(Tkin_exp[0])
    nH2_coe_here  = Nco_coe[j % num_Nco_coe] # Nco_coe 數字上等於 nH2_coe, 因為 nH2 & Nco's step相等
    nH2_exp_here  = j//num_Nco_coe + int(nH2_exp[0])
    Nco_coe_here  = round(X1213_inv[m] * Nco_coe[k % num_Nco_coe], 4)
    Nco_exp_here  = k//num_Nco_coe + int(Nco_exp[0])

    # _fn for fileName, round() used :)
    Tkin_fn = f'{round(step_Tkin_exp * i + int(Tkin_exp[0]), round_Tkin)}'
    nH2_fn  = f'{round(nH2_coe_here, round_Nco)}e{nH2_exp_here}' 
    Nco_fn  = f'{round(Nco_coe_here, round_Nco)}e{Nco_exp_here}'
    X1213_here = X1213[m]

    # write info into .inp file 
    file = open(f'{radexioPath}/input_{model_5d}_{mole_1}/{Tkin_fn}_{nH2_fn}_{Nco_fn}_{X1213_here}.inp', 'w')
    file.write(f'{mole_1}.dat\n')
    file.write(f'{radexioPath}/output_{model_5d}_{mole_1}/{Tkin_fn}_{nH2_fn}_{Nco_fn}_{X1213_here}.out\n')

    file.write('100 400'+'\n')                       ### output frequency range (GHz)
    file.write(f'{Tkin_coe_here}e{Tkin_exp_here}\n') ### kinetic temperature (K)
    file.write('1\n')                                #   number of collision partners
    file.write('H2\n')                               #   first collision partner
    file.write(f'{nH2_coe_here}e{nH2_exp_here}\n')   ### density of first collision partner (cm^-3)
    file.write('2.73'+'\n')                          #   temperature of background radiation
    file.write(f'{Nco_coe_here}e{Nco_exp_here}\n')   ### molecular column density (cm^-2)
    file.write(f'{linewidth}\n')                     #   line width (km/s)
    file.write('0\n')                                #   run another calculation (or not, y/n = 1/0)
    file.close() # aftercare
   
def writeInputs_m2(i, j, k, m, n):
    # value in .inp
    Tkin_coe_here = Tkin_coe[i % num_Tkin_coe]
    Tkin_exp_here = i//num_Tkin_coe + int(Tkin_exp[0])
    nH2_coe_here  = Nco_coe[j % num_Nco_coe] # Nco_coe 數字上等於 nH2_coe, 因為 nH2 & Nco's step相等
    nH2_exp_here  = j//num_Nco_coe + int(nH2_exp[0])
    Nco_coe_here  = round(X1318_inv[n] * X1213_inv[m] * Nco_coe[k%num_Nco_coe], 4)
    Nco_exp_here  = k//num_Nco_coe + int(Nco_exp[0])

    # _fn for fileName, round() used :)
    Tkin_fn = f'{round(step_Tkin_exp * i + int(Tkin_exp[0]), round_Tkin)}'
    nH2_fn  = f'{round(nH2_coe_here, round_Nco)}e{nH2_exp_here}' 
    Nco_fn  = f'{round(Nco_coe_here, round_Nco)}e{Nco_exp_here}'
    X1213_here = X1213[m]
    X1318_here = X1318[n]

    # write info into .inp file 
    file = open(f'{radexioPath}/input_{model_5d}_{mole_2}/{Tkin_fn}_{nH2_fn}_{Nco_fn}_{X1213_here}_{X1318_here}.inp', 'w')
    file.write(f'{mole_2}.dat\n')
    file.write(f'{radexioPath}/output_{model_5d}_{mole_2}/{Tkin_fn}_{nH2_fn}_{Nco_fn}_{X1213_here}_{X1318_here}.out\n')

    file.write('100 400'+'\n')                       ### output frequency range (GHz)
    file.write(f'{Tkin_coe_here}e{Tkin_exp_here}\n') ### kinetic temperature (K)
    file.write('1\n')                                #   number of collision partners
    file.write('H2\n')                               #   first collision partner
    file.write(f'{nH2_coe_here}e{nH2_exp_here}\n')   ### density of first collision partner (cm^-3)
    file.write('2.73'+'\n')                          #   temperature of background radiation
    file.write(f'{Nco_coe_here}e{Nco_exp_here}\n')   ### molecular column density (cm^-2)
    file.write(f'{linewidth}\n')                     #   line width (km/s)
    file.write('0\n')                                #   run another calculation (or not, y/n = 1/0)
    file.close() # aftercare

# --------------------------------- def runRADEX_m*(): -------------------------------- #
def runRADEX_m0(i, j, k):
    # _fn for fileName
    Tkin_fn = f'{round(step_Tkin_exp * i + int(Tkin_exp[0]), round_Tkin)}'
    nH2_fn  = f'{round(Nco_coe[j%num_Nco_coe], round_Nco)}e{j//num_Nco_coe + int(nH2_exp[0])}' 
    Nco_fn  = f'{round(Nco_coe[k%num_Nco_coe], round_Nco)}e{k//num_Nco_coe + int(Nco_exp[0])}'
    # os command
    radexOut = os.system(f'radex < {radexioPath}/input_{model_5d}_{mole_0}/{Tkin_fn}_{nH2_fn}_{Nco_fn}.inp')
    return radexOut

def runRADEX_m1(i, j, k, m):
    # _fn for fileName
    Tkin_fn = f'{round(step_Tkin_exp * i + int(Tkin_exp[0]), round_Tkin)}'
    nH2_fn  = f'{round(Nco_coe[j%num_Nco_coe], round_Nco)}e{j//num_Nco_coe + int(nH2_exp[0])}' 
    Nco_fn  = f'{round(Nco_coe[k%num_Nco_coe], round_Nco)}e{k//num_Nco_coe + int(Nco_exp[0])}'
    X1213_here = X1213[m]
    # os command
    radexOut = os.system(f'radex < {radexioPath}/input_{model_5d}_{mole_1}/{Tkin_fn}_{nH2_fn}_{Nco_fn}_{X1213_here}.inp')
    return radexOut

def runRADEX_m2(i, j, k, m, n):
    # _fn for fileName
    Tkin_fn = f'{round(step_Tkin_exp * i + int(Tkin_exp[0]), round_Tkin)}'
    nH2_fn  = f'{round(Nco_coe[j%num_Nco_coe], round_Nco)}e{j//num_Nco_coe + int(nH2_exp[0])}' 
    Nco_fn  = f'{round(Nco_coe[k%num_Nco_coe], round_Nco)}e{k//num_Nco_coe + int(Nco_exp[0])}'
    X1213_here = X1213[m]
    X1318_here = X1318[n]
    # os command
    radexOut = os.system(f'radex < {radexioPath}/input_{model_5d}_{mole_2}/{Tkin_fn}_{nH2_fn}_{Nco_fn}_{X1213_here}_{X1318_here}.inp')
    return radexOut


# --------------- Use Functions write_inputs_m*() for molecules0,1,2 ------------------- #
print('Start to write .inp files...')
Parallel(n_jobs = num_cores)(
    delayed(writeInputs_m0)(i, j, k)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )              
Parallel(n_jobs = num_cores)(
    delayed(writeInputs_m1)(i, j, k, m)
    for m in range(0, num_X1213)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )
Parallel(n_jobs = num_cores)(
    delayed(writeInputs_m2)(i, j, k, m, n)
    for n in range(0, num_X1318)
    for m in range(0, num_X1213)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )
input_time = time.time()
print(f'It took {(input_time - start_time):.2f} seconds to write all .inp files.')

# ------------------------- Run RADEX for molecules 0,1,2 ------------------------------ #
print('Start RADEXing ...')
Parallel(n_jobs = num_cores)(
    delayed(runRADEX_m0)(i, j, k)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )  
Parallel(n_jobs = num_cores)(
    delayed(runRADEX_m1)(i, j, k, m)
    for m in range(0, num_X1213)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )          
Parallel(n_jobs = num_cores)(
    delayed(runRADEX_m2)(i, j, k, m, n)
    for n in range(0, num_X1318)
    for m in range(0, num_X1213)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )

radex_time = time.time()
print(f'It took {(radex_time - input_time):.2f} seconds to finish running RADEX.')


### ----------------------------- Save Models into .npy Files ------------------------------- ###
# --------------------------- def radex_flux(): **from bayes repo** ---------------------------- #
def extractFlux(i, j, k, m, n):
    Tkin_fn = f'{round(step_Tkin_exp * i + int(Tkin_exp[0]), round_Tkin)}'
    nH2_fn  = f'{round(Nco_coe[j%num_Nco_coe], round_Nco)}e{j//num_Nco_coe + int(nH2_exp[0])}' 
    Nco_fn  = f'{round(Nco_coe[k%num_Nco_coe], round_Nco)}e{k//num_Nco_coe + int(Nco_exp[0])}'
    X1213_here = X1213[m]
    X1318_here = X1318[n]
    
    outfile_0 = f'{radexioPath}/output_{model_5d}_{mole_0}/{Tkin_fn}_{nH2_fn}_{Nco_fn}.out'
    outfile_1 = f'{radexioPath}/output_{model_5d}_{mole_1}/{Tkin_fn}_{nH2_fn}_{Nco_fn}_{X1213_here}.out'
    outfile_2 = f'{radexioPath}/output_{model_5d}_{mole_2}/{Tkin_fn}_{nH2_fn}_{Nco_fn}_{X1213_here}_{X1318_here}.out'
    
    # Extract reliable flux predictions (avoid those with convergence issues)
    if np.loadtxt(outfile_0, skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_0 = np.full((3,), np.nan)
    else:
        flux_0 = np.genfromtxt(outfile_0, skip_header=13)[:,11]

    if np.loadtxt(outfile_1, skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_1 = np.full((3,), np.nan)
    else:    
        flux_1 = np.genfromtxt(outfile_1, skip_header=13)[:,11]

    if np.loadtxt(outfile_2, skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_2 = np.full((3,), np.nan)
    else:    
        flux_2 = np.genfromtxt(outfile_2, skip_header=13)[:,11]
    
    return k, i, j, m, n, flux_0, flux_1, flux_2

# --------------------------------------- Run extractFlux(): ------------------------------------ #
print('Constructing flux model grids...')
results = Parallel(n_jobs=num_cores, verbose=5)(
    delayed(extractFlux)(i, j, k, m, n)
    for n in range(0, num_X1318)
    for m in range(0, num_X1213)
    for k in range(num_Nco_exp)
    for j in range(num_nH2_exp)
    for i in range(num_Tkin_exp)
    )

# -------------------------------- Containers for File Saving ----------------------------------- #
transis = ['10', '21', '32'] # (i think) model grids should cover everything
mole_info = [  # molespiece, (initial flux array's shape)
    ('co',   (num_Nco_exp, num_Tkin_exp, num_nH2_exp)),
    ('13co', (num_Nco_exp, num_Tkin_exp, num_nH2_exp, num_X1213)),
    ('c18o', (num_Nco_exp, num_Tkin_exp, num_nH2_exp, num_X1213, num_X1318)),
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
                flux_model[f'{molesp}-{t}']["flux"][k, i, j] = flux_data[m_idx][t_idx]
            elif molesp == '13co':
                flux_model[f'{molesp}-{t}']["flux"][k, i, j, m] = flux_data[m_idx][t_idx]
            elif molesp == 'c18o':
                flux_model[f'{molesp}-{t}']["flux"][k, i, j, m, n] = flux_data[m_idx][t_idx]

'''
保留這個東西因為這個太他媽懸吊了
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
            cache = np.repeat(theFlux[:,:,:, np.newaxis], num_X1213, axis=3) # used to be 'temp'
            theFlux_5d = np.repeat(cache[:,:,:,:, np.newaxis], num_X1318, axis=4)
        elif molesp == '13co':
            theFlux_5d = np.repeat(theFlux[:,:,:,:, np.newaxis], num_X1318, axis=4)
        elif molesp == 'c18o':
            theFlux_5d = theFlux
        flux_model[f'{molesp}-{t}']["flux_5d"] = theFlux_5d

for molename in flux_model.keys(): # Save "flux_5d" into .npy
    np.save(f'{npyPath}/flux_{model_5d}_{molename}.npy', flux_model[molename]["flux_5d"]) # (filename) modi by qing (20260317)

ratio5d_time = time.time()

# ---------------------------------- Construct 6D Flux Models --------------------------------- #
'''
以下的部分不是 radex_pipeline.py 了
來自 flux_model_6d.py, Eltha
不知道為什麼 Eltha 女士要分開寫, 但是合在一起同樣能避免要再設一次一桶變數的問題
'''
beam_fill = 10 ** np.arange(-1.3, 0.1, 0.1)
beamFactor = beam_fill.reshape(1, 1, 1, 1, 1, beam_fill.shape[0]) # factor 是亂叫的

# Construct 6d-flux models from 5d by adding the beam filling factor dimension
for molesp, _ in mole_info:
    for t in transis:
        theFlux_5d = flux_model[f'{molesp}-{t}']["flux_5d"]
        theFlux_6d = theFlux_5d.reshape(num_Nco_exp, num_Tkin_exp, num_nH2_exp,
                                        num_X1213, num_X1318,1) * beamFactor
        flux_model[f'{molesp}-{t}']["flux_6d"] = theFlux_6d

for molename in flux_model.keys(): # Save "flux_6d" into .npy
    np.save(f'{npyPath}/flux_{model_6d}_{molename}.npy', flux_model[molename]["flux_6d"])
print('Flux_6d models saved.')
flux6d_time = time.time()

### ------------------------------- Write Time Records ------------------------------------ ###
timerec = open(f'{projectRoot}/docs/radex-pipeline_timeRecord.txt', 'w') # made by qing (20260113)
timerec.write(f'It took {(input_time - start_time):.2f} seconds to write all .inp files.\n')
timerec.write(f'It took {(radex_time - input_time):.2f} seconds to finish running RADEX.\n')
timerec.write(f'It took {(fluxini_time - radex_time):.2f} seconds to save 3d, 4d, 5d flux models.\n')
timerec.write(f'It took {(ratio5d_time - fluxini_time):.2f} seconds to save 5d ratio models.\n')
timerec.write(f'It took {(flux6d_time - ratio5d_time):.2f} seconds to save 6d flux models.\n')
timerec.close()

print('Sincere congratulations! This script arrived here without any obstacles. <3')