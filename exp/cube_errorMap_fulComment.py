# You should put this script on feifei,
# because of the hard-coded folder path
'''
Make the error map of datacubes, which had been cropped by CASA ({projectRoot}/data/alma_cube/cropped_cube)
ever ring of **dr** have different noise level...?

多虧我大便一般的寫法, 跑這個腳本需要頗多時間哈哈屁眼
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
#dataPath = f'{projectRoot}/data/alma_cube/cropped_cube'
dataPath = f'{projectRoot}/data/alma_cube/smoothed_cube'

# (mole_fileName, band_fileName, (blankChannel))
moles_info = [('co-10',   '3b', (113, 320, 727, 906)),
              ('13co-10', '3a', (56, 316, 721, 900)),
              ('c18o-10', '3a', (182, 475, 893, 1094)),
              ('co-21',   '6a', (86, 327, 1036, 1323)),
              ('13co-21', '6a', (41, 257, 1012, 1544)),
              ('c18o-21', '6a', (65, 275, 1043, 1200)),
              ]
noiseList, radiiList, errorMap = [], [], []
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
# errorMap
[[co-10的error map], [13co-10的error map], ...]
'''

dr = 0.2 * u.arcsec # ring-shaped mask 的寬度, radius_outer += dr
# Main
for molename, band, cblank in moles_info:
    # --------------------------- Get Info from Cube --------------------------- #
    cube = SpectralCube.read(f'{dataPath}/cube_Band{band}_{molename}_smooth3.2as.fits')
    print(f'cube_Band{band}_{molename}_smooth3.2as.fits was loaded.')

    # Find the **Center** of the Observation
    ra_crval  = cube.wcs.wcs.crval[0] * u.deg
    dec_crval = cube.wcs.wcs.crval[1] * u.deg
    dec_cr_rad = dec_crval.to(u.rad) # 用來修正投影用的所以單位是 rad, 需要修正因為 Circinus 有點高緯

    # Length-related and Distance Matrix (每點與中心的距離矩陣)
    dec_mat, ra_mat = cube.spatial_coordinate_map
    '''# .spatial_coordinate_map 回傳 dec, ra 矩陣, 他媽的什麼爛順序, 
    單位是 deg, *_crval 系列也都是 deg 為單位, 所以等下可以運算每點與中心(*_crval)距離
    '''
    delta_dec = (dec_mat - dec_crval) # 跨越緯線的長度(在兩條緯線之間移動)不會變, 所以就一般一般
    delta_ra = (ra_mat - ra_crval) * np.cos(dec_cr_rad) # 跨越經線的長度, 乘上中心點的緯度 (仰角) 作為修正, 因為高緯的倆驚現距離短er
    dist_mat = np.sqrt(delta_ra**2 + delta_dec**2).to(u.arcsec) # 就是計算距離, 一次性算完
 
    fov_r = (0.5*(dec_mat.max() - dec_mat.min())).to(u.arcsec) # field of view 的 ridius 的意思


    # --------------------------- Initilize Error Map --------------------------- #
    #errorMap_mole = np.zeros_like(dist_mat.value)
    errorMap_mole = np.full_like(dist_mat.value, np.nan)
    '''
    先塞一堆**沒單位的** nan, 主要是需要和 dist_mat 一樣長相的一塊板子
    待會再填值
    因為這邊沒單位, 所以後面填值的時候也不能填入有單位的值
    因為我的 noise 在算的時候是有單位的 (noise = 0 * (u.Jy/u.beam))
    所以在將 noise 填入 errorMap_mole 的時候要先除掉單位 (noise.value)

    撇掉單位的好處是 imshow() 不會抽風, 算是誤打誤撞了

    題外話:
    co(1-0) 外面會有一圈 0, 他媽的那個 cube 怎麼切怎麼炸
    '''


    # -------------- Measure Noise (std.) in Each Ring-Shaped Mask -------------- #
    noiseList_mole = [] # initialize 次拋, 裝的是一款 mole 在各種遮罩下的噪音
    
    # ring-shaped mask's parameters
    radiiList_mole = [] # initilize
    radius_inner = 0 * u.arcsec 
    radius_outer = 0.2 * u.arcsec # 第一次是內圈為 0, 外圈 1個dr arcsec 的圓形

    while radius_outer < fov_r: # 兩個單位都是角秒
        radiiList_mole.append((radius_inner.copy(), radius_outer.copy())) # tuple = (內徑, 外徑)
        #print(f'the radii of ring: {radius_inner} and {radius_outer}') # 靠北沒問題啊
        
        ringMask = (dist_mat > radius_inner) & (dist_mat <= radius_outer) # 區間內標示為 True, use "&" rather than "and".
        cube_masked = cube.with_mask(ringMask)
        noise = 0 * (u.Jy/u.beam) # 歸零，放個單位
        for c in cblank:
            noise += np.nanstd(cube_masked[c].filled_data[:])
        noiseList_mole.append(noise / len(cblank)) # 4 個空白切片的平均...


    # ----------------------------- Fill a Ring of Error Map ----------------------------- #
        errorMap_mole[ringMask] = noiseList_mole[-1].value # 當前這圈(ringMask) 填入最新的(index = -1)一圈噪音, 撇掉單位
        '''
        欸幹這超扯, 布林索引, 就像是真的 mask 一樣
        ringMask 是一個布林矩陣, think it as a matrix that only inside the "ring" is True, else Flase.
        errorMap_mole[ringMask] 就是寫 True 的地方做接下來的動作(填值), 其餘維持原樣(原本是 zeros_like matrix...是否應該改成 nan?) 
        '''
        ### next ring ###
        radius_inner = radius_outer.copy()
        radius_outer += dr
        """錯誤大坑寫法之
        radius_inner = radius_outer
        radius_outer += dr

        操操操操操我之前遇過類似的問題!應該是物數作業的時候
        astropy.units.Quantity 是可變物件, 
        寫 radius_inner = radius_outer 時，並不是把「數值」傳過去，而是讓兩個變數指向同一個物件（同一個記憶體位址）

        就像是現在有兩個變數「阿青」和「年糕」, 已知楊的別稱是阿青, 也就是「阿青」這個變數實際上是指向楊
        當「年糕」與「阿青」等價時, 這倆綽號實際傷都指向楊 (即 radius_inner = radius_outer 這種操作)
        楊 aka 記憶體位置才是**本體**

        當本體變動時, 會牽連所有指向本體的綽號意義, 
        換成 python 的例子就是 radius_outer += dr 這個操作改變ㄌ radius_outer 指向的物件的數值,
        因為 radius_inner 和 radius_outer 指向同一個物件, 所以 radius_inner 的數值也會跟著改變, 
        造成 radiiList 內餡料不符預期
        解方:
        1. .copy(), 確保賦值過去的是一個新東西, 存入 radiiList_mole 的時候也用 .copy(), 這樣可以保留單位
        2. 存進 radiiList_mole 的時候用 .value, 只存值的話就不是 astropy.units.Quantity, 就不是可變物件了
        """

    ### save result and go to next molecule ###
    radiiList.append(radiiList_mole)
    noiseList.append(noiseList_mole)
    errorMap.append(errorMap_mole)
    print(f"{molename}'s error map was done :)")

# /Main
if len(radiiList) == len(moles_info) and len(noiseList) == len(moles_info) and len(errorMap) == len(moles_info):
    print('At least no BIG problem (?)')

# Plot
fig, ax = plt.subplots(2, 3, figsize=(10, 6)) # 不管怎麼調都是一個醜樣
ax_flat = ax.flatten() # 壓成 1d 這樣可以用洄圈, 之前慣用的寫法
for i in range(len(moles_info)):
    subplot = ax_flat[i].imshow(errorMap[i], origin='lower', cmap='gray', vmin=0, vmax=np.nanmax(errorMap[i]))
    fig.colorbar(subplot, ax=ax_flat[i])
    ax_flat[i].set_title(f"{moles_info[i][0]}'s error map")

plt.tight_layout() # 神奇小魔法
plt.show()