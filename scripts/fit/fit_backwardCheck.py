# Script for feifei because I need mpl :)
'''
fit 出來的物理參數再丟回 radex, 看 intensity
理論上來說線上和線下應該是一樣的, 所以這邊先用線下
不過有鑒於老豆很執著於線上, 所以還是留一個尾巴工作

幹幹幹幹寫得好醜喔我不能接受!
單因為這個人超級拖拖拉拉所以先度過組會再說
'''
# --------------------------------- Import Module --------------------------------- #
from astropy.io import fits
import matplotlib.pyplot as plt
#import matplotlib.lines as mlines
import numpy as np

# ------------------------------- Path Variables -------------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
modelPath = f'{projectRoot}/data/model_npy'
dataPath = f'{projectRoot}/data/regrid_map'
productPath = f'{projectRoot}/products/fittingResult_ugly'
ndmodel = 6

# -------------------------------- Basic Variables ------------------------------- #
pix_y, pix_x = 439, 396
caliError = 0.1 # calibration error, by Eltha

# ((molespiece-transis), 要用 mask 掉多少 sigma 的 mom0, imshow()的上限)
moles_info = [('co-10',   3.0, 1400), 
              ('13co-10', 3.0, 100),
              ('co-21',   3.0, 1300), 
              ('13co-21', 3.0, 300), 
              ('co-32',   3.0, 1100),
              ('c18o-21', 3.0, 30),
             ]
nline = len(moles_info)

# ------------------------------- phy2ps ------------------------------- #
# best physical condiiton to best set
best_phy = np.load(f'{productPath}/map_bestPhyCondi_6line_wholemap_v2.npy') # shape:(900, 900, molename(6))
Nco_best, Tk_best, nH2_best, X1213_best, X1318_best, Phi_best = best_phy.transpose(2, 0, 1)
'''
因為[var] = npArray 會沿著 array 第0軸解開,
所以先把 npArray 的軸序用 np.transpose() 掉換一下,
這樣 *_best 都會是 900*900 的 array 了
'''
bs0 = np.round((Nco_best-15.) / 0.2, 1) # round(, 1) 好像是 default?
bs1 = np.round((Tk_best-1.) / 0.1)
bs2 = np.round((nH2_best-2.) / 0.2)
bs3 = np.round((X1213_best-10.) / 10)
bs4 = np.round((X1318_best-2.))
bs5 = np.round((Phi_best-0.05) / 0.05)
""" 計算依據
Nco_best = np.round(0.2 * best_set[0] + 15., 1)
Tk_best = 0.1 * best_set[1] + 1.
nH2_best = 0.2 * best_set[2] + 2.
X1213_best = np.round(10 * best_set[3] + 10., 1)
X1318_best = np.round(1 * best_set[4] + 2., 1)
Phi_best = np.round(0.05 * best_set[5] + 0.05, 1)
"""
best_set_float = np.stack([bs0, bs1, bs2, bs3, bs4, bs5], axis=-1)
'''
stack 是堆疊, axis=-1 可以疊成 (900, 900, 6), 否則會是 (6, 900, 900)
axis=n 就是決定要在哪邊插入多的維度, n=-1 就是最後一個
這邊的 6 是 6個在 flux_model 裡面找人的 index, 不是譜線數量
'''
valid_mask = ~np.isnan(best_set_float)
best_set = np.zeros_like(best_set_float, dtype=int)
best_set[valid_mask] = np.round(best_set_float[valid_mask]).astype(int)
#print(best_set.shape) # (900, 900, 6)

# ------------------------------- Load Data ------------------------------- #
moles_data = {}
for molename, nsig, _ in moles_info:
    # Load Flux Model (.npy)
    flux_model = np.load(f'{modelPath}/flux_{ndmodel}d-coarse2_{molename}.npy')
    # 反推的 intensity map (contain, here)
    flux_fit = np.full((best_phy.shape[0], best_phy.shape[1]), np.nan) # 900*900
    # Load real flux data from mom0 (.npy)
    flux_obs = np.load(f'{dataPath}/mom0_{molename}_smooth3.2as_{nsig}sigma_regrid.npy')
    # 反推
    flux_fit = flux_model[tuple(best_set.transpose(2, 0, 1))] # flux_model[best_set_pix] = flux_fit_pix
    flux_fit[~valid_mask.any(axis=-1)] = np.nan
    '''
    # Import Error Maps (.fits)
    emap = fits.open(f'{dataPath}/emap_{molename}_regrid.fits')[0].data.squeeze()
    # Error != Noise(from emap)
    error = np.sqrt(emap**2 + (caliError * flux_obs)**2)
    '''

    # Put data into dict.
    moles_data[molename] = {
        "flux_mode": flux_model,
        "flux_fit": flux_fit,
        "flux_obs": flux_obs,
        #"residual": flux_obs - flux_fit,
    }

# ------------------------------- Figures ------------------------------- #
fig, ax = plt.subplots(3, 2, figsize=(5, 8)) # 存下來就好看了
ax_flat = ax.flatten() # 壓成 1d 這樣可以用洄圈
for i in range(nline):
    molename = moles_info[i][0]
    splot = ax_flat[i].imshow(moles_data[molename]["flux_fit"][100:750, 100:750], 
                                origin='lower', cmap='inferno',
                                vmin=0, vmax=moles_info[i][2])
    cbar = fig.colorbar(splot, ax=ax_flat[i], fraction=0.046, pad=0.04) # 神奇小數值
    #ax_flat[i].set_title(f'{molename}')
    cbar.set_label('flux (K * km/s)')

plt.tight_layout() # 神奇妙妙工具
#plt.savefig(f'{productPath}/fig_fitFlux.png', dpi=300, bbox_inches='tight')
plt.show()