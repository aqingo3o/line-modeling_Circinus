'''radex-pipelind_constructFlux.py
This script is intended to serve as a smaller-scale workflow version of `radex_pipeline.py`, from Eltha.

準確來說是我改過的 radex-pipeline_lite.py 的後1/3部分
因為一次全部跑完的話有點懸, 所以就分成三部分了。
'''
# Module
import numpy as np
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

# def radexFlux():
# 不知道這是幹啥的
def radex_flux(i, j, k, m, n):
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
    if np.loadtxt(outfile_0, skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_0 = np.full((3,), np.nan)
    else:
        flux_0 = np.genfromtxt(outfile_0, skip_header=13)[:, 11]

    if np.loadtxt(outfile_1, skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_1 = np.full((3,), np.nan)
    else:    
        flux_1 = np.genfromtxt(outfile_1, skip_header=13)[:, 11]

    if np.loadtxt(outfile_2, skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_2 = np.full((3,), np.nan)
    else:    
        flux_2 = np.genfromtxt(outfile_2, skip_header=13)[:, 11]
    
    return k, i, j, m, n, flux_0, flux_1, flux_2
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