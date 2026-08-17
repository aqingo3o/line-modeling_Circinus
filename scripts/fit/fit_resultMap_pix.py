# Do this on feifei because I need mpl
# Use the result of 'fit_fitMANYpix_parallel.py'
# Please first scp back fitting results from blackhole if fitting was done on the server.
'''
update: 2026-08-15, Use result from products/fittingReslut_newscript/
                    , which is come from model grid I mdae by MYSELF (and best fit).
'''
import numpy as np
import matplotlib.pyplot as plt

projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
resultPath = f'{projectRoot}/products/fittingReslut_newscript'

fitting_method = 'bestFit' # or 'MCMC', 'likkelyHood'

map_chi2_min = np.load(f'{resultPath}/map_chi2Min_4para.npy')
map_best_phy = np.load(f'{resultPath}/map_bestPhyCondi_4para.npy')

# 5 panels: 4 physical conditions + chi2
# Order matter!
phy_info = [
    # ('plot title', (map range), 'unit', 'cmap')
    ('Kinetic Temperature (Tk)', (10, 80),    'Kelvin',      'hot'), 
    ('Number Density (nH2)',     (9e2, 9e4),     r'cm$^{-3}$', 'inferno'), 
    ('Column Density (Nco)',     (1e19, 7e19), r'cm$^{-2}$', 'inferno'),
    ('Beam Filling Factor',      (-0.1, 0.4),     '',            'gray'),
    ]

# Plottinggg
fig, ax = plt.subplots(2, 3, figsize=(14, 7)) # 存下來就好看了
ax_flat = ax.flatten() # 壓成 1d 這樣可以用洄圈
for i in range(5):
    if i == 4: #chi2
        splot = ax_flat[i].imshow(map_chi2_min, vmax=20,
                                  origin='lower', cmap='tab10')
        cbar = fig.colorbar(splot, ax=ax_flat[i], fraction=0.046, pad=0.04)
        ax_flat[i].set_title('chi2')
        print()
    else: # physical conditions
        splot = ax_flat[i].imshow(map_best_phy[:, :, i], vmax=phy_info[i][1][1],
                                  origin='lower', cmap=phy_info[i][3])
        cbar = fig.colorbar(splot, ax=ax_flat[i], fraction=0.046, pad=0.04) # 神奇小數值
        ax_flat[i].set_title(f'{phy_info[i][0]}')
        cbar.set_label(phy_info[i][2])

ax_flat[-1].set_visible(False) # 神奇妙妙工具1
plt.tight_layout() # 神奇妙妙工具2
plt.savefig(f'{resultPath}/fig_{fitting_method}_resultMap.png',
            dpi=300, bbox_inches='tight')
plt.show()