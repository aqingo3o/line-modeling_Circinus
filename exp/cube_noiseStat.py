# You MUST put this script on feifei,
# because of the hard-coded folder path
'''
How much Jy/beam of noise should be masked when generating mom0.  
the datacubes had been cropped by CASA ({projectRoot}/data/alma_cube/cropped_cube)
(can't do crop on feifei due to some cubes are too big.)
'''

from astropy import units as u
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')

# Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus'
dataPath = f'{projectRoot}/data/alma_cube/cropped_cube'

# (mole_fileName, band_fileName, (blankChannel))
moles_info = [('co-10',   '3b', (113, 320, 727, 906)),
              ('13co-10', '3a', (56, 316, 721, 900)),
              ('c18o-10', '3a', (182, 475, 893, 1094)),
              ('co-21',   '6a', (86, 327, 1036, 1323)),
              ('13co-21', '6a', (41, 257, 1012, 1544)),
              ('c18o-21', '6a', (65, 275, 1043, 1200))
              ]

noiseList, radiiList = [], []

# Main
radii_step = 0.5 * u.arcsec
for molename, band, cblank in moles_info:
    cube = SpectralCube.read((f"{dataPath}/cube_Band{band}_{molename}_cropped.fits"))
    print(f'cube_Band{band}_{molename}_cropped.fits was loaded.')

    # 以中心為中心畫圓
    ra_crval  = cube.wcs.wcs.crval[0] * u.deg
    dec_crval = cube.wcs.wcs.crval[1] * u.deg
    dec_cr_rad = dec_crval.to(u.rad) # 用來修正投影用的, 因為 Circinus 有點高緯

    dec_mat, ra_mat = cube.spatial_coordinate_map
    delta_dec = (dec_mat - dec_crval)
    delta_ra = (ra_mat - ra_crval) * np.cos(dec_cr_rad) 
    dist_mat = np.sqrt(delta_ra**2 + delta_dec**2).to(u.arcsec)
 
    fov_r = (0.5*(dec_mat.max() - dec_mat.min())).to(u.arcsec) # field of view 的 ridius 的意思
    noiseList_mole = [] # 次拋, 裝的是一個 mole 在各種遮罩下的噪音
    radiiList_mole = np.arange(1, fov_r.value, step=radii_step.value)
    '''# 因為 range() 不能處理浮點步長
    .value 的原因是只要數值不要單位
    '''

    for r in radiiList_mole:
        mask = dist_mat.value <= r # <= 的標示為 True
        cube_masked = cube.with_mask(mask)
        noise = 0 * (u.Jy/u.beam) # 歸零，放個單位
        for c in cblank:
            noise += np.nanstd(cube_masked[c].filled_data[:])
            '''# 他媽的這邊我用超久
            cube[c] 就是 cube 的第c個 channel
            filled_data[:] 像是取出所有值並轉職成一維陣列？
            因為充滿 nan 所以要用 np.nanstd()
            '''
        noiseList_mole.append(noise / len(cblank))

    noiseList.append(noiseList_mole)
    radiiList.append(radiiList_mole)
    print(f'Noise statistics for {molename} was done :)')

if len(noiseList)==6:
    print('At least no BIG problem?')

"""
# 應該寫點能把資料存下來的不然有點浪費時間
"""

# plot
# 非常髒的 顧前不顧後的寫法
fig, ax = plt.subplots(2, 3, figsize=(10, 6)) # 不管怎麼調都是一個醜樣
ax_flat = ax.flatten()
for i in range(len(moles_info)):
    noiseList_dimless = []
    for j in noiseList[i]:
        noiseList_dimless.append(j.value)
    ax_flat[i].plot(radiiList[i], noiseList_dimless)
    ax_flat[i].set_title(f'{moles_info[i][0]} noise to r_mask')
    if i==0 or i==3:
        ax_flat[i].set_ylabel('std (Jy/beam)')
    if i>2:
        ax_flat[i].set_xlabel('radius_mask (arcsec)')

    # find peak
    # 好像來不能好
    peaks, _ = find_peaks(radiiList[i], height=0.002)
    ax_flat[i].plot(peaks, radiiList[i][peaks], "x")

   
plt.tight_layout() # 神奇妙妙工具
plt.show()