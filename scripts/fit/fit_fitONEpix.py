# Script for feifei because i need mpl.
# can be put in any sub-folder, but I recommand scripts/
'''
Flux models imported in this script are from scripts/radex_fluxModel.py
Fit one pixel and see if any big mistake occur.

ref:
- https://github.com/ElthaTeng/multiline-bayesian-modeling

update: 2026-08-12, Use new model that build BY MYSELF! (lots uncertainty)
        2026-08-14, Just good news to know: given out chi2_reduce ~= 0.98 
                    in pixel (43, 43) :D
'''

# ------------------------ Import Module ---------------------- #
from astropy.io import fits
import matplotlib.pyplot as plt
#import matplotlib.lines as mlines
import numpy as np

# ---------------------- Path Variables ----------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
modelPath = f'{projectRoot}/data/model_npy'
mapPath = f'{projectRoot}/data/regrid_map_nyq'
productPath = f'{projectRoot}/products/fittingResult_onepix'

# ---------------------- Basic Variables ---------------------- #
pix_y, pix_x = 43, 43
caliError = 0.1 # calibration error, by Eltha

# ((molespiece-transis), 要用 mask 掉多少 sigma 的 mom0)
moles_info = [('co-10',   1.0), 
              ('co-21',   1.0), 
              ('co-32',   1.0),
              ('13co-10', 1.0),
              ('13co-21', 1.0), 
              ('c18o-21', 1.0),
             ]
with_bf = True
fitting_material = {}

# --------------------- Get Modeling Material ------------------ #
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
    flux_obs = np.load(f'{mapPath}/mom0_{molename}_smooth3.2as_{nsig}sigma_regrid.npy')[pix_y, pix_x]
    # Import Error Maps (.fits)
    emap = fits.open(f'{mapPath}/emap_{molename}_regrid.fits')[0].data[pix_y, pix_x]

    # Error != Noise(from emap)
    error = np.sqrt(emap**2 + (caliError * flux_obs)**2)

    # Put Material into Dict.
    fitting_material[molename] = {
        "flux_model": flux_model,
        "flux_obs": flux_obs,
        "noise": emap,
        "error": error
    }

# -------------------- Show Something.. ----------------------- #
print()
print('< Flux Information >')
for molename, material_set in fitting_material.items():
    flux_obs = material_set["flux_obs"]
    error = material_set["error"]
    print(f'{molename:<8}: {flux_obs:>7.3f} ± {error:<5.2f} K km s-1')
print()
'''
print('< NaN in Model?>')
# If caculation of RADEX didn't converge, a NaN will be filled into flux model.
print("WARNING: If there is 'NaN' in flux model, chi2_sum will become a piece of shit.")
for molename, material_set in fitting_material.items():
    if np.isnan(material_set["flux_model"]).any():
        print(f'{molename:>7} has NaN in flux model :(')
    else:
        print(f'{molename:>7} has no NaN in flux model :)')
print()
'''

# --------------------------- Chi2 ----------------------------- #
# Compute chi2 Array
model_shape = fitting_material['c18o-21']['flux_model'].shape # any molename can work, (12012, 14)
chi2_sum = np.zeros(model_shape)

for molename, material_set in fitting_material.items():
    line_chi2 = ((material_set["flux_model"] - material_set["flux_obs"]) / material_set["error"]) ** 2
    chi2_sum += line_chi2

chi2_min = np.nanmin(chi2_sum)
best_set = np.unravel_index(np.nanargmin(chi2_sum, axis=None), # 這個好欸 model 長啥樣都能用
                            model_shape) # (phyCondi, Phib), 應該是這樣

# Chi2 Contribution of Each Line
print('< Chi2 Contribution of Each Line >')
for molename, material_set in fitting_material.items():
    line_chi2 = ((material_set["flux_model"][best_set] - material_set["flux_obs"]) / material_set["error"]) ** 2
    print(f"{molename:>7}'s chi2 = {line_chi2:.3f}")
print()

# -------------------- Show Fitting Results --------------------- #
print(f'< Best Physical Conditions? >  minumum chi2 = {chi2_min:.2f}')
best_phy = phyArray[best_set[0]]
Tk_best, nH2_best, Nco_best = best_phy[0], best_phy[1], best_phy[2]
print(f"{'Best Kinetic Temperature':<24} {'(T_k)':<9}: {Tk_best:<5} K")
print(f"{'Best Number Density':<24} {'(n_H2)':<9}: {nH2_best:<5} cm^-3")
print(f"{'Best CO Column Density':<24} {'(N_co)':<9}: {Nco_best:<5} cm^-2")
if with_bf:
    Phi_best = Phib[best_set[1]]
    print(f"{'Best Beam Filling Factor':<24} {'(Phi_bf)':<9}: {Phi_best:<5}")


'''
# ------------------------- flux_obs v.s flux_model ----------------------------- #
mole_name_list = []
flux_obs_pix = []
flux_model_pix = []
error_pix = []

for molename, _ in moles_info:
    mole_name_list.append(molename)
    flux_model_pix.append(fitting_material[molename]["flux_model"][best_set])
    flux_obs_pix.append(fitting_material[molename]["flux_obs"])
    error_pix.append(fitting_material[molename]["error"])

x_axis = np.arange(len(moles_info))

plt.figure(figsize=(6, 5))
plt.scatter(x_axis, flux_model_pix,
            marker='x', color='r', s=40,
            label='Model (Best Fit)')
plt.errorbar(x_axis, flux_obs_pix, 
             yerr=error_pix,
             fmt='o', color='k', markersize=4, capsize=3,
             label='Observed')

plt.xticks(x_axis, mole_name_list) #rotation=45
plt.xlabel('molecular lines')
plt.ylabel('Flux (K km/s)')
plt.legend()
plt.title(f'Flux Comparison of ({pix_x}, {pix_y}),  chi2={chi2_min:.2f}')
plt.savefig(f'{productPath}/fig_fluxComparison_onepix.png', dpi=300, bbox_inches='tight')
plt.show()
'''