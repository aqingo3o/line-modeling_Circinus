# You should put this script on feifei,
# because of the hard-coded folder path
'''
Make the error map of datacubes, which had been cropped by CASA ({projectRoot}/data/alma_cube/cropped_cube)
ever ring of **dr** have different noise level...?

多虧我大便一般的寫法, 跑這個腳本需要頗多時間哈哈屁眼

因為要加上座標的關係, 才決定用字典儲存資料...每次做到最後就會變成這一步
再開一個新串列我真的會擔心索引爆掉
'''

from astropy import units as u
import matplotlib.pyplot as plt
import numpy as np
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')
warnings.filterwarnings('ignore', message='Degrees of freedom <= 0 for slice')

# Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus'
dataPath = f'{projectRoot}/data/alma_cube/smoothed_cube'

# (mole_fileName, band_fileName, (blankChannel))
# mole_info 和 cube_info 要分開份是因為這樣才可以點菜!
moles_info = [('co-10',   '3b', (113, 320, 727, 906)),
              ('13co-10', '3a', (56, 316, 721, 900)),
              ('c18o-10', '3a', (182, 475, 893, 1094)),
              ('co-21',   '6a', (86, 327, 1036, 1323)),
              ('13co-21', '6a', (41, 257, 1012, 1544)),
              ('c18o-21', '6a', (65, 275, 1043, 1200)),
              ]

cube_info = {} 
'''
cube_info =  {[mole1], [mole2], ...}
字典可以以文字為索引
其中 cube_info[molen] = {
        "cube":  cube, # cube 本人
        "wcs":   cube.wcs.celestial,              # error map 的座標物件, 所以是二維
        "rmask": ringMaskList_mole, # 直接存 mask 了
        "emap":  erreoMap_mole,     # error map array (把 noise 填入 ring or 初始化的東西)
    }
雙層字典的概念, 方便以鍵取值
'''

dr = 0.2 * u.arcsec # ring-shaped mask 的寬度, radius_outer += dr

for molename, band, _ in moles_info:
    # --------------------------- Get Info from Cube --------------------------- #
    # Load the Cube
    cube = SpectralCube.read(f'{dataPath}/cube_Band{band}_{molename}_smooth3.2as.fits')
    print(f'cube_Band{band}_{molename}_smooth3.2as.fits was loaded.')
    
    # Find the **Center** of the Observation
    ra_crval  = cube.wcs.wcs.crval[0] * u.deg
    dec_crval = cube.wcs.wcs.crval[1] * u.deg
    dec_cr_rad = dec_crval.to(u.rad) # 用來修正投影用的所以單位是 rad, 需要修正因為 Circinus 有點高緯

    # Length-related and Distance Matrix (獲取每點與中心的距離矩陣)
    dec_mat, ra_mat = cube.spatial_coordinate_map
    '''# .spatial_coordinate_map 回傳 dec, ra 矩陣, 他媽的什麼爛順序, 
    單位是 deg, *_crval 系列也都是 deg 為單位, 所以等下可以運算每點與中心(*_crval)距離
    '''
    delta_dec = (dec_mat - dec_crval) # 跨越緯線的長度(在兩條緯線之間移動)不會變, 所以就一般一般
    delta_ra = (ra_mat - ra_crval) * np.cos(dec_cr_rad) # 跨越經線的長度, 乘上中心點的緯度 (仰角) 作為修正, 因為高緯的倆驚現距離短er
    dist_mat = np.sqrt(delta_ra**2 + delta_dec**2).to(u.arcsec) # 就是計算距離, 一次性算完

    rfov = (0.5 * (dec_mat.max()-dec_mat.min())).to(u.arcsec) # field of view 的 ridius 的意思

    # --------------------------- Make Ring-like Masks --------------------------- #
    # Initilize
    ringMaskList_mole = [] 
    radius_inner = 0 * u.arcsec 
    radius_outer = 0.2 * u.arcsec # 第一次是內圈為 0, 外圈 1個dr arcsec 的圓形

    while radius_outer < rfov: # 兩個單位都是角秒
        ringMask = (dist_mat > radius_inner) & (dist_mat <= radius_outer) # 區間內標示為 True, use "&" rather than "and".
        ringMaskList_mole.append(ringMask.copy()) # !!! 注意可變物件的問題 !!! 詳見 github history 吧
        # Next Ring
        radius_inner = radius_outer.copy()
        radius_outer += dr

    # Save Cube Information and Ring Masks into dict.
    cube_info[molename] = {
        "cube":  cube, # cube 本人
        "wcs":   cube.wcs.celestial, # 要給 erroeMap 用的座標所以是二維, cube.wcs 有三維的樣子
        "rmask": ringMaskList_mole,
        "emap":  np.full_like(dist_mat.value, np.nan),
    }
    '''# "emap"
    先塞一堆**沒單位的** nan, 主要是需要和 dist_mat 一樣長相的一塊板子
    待會再填值
    因為這邊沒單位, 所以後面填值的時候也不能填入有單位的值
    因為我的 noise 在算的時候是有單位的 (noise = 0 * (u.Jy/u.beam))
    所以在將 noise 填入 errorMap_mole 的時候要先除掉單位 (noise.value)

    撇掉單位的好處是 imshow() 不會抽風, 算是誤打誤撞了

    題外話:
    co(1-0) 外面會有一圈 0, 他媽的那個 cube 怎麼切怎麼炸
    '''

# ----------- Measure an d Filling Noise (std.) in Each Ring-Shaped Mask ------------ #
for molename, _, cblank in moles_info:
    # Measuring Noise
    for ringMask in cube_info[molename]['rmask']:
        cube_masked = cube_info[molename]['cube'].with_mask(ringMask)
        noise = 0 * (u.Jy/u.beam) # 歸零, 放個單位
        for c in cblank: # each blank channel
            noise += (np.nanstd(cube_masked[c].filled_data[:])) / (len(cblank))
    # Filling Noise
        cube_info[molename]['emap'][ringMask] = noise.value # 填 error map 的時候不要單位

    print(f"{molename}'s error map was done :)")
    # Go to Next Molecule :)

# ------------------------------- Plot Error Maps ------------------------------- #
fig, ax = plt.subplots(2, 3, figsize=(10, 6))
ax_flat = ax.flatten() # 壓成 1d 這樣可以用洄圈, 之前慣用的寫法

i = 0
for molename, _, _ in moles_info:
    errorMap = cube_info[molename]['emap']
    im = ax_flat[i].imshow(errorMap, origin='lower', cmap='gray', vmin=0, vmax=np.nanmax(errorMap))
    fig.colorbar(im, ax=ax_flat[i]) # 他媽的有夠雞巴醜拜託改一下好不好, 一根在那邊是三小
    ax_flat[i].set_title(f"{molename}'s error map")
    i += 1 # 有點醜但就這樣吧!

plt.tight_layout() # 神奇小魔法
plt.show()