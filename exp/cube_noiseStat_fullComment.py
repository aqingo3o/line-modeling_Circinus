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
'''
moles_info = [
    ('co-10',   '3b', ()),
    ('13co-10', '3a', (56, 316, 721, 900)),
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

noiseList = []
radiiList = []
'''
# noiseList
[[co-10在各種尺寸遮罩下的噪音], [13co-10在各種尺寸遮罩下的噪音], [c18o-10在各種尺寸遮罩下的噪音], ...]
# radiiList
[[co-10的各種尺寸的遮罩], [13co-10的各種尺寸的遮罩], [c18o-10的各種尺寸的遮罩], ...]
'''

# Main
radii_step = 0.5 * u.arcsec # 每 0.5 arcsec 做一個 mask
for molename, band, cblank in moles_info: # cblank 是一個長度4的channel串列，標示空的channel
    cube = SpectralCube.read((f"{dataPath}/cube_Band{band}_{molename}_cropped.fits"))
    print(f'cube_Band{band}_{molename}_cropped.fits was loaded.')

    # 以中心為中心畫圓
    ra_crval  = cube.wcs.wcs.crval[0] * u.deg # ra213, dec-65, print(cube)說的, 也可以看 carta
    dec_crval = cube.wcs.wcs.crval[1] * u.deg # ra&dec 的分辨方式是看數值(參考 print(cube)的輸出, 單位是 deg, 和 carta 不一樣)
    dec_cr_rad = dec_crval.to(u.rad) # 用來修正投影用的, 因為 Circinus 有點高緯

    dec_mat, ra_mat = cube.spatial_coordinate_map
    '''# .spatial_coordinate_map 這 api 裡面根本沒寫啊?
    回傳 dec, ra 矩陣, 他媽的什麼爛順序, 
    單位是 deg
    *_crval 系列也都是 deg 為單位, 所以等下可以運算每點與中心(*_crval)距離
    '''

    delta_dec = (dec_mat - dec_crval) # 跨越緯線的長度(在兩條尾線之間移動)不會變, 所以就一般一般
    delta_ra = (ra_mat - ra_crval) * np.cos(dec_cr_rad) 
    '''# 乘上中心點的緯度 (仰角) 作為修正
    高緯度的東西跨越經線的時候走的距離比較短
    極點 (90) 的時候跨越經線(delta_ra)的距離為零
    '''
    dist_mat = np.sqrt(delta_ra**2 + delta_dec**2).to(u.arcsec) # 各點與中心(_crval)的距離矩陣, 都換成角秒
 
    fov_r = (0.5*(dec_mat.max() - dec_mat.min())).to(u.arcsec) # field of view 的 ridius 的意思
    '''# 座標最大減最小 的一半 就是整個視野的半徑
    用 dec 算因為他不會變形, 用 ra 也可以啦但要乘 cos(dec_cr_rad)

    原本的單位是 deg, 用 .to() 換成角秒

    幹您娘每個我覺得意義相同的東西值都有差
    print(dec_mat.max() - dec_crval) ---> 0.016054985457955695 deg
    print(dec_crval - dec_mat.min()) ---> 0.016200000215832233 deg
    誒換成角秒會有差欸, 所以中心座標不在幾何中心啊?

    喔但是這點差沒關係啦幹估計噪音而已是要做多久
    會跟 carat 看起來有差是因為他媽的外面那圈 nan(底色) 也是在數據的範圍內啊
    image 其實是正方形, 操

    我的理念就是, 邊緣圈到一堆 nan 的話一定會很醜, 那我就知道這些是爛數據了
    '''
    
    noiseList_mole = [] # 次拋, 裝的是一個 mole 在各種遮罩下的噪音
    radiiList_mole = np.arange(1, fov_r.value, step=radii_step.value)
    '''# 因為 range() 不能處理浮點步長
    .value 的原因是只要數值不要單位
    '''

    for r in radiiList_mole:
        mask = dist_mat.value <= r # <= 的標示為 True
        cube_masked = cube.with_mask(mask)
        '''#做 masking
        用 .with_mask(), 括號中間填入遮罩物件(mask 本人)
        因為 .with_mask() 只作用在 cube 上, 所以要先 mask 再切片
        
        mask 只是把 mask 外的東西標記為 nan, 並沒有真的去「切」影像
        所以
        print(cube)
        print(cube_masked)
        會看起來一樣
        '''
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
    radiiList.append(radiiList_mole) # 寫在這邊比較對稱哈哈
#'''
print(noiseList)
print(len(noiseList[0]))
print('finalllllllllly')