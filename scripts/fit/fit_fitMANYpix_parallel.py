# This script should process on blackhole:)
'''
Fit observation data that we made from prePrecess/ to 6d RADEX grid.
more python syntax detail can be find in fit_fitONEpix_fullComment.py,

Success on the server (blackhole) :D

update: 2026-07-07, Revise the filename.
        2026-07-22, use mom0 maps(-1 sigma, used to use -3 sigma) as fitting material.
	    2026-07-28, use mom0 maps that regrid by Nyquist sampling (0.1*beam size),
                    89*89 pix for each map...
        2026-07-29, change the caculation of 'best2phy()' to fit in new physical condition range.
        2026-08-14, Use model by aqing with constant abundance ratio.
        2026-09-02, Use resolved maps (0.41 arcsec) to fit, only 4 CO lines this time.
'''

# ---------------------- Import Module ---------------------- #
from astropy.io import fits
from joblib import Parallel, delayed
import numpy as np
import time

startTime = time.time()
# ---------------------- Path Variables ---------------------- #
projectRoot = '/home/aqing/Documents/line-modeling_Circinus' # blackhole
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
modelPath = f'{projectRoot}/data/model_npy'
mom0Path = f'{projectRoot}/data/regrid_map_nyq'
productPath = f'{projectRoot}/products/fittingResult_notsure'

# --------------------- Basic Variables ---------------------- #
caliError = 0.1 # calibration error, by Eltha

# ((molespiece-transis), 要用 mask 掉多少 sigma 的 mom0)
moles_info = [#('co-10',   3.0),
              #('13co-10', 3.0),
              ('co-21',   3.0),
              ('13co-21', 3.0),
              #('c18o-21', 1.0),
              ('co-32',   5.0),
              ('co-65',   4.0),
             ]

# ------------------------ Load Data ------------------------- #
'''
Check every line in this block before fitting.
Won't take you too much time for checking,
but re-start a fitting propress wastes time!
'''
# Beam size, we have [3.2, 0.41] now.
bsize = 0.41

data_shape = np.load(
    f'{mom0Path}/mom0_co-32_smooth{bsize}as_5.0sigma_regrid.npy'
    ).shape # i.e. naxis1&2 says image is 89*89 in spatial, data_shape == (89, 89)
print(f'Data shape: {data_shape}, pixel number of image.')

# phyArray, for 反推, only need N12co
phyArray = np.load(f'{modelPath}/phy_plain-model_Tk-nH2-Nco.npy')

# Beam-filling factor or not
with_bf = False
if with_bf:
    Phib = np.load(f'{modelPath}/phy_plain-model_Phibf.npy')
    num_para = 4
else:
    num_para = 3

# Load Flux Model (.npy)
model_shape = np.load(
    f'{modelPath}/flux_plain-model_{num_para}para_c18o-10.npy'
    ).shape # any molename can work
print(f'Model shape: {model_shape}, (RADEX physical parameters grid, beam-filling factor grid)')

flux_model = {} # 只裝 model
for molename, nsig in moles_info: # pixel independent
    flux_model[molename] = {"flux_model": np.load(
        f'{modelPath}/flux_plain-model_{num_para}para_{molename}.npy')}

# --------------- def: Get Physical Conditions from chi2_min --------------- #
'''
input: chi2_array
然後會用 unravel_index() 找出對應的 index
然後就可以從 index 反推出對應的 physical condition

bs2phy 是 best set to physical condition 的意思
有點簡寫了哈
'''
def bs2phy(chi2_array):
    if np.all(np.isnan(chi2_array)): # 如果整個 chi2_sum 都是 NaN, 就回傳一組 NaN
        return np.full(num_para, np.nan)
    best_set = np.unravel_index(np.nanargmin(chi2_array, axis=None), chi2_array.shape)
    '''
    flat_idx = np.nanargmin() # 展平之後, 忽略 nan 尋找最小值的 idx
    best_set = np.unravel_index() # Turn flatten index into nd array's idx
                                  # >> shape like: (9152, 14) 
    '''
    Tk_best = phyArray[best_set[0]][0]
    nH2_best = phyArray[best_set[0]][1]
    Nco_best = phyArray[best_set[0]][2]
    if with_bf:
        Phib_best = Phib[best_set[1]] # 因為我 Phibf 是另外存的, 最佳索引在 best_set 的另一邊
        return [Tk_best, nH2_best, Nco_best, Phib_best]
    else:
        return [Tk_best, nH2_best, Nco_best]

