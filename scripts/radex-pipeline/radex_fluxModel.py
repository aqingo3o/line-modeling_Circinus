# Script for feifei or blackhole.
# Put this script under {projectRoot}, (i.e. /home/aqing/Documents/line-modleing_Circiuns/)
# Remaining dependency paths will be created automatically.
'''
因為一些發現, 總之要自己寫這個程式了, 不知道是大事很妙還是大事不妙
雖然這個程式並非出現在工作的前期 (也就是我已經擁有熟成的檔案結構)
但為了後續復現的方便 && 這隻程式高度資料夾路徑依賴
為了防止程式開始跑了才發現很多東西不存在, 我保留了自動建立檔案結構的部分。

程式湯底來自 Eltha 女士的 radex_pipeline.py, flux_model_6d.py, 
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

# ------------------------------- Import Module ------------------------------- #
from joblib import Parallel, delayed
import numpy as np
import os
from pathlib import Path
import time

# -------------------------- Build Folder Structure ---------------------------- #
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

# ------------------------------- Path Variables ---------------------------------- #
projectRoot = '/home/aqing/Documents/line-modeling_Circinus' # blackhole
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
radexioPath = f'{projectRoot}/data/radex_io' # a VAST number of files
npyPath = f'{projectRoot}/data/model_npy'    # extracted flux model
d_with_bf = '5d' # model's dimensiom with beam filling factor

### ------------------------------ RADEX Pipeline ------------------------------- ###
start_time = time.time()
# -------------------------------- Basic Variables -------------------------------- #
num_cores = 20 # joblib
linewidth = 300 # km/s
mole0 = 'co'
mole1 = '13co'
mole2 = 'c18o'

# ------------------------- Set Physical Conditions Range ---------------------------- #
'''
就這邊的東西可以改,
應該說下面可以改的東西就剩檔名了
'''
expstep_Tk = 0.1
expstep_nH2 = 0.2
expstep_Nco = expstep_nH2 # step size for Nco and nH2 should be the same (idky)
'''
stepex_*: 指數部分的 step
i.e. Tkin -> 10^1, 10^1.1, 10^1.2, ... 10^2.7
'''
'''
Tk_exp = np.arange(1., 2.8,  step=expstep_Tk)    # 前面的經驗說, 要從整數開始 but idky
nH2_exp = np.arange(2.,  6.1,  step=expstep_nH2) # 多的那 .1 是因為 arange() 會在終點前停下
Nco_exp = np.arange(15., 20.1, step=expstep_Nco) # 多家的那一點(小於step)是為了確保能停在預期的數字
'''
# FOR TEST
Tk_exp = np.arange(1., 1.6,  step=expstep_Tk)
nH2_exp = np.arange(2.,  3.7,  step=expstep_nH2)
Nco_exp = np.arange(15., 16.1, step=expstep_Nco)
# FOR TEST

Tk_coe = np.arange(1, 10, step=1)
nH2_coe = np.arange(1, 10, step=1)
Nco_coe = np.arange(1, 10, step=1) # 先這樣試試?

X_13co = np.arange(10, 126, step=10)
X_c18o = np.arange(2, 21,   step=1)

# ----------------------------------- Pre-processing -------------------------------- #
factors_13co = 1./X_13co  
factors_c18o = 1./X_c18o

num_Tk_exp = len(Tk_exp)
num_nH2_exp = len(nH2_exp)
num_Nco_exp = len(Nco_exp)
num_Tk_coe = len(Tk_coe)
num_nH2_coe = len(nH2_coe)
num_Nco_coe = len(Nco_coe)
num_X1213 = len(X_13co)
num_X1318 = len(X_c18o)

# ------------------------------- def writeInputs_m*(): ------------------------------ #
def writeInputs_m0(i, j, k):
    pow_Tk = i//num_Tk_coe + int(Tk_exp[0])
    Tk = round(expstep_Tk*i + int(Tk_exp[0]), 1)
    pow_nH2 = j//num_nH2_coe + int(nH2_exp[0])
    pow_Nco = k//num_Nco_coe + int(Nco_exp[0])
    
    pre_Tk = Tk_coe[i%num_Tk_coe]
    pre_nH2 = str(nH2_coe[j%num_nH2_coe])
    pre_Nco = Nco_coe[k%num_Nco_coe]

    file = open(f'{radexioPath}/input_{mole0}/{Tk}_{round(pre_nH2, 1)}e{pow_nH2}_{round(pre_Nco, 1)}e{pow_Nco}.inp', 'w')
    file.write(f'{mole0}.dat\n')
    file.write(f'{radexioPath}/output_{mole0}/{Tk}_{round(pre_nH2, 1)}e{pow_nH2}_{round(pre_Nco, 1)}e{pow_Nco}.out\n')
    file.write('100 400\n')
    file.write(f'{pre_Tk}e{pow_Tk}\n')
    file.write('1\n')
    file.write('H2\n')
    file.write(f'{pre_nH2}e{pow_nH2}\n')
    file.write('2.73'+'\n')
    file.write(f'{pre_Nco}e{pow_Nco}\n')
    file.write(linewidth+'\n')
    file.write('0\n')
    file.close() 

def write_inputs_m1(i,j,k,m):
    powi = str(i//cycle_temp + int(Tk_exp[0]))
    Tk = str(round(expstep_Tk*i + int(Tk_exp[0]), round_temp))
    powj = j//cycle_dens + int(nH2_exp[0])
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco_exp[0]))
    
    prei = str(Tk_dex[i%cycle_temp])
    prej = str(co_dex[j%cycle_dens])
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    prek = str(round(factors_13co[m]*co_dex[k%cycle_dens],4))
    x13co = str(X_13co[m])
    codex = str(round(co_dex[k%cycle_dens], round_dens))

    file = open(f'{radexioPath}/input_{mole1}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}.inp', 'w')
    file.write(f'{mole1}.dat\n')
    file.write(f'{radexioPath}/output_{mole1}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}.out\n')
    file.write('100'+' '+'400'+'\n')
    file.write(prei+'e'+powi+'\n')
    file.write('1\n')
    file.write('H2\n')
    file.write(prej+'e'+n_h2+'\n')
    file.write('2.73'+'\n')
    file.write(prek+'e'+N_co+'\n')
    file.write(linewidth+'\n')
    file.write('0\n')
    file.close()   

def write_inputs_m2(i,j,k,m,n):
    powi = str(i//cycle_temp + int(Tk_exp[0]))
    Tk = str(round(expstep_Tk*i + int(Tk_exp[0]), round_temp))
    powj = j//cycle_dens + int(nH2_exp[0])
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco_exp[0]))
    
    prei = str(Tk_dex[i%cycle_temp])
    prej = str(co_dex[j%cycle_dens])
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    prek = str(round(factors_c18o[n]*factors_13co[m]*co_dex[k%cycle_dens],6))
    x13co = str(X_13co[m])
    xc18o = str(X_c18o[n])
    codex = str(round(co_dex[k%cycle_dens], round_dens))

    file = open(f'{radexioPath}/input_{mole2}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}_{xc18o}.inp', 'w')
    file.write(f'{mole2}.dat\n')
    file.write(f'{radexioPath}/output_{mole2}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}_{xc18o}.out\n')
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

# --------------------------------- def run_radex_m*(): -------------------------------- #
def run_radex_m0(i,j,k):
    powj = j//cycle_dens + int(nH2[0])
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    codex = str(round(co_dex[k%cycle_dens], round_dens))
    run = os.system(f'radex < {radexioPath}/input_{mole0}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}.inp')
    return run

def run_radex_m1(i,j,k,m):
    powj = j//cycle_dens + int(nH2[0])
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    x13co = str(X_13co[m])
    codex = str(round(co_dex[k%cycle_dens], round_dens)) 
    run = os.system(f'radex < {radexioPath}/input_{mole1}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}.inp')
    return run

def run_radex_m2(i,j,k,m,n):
    powj = j//cycle_dens + int(nH2[0])
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))    
    x13co = str(X_13co[m])
    xc18o = str(X_c18o[n])
    codex = str(round(co_dex[k%cycle_dens], round_dens))  
    run = os.system(f'radex < {radexioPath}/input_{mole2}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}_{xc18o}.inp')
    return run

"""
# --------------- Use Functions write_inputs_m*() for molecules0,1,2 ------------------- #
print('Start to write .inp files...')
Parallel(n_jobs=num_cores)(
    delayed(write_inputs_m0)(i,j,k)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )              
Parallel(n_jobs=num_cores)(
    delayed(write_inputs_m1)(i,j,k,m)
    for m in range(0,num_X12to13)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )
Parallel(n_jobs=num_cores)(
    delayed(write_inputs_m2)(i,j,k,m,n)
    for n in range(0,num_X13to18)
    for m in range(0,num_X12to13)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )
input_time = time.time()
print(f'It took {(input_time - start_time):.2f} seconds to write all .inp files.')

# ------------------------- Run RADEX for molecules 0,1,2 ------------------------------ #
print('Start RADEXing ...')
Parallel(n_jobs=num_cores)(
    delayed(run_radex_m0)(i,j,k)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )  
Parallel(n_jobs=num_cores)(
    delayed(run_radex_m1)(i,j,k,m)
    for m in range(0,num_X12to13)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )          
Parallel(n_jobs=num_cores)(
    delayed(run_radex_m2)(i,j,k,m,n)
    for n in range(0,num_X13to18)
    for m in range(0,num_X12to13)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )
radex_time = time.time()
print(f'It took {(radex_time - input_time):.2f} seconds to finish running RADEX.')


### ----------------------------- Save Models into .npy Files ------------------------------- ###
# --------------------------- def radex_flux(): **from bayes repo** ---------------------------- #
def radex_flux(i,j,k,m,n):
    powj = j//cycle_dens + int(nH2[0])
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))   
    x13co = str(X_13co[m])
    xc18o = str(X_c18o[n])
    codex = str(round(co_dex[k%cycle_dens], round_dens))

    outfile_0 = f'{radexioPath}/output_{mole0}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}.out'
    outfile_1 = f'{radexioPath}/output_{mole1}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}.out'
    outfile_2 = f'{radexioPath}/output_{mole2}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}_{xc18o}.out'

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

# --------------------------------------- Run radex_flux(): ------------------------------------ #
print('Constructing flux model grids...')
results = Parallel(n_jobs=num_cores, verbose=5)(
    delayed(radex_flux)(i,j,k,m,n)
    for n in range(0, num_X13to18)
    for m in range(0, num_X12to13)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )

# -------------------------------- Containers for File Saving ----------------------------------- #
transis = ['10', '21', '32'] # (i think) model grids should cover everything
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