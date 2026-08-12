# Script for feifei or blackhole.
# Put this script under {projectRoot}, (i.e. /home/aqing/Documents/line-modleing_Circiuns/)
# Remaining dependency paths will be created automatically.
'''
因為一些發現, 總之要自己寫這個程式了, 不知道是大事很妙還是大事不妙
雖然這個程式並非出現在工作的前期 (也就是我已經擁有熟成的檔案結構)
但為了後續復現的方便 && 這隻程式高度資料夾路徑依賴
為了防止程式開始跑了才發現很多東西不存在, 我保留了自動建立檔案結構的部分。

然後靠北我根本不知道這是不是對的, 幹

程式湯底來自 Eltha 女士的 radex_pipeline.py

Current version remove two *Abudance Ratio* as member of model grid.
Because I'm not sure if we need abudance ratio for science purpose or not.
Fewer fitting parameters may led to something good?
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

# -------------------------- Path Variables -------------------------- #
radexioPath = f'{projectRoot}/data/radex_io' # a VAST number of files
npyPath = f'{projectRoot}/data/model_npy'    # extracted flux model

start_time = time.time()
# ------------------------- Basic Variables ------------------------- #
num_cores = 20  # joblib
linewidth = 300 # km/s
phy_para = ['Kinetic Temperature', 'Number Density', 'Column Density'] # keys of model_grid
mole_species = ['co', '13co', 'c18o']
transis = ['10', '21', '32', '43'] # (i think) model grids should cover everything

# ----------------- Set Physical Conditions Range ------------------- #
expstep_Tk = 0.1
expstep_nH2 = 0.2
expstep_Nco = expstep_nH2 # step size for Nco and nH2 should be the same (idky)
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

# ------------------------- Pre-processing ------------------------- #
for paraname in phy_para:
    aeb = []
    for fexp in model_grid[paraname]["fracExp"]:
        coe = 10 ** (fexp - int(fexp)) # frac-part of fexp will turn into pre(coe
        aeb.append(f'{round(coe, 4)}e{int(fexp)}')
    model_grid[paraname]["AeB"] = np.array(aeb)

# ------------------------- writeInputs(): ------------------------- #
def writeInputs(molesp, Tk, nH2, Nco):
    file = open(f'{radexioPath}/input_{molesp}/{Tk}_{nH2}_{Nco}.inp', 'w')
    file.write(f'{molesp}.dat\n')
    file.write(f'{radexioPath}/output_{molesp}/{Tk}_{nH2}_{Nco}.out\n')
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

for molesp in mole_species:
    print(f'Writing .inp files for {molesp} ...')
    Parallel(n_jobs=num_cores)(
        delayed(writeInputs)(molesp, Tk ,nH2, Nco)
        for Nco in model_grid["Column Density"]["AeB"]
        for nH2 in model_grid["Number Density"]["AeB"]
        for Tk in model_grid["Kinetic Temperature"]["AeB"]
        )
input_time = time.time()
print(f'It took {(input_time - start_time):.2f} seconds to write all .inp files.')
print()

# --------------------------- runRADEX(): -------------------------- #
def runRADEX(molesp, Tk ,nH2, Nco):
    inpPath = f'{radexioPath}/input_{molesp}/{Tk}_{nH2}_{Nco}.inp'
    # create tempoary indep-folder for each caculation, avoiding "Error open radex.log"
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(inpPath, 'r') as inpFile:
            subprocess.run(
                ['radex'],     # the command
                stdin=inpFile, # equal to "< input.inp" of Shell
                cwd=temp_dir,
                stdout=subprocess.DEVNULL, # Silence terminal message I/O
                stderr=subprocess.DEVNULL,
            )

for molesp in mole_species:
    print(f'Start RADEXing for {molesp} ...')
    Parallel(n_jobs=num_cores)(
        delayed(runRADEX)(molesp, Tk ,nH2, Nco)
        for Nco in model_grid["Column Density"]["AeB"]
        for nH2 in model_grid["Number Density"]["AeB"]
        for Tk in model_grid["Kinetic Temperature"]["AeB"]
        )
radex_time = time.time()
print(f'It took {(radex_time - input_time):.2f} seconds to finish running RADEX.')
print()

# ------------------------- Get Model Flux ------------------------- #
flux_model = {}
def getMflux(molesp, Tk, nH2, Nco):
    physet = f'{Tk}_{nH2}_{Nco}'
    outFile = f'{radexioPath}/output_{molesp}/{physet}.out'
    # Extract reliable flux predictions (avoid those with convergence issues)
    if np.loadtxt(outFile, skiprows=10, max_rows=1, dtype='str')[3] == '****':
        mflux = np.full(len(transis), np.nan)
        print(f'{outFile} has converage issue :(') # 這邊像要做一個寫入啊哈, 但不是必要的
    else:
        mflux = np.genfromtxt(outFile, skip_header=13)[:, 11]
    return physet, mflux

for molesp in mole_species:
    print(f"Extracting model flux from {molesp}'s output files...")
    resultset = Parallel(n_jobs=num_cores)( # 這邊要用東西裝 return, resultset -> [physet, ]
                    delayed(getMflux)(molesp, Tk ,nH2, Nco)
                    for Nco in model_grid["Column Density"]["AeB"]
                    for nH2 in model_grid["Number Density"]["AeB"]
                    for Tk in model_grid["Kinetic Temperature"]["AeB"]
                    )
    for t_idx in range(len(transis)):
        mfluxArray = []
        for _, mflux in resultset:
            mfluxArray.append(mflux[t_idx])

        flux_model[f'{molesp}-{transis[t_idx]}'] = {
            "Flux Model": np.array(mfluxArray),
        }

# Turn physical conditions value into array and save as .npy
phyArray = []
for physet, _ in resultset:
    phyArray_sub = []
    for phy in physet.split('_'):
        phyArray_sub.append(float(phy)) # follow the order: Tk, nH2, Nco
    phyArray.append(phyArray_sub)
np.save(f'{npyPath}/phy_plain-model_Tk-nH2-Nco.npy', np.array(phyArray))

# Save ["Flux Model"] as .npy
for molename in flux_model.keys():
    np.save(f'{npyPath}/flux_plain-model_{len(phy_para)}para_{molename}.npy',
            flux_model[molename]["Flux Model"])
inimodel_time = time.time()
print('Flux models and physical condition array are saved.')

# ----------------------- Write Time Records ----------------------- #
timerec = open(f'{projectRoot}/docs/radex-pipeline_timeRecord.txt', 'w')
timerec.write(f'It took {(input_time - start_time):.2f} seconds to write all .inp files.\n')
timerec.write(f'It took {(radex_time - input_time):.2f} seconds to finish running RADEX.\n')
timerec.write(f'It took {(inimodel_time - radex_time):.2f} seconds to save flux and physical models.\n')
timerec.close()
print()
print('Sincere congratulations! This script arrived here without any obstacles. <3')