# This script can run on blackhole.
# Take 5 hours to finish without Parallel processing, ugly but it works:)
'''
from fit_fitONEpix_fullComment.py, 細節的註解可以看那邊, 
在 server(@blackhole) 上跑成功過喔喔
'''

### ----------------------------- Import Module ---------------------------- ###
from astropy.io import fits
import numpy as np
import time

startTime = time.time()
### --------------------------- Path Variables ----------------------------- ###
#projectRoot = '/home/aqing/Documents/line-modeling_Circinus' # blackhole
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
modelPath = f'{projectRoot}/data/model_npy'
mom0Path = f'{projectRoot}/data/mom0_npy'
emapPath = f'{projectRoot}/data/error_map'
productPath = f'{projectRoot}/products'

ndmodel = 6 # nd, 5d, 6d; coarse2 的部分寫在 formatting

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
             ]

fitting_material = {}
for molename, nsig in moles_info:
    # Load Flux Model (.npy)
    flux_model = np.load(f'{modelPath}/flux_{ndmodel}d-coarse2_{molename}.npy')
    fitting_material[molename] = {"flux_model": flux_model}

### --------------------- Containers for Fitting Results -------------------- ###
map_best_phy = np.full((900, 900, 6), np.nan)
map_chi2_min = np.full((900, 900), np.nan)

### ------------------ Get Physical Conditions from chi2_min ---------------- ###
def bs2phy(chi2_array):
    '''
    best set to physical condition 的意思
    有點簡寫了哈
    '''
    if np.all(np.isnan(chi2_array)):
        return (np.nan, np.nan, np.nan, np.nan, np.nan, np.nan)
    
    best_set = np.unravel_index(np.nanargmin(chi2_array, axis=None), chi2_array.shape)

    Nco_best = np.round(0.2 * best_set[0] + 15., 1)
    Tk_best = 0.1 * best_set[1] + 1.
    nH2_best = 0.2 * best_set[2] + 2.
    X1213_best = np.round(10 * best_set[3] + 10., 1)
    X1318_best = np.round(1 * best_set[4] + 2., 1)
    Phi_best = np.round(0.05 * best_set[5] + 0.05, 1)
    return (Nco_best, Tk_best, nH2_best, X1213_best, X1318_best, Phi_best)

### ------------------------------- START! ---------------------------------- ###
print('READY? GO!')
for i in range(350, 551):
    for j in range(350, 551):
        pix_y, pix_x = i, j
        pix_permitted = True # Mark pixel's status, be checked later

        # ------------- Get fiiting materials ------------- #
        for molename, nsig in moles_info:
            # Load Real Flux Data from mom0 (.npy)
            flux_obs = np.load(f'{mom0Path}/mom0_unitK_reproj_{molename}_smooth3.2as_{nsig}sigma.npy')[pix_y, pix_x] # 注意軸序!
            # Import Error Maps (.fits)
            emap = fits.open(f'{emapPath}/emap_unitK_reproj_{molename}_smooth3.2as.fits')[0].data[pix_y, pix_x] # 注意軸序!
            if np.isnan(flux_obs) or np.isnan(emap):
                pix_permitted = False # Mark as bad pixel
                break
            
            # Error != Noise(from emap)
            error = np.sqrt(emap**2 + (caliError * flux_obs)**2)
            if error <= 0 or np.isnan(error):
                pix_permitted = False # Mark as bad pixel
                break

            # Put Material into Dict.
            fitting_material[molename]["flux_obs"] = flux_obs
            fitting_material[molename]["noise"] = emap
            fitting_material[molename]["error"] = error

        # ------------------- GO! or NO GO ------------------ #
        if not pix_permitted: # Fill 'NaN' in for bad pixel
            map_best_phy[pix_y, pix_x, :] = np.nan
            map_chi2_min[pix_y, pix_x] = np.nan
            print(f'WARNING: Skipped ({pix_x}, {pix_y}) due to bad data.')
            continue

        # --------------- Compute chi^2 Array --------------- #
        chi2_sum = np.zeros(model_shape)
        for molename, material_set in fitting_material.items():
            chi2_sum += ((material_set["flux_model"] - material_set["flux_obs"]) / material_set["error"]) ** 2

        # --------------- Get Physical Conditions --------------- #
        map_chi2_min[pix_y, pix_x] = np.nanmin(chi2_sum)
        map_best_phy[pix_y, pix_x, :] = bs2phy(chi2_sum)
        print(f'({pix_x}, {pix_y}) done!', end='\r')
    print()

np.save(f'{productPath}/fittingResult_ugly/map_chi2_min.npy', map_chi2_min)
np.save(f'{productPath}/fittingResult_ugly/map_best_phyicalCondi.npy', map_best_phy)
print(f'Fitting results are saved in {productPath}/fittingResult_ugly/')
endTime = time.time()
print(f'It took {(endTime - startTime):.1f} seconds to finish fitting the whole map:)')