# --------------------------- def: Fix ONE pixel --------------------------- #
'''
input:  pixel index (order: y, x)
output: (pix_y, pix_x, chi2_min, best_phy)
'''
def fit1pix(pix_y, pix_x):
    pix_permitted = True # 標示 pixel 的狀態, 等下要過檢查點

    local_fitMaterial = {} # **FOR PARALLEL** #

    # ------------- Get fiiting materials ------------- #
    for molename, nsig in moles_info:
        # Load Real Flux Data from mom0 (.npy)
        flux_obs = np.load(f'{mom0Path}/mom0_{molename}_smooth{bsize}as_{nsig}sigma_regrid.npy')[pix_y, pix_x]
        # Import Error Maps (.fits)
        emap = fits.open(f'{mom0Path}/emap_{molename}_smooth{bsize}as_regrid.fits')[0].data[pix_y, pix_x]
        #** flux_obs & emap 的檢查點 **#
        if np.isnan(flux_obs) or np.isnan(emap):
            pix_permitted = False # 標示為壞 pixel
            break # 只要一個分子壞掉，就不用跑剩下的分子了

        # Error != Noise(from emap)
        error = np.sqrt(emap**2 + (caliError * flux_obs)**2)
        #** error 的檢查點 **#
        if error <= 0 or np.isnan(error):
            pix_permitted = False
            break # error 是爛值也跳掉

        # Put Material into Dict.
        local_fitMaterial[molename] = {
            "flux_model": flux_model[molename]["flux_model"],
            "flux_obs": flux_obs,
            "noise": emap,
            "error": error,
        }

    # ------------------- GO! or NO GO ------------------ #
    if not pix_permitted:
        return (pix_y, pix_x, np.nan, [np.nan]*num_para) # (y, x, chi2, [Tk, nH2, Nco, Phib])

    # --------------- Compute chi^2 Array --------------- #
    # pix_permitted = True 可以上天堂
    chi2_sum = np.zeros(model_shape)
    for molename, material_set in local_fitMaterial.items():
        chi2_sum += ((material_set["flux_model"] - material_set["flux_obs"]) / material_set["error"]) ** 2

    # ------------- Get Physical Conditions ------------- #
    best_phy = bs2phy(chi2_sum)
    chi2_min = np.nanmin(chi2_sum)
    return (pix_y, pix_x, chi2_min, best_phy)


# ------------------------------ START! ------------------------------ #
print('------------------- READY? GO! -------------------')

results = Parallel(n_jobs=-1)( # 用掉所有的緒是不道德的!
    delayed(fit1pix)(y, x)
    for y in range(data_shape[0]) for x in range(data_shape[1])
)
print('Done!')
fitTime = time.time()
print(f'It took {(fitTime - startTime):.2f} seconds to fit whole map:)')

# --------------- Fill back to result_arrays --------------- #
map_best_phy = np.full((data_shape[0], data_shape[1], num_para), np.nan)
map_chi2_min = np.full(data_shape, np.nan)

for y, x, chi2_mn, best_phy in results:
    map_best_phy[y, x] = best_phy
    map_chi2_min[y, x] = chi2_mn

np.save(f'{productPath}/map_chi2Min_{num_para}para_resolved.npy',
        map_chi2_min)
np.save(f'{productPath}/map_bestPhyCondi_{num_para}para_resolved.npy',
        map_best_phy)
print('Results are saved as .npy files.')
endTime = time.time()
print(f'It took {(endTime - fitTime):.2f} seconds to fill back the result arrays.')