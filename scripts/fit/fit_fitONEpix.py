# Run this script on feifei, due to the file structure.
# can be put in any sub-folder, but I recommand scripts/
'''
當然是從 Eltha 那邊抄的, 適應了 feifei 的檔案環境, 
import 的 flux model 來自 scripts/radex_fluxModel.py

fullComment 版含有 contuors plot 的部份
但這邊沒有 因為我看不懂先刪掉了

沒有存太多東西下來, 因為只 fit one pixel, 
隨時重跑都是可以的
'''

# --------------------------------- Import Module --------------------------------- #
from astropy.io import fits
import matplotlib.pyplot as plt
#import matplotlib.lines as mlines
import numpy as np

# ------------------------------- Path Variables ---------------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
modelPath = f'{projectRoot}/data/model_npy'
mom0Path = f'{projectRoot}/data/mom0_npy'
emapPath = f'{projectRoot}/data/error_map'
productPath = f'{projectRoot}/products'

ndmodel = 6

# -------------------------------- Basic Variables -------------------------------- #
pix_y, pix_x = 439, 396
caliError = 0.1 # calibration error, by Eltha

# ((molespiece-transis), 要用 mask 掉多少 sigma 的 mom0)
moles_info = [('co-10',   3.0), 
              ('13co-10', 3.0), 
              #('c18o-10', 3.0), 
              ('co-21',   3.0), 
              ('13co-21', 3.0), 
              ('c18o-21', 3.0),
             ]
fitting_material = {}

# ------------------------ Get Modeling Material ---------------------------------- #
for molename, nsig in moles_info:
    # Load Flux Model (.npy)
    flux_model = np.load(f'{modelPath}/flux_{ndmodel}d-coarse2_{molename}.npy')
    # Load Real Flux Data from mom0 (.npy)
    flux_obs = np.load(f'{mom0Path}/mom0_unitK_reproj_{molename}_smooth3.2as_{nsig}sigma.npy')[pix_y, pix_x]
    # Import Error Maps (.fits)
    emap = fits.open(f'{emapPath}/emap_unitK_reproj_{molename}_smooth3.2as.fits')[0].data[pix_y, pix_x]

    # Error != Noise(from emap)
    error = np.sqrt(emap**2 + (caliError * flux_obs)**2)

    # Put Material into Dict.
    fitting_material[molename] = {
        "flux_model": flux_model,
        "flux_obs": flux_obs,
        "noise": emap,
        "error": error
    }

# ------------------------ Show Something.. ---------------------------------- #
print()
# Maybe Flux Information?
print('< Flux Information >')
for molename, material_set in fitting_material.items():
    flux_obs = material_set["flux_obs"]
    error = material_set["error"]
    print(f'{molename:<8}: {flux_obs:>7.3f} ± {error:<5.2f} K km s-1') # veryy beautifulll
print()
        
# NaN in flux_model?
print('< NaN in Model?>')
print("WARNING: If there is 'NaN' in flux model, chi2_sum will become a piece of shit.")
for molename, material_set in fitting_material.items():
    if np.isnan(material_set["flux_model"]).any():
        print(f'{molename:>7} has NaN in flux model :(')
    else:
        print(f'{molename:>7} has no NaN in flux model :)')
print()

# ----------------------------------- Chi2 ----------------------------------- #
# Compute chi^2 Array
model_shape = fitting_material['c18o-21']['flux_model'].shape # any molename can work
chi2_sum = np.zeros(model_shape)
for molename, material_set in fitting_material.items():
    chi2_sum += ((material_set["flux_model"] - material_set["flux_obs"]) / material_set["error"]) ** 2

chi2_min = np.nanmin(chi2_sum)
best_set = np.unravel_index(np.nanargmin(chi2_sum, axis=None), model_shape)

# Chi2 Contribution of Each Line
print('< Chi2 Contribution of Each Line >')
for molename, material_set in fitting_material.items():
    line_chi2 = ((material_set["flux_model"][best_set] - material_set["flux_obs"]) / material_set["error"]) ** 2
    print(f"{molename:>7}'s chi2 = {line_chi2:.3f}")
print()

# --------------------------- Show Fitting Results ------------------------------ #
# (chi2_min, best_set)
print(f'minumum chi2 = {chi2_min:.2f}, at best set: {best_set}')
print("The best set's order follow [Nco, Tk, nH2, X(12/13), X(13/18), Phi_bf]")
print()

# Get Physical Conditions from best_set
Nco_best = np.round(0.2 * best_set[0] + 15., 1)
Tk_best = 0.1 * best_set[1] + 1.
nH2_best = 0.2 * best_set[2] + 2.
X12to13_best = np.round(10 * best_set[3] + 10., 1)
X13to18_best = np.round(1 * best_set[4] + 2., 1)
Phi_best = np.round(0.05 * best_set[5] + 0.05, 1)

# (Physical Conditions)
print('< Best Physical Conditions? >')
print(f"{'Best CO Column Density':<30} {'(N_co)':<9}: 10^{Nco_best:<5} cm^-2")
print(f"{'Best Kinetic Temperature':<30} {'(T_k)':<9}: 10^{Tk_best:<5} K")
print(f"{'Best Number Density':<30} {'(n_H2)':<9}: 10^{nH2_best:<5} cm^-3")
print(f"{'Best 12CO/13CO Abundance Ratio':<30} {'(X_12/13)':<9}: {X12to13_best:<5}")
print(f"{'Best 13CO/C18O Abundance Ratio':<30} {'(X_13/18)':<9}: {X13to18_best:<5}")
print(f"{'Best Beam Filling Factor':<30} {'(Phi_bf)':<9}: {Phi_best:<5}")
      
np.save(f'{productPath}/chi2_tt/chi2Sum_{ndmodel}d-coarse2_tt_{pix_x}-{pix_y}', chi2_sum)

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


plt.figure(figsize=(8, 5))
plt.scatter(x_axis, flux_model_pix,
            marker='x', color='r', s=40,
            label='Model (Best Fit)')
plt.errorbar(x_axis, flux_obs_pix, 
             yerr=error_pix,
             fmt='o', color='k', markersize=4, capsize=3,
             label='Observed')

plt.xticks(x_axis, mole_name_list, rotation=45)
plt.xlabel('molecular lines')
plt.ylabel('Flux (K km/s)')
plt.legend()
plt.title(f'Flux Comparison of ({pix_x}, {pix_y}),  chi2={chi2_min:.2f}')
plt.savefig(f'{productPath}/figure/fig_fluxComparison_onepix.png', dpi=300, bbox_inches='tight')
plt.show()