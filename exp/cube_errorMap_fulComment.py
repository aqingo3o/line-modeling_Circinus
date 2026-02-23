# You should put this script on feifei,
# because of the hard-coded folder path
'''
Make the error map of datacubes, which had been cropped by CASA ({projectRoot}/data/alma_cube/cropped_cube)
ever ring of **dr** have different noise level...?
'''

from astropy import units as u
import matplotlib.pyplot as plt
import numpy as np
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')

# Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus'
#dataPath = f'{projectRoot}/data/alma_cube/cropped_cube'
dataPath = f'{projectRoot}/data/alma_cube/smoothed_cube'

# (mole_fileName, band_fileName, (blankChannel))
'''
moles_info = [('co-10',   '3b', (113, 320, 727, 906)),
              ('13co-10', '3a', (56, 316, 721, 900)),
              ('c18o-10', '3a', (182, 475, 893, 1094)),
              ('co-21',   '6a', (86, 327, 1036, 1323)),
              ('13co-21', '6a', (41, 257, 1012, 1544)),
              ('c18o-21', '6a', (65, 275, 1043, 1200)),
              ]
'''
# test
moles_info = [('co-10',   '3b', (113, 320, 727, 906)),
              ]
print(len(moles_info))
noiseList, radiiList = [], []
'''
# noiseList
[[co-10每個 ring 中的噪音], [13co-10每個 ring 中的噪音], [c18o-10每個 ring 中的噪音], ...]
# radiiList
[
 [(co-10第1個ring的內徑, 外徑), (co-10第2個ring的內徑, 外徑), ...], 
 [(13co-10第1個ring的內徑, 外徑), (13co-10第2個ring的內徑, 外徑), ...], 
 [(c18o-10第1個ring的內徑, 外徑), (c18o-10第2個ring的內徑, 外徑), ...],
 ...
]
'''

# Main
dr = 0.5 # unit=arcsec. ring-shaped mask 的寬度, radius_outer += dr

for molename, band, cblank in moles_info:
    # load the cube
    cube = SpectralCube.read(f'{dataPath}/cube_Band{band}_{molename}_smooth3.2as.fits')
    print(f'cube_Band{band}_{molename}_smooth3.2as.fits was loaded.')

    # 以中心為中心畫圓
    ra_crval  = cube.wcs.wcs.crval[0] * u.deg
    dec_crval = cube.wcs.wcs.crval[1] * u.deg
    dec_cr_rad = dec_crval.to(u.rad) # 用來修正投影用的, 因為 Circinus 有點高緯

    dec_mat, ra_mat = cube.spatial_coordinate_map
    '''# .spatial_coordinate_map 回傳 dec, ra 矩陣, 他媽的什麼爛順序, 
    單位是 deg, *_crval 系列也都是 deg 為單位, 所以等下可以運算每點與中心(*_crval)距離
    '''

    # 每點與中心的距離矩陣
    delta_dec = (dec_mat - dec_crval) # 跨越緯線的長度(在兩條緯線之間移動)不會變, 所以就一般一般
    delta_ra = (ra_mat - ra_crval) * np.cos(dec_cr_rad) # 跨越經線的長度, 乘上中心點的緯度 (仰角) 作為修正, 因為高緯的倆驚現距離短er
    dist_mat = np.sqrt(delta_ra**2 + delta_dec**2).to(u.arcsec) # 就是計算距離, 一次性算完
 
    fov_r = (0.5*(dec_mat.max() - dec_mat.min())).to(u.arcsec) # field of view 的 ridius 的意思
    noiseList_mole = [] # 次拋, 裝的是一款 mole 在各種遮罩下的噪音

    # ring-shaped mask's parameters
    radiiList_mole = [] # initilize
    '''
    radius_inner = 0 * u.arcsec 
    radius_outer = 1 * u.arcsec 
    '''
    radius_inner = 0
    radius_outer = 1 # 第一次是內圈為0, 外圈 1 arcsec 的圓形

    # for each molecule
    while radius_outer < fov_r.value:
        radiiList_mole.append((radius_inner, radius_outer)) # tuple = (內徑, 外徑), 這邊 dimless 但單位是 arcsec
        
        ringMask = (dist_mat.value > radius_inner) and (dist_mat.value <= radius_outer) # 區間內標示為 True
        cube_masked = cube.with_mask(ringMask)
        noise = 0 * (u.Jy/u.beam) # 歸零，放個單位
        for c in cblank:
            noise += np.nanstd(cube_masked[c].filled_data[:])
            '''# 他媽的這邊我用超久
            cube[c] 就是 cube 的第c個 channel
            filled_data[:] 像是取出所有值並轉職成一維陣列？
            因為充滿 nan 所以要用 np.nanstd()
            '''
        noiseList_mole.append(noise / len(cblank)) # 4 個空白切片的平均...

        # next ring
        radius_inner = radius_outer
        radius_outer += dr

    noiseList.append(noiseList_mole)
    radiiList.append(radiiList_mole)
    print(f'Noise statistics for {molename} was done :)')


if len(noiseList) == len(moles_info):
    print('At least no BIG problem?')