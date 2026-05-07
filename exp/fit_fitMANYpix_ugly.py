# Run this script on feifei, due to the file structure.
# can be put in any sub-folder, but I recommand scripts/
'''
naa
'''

### ----------------------------- Import Module ---------------------------- ###
from astropy.io import fits
import numpy as np

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
              ('c18o-10', 3.0),
              ('co-21',   3.0),
              ('13co-21', 3.0),
              ('c18o-21', 3.0),
             ]
fitting_material = {} # fitting 的材料, 雙層字典君

for molename, nsig in moles_info: # pixel independent
    # Load Flux Model (.npy)
    flux_model = np.load(f'{modelPath}/flux_{ndmodel}d-coarse2_{molename}.npy')
    fitting_material[molename] = {"flux_model": flux_model}

### ------------------------------- START! ---------------------------------- ###
for i in range(450, 460):
    for j in range(450, 460):
        pix_y, pix_x = i, j

        # ------------- Get fiiting materials ------------- #
        for molename, nsig in moles_info:
            # Load Real Flux Data from mom0 (.npy)
            flux_obs = np.load(f'{mom0Path}/mom0_unitK_reproj_{molename}_smooth3.2as_{nsig}sigma.npy')[pix_y, pix_x] # 注意軸序!
            # Import Error Maps (.fits)
            emap = fits.open(f'{emapPath}/emap_unitK_reproj_{molename}_smooth3.2as.fits')[0].data[pix_y, pix_x] # 注意軸序!
            # Error != Noise(from emap)
            error = np.sqrt(emap**2 + (caliError * flux_obs)**2)

            # Put Material into Dict.
            fitting_material[molename]["flux_obs"] = flux_obs
            fitting_material[molename]["noise"] = emap
            fitting_material[molename]["error"] = error

        # --------------- Compute chi^2 Array --------------- #
        chi2_sum = np.zeros(model_shape)
        for molename, material_set in fitting_material.items():
            # 依照 molename 走訪...
            chi2_sum += ((material_set["flux_model"] - material_set["flux_obs"]) / material_set["error"]) ** 2
        np.save(f'{productPath}/chi2_tt/chi2Sum_{ndmodel}d-coarse2_tt_{pix_x}-{pix_y}', chi2_sum)
        print(f'({pix_x}, {pix_y}) done!')





"""
下面的還沒用到哈哈
"""
### -------------------- Get Physical Conditions from best_set -------------------- ###

def bs2phy(chi2_array):
    best_set = np.unravel_index(np.nanargmin(chi2_array, axis=None), chi2_array.shape)

    Nco_best = np.round(0.2 * best_set[0] + 15., 1)
    Tk_best = 0.1 * best_set[1] + 1. # 加了小數點, 避免他在那邊叫說 float64 怎樣的
    nH2_best = 0.2 * best_set[2] + 2.
    X1213_best = np.round(10 * best_set[3] + 10., 1)
    X1318_best = np.round(1 * best_set[4] + 2., 1)
    Phi_best = np.round(0.05 * best_set[5] + 0.05, 1) # 這個找不到來源雞掰
    return (Nco_best, Tk_best, nH2_best, X1213_best, X1318_best, Phi_best)
'''
[the 還原參考], from radex_fluxModel.py 很前面的地方
Nco = np.arange(15., 20.1, 0.2)
Tkin = np.arange(1., 2.8, 0.1)
nH2 = np.arange(2., 5.1, 0.2) # step size for Nco and nH2 should be the same
X_13co = np.arange(10, 205, 10)
X_c18o = np.arange(2, 21, 1)
round_dens, round_temp = 1, 1

Nco, nH2, Tkin 都是指數部分(10^a的a)
'''