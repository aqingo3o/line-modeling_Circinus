# You MUST put this script on feifei,
# because of the hard-coded folder path
'''
How much Jy/beam of noise should be masked when generating mom0.  
the datacubes had been cropped by CASA ({projectRoot}/data/alma_cube/cropped_cube)
(can't do crop on feifei due to some cubes are too big.)
'''

from astropy import units as u
import numpy as np
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')

# Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # 因為不知道校本確切來說會放哪所以這樣比較順暢吧
dataPath = f'{projectRoot}/data/alma_cube/cropped_cube'

# (mole_fileName, band_fileName, (blankChannel))
moles_info = [ # for test
    ('13co-10', '3a', (56, 316, 721, 900)),
]

noiseList = []
radiiList = []

# Main
radii_step = 0.5 * u.arcsec # 每 0.5 arcsec 做一個 mask
for molename, band, cblank in moles_info:
    cube = SpectralCube.read((f"{dataPath}/cube_Band{band}_{molename}_cropped.fits"))
    print(f'cube_Band{band}_{molename}_cropped.fits was loaded.')

    ra_crval  = cube.wcs.wcs.crval[0] * u.deg
    dec_crval = cube.wcs.wcs.crval[1] * u.deg
    dec_cr_rad = dec_crval.to(u.rad) # 修正投影用的, Circinus 有點高緯

    dec_mat, ra_mat = cube.spatial_coordinate_map
    delta_dec = (dec_mat - dec_crval)
    delta_ra = (ra_mat - ra_crval) * np.cos(dec_cr_rad)
    dist_mat = np.sqrt(delta_ra**2 + delta_dec**2).to(u.arcsec)
    fov_r = (0.5*(dec_mat.max() - dec_mat.min())).to(u.arcsec) # field of view 的 ridius 的意思

    noiseList_mole = []
    radiiList_mole = np.arange(1, fov_r.value, step=radii_step.value)
    for r in radiiList_mole:
        mask = dist_mat.value <= r # <= 的標示為 True
        cube_masked = cube.with_mask(mask)
        noise = 0 * (u.Jy/u.beam) # 歸零，放個單位
#'''
        for c in cblank:
            noise = np.nanstd(cube_masked[c].filled_data[:])
            '''# 他媽的這邊我用超久
            cube[c] 就是 cube 的第c個 channel
            filled_data[:] 像是取出所有值並轉職成一維陣列？
            因為充滿 nan 所以要用 np.nanstd()
            '''
        noiseList_mole.append(noise / len(cblank)) # avg

    noiseList.append(noiseList_mole)
    radiiList.append(radiiList_mole)
#'''
print(noiseList)
print(len(noiseList[0]))
print('finalllllllllly')