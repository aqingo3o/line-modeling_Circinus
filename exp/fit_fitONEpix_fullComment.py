# Run this script on feifei, due to the file structure.
# can be put in any sub-folder, but I recommand scripts/
'''
當然是從 Eltha 那邊抄的, 適應了 feifei 的檔案環境, 
import 的 flux model 來自 scripts/radex_fluxModel.py
(update at 20260321)
'''

# --------------------------------- Import Module --------------------------------- #
from astropy.io import fits
from joblib import Parallel, delayed
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import os
from pathlib import Path # for finding file, path
import time

# ------------------------------- Path Variables ---------------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
modelPath = f'{projectRoot}/data/model_npy'
mom0Path = f'{projectRoot}/data/mom0_npy'
emapPath = f'{projectRoot}/data/error_map'
productPath = f'{projectRoot}/products'

ndmodel = 6 # nd, 5d, 6d, coarse2 的部分寫在 formatting

# -------------------------------- Basic Variables -------------------------------- #
pix_x, pix_y = 100, 100 # choose a spatial pixel
caliError = 0.1 # calibration error, by Eltha
# ((molespiece-transis), 要用 mask 掉多少 sigma 的 mom0)
moles_info = [('co-10', 3.0), ('13co-10', 3.0), ('c18o-10', 3.0), 
              ('co-21', 3.0), ('13co-21', 3.0), ('c18o-21', 3.0),
             ]
fitting_material = {} # fitting 的材料, 雙層字典君
fitting_result = {}   # fitting 的結果, 一樣雙重字典, 分開放吧 不缺這點記憶體

# ------------------------ Get Modeling Material ---------------------------------- #
for molename, nsig in moles_info:
    # Load Flux Model (.npy)
    flux_model = np.load(f'{modelPath}/flux_{ndmodel}d-coarse2_{molename}.npy')
    # Load Real Flux Data from mom0 (.npy)
    flux_obs = np.load(f'{mom0Path}/mom0_unitK_{molename}_smooth3.2as_{nsig}sigma.npy')[pix_x, pix_y]
    # Import Error Maps (.fits)
    emap = fits.open(f'{emapPath}/emap_{molename}_smooth3.2as.fits')[0].data[pix_x, pix_y]

    # Error != Noise(from emap)
    error = np.sqrt(emap**2 + (caliError * flux_obs)**2)

    # Put Material into Dict.
    fitting_material[molename] = {
        "flux_model": flux_model,
        "flux_obs": flux_obs,
        "noise": emap,
        "error": error
    }
    # Show something...
    if molename == 'co-10' or molename == 'co-21': # 為了好看
        print(f'{molename}:   {flux_obs:.3f} ± {error:.2f} (K km s-1)')
    else:
        print(f'{molename}: {flux_obs:.3f} ± {error:.2f} (K km s-1)')



#############################
"""
# Compute minimum chi^2 and its correspoding parameter set
# 屁眼我不知這這裡為什麼這麼算, 就只是先跑動再說
'''# model - flux 就是殘差！ 欸等下這堆就是在算卡方值啊
# 但為什麼要把全部的東西加在一起？
會有這個問題就是他媽的沒想清楚說是在 fit 什麼
'''
chi_sum = ((model_co10 - flux_co10) / err_co10)**2
chi_sum = chi_sum + ((model_co21 - flux_co21) / err_co21)**2
chi_sum = chi_sum + ((model_13co10 - flux_13co10) / err_13co10)**2
chi_sum = chi_sum + ((model_13co21 - flux_13co21) / err_13co21)**2
chi_sum = chi_sum + ((model_c18o10 - flux_c18o10) / err_c18o10)**2
chi_sum = chi_sum + ((model_c18o21 - flux_c18o21) / err_c18o21)**2

idx_min = np.unravel_index(np.nanargmin(chi_sum, axis=None), chi_sum.shape)
par_min = np.asarray(idx_min)
Nco = np.round(0.2*par_min[0] + 16., 1)
X13to18 = np.round(1.5*par_min[4] + 2., 1)
Phi = np.round(0.05*par_min[5] + 0.05, 1)
extent_nT = (2.,5.2,1,2.4)

T_best = 0.1*par_min[1] + 1.
n_best = 0.2*par_min[2] + 2.
X12to13 = np.round(10*par_min[3] + 10., 1)

print('Minumum chi^2 =', np.nanmin(chi_sum), 'at', idx_min)
print('i.e. (Nco, Tk, nH2, X(12/13), X(13/18), Phi) =', Nco, T_best, n_best, X12to13, X13to18, Phi)
np.save(f'{productPath}/chi2_{model}_ewcor_{idx_x}_{idx_y}', chi_sum)

idx_N = par_min[0]
idx_X1 = par_min[3]
idx_X2 = par_min[4]
idx_Phi = par_min[5]

# Contour plots
# 喔這張圖我看不懂，亂亂的線
slice_co10 = model_co10[idx_N, :, :, idx_X1, idx_X2, idx_Phi]  
slice_co21 = model_co21[idx_N, :, :, idx_X1, idx_X2, idx_Phi]
slice_13co21 = model_13co21[idx_N, :, :, idx_X1, idx_X2, idx_Phi]
slice_13co10 = model_13co10[idx_N, :, :, idx_X1, idx_X2, idx_Phi]
slice_c18o21 = model_c18o21[idx_N, :, :, idx_X1, idx_X2, idx_Phi]
slice_c18o10 = model_c18o10[idx_N, :, :, idx_X1, idx_X2, idx_Phi]

con_co10 = plt.contour(slice_co10, origin='lower', 
                       levels = np.array((flux_co10-err_co10, flux_co10+err_co10)),
                       extent = extent_nT, colors='gray'
                       )
con_co21 = plt.contour(slice_co21, origin='lower',
                       levels = np.array((flux_co21-err_co21, flux_co21+err_co21)), 
                       extent = extent_nT, colors = 'k', linestyles = 'dashed'
                       )
con_13co10 = plt.contour(slice_13co10, origin='lower',
                         levels = np.array((flux_13co10-err_13co10, flux_13co10+err_13co10)),
                         extent = extent_nT, colors ='b', linestyles = 'dotted'
                         )
con_13co21 = plt.contour(slice_13co21, origin='lower',
                         levels = np.array((flux_13co21-err_13co21, flux_13co21+err_13co21)),
                         extent = extent_nT, colors = 'c'
                        )
con_c18o10 = plt.contour(slice_c18o10, origin='lower',
                         levels = np.array((flux_c18o10-err_c18o10, flux_c18o10+err_c18o10)),
                         extent = extent_nT, colors = 'r', linestyles = 'dashdot'
                         )
con_c18o21 = plt.contour(slice_c18o21, origin='lower',
                         levels = np.array((flux_c18o21-err_c18o21, flux_c18o21+err_c18o21)),
                         extent = extent_nT, colors = 'm'
                         )

plt.gca().clabel(con_co10, inline=1, fontsize=10, fmt='%1.1f')
plt.gca().clabel(con_co21, inline=1, fontsize=10, fmt='%1.1f')
plt.gca().clabel(con_13co21, inline=1, fontsize=10, fmt='%1.1f')
plt.gca().clabel(con_13co10, inline=1, fontsize=10, fmt='%1.1f')
plt.gca().clabel(con_c18o21, inline=1, fontsize=10, fmt='%1.1f')
plt.gca().clabel(con_c18o10, inline=1, fontsize=10, fmt='%1.1f')

line_co10 = mlines.Line2D([], [], color='gray', label='CO 1-0')
line_co21 = mlines.Line2D([], [], color='k', label='CO 2-1', ls='--')
line_13co10 = mlines.Line2D([], [], color='b', label='13CO 1-0')
line_13co21 = mlines.Line2D([], [], color='c', label='13CO 2-1', ls=':')
line_c18o10 = mlines.Line2D([], [], color='r', label='C18O 1-0')
line_c18o21 = mlines.Line2D([], [], color='m', label='C18O 2-1', ls='-.')

legend = plt.legend(handles=[line_co10,line_co21, line_13co10, line_13co21, line_c18o10, line_c18o21], loc='lower left')  #, prop=lprop 

plt.title(r'$\log \left( N_{CO}\cdot\frac{15\ km\ s^{-1}}{\Delta v}\right)$ ='+str(Nco)+r'; $X_{12/13}$ ='+str(X12to13)+r'; $X_{13/18}$ ='+str(X13to18)+r'; $\log(\Phi_{bf})$ ='+str(Phi))
plt.fill_between([n_best,n_best+0.2], [T_best,T_best], [T_best+0.1,T_best+0.1], color='red', alpha='0.7')
plt.ylabel(r'$\log\ T_k\ (K)$', fontsize=12)
plt.xlabel(r'$\log\ n_{H_2}\ (cm^{-3})$', fontsize=12)
plt.savefig(f'{productPath}/flux_{model}_rmcor_contours_{idx_x}_{idx_y}_cal10-20.pdf', bbox_inches='tight', format='pdf')

plt.tight_layout()
plt.show()
"""