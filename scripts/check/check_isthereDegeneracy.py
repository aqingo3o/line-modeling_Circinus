# Script for both feifei and blackhole
'''
湯底來自 fit_fit)NEpix.py,
To check if there is a degeneracy: 
different physical conditions give similarly intensity (flux_model).
'''

import numpy as np

# ------------------ Path Variables ------------------ #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
modelPath = f'{projectRoot}/data/model_npy'
mapPath = f'{projectRoot}/data/regrid_map_resolved'
productPath = f'{projectRoot}/products/fittingResult_resolved'

# ------------------ Basic Variables ------------------ #
pix_y, pix_x =200, 190
bsize = 0.41 # arcsec, we have [3.2, 0.41, ] now.
with_bf = True
caliError = 0.1 # calibration error, by Eltha

# ((molespiece-transis), 要用 mask 掉多少 sigma 的 mom0)
moles_info = [#('co-10',   1.0),
              ('13co-21', 3.0),
              ('co-21',   3.0), 
              ('co-32',   5.0),
              #('13co-10', 1.0),
              #('c18o-21', 1.0),
              ('co-65',   4.0)
             ]

fitting_material = {}

# ---------------- Get Modeling Material ---------------- #
phyArray = np.load(f'{modelPath}/phy_plain-model_Tk-nH2-Nco.npy') # for 反推, only need N12co

if with_bf:
    Phib = np.load(f'{modelPath}/phy_plain-model_Phibf.npy')
    num_para = 4
else:
    num_para = 3

for molename, nsig in moles_info:
    # Load Flux Model (.npy)
    flux_model = np.load(f'{modelPath}/flux_plain-model_{num_para}para_{molename}.npy')
    # Load Real Flux Data from mom0 (.npy)
    flux_obs = np.load(f'{mapPath}/mom0_{molename}_smooth{bsize}as_{nsig}sigma_regrid.npy')[pix_y, pix_x]
    # Import Error Maps (.fits)
    emap = np.load(f'{mapPath}/emap_{molename}_smooth{bsize}as_regrid.npy')[pix_y, pix_x]

    # Error != Noise(from emap)
    error = np.sqrt(emap**2 + (caliError * flux_obs)**2)

    # Put Material into Dict.
    fitting_material[molename] = {
        "flux_model": flux_model,
        "flux_obs": flux_obs,
        "noise": emap,
        "error": error
    }

# ----------------- flux_obs Information ------------------ #
print()
print('< Observation Flux Information >')
for molename, material_set in fitting_material.items():
    flux_obs = material_set["flux_obs"]
    error = material_set["error"]
    print(f'{molename:<8}: {flux_obs:>7.3f} ± {error:<5.2f} K km s-1')
print()

# -------------------------- Chi2 -------------------------- #
# Compute chi2 Array
model_shape = fitting_material['co-21']['flux_model'].shape # any molename can work, (9152, 14)

chi2_sum = np.zeros(model_shape)
for molename, material_set in fitting_material.items():
    line_chi2 = ((material_set["flux_model"] - material_set["flux_obs"]) / material_set["error"]) ** 2
    chi2_sum += line_chi2

# ----------------- The kth Smallest Values ---------------- #
kth = 5 # 前 kth 小的 chi2 value
'''
Naming logic:
    rankth_idx_flat >>
    rankth: rank + kth, 前 kth 小的東西嘍
    idx: 是索引不是真值
    flat: axis=None 的話就會是 flatten 的, that's why we need np.unravel_index
'''
rankth_idx_flat = np.argpartition(chi2_sum, kth, axis=None)[:kth]
rankth_idx = tuple(
    zip(*np.unravel_index(rankth_idx_flat, model_shape)) # 程式詳見 2006-09-07 的 itoya
    ) 

# --------------- Show Fitting Results (kth) --------------- #
print(f'--------------- Best {kth}th Fitting Result ----------------')
for i in rankth_idx:
    print(f'Chi2 value = {chi2_sum[i]:2f}')

    print('------------ Model flux ----------')
    for molename, material_set in fitting_material.items():
        flux_model = material_set["flux_model"]
        print(f'{molename:<8}: {flux_model[i]:>7.3f}  K km s-1')

    print('---------- Phy conditions ---------')
    best_phy = phyArray[i[0]]
    Tk_best, nH2_best, Nco_best = best_phy[0], best_phy[1], best_phy[2]
    print(f"{'Best Kinetic Temperature':<24} {'(T_k)':<9}: {Tk_best:<5} K")
    print(f"{'Best Number Density':<24} {'(n_H2)':<9}: {nH2_best:<5} cm^-3")
    print(f"{'Best CO Column Density':<24} {'(N_co)':<9}: {Nco_best:<5} cm^-2")
    if with_bf:
        Phi_best = Phib[i[1]]
        print(f"{'Best Beam Filling Factor':<24} {'(Phi_bf)':<9}: {Phi_best:<52f}")
    print()
