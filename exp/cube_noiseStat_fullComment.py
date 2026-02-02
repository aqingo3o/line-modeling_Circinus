# You MUST put this script on feifei,
# because of the hard-coded folder path
'''
How much Jy/beam of noise should be masked when generating mom0.  
the datacubes had been cropped by CASA ({projectRoot}/data/alma_cube/cropped_cube)
(can't do crop on feifei due to some cubes are too big.)
'''

from astropy.io import fits
from astropy import units as u
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')

# Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # 因為不知道校本確切來說會放哪所以這樣比較順暢吧
dataPath = f'{projectRoot}/data/alma_cube/cropped_cube'

# (mole_fileName, band_fileName, (blankChannel))
'''
moles_info = [
    ('co-10',   '3b', ()),
    ('13co-10', '3a', ()),
    ('c18o-10', '3a', ()),
    ('co-21',   '6a', ()),
    ('13co-21', '6a', ()),
    ('c18o-21', '6a', ()),
]
'''
moles_info = [ # for test
    #('co-10',   '3b', ()),
    ('13co-10', '3a', (56, 316, 721, 900)),
]
radii_step = 0.5 * u.arcsec

noiseList = []
radiiList = []
'''
# noiseList
[[co-10在各種尺寸遮罩下的噪音], [13co-10在各種尺寸遮罩下的噪音], [c18o-10在各種尺寸遮罩下的噪音], ...]
# radiiList
[[co-10的各種尺寸的遮罩], [13co-10的各種尺寸的遮罩], [c18o-10的各種尺寸的遮罩], ...]
'''

for molename, band, cblank in moles_info: # cblank 是一個長度4的channel串列，標示空的channel
    cube = SpectralCube.read((f"{dataPath}/cube_Band{band}_{molename}_cropped.fits"))
    print(f'cube_Band{band}_{molename}_cropped.fits was opened.')

    ra_crval  = cube.wcs.wcs.crval[0] * u.deg # 以中心為中心畫圓
    dec_crval = cube.wcs.wcs.crval[1] * u.deg # ra&dec 的分辨方式是看數值(參考 print(cube)的輸出, 單位是 deg, 和 carta 不一樣)
    # astropy.unit 的用法是標上他的單位
    # 不是標上你希望的單位白痴  
    # 希望的話要用 .to(u.arcsec) 這樣
    ra_mat, dec_mat = cube.spatial_coordinate_map # 回傳 ra, dec 矩陣
    # 他媽的這 api 裡面根本沒寫啊？
    dist_mat = np.sqrt((ra_mat-ra_crval)**2 + (dec_mat-dec_crval)**2).to(u.arcsec) # 各點與中心(_crval)的距離矩陣
    radii_fov = (0.5*(ra_mat.max() - ra_mat.min())).to(u.arcsec) # 座標最大減最小的一半就是整個視野的半徑, 
    # 原本的單位是 deg, 用 .to() 換成角秒
    # 因為我的 fov看起來很正圓，所以就用 ra 當代表就好（沒差啦報錯再說哈哈）
    
    noiseList_mole = [] # 次拋, 裝的是一個 mole 在各種遮罩下的噪音
    radiiList_mole = np.arange(1, radii_fov.value, step=radii_step.value) # 因為 range() 不能處理浮點步長
    # .value 的原因是只要數值不要單位
    for r in radiiList_mole:
        region = dist_mat.value <= r # mask 的意思但繼承 carta 所以叫他 region
        cube_masked = cube.with_mask(region)
        # .with_mask() 中間填入遮罩
        # 因為 mask 只作用在 cube 上, 所以要先 mask 再切片
        noise = 0
        for c in cblank:
            noise += cube_masked[c].filled_data[:].std()
            # cube[c] 就是 cube 的第c個 channel
            # ._data().std()
        noiseList_mole.append(noise / len(cblank)) # avg

    noiseList.append(noiseList_mole)
    radiiList.append(radiiList_mole) # 寫在這邊比較對稱哈哈
print('done here') # 沒事的就是會奔一堆警告不要緊的
print(noiseList)