# Can be run on Lab machine(ubuntu) or feifei(macOS)
# Auto set the folder structure
# You MUST put this script under your project root (i.e. ~/line-modeling_Circinus/thisScript.py)
# 對如果要把這個腳本放進 projectRoot/scripts/ 的話, 請跑完之後再放, 雖然很怪洨但先這樣吧?
'''
程式湯底來自 Eltha 女士的 radex_pipeline.py, flux_model_6d.py, 
對標寒假的工作算是 radex-pipeline_setFolder-modiPath-add6d.py, 
盡量的改變了檔案命名的方式, 但因為牽涉到平行處理, 有些地方我不敢亂動
果然不是親自寫的程式用起來多半有點不安心...

最前面的部分包含了設定整個工作空間的資料夾結構 (make_projectRoot.py && make_folders.py)
因為 radex-pipeline 系列的工作會有很多寫入檔案的機會, 所以對於相同命名的環境要求有點多
因此, 就算還沒有開始處理 cube, moment maps, 也可以先跑這支程式喔
----------------------------------------------------------------------------------
然後這支程式真的狗幹長, 所以提供了目錄
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
- Construct 5D Ratio Models
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
radexioPath = f'{projectRoot}/data/radex_io' # 巨幅檔案數目的那個
npyPath = f'{projectRoot}/data/model_npy'    # extract flux 的那些
model_5d = '5d-coarse2' # level3 那邊相依的, 至今未知用途...
model_6d = '6d-coarse2'

### ------------------------------ RADEX Pipeline ------------------------------- ###
start_time = time.time()
# -------------------------------- Basic Variables -------------------------------- #
num_cores = 20 # joblib
linewidth = 15 # km/s
molecule_0 = 'co'
molecule_1 = '13co'
molecule_2 = 'c18o'

# ----------------------------- Physical Conditions Grid ---------------------------- #
Nco = np.arange(15., 20.1, 0.2)
Tkin = np.arange(1., 2.8, 0.1)
nH2 = np.arange(2., 5.1, 0.2) # step size for Nco and nH2 should be the same
X_13co = np.arange(10, 205, 10)
X_c18o = np.arange(2, 21, 1)
round_dens, round_temp = 1, 1

# ----------------------------------- Pre-processing -------------------------------- #
incr_dens = round(Nco[1] - Nco[0],1)
incr_temp = round(Tkin[1] - Tkin[0],1)
diff_Tk = Tkin[1] - Tkin[0]
co_dex = np.round(10**np.arange(0.,1.,incr_dens), 4)
Tk_dex = np.round(10**np.arange(0.,1.,incr_temp), 4)
factors_13co = 1./X_13co  
factors_c18o = 1./X_c18o
num_Nco = Nco.shape[0]
num_Tk = Tkin.shape[0]
num_nH2 = nH2.shape[0]
cycle_dens = co_dex.shape[0]
cycle_temp = Tk_dex.shape[0]
num_X12to13 = X_13co.shape[0]
num_X13to18 = X_c18o.shape[0]

# ------------------------------- def write_inputs_m*(): ------------------------------ #
def write_inputs_m0(i,j,k):
    powi = str(i//cycle_temp + int(Tkin[0]))
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    powj = j//cycle_dens + int(nH2[0])
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prei = str(Tk_dex[i%cycle_temp])
    prej = str(co_dex[j%cycle_dens])
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    prek = str(co_dex[k%cycle_dens])
    codex = str(round(co_dex[k%cycle_dens], round_dens))

    file = open(f'{radexioPath}/input_{model_5d}_{molecule_0}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}.inp', 'w')
    file.write(molecule_0+'.dat\n')
    file.write(f'{radexioPath}/output_{model_5d}_{molecule_0}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}.out\n')
    # 因為平行處理所以就不設 'filename' 這種多個函式會共用的變數了哈
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

def write_inputs_m1(i,j,k,m):
    powi = str(i//cycle_temp + int(Tkin[0]))
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    powj = j//cycle_dens + int(nH2[0])
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prei = str(Tk_dex[i%cycle_temp])
    prej = str(co_dex[j%cycle_dens])
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    prek = str(round(factors_13co[m]*co_dex[k%cycle_dens],4))
    x13co = str(X_13co[m])
    codex = str(round(co_dex[k%cycle_dens], round_dens))

    file = open(f'{radexioPath}/input_{model_5d}_{molecule_1}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}.inp', 'w')
    file.write(molecule_1+'.dat\n')
    file.write(f'{radexioPath}/output_{model_5d}_{molecule_1}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}.out\n')
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

def write_inputs_m2(i,j,k,m,n):
    powi = str(i//cycle_temp + int(Tkin[0]))
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    powj = j//cycle_dens + int(nH2[0])
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prei = str(Tk_dex[i%cycle_temp])
    prej = str(co_dex[j%cycle_dens])
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    prek = str(round(factors_c18o[n]*factors_13co[m]*co_dex[k%cycle_dens],6))
    x13co = str(X_13co[m])
    xc18o = str(X_c18o[n])
    codex = str(round(co_dex[k%cycle_dens], round_dens))

    file = open(f'{radexioPath}/input_{model_5d}_{molecule_2}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}_{xc18o}.inp', 'w')
    file.write(molecule_2+'.dat\n')
    file.write(f'{radexioPath}/output_{model_5d}_{molecule_2}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}_{xc18o}.out\n')
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
    run = os.system(f'radex < {radexioPath}/input_{model_5d}_{molecule_0}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}.inp')
    return run

def run_radex_m1(i,j,k,m):
    powj = j//cycle_dens + int(nH2[0])
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    x13co = str(X_13co[m])
    codex = str(round(co_dex[k%cycle_dens], round_dens)) 
    run = os.system(f'radex < {radexioPath}/input_{model_5d}_{molecule_1}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}.inp')
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
    run = os.system(f'radex < {radexioPath}/input_{model_5d}_{molecule_2}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}_{xc18o}.inp')
    return run

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

    outfile_0 = f'{radexioPath}/output_{model_5d}_{molecule_0}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}.out'
    outfile_1 = f'{radexioPath}/output_{model_5d}_{molecule_1}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}.out'
    outfile_2 = f'{radexioPath}/output_{model_5d}_{molecule_2}/{Tk}_{prej_r}e{n_h2}_{codex}e{N_co}_{x13co}_{xc18o}.out'

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
            cache = np.repeat(theFlux[:,:,:, np.newaxis], num_X12to13, axis=3) # used to be 'temp'
            theFlux_5d = np.repeat(cache[:,:,:,:, np.newaxis], num_X13to18, axis=4)
        elif molesp == '13co':
            theFlux_5d = np.repeat(theFlux[:,:,:,:, np.newaxis], num_X13to18, axis=4)
        elif molesp == 'c18o':
            theFlux_5d = theFlux
        flux_model[f'{molesp}-{t}']["flux_5d"] = theFlux_5d

for molename in flux_model.keys(): # Save "flux_5d" into .npy
    np.save(f'{npyPath}/flux_{model_5d}_{molename}.npy', flux_model[molename]["flux_5d"]) # (filename) modi by qing (20260317)

# -------------------------------- Construct 5D Ratio Models ------------------------------------- #
# 這邊不知道怎麼辦，但是沒關係因為這邊後面用不到
# 想一下怎麼讀出來就好立
'''
ratio_co = co21_5d/co10_5d
ratio_13co = c13o_32_5d/c13o_21_5d
ratio_c18o = flux_c18o32/flux_c18o21
ratio_co213co = co21_5d/c13o_21_5d
ratio_co2c18o = co21_5d/flux_c18o21
ratio_13co2c18o_21 = c13o_21_5d/flux_c18o21
ratio_13co2c18o_32 = c13o_32_5d/flux_c18o32

# 這邊真沒招...還得想想
np.save(f'{npyPath}/ratio_{model_5d}_co-21_over_co-10.npy',     ratio_co) # (filename) modi by qing (20260113)
np.save(f'{npyPath}/ratio_{model_5d}_13co-32_over_13co-21.npy', ratio_13co)
np.save(f'{npyPath}/ratio_{model_5d}_c18o-32_over_c18o-21.npy', ratio_c18o)
np.save(f'{npyPath}/ratio_{model_5d}_co-21_over_c13o-21.npy',   ratio_co213co)
np.save(f'{npyPath}/ratio_{model_5d}_co-21_over_c18o-21.npy',   ratio_co2c18o)
np.save(f'{npyPath}/ratio_{model_5d}_13co-21_over_c18o-21.npy', ratio_13co2c18o_21)
np.save(f'{npyPath}/ratio_{model_5d}_13co-32_over_c18o-32.npy', ratio_13co2c18o_32)
print('Ratio models saved.')
'''
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