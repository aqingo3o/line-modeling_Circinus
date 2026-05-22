# Do this on feifei because I need mpl
# Use the results from fitMANYpix_parallel.py
'''
Modify from fir_resultMap_pix.py,
但試圖用一點類似中心點 offset 的東西 (belike MVP.io)
'''
# ------------------------------ Modules ------------------------------ #
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.io import fits
import astropy.units as u
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------- PATH -------------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
mom0Path = f'{projectRoot}/data/mom0_map'
resultPath = f'{projectRoot}/products/fittingResult'

# ----------------------------- Load Data ------------------------------ #
# map_convert2KandReproj.py used CO(2-1) as reprojecting tmeplate
template = fits.open(f'{mom0Path}/mom0_co-21_smooth3.2as_3.0sigma.fits')[0] 
# Choose which set of fitting result
nline = '6line'
whichone = 'wholemap' ###
map_chi2_min = np.load(f'{resultPath}/map_chi2Min_{nline}_{whichone}.npy')
map_best_phy = np.load(f'{resultPath}/map_bestPhyCondi_{nline}_{whichone}.npy')

# --------------------------- Template Info ---------------------------- #
template_data = template.data.squeeze() # image part, can be imshow()
template_wcs2 = WCS(template.header).celestial # .celestial = .dropaxis(n)?

# ------------------------ Refill Result Arrays ------------------------ #
'''
*** 
不太確定是否需要這個步驟, 搞不好 astropy 聰明的不得了?
但為了以防萬一還是做了
***

為了等下畫圖的時候比較方便對齊,
把 fitting 的時候亂寫的 map_* array (result array)
重新填充到與 template 形狀相同的 full* 中

前提是 map_* 是方陣, 並且 chi2_min 和 beest_phy 的大小會是一樣的
不管啦這是我要用的不用那麼 universal 的考慮啦!
'''
if map_chi2_min.shape == template_data.shape:
    chi2_min_full = map_chi2_min
    best_phy_full = map_best_phy # 理論上他倆在空間維度的形狀應該相同, 就只檢查一次了
                                 # 我沒無聊到這倆寫不同形狀的吧!
else:
    old_shape = map_chi2_min.shape[0] # 因為是方陣所以才能這麼寫
    chi2_min_full = np.full(template_data.shape, np.nan) # template_data.shape is tuple!
    chi2_min_full[0:old_shape, 0:old_shape] = map_chi2_min
    best_phy_full = np.full((template_data.shape[0], template_data.shape[1], 6)
                            ,np.nan) # 多一維好麻煩啊
    best_phy_full[0:old_shape, 0:old_shape, :] = map_best_phy
    print('Refilled.')

# --------------------------- Figure Setting ---------------------------- #
# Figure Panels
'''
Set figures' title, unit and color map herer
7 panels: 6 physical conditions + chi2
** phy_info's Order matter! **
'''
phy_info = [ # ('plot title', 'unit', 'cmap')
    ('Colum Density (Nco)',      r'log$N_{\rm CO}$ (cm$^{-2}$)',  'inferno'),
    ('Kinetic Temperature (Tk)', r'log$T_{\rm k}$ (K)',           'hot'), 
    ('Number Density (nH2)',     r'log$n_{\rm H_2}$ (cm$^{-3}$)', 'inferno'), 

    ('12CO/13CO Abundance Ratio', '', 'jet'), # dimless
    ('13CO/C18O Abundance Ratio', '', 'jet'), 
    ('Beam Filling Factor',       '', 'gray'),
    ]

# Image Range
if whichone == 'partial':
    imrange = (340, 560)
elif whichone == 'wholemap':
    if nline == '5line':
        imrange = (50, 840)
    elif nline == '6line':
        imrange = (200, 700)
    #imrange = (200, 600)

#'''
# -------------------------- Plot with WCS --------------------------- #
# 直接是世界座標的
fig_wcs, ax = plt.subplots(2, 4, figsize=(20, 10), subplot_kw={'projection': template_wcs2}) # 存下來就好看了
ax_flat = ax.flatten() # 壓成 1d 這樣可以用洄圈
for i in range(7):
    if i == 6: #chi2
        splot = ax_flat[i].imshow(chi2_min_full, vmax=6, origin='lower', cmap='tab10')

        cbar = fig_wcs.colorbar(splot, ax=ax_flat[i], fraction=0.046, pad=0.04)
        ax_flat[i].set_xlabel('Right Ascension')
        ax_flat[i].set_ylabel('Declination')
        ax_flat[i].set_title('chi2 min')
    else: # physical conditions
        splot = ax_flat[i].imshow(best_phy_full[:, :, i], origin='lower', cmap=phy_info[i][2])
        cbar = fig_wcs.colorbar(splot, ax=ax_flat[i], fraction=0.046, pad=0.04) # 神奇小數值
        cbar.set_label(phy_info[i][1])
        ax_flat[i].set_xlabel('Right Ascension')
        ax_flat[i].set_ylabel('Declination')
        ax_flat[i].set_title(f'{phy_info[i][0]}')

ax_flat[-1].set_visible(False) # 新技術欸, 關掉多餘的 ax
plt.tight_layout() # 神奇妙妙工具
#'''

# -------------------------- Plot with offset -------------------------- #
