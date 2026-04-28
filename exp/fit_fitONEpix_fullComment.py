# Run this script on feifei, due to the file structure.
# can be put in any sub-folder, but I recommand scripts/
'''
當然是從 Eltha 那邊抄的, 適應了 feifei 的檔案環境, 
import 的 flux model 來自 scripts/radex_fluxModel.py
(update at 20260321)
'''

# --------------------------------- Import Module --------------------------------- #
from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np

# ------------------------------- Path Variables ---------------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
modelPath = f'{projectRoot}/data/model_npy'
mom0Path = f'{projectRoot}/data/mom0_npy'
emapPath = f'{projectRoot}/data/error_map'
productPath = f'{projectRoot}/products'

ndmodel = 6 # nd, 5d, 6d; coarse2 的部分寫在 formatting
'''
等一下,
我是先覺得我只有 6 條線, 所以我就用少一點參數的版本 (Phi 先刪掉, 因為他是最後一個)
但是 Eltha 也是 6 條線 6 個參數耶?
'''

# -------------------------------- Basic Variables -------------------------------- #
pix_y, pix_x = 439, 396 # choose a spatial pixel, 他媽的老子精挑細選到一個大家都有值得地方真他媽辛苦我自己了
                        # 注意軸序! 可以 print 出來與 CARTA 對照
caliError = 0.1 # calibration error, by Eltha

# ((molespiece-transis), 要用 mask 掉多少 sigma 的 mom0)
moles_info = [('co-10',   3.0), 
              ('13co-10', 3.0), 
              #('c18o-10', 3.0), 
              ('co-21',   3.0), 
              ('13co-21', 3.0), 
              ('c18o-21', 3.0),
             ]
fitting_material = {} # fitting 的材料, 雙層字典君
fitting_result = {}   # fitting 的結果, 一樣雙重字典, 分開放吧 不缺這點記憶體

# ------------------------ Get Modeling Material ---------------------------------- #
for molename, nsig in moles_info:
    # Load Flux Model (.npy)
    flux_model = np.load(f'{modelPath}/flux_{ndmodel}d-coarse2_{molename}.npy')
    # Load Real Flux Data from mom0 (.npy)
    flux_obs = np.load(f'{mom0Path}/mom0_unitK_reproj_{molename}_smooth3.2as_{nsig}sigma.npy')[pix_y, pix_x] # 注意軸序!
    # Import Error Maps (.fits)
    emap = fits.open(f'{emapPath}/emap_unitK_reproj_{molename}_smooth3.2as.fits')[0].data[pix_y, pix_x] # 注意軸序!

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
print() # 先換一行比較好看
# Maybe Flux Information?
print('< Flux Information >')
for molename, material_set in fitting_material.items():
    flux_obs = material_set["flux_obs"]
    error = material_set["error"]
    print(f'{molename:<8}: {flux_obs:>7.3f} ± {error:<5.2f} K km s-1') # veryy beautifulll
print()
        
# NaN in flux_model?
#'''
print('< NaN in Model?>')
print("WARNING: If there is 'NaN' in flux model, chi2_sum will become a piece of shit.")
for molename, material_set in fitting_material.items():
    if np.isnan(material_set["flux_model"]).any():
        print(f'{molename:>7} has NaN in flux model :(') # True 就會輸出這行
    else:
        print(f'{molename:>7} has no NaN in flux model :)')
print()
#'''

# --------------------------------- Chi2... ---------------------------------- #
'''
以下在做的事情:
首先建立一個都是 0 的卡方值網格,
molename 隨便填都行, 這邊就是跟 co-10 最熟所以選他
因為這邊 import 的 model 是 6d 的, 所以總之就是建立一個形狀一樣的卡方網格
(model_shape = )
(做成網個方便我寫迴圈 (26, 18, 16, 20, 19, 14))
Then, each point in this grid points to a SET of physical condition
一組物理條件會對應一個 flux (K km s-1)
就是用 model flux(flux_model) and real flux(flux_obs) 去計算 chi2

np.zeros(): input shape
np.zeros_like(): input a template array
'''
# Compute chi^2 Array
model_shape = fitting_material['c18o-21']['flux_model'].shape # any molename can work
chi2_sum = np.zeros(model_shape)
for molename, material_set in fitting_material.items():
    # 依照 molename 走訪...
    chi2_sum += ((material_set["flux_model"] - material_set["flux_obs"]) / material_set["error"]) ** 2

chi2_min = np.nanmin(chi2_sum) # 這裡的 min 是在找卡方值網格裡的最小值, 不是在找哪個 molename 的最小值
best_set = np.unravel_index(np.nanargmin(chi2_sum, axis=None), chi2_sum.shape) # 不清楚這個用法但是先寫了

# Chi2 Contribution of Each Line
#'''
print('< Chi2 Contribution of Each Line >')
for molename, material_set in fitting_material.items():
    line_chi2 = ((material_set["flux_model"][best_set] - material_set["flux_obs"]) / material_set["error"]) ** 2
    print(f"{molename:>7}'s chi2 = {line_chi2:.3f}")
print()
#'''

# ------------------------- Show Fitting Results . ------------------------------ #
# (chi2_min, best_set)
print(f'minumum chi2 = {chi2_min:.2f}, at best set: {best_set}')
print("The best set's order follow [Nco, Tk, nH2, X(12/13), X(13/18), Phi_bf]") # 也是從 radex_fluxModle.py 猜的
print()

# Get Physical Conditions from best_set
'''
我覺得這應該算暫時的, 
應該要從 radex_fluxModel.py 那邊匯出網格, 
然後這邊讀那個網格 ...
就算是 .txt 也是要
'''
Nco_best = np.round(0.2 * best_set[0] + 16., 1)
Tk_best = 0.1 * best_set[1] + 1. # 加了小數點, 避免他在那邊叫說 float64 怎樣的
nH2_best = 0.2 * best_set[2] + 2.
X12to13_best = np.round(10 * best_set[3] + 10., 1)
X13to18_best = np.round(1.5 * best_set[4] + 2., 1)
Phi_best = np.round(0.05 * best_set[5] + 0.05, 1)

extent_nT = (2.,5.2,1,2.4) # 這不知道是啥, 先留著

# (Physical Conditions)
print('< Best Physical Conditions? >')
print(f"{'Best CO Column Density':<30} {'(N_co)':<9}: {Nco_best:<5} cm^-2")
print(f"{'Best Kinetic Temperature':<30} {'(T_k)':<9}: {Tk_best:<5} K")
print(f"{'Best Collision Partner Density':<30} {'(n_H2)':<9}: {nH2_best:<5} cm^-3")
print(f"{'Best 12CO/13CO Abundance Ratio':<30} {'(X_12/13)':<9}: {X12to13_best:<5}")
print(f"{'Best 13CO/C18O Abundance Ratio':<30} {'(X_13/18)':<9}: {X13to18_best:<5}")
print(f"{'Best Beam Filling Factor':<30} {'(Phi_bf)':<9}: {Phi_best:<5}")
      

#np.save(f'{productPath}/chi2_{ndmodel}_ewcor_{pix_x}_{pix_y}', chi2_sum)


"""
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