# Script for feifei because I need mpl :)
'''
Physical parameters obtained from fitting correspond to which model flux?

對於我寫的爛一點都不最佳的仇視感到抱歉, 不知道為什麼最近眼睛一直看不清楚
也許是我要瞎了

update: 2026-09-19: Fix dimension problem and generalize this script.
'''

import matplotlib.pyplot as plt
import numpy as np
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei

# ------------------- Choose a mode (manual) ------------------- #
mode = 'resolved' # >> 'resolved', 'regular'(<< old 4 lines)
fitting_method = 'chi2min' # >> 'MCMC', 'liklyhood', 'chi2min'
with_bf = True
num_para = 3 + int(with_bf) + int('hco+' in mode)

# --------------- Select material by mode (auto) --------------- #
'''
About parameters' order in `moles_info`:
((molespiece-transis), 要用 mask 掉多少 sigma 的 mom0, imshow()的上限)
'''
if mode == 'regular':
    modelPath = f'{projectRoot}/data/model_no-hco+'
    phyArray = np.load(f'{modelPath}/phy_plain-model_Tk-nH2-Nco.npy')
    bsize = 3.2
    mom0Path = f'{projectRoot}/data/regrid_map_nyq'
    resultPath = f'{projectRoot}/products/fittingResult_newscript'
    best_phy = np.load(f'{resultPath}/map_bestPhyCondi_{num_para}para_newlw.npy')
    moles_info = [('co-10',   3.0, 2400), ('13co-10', 3.0, 1000),
                  ('co-21',   3.0, 2500), ('13co-21', 3.0, 450),
                  ('c18o-21', 3.0, 1000), ('co-32',   3.0, 2400)]
elif mode == 'resolved':
    modelPath = f'{projectRoot}/data/model_no-hco+' # model grid 沒有 re不resolve 的問題
    phyArray = np.load(f'{modelPath}/phy_plain-model_Tk-nH2-Nco.npy')
    bsize = 0.41
    mom0Path = f'{projectRoot}/data/regrid_map_resolved'
    resultPath = f'{projectRoot}/products/fittingResult_resolved'
    best_phy = np.load(f'{resultPath}/map_bestPhyCondi_{num_para}para_resolved.npy')
    moles_info = [('co-21',   3.0, 2500), ('13co-21', 3.0, 450),
                  ('co-32',   5.0, 2400), ('co-65',   4.0, 2200)]
else:
    print('Please choose a MODE in the begin of this script.')

# ------------------------- Load data -------------------------- #
# Beam-filling factor array
if with_bf:
    Phib = np.load(f'{modelPath}/phy_plain-model_Phibf.npy')

# flux model and mom0 maps
fluxx = {}
datashape = best_phy.shape[:2] # Equals to any mole's mom0(observe) shape. (358, 358)
for molename, nsig, _ in moles_info:
    fluxx[molename] = {
        "model":   np.load(f'{modelPath}/flux_plain-model_{num_para}para_{molename}.npy'),
        "observe": np.load(f'{mom0Path}/mom0_{molename}_smooth{bsize}as_{nsig}sigma_regrid.npy'),
        "predict": np.full(datashape, np.nan)
    }

# ----------------- Find correct index in phyArray ----------------- #
'''
Get the fitting result from `best_phy` (shape=(58, 358, 4)),
and find out where (what is the **index**) is 
the best fit physical condition set in `phyArray`.

The **index** of `phyArray` equal to the index of flux model.
For more explaination, plz refer to itoya.

`matchMask` and `found` 是共用的
'''
matchIdx_phy = np.full(datashape, np.nan) # Container with correct shape
matchIdx_phib = np.full(datashape, np.nan)

for y in range(datashape[0]):
    for x in range(datashape[1]):
        # physical parameters' dimension
        matchMask = np.all(phyArray == best_phy[y, x, :3], # :3 for three phy para: Tk, nH2, Nco.
                           axis=1)
        found = np.where(matchMask)[0] #phyyyy
        if len(found) == 1:
            matchIdx_phy[y, x] = found[0] # matchIdx[y, x] = found will become erorr in higher numpy version. 
        elif len(found) > 1:
            print('more than 1 best set?')
        elif len(found) == 0:
            pass # no match
        else:
            print('idky :)')
        # beam filling factor's dimension
        found = np.where(Phib == best_phy[y, x, 3])[0] # `Phib` is 1D grid, no axis or np.all() needed.
        if len(found) == 1:
            matchIdx_phib[y, x] = found[0] # matchIdx[y, x] = found will become erorr in higher numpy version. 
        elif len(found) > 1:
            print('more than 1 best set?')
        elif len(found) == 0:
            pass # no match
        else:
            print('idky :)')

# ---------------  Find out predicted flux by model ---------------- #
validMask = ~np.isnan(matchIdx_phy) & ~np.isnan(matchIdx_phib) # Only find out the predicted flux for valid pixel
validIdx_phy = matchIdx_phy[validMask].astype(int)
validIdx_phib = matchIdx_phib[validMask].astype(int)

for molename in fluxx.keys():
    mflux = fluxx[molename]["model"]
    fluxx[molename]["predict"][validMask] = mflux[validIdx_phy, validIdx_phib]
    '''
    fuck i dont actually under stand why i do this
    but it works so i dot car
    '''

# ------------------------  Make the figures ----------------------- #
fig, ax = plt.subplots(2, 3, figsize=(14, 7)) # 存下來就好看了
ax_flat = ax.flatten() # 壓成 1d 這樣可以用洄圈

for i, m in enumerate(moles_info):
    splot = ax_flat[i].imshow(fluxx[m[0]]["predict"],
                              vmax=m[2], origin='lower')
    ax_flat[i].set_title(f'predicted flux of {m[0]}')
    cbar = fig.colorbar(splot, ax=ax_flat[i], fraction=0.046, pad=0.04) # 精心調整的小數值

plt.tight_layout() # 神奇妙妙工具
plt.show()