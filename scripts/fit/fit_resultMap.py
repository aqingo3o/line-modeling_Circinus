# Do this on feifei because I need mpl
'''
Read fitting results from
- map_chi2Min_partial.npy
- map_bestPhyCondi_partial.npy
and make maps out of it.
'''
import numpy as np
import matplotlib.pyplot as plt

projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
resultPath = f'{projectRoot}/products/fittingResult'

whichone = 'partial'
if whichone == 'partial':
    imrange = (340, 560)
elif whichone == 'wholemap':
    imrange = ()

map_chi2_min = np.load(f'{resultPath}/map_chi2Min_{whichone}.npy')
map_best_phy = np.load(f'{resultPath}/map_bestPhyCondi_{whichone}.npy')
phy_info = [ # Order matter!
    # ('plot title', 'unit', 'cmap')
    ('Colum Density (Nco)',      r'log$N_{\rm CO}$ (cm$^{-2}$)',  'inferno'),
    ('Kinetic Temperature (Tk)', r'log$T_{\rm k}$ (K)',           'hot'), 
    ('Number Density (nH2)',     r'log$n_{\rm H_2}$ (cm$^{-3}$)', 'inferno'), 

    ('12CO/13CO Abundance Ratio', '', 'jet'), 
    ('13CO/C18O Abundance Ratio', '', 'jet'), 
    ('Beam Filling Factor',       '', 'gray'),
    ]

fig, ax = plt.subplots(2, 4, figsize=(12, 12))
ax_flat = ax.flatten() # 壓成 1d 這樣可以用洄圈
for i in range(7):
    if i == 6:
        splot = ax_flat[i].imshow(map_chi2_min[imrange[0]:imrange[1], imrange[0]:imrange[1]], 
                                  origin='lower', cmap='gray')
        cbar = fig.colorbar(splot, ax=ax_flat[i], fraction=0.046, pad=0.04)
        ax_flat[i].set_title('chi2 min')
    else:
        splot = ax_flat[i].imshow(map_best_phy[imrange[0]:imrange[1], imrange[0]:imrange[1], i], 
                                  origin='lower', cmap=phy_info[i][2])
        cbar = fig.colorbar(splot, ax=ax_flat[i], fraction=0.046, pad=0.04) # 神奇小數值
        ax_flat[i].set_title(f'{phy_info[i][0]}')
        cbar.set_label(phy_info[i][1])
        
ax_flat[-1].set_visible(False) # 新技術欸
plt.tight_layout() # 神奇妙妙工具
plt.savefig(f'{resultPath}/map_fittingResult_{whichone}.png', dpi=300, bbox_inches='tight')
plt.show()