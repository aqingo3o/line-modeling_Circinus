# This script should process on blackhole:)
'''
from fit_fitONEpix_fullComment.py,
Success on the server :D
'''

### ----------------------------- Import Module ---------------------------- ###
from astropy.io import fits
from joblib import Parallel, delayed
import numpy as np
import time

startTime = time.time()
### --------------------------- Path Variables ----------------------------- ###
projectRoot = '/home/aqing/Documents/line-modeling_Circinus' # blackhole
#projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
modelPath = f'{projectRoot}/data/model_npy'
mom0Path = f'{projectRoot}/data/mom0_npy'
emapPath = f'{projectRoot}/data/error_map'
productPath = f'{projectRoot}/products'

ndmodel = 6

### ---------------------------- Basic Variables ---------------------------- ###
caliError = 0.1 # calibration error, by Eltha
model_shape = np.load(f'{modelPath}/flux_{ndmodel}d-coarse2_c18o-10.npy').shape # any molename can work

# ((molespiece-transis), 要用 mask 掉多少 sigma 的 mom0)
moles_info = [('co-10',   3.0),
              ('13co-10', 3.0),
              #('c18o-10', 3.0),
              ('co-21',   3.0),
              ('13co-21', 3.0),
              ('c18o-21', 3.0),
              ('co-31',   3.0),
             ]

nline = len(moles_info)
flux_model = {} # 只裝 model
for molename, nsig in moles_info: # pixel independent
    # Load Flux Model (.npy)
    flux_model[molename] = {"flux_model": np.load(f'{modelPath}/flux_{ndmodel}d-coarse2_{molename}.npy')}

### --------------- def: Get Physical Conditions from chi2_min -------------- ###
def bs2phy(chi2_array):
    '''
    best set to physical condition 的意思
    有點簡寫了哈
    '''
    if np.all(np.isnan(chi2_array)): # 如果整個 chi2_sum 都是 NaN, 就回傳一組 NaN
        return (np.nan, np.nan, np.nan, np.nan, np.nan, np.nan)

    best_set = np.unravel_index(np.nanargmin(chi2_array, axis=None), chi2_array.shape)

    Nco_best = np.round(0.2 * best_set[0] + 15., 1)
    Tk_best = 0.1 * best_set[1] + 1.
    nH2_best = 0.2 * best_set[2] + 2.
    X1213_best = np.round(10 * best_set[3] + 10., 1)
    X1318_best = np.round(1 * best_set[4] + 2., 1)
    Phi_best = np.round(0.05 * best_set[5] + 0.05, 1)
    return (Nco_best, Tk_best, nH2_best, X1213_best, X1318_best, Phi_best)

### --------------------------- def: Fix ONE pixel -------------------------- ###
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
        flux_obs = np.load(f'{mom0Path}/mom0_unitK_reproj_{molename}_smooth3.2as_{nsig}sigma.npy')[pix_y, pix_x]
        # Import Error Maps (.fits)
        emap = fits.open(f'{emapPath}/emap_unitK_reproj_{molename}_smooth3.2as.fits')[0].data[pix_y, pix_x]
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
        return (pix_y, pix_x, np.nan, [np.nan]*6)

    # --------------- Compute chi^2 Array --------------- #
    # pix_permitted = True 可以上天堂
    chi2_sum = np.zeros(model_shape)
    for molename, material_set in local_fitMaterial.items():
        chi2_sum += ((material_set["flux_model"] - material_set["flux_obs"]) / material_set["error"]) ** 2

    # --------------- Get Physical Conditions --------------- #
    best_phy = bs2phy(chi2_sum)
    chi2_min = np.nanmin(chi2_sum)
    return (pix_y, pix_x, chi2_min, best_phy)

### ------------------------------- START! ---------------------------------- ###
print('READY? GO!')

results = Parallel(n_jobs=-1)( # 用掉所有的緒是不道德的! 
    delayed(fit1pix)(y, x) 
    for y in range(800) for x in range(800)
)
print('Done!')
fitTime = time.time()
print(f'It took {(fitTime - startTime):.2f} seconds to finish fitting whole map:)')
### --------------------- Fill back to result_arrays -------------------- ###
map_best_phy = np.full((850, 850, 6), np.nan) # 6 個 physical condition
map_chi2_min = np.full((850, 850), np.nan) # 雖然只有 740 個 pix, 
                                           # 但因為是認 idx, 不是認空間的, 所以還是設多一點
for y, x, chi2_mn, phy_condi in results:
    map_best_phy[y, x, :] = phy_condi
    map_chi2_min[y, x] = chi2_mn

np.save(f'{productPath}/fittingResult_ugly/map_chi2Min_{nline}_wholemap.npy', map_chi2_min)
np.save(f'{productPath}/fittingResult_ugly/map_bestPhysicalCondi_{nline}_wholemap.npy', map_best_phy)
print('Results are saved as .npy files.')
endTime = time.time()
print(f'It took {(endTime - fitTime):.2f} seconds to fill back the result arrays.')