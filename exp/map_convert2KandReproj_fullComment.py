# Run this script on feifei, due to the file structure.
# Works on mom0 and error maps.
'''
Convert the flux density unit of mom0 and error maps from Jy/beam to Kelvin, 
2 = to ;)
And reproject maps to CO(2-1)'s grid, for the next step fitting.

from mom0_convert2K_fulComment.py, 但已將 converting 的迴圈改成了矩陣相乘
因為加上 reproject 的動作所以新開一個檔,
並且這會取代 scripts/mom0_convert2K.py as scripts/map_convert2KandReproj.py

Tech ref:
- astropy.Units, Brightness Temperature and Surface Brightness Equivalency: 
    https://docs.astropy.org/en/stable/units/equivalencies.html#built-in-equivalencies
- the equivakency -- brightness_temperature():
    https://docs.astropy.org/en/stable/api/astropy.units.brightness_temperature.html#astropy.units.brightness_temperature
- <Tools>: 
    並無, 因爲老子根他媽本看不懂
- reproject-Regular celestial images and cubes: 
    https://reproject.readthedocs.io/en/stable/celestial.html
- reproject_adaptive:
    https://reproject.readthedocs.io/en/stable/api/reproject.reproject_adaptive.html#reproject.reproject_adaptive

** 這邊用了雙層回圈進行計算, 非常之缺乏效率
   比較優良的寫法請見 scripts/
   以及, 這邊因為是舊版, 沒有存檔成 .npy 的功能
   完全就是一個懷舊情懷
'''

# --------------------------------- Import Module -------------------------------- #
from astropy.io import fits
from astropy import units as u
import glob
import numpy as np
from reproject import reproject_adaptive
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')

# ------------------------------- Path Variables ---------------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
mom0Path = f'{projectRoot}/data/mom0_map'
emapPath = f'{projectRoot}/data/error_map'
mom0npyPath = f'{projectRoot}/data/mom0_npy'

# --------------------------- Constants & Variables ------------------------------- #
smoothTO = 3.2 # 因為之後可能會 smooth 到不同 beam size... 早該這麼幹了
fwhm2sigma = 1. / (8 * np.log(2))**0.5 # Gaussian beam 的常數
z = 0.001448 * u.dimensionless_unscaled # red shift of the Circinus
count = 1 # 迴圈計數用的
maps_info = {}

# -------------------------- Read Mom0 Files **Name** ----------------------------- #
'''
用了讀檔案之術, 因為有些 sigma 的 mom0 之後可能會刪掉...
還是直接讀比較直觀吧
'''
mom0_fn = [] # fn for fileName
for i in glob.glob(f'{mom0Path}/mom0_*.fits'):
    mom0_fn.append(i[len(mom0Path)+1:])
mom0_fn.sort() # 整理一下, 下個檢查點會比較方便
'''
簡化到有點噁心了, 全部展開來寫應該是這樣

mom0FULL = glob.glob(f'{mom0Path}/mom0_*.fits')
# mom0FULL 是一個串列, 裡面會像是
# 這樣 '/Users/aqing/Documents/1004/line-modeling_Circinus/data/mom0_map/mom0_co-21_smooth3.2as_5.0sigma.fits'
# 這樣子的一整坨, 全部的檔名
# 因為要切切的話, 前面那串包含在 mom0Path 中的部分都是不必要的

mom0_fn = []
# 所以創造一個 mom0_fn 串列裝 'mom0_13co-21_smooth3.2as_4.5sigma.fits' 這樣的短檔名

for i in mom0FULL:
    shortName = i[len(mom0Path)+1:]]
    # 短檔名就是前面那坨 (including in momPath) 都不要
    # 試過減號不行了, 所以用字串的索引取值
    # type(i) >> <class 'str'>, i[0] 眾所周知, i[3:] 則代表從索引 3 一直取到最後
    # 在這個場合就是從 len(mom0Path) 取到最後
    # p.s. 微調之後發現是 len(mom0Path)+1 會更好, 反正 print() 出來看看都看得出來 
    mom0_fn.append(shortName)

print(mom0_fn[1])
以上, 變數能省則省
'''
files_info = [] # split filename into elements
for i in mom0_fn:
    sub_fns = i.split('_')
    if 'unitK' in sub_fns:
        mom0_fn.remove(i) # fuck it doesn't work
    files_info.append((sub_fns[0], sub_fns[1], sub_fns[3][:3]))
    '''
    因為 mom0 的檔名規範是 mom0_13co-21_smooth3.2as_5.0sigma.fits 這樣
    以 '_' 為分隔符切出來的串列會是 ['mom0', '13co-21', 'smooth3.2as', '5.0sigma.fits']
    這邊將 map 種類, molecule 以及存在的 Nsigma 版本存成 tuple, 並塞進 mom0_info
    繞很大一圈只希望有些版本的 sigma 刪掉後腳本仍然能自己運行...
    '''

'''# 容器總結 (有用到的)
- mom0_fn:    字串餡兒的串列, 從 folder 裡讀未轉換亮度單位的 mom0.fits 檔名, 
- files_info: 大串列包小元組, 切分後的檔名關鍵字, 以 tuple 儲存, 
              i.e. [('mom0', 'co-10', '3.0'), ('mom0', '13co-21', '4.5'), ...]
'''

# ------------------ Add Emaps' Files **Name** into files_info --------------------- #
'''
因為想要 error map 和 mom0 進同一個流水線
所以 emap 的檔名也要寫進去 files_info
'''
emap_fn = [] # fn for fileName
for i in glob.glob(f'{emapPath}/emap_*.fits'):
    emap_fn.append(i[len(emapPath)+1:])
emap_fn.sort() # 整理一下, 下個檢查點會比較方便
for i in emap_fn:
    sub_fns = i.split('_')
    '''
    error map filename formation: emap_co-21_smooth3.2as.fits
    '''
    files_info.append((sub_fns[0], sub_fns[1], 0.0)) # emap don't have nsig


# ---------------- 1. Convert the Intensity Unit (Jy/beam -> K) -------------------- #
for maptype, molename, nsig in files_info:
    if maptype == 'emap':
        # Get Data from Error Map
        hdu = fits.open(f'{emapPath}/emap_{molename}_smooth{smoothTO}as.fits')[0] # astropy.io
    elif maptype == 'mom0': 
        # Get Data from mom0s
        hdu = fits.open(f'{mom0Path}/mom0_{molename}_smooth{smoothTO}as_{nsig}sigma.fits')[0] # astropy.io

    map_Jb = hdu.data.squeeze() # Jy/beam 簡稱他嗎雞ㄅ, 這個是可以 imshow() 的那個部分, ssp 時期好像叫他 ima
    map_K = np.full_like(map_Jb, np.nan) # 先畫一張空白的圖

    header = hdu.header
    f0 = header['RESTFRQ'] * u.Hz
    freq = f0 / (1+z) # shifted frequency
    bmaj, bmin = header['BMAJ'] * u.deg, header['BMAJ'] * u.deg # fwhm 的部分
    OmegaB = (2 * np.pi) * (bmaj * fwhm2sigma) * (bmin * fwhm2sigma) # ()是好看用的
    
    # Converting
    cvFactor = (1 * u.Jy/OmegaB).to(u.K, equivalencies=u.brightness_temperature(freq)).value
    print(f"Converting intensity unit of {molename}'s mom0...")
    map_K = map_Jb * cvFactor # matrix <3
    print(f'Finish the convertion! ({count}/{len(files_info)})')
    count += 1

    # Save into maps_info
    if maptype == 'emap':
        maps_info[f'{maptype}_{molename}'] = {
            "header" : hdu.header,
            "unitK": map_K,
            }
    elif maptype == 'mom0': 
        maps_info[f'{maptype}_{molename}_{nsig}'] = {
            "header" : hdu.header,
            "unitK": map_K,
            }
        


# ---------------------------- 2. Reproject to CO(2-1) ------------------------------ #
# Make Reprojt Template
template_map = fits.open(f'{mom0Path}/mom0_co-21_smooth3.2as_3.0sigma.fits')[0] # use CO(2-1) as template

#################################他媽的就是做到這邊
template_wcs = WCS(template_hdu.header).celestial # 確保只有 RA/Dec
### 還有 target shape 的問題嗎的啊啊啊啊好玄幻
### 我之前是這樣做的哪 他媽的我早就忘記了
###但是茜草裡面記載有關wcs的搞補好可以修好 ssp 時留下的驚天大疑問
##############################



'''
All cube wiil be reproject with THIS template
選擇 CO(2-1) 因為他的網格比較細 (一個 pixel 對應到的 arcsec 最少)

之後可能會做類似: 視野以 CO(1-0) 為準, 網格大小以 CO(2-1) 為準的新投影
但因為現在主打的是一個跑出來就好, 所以就先犧牲外圈的視野了
'''
revise_header_kw = ['NAXIS1', 'NAXIS2', 'CDELT1', 'CDELT2', 'CRPIX1', 'CRPIX2'] # to revise these header keywords
template_header_kw = {}
for i in revise_header_kw:
    template_header_kw[i] = template_map.header[i]

print(template_header_kw)
'''
因為想說這樣就只要讀一次 header,
走訪字典應該比走訪 spectral cube object 要省時間?
'''

"""
# Show CDELT (header keyword, n arcsec per pixel)
print('Before reprojecting: ')
print('I known TMI but i dont car ;))')
for i in maps_info.keys():
    cdelt = abs(maps_info[i]["header"]['CDELT1'] * 3600)
    print(f"{i}: {cdelt:.3f} arcsec/pixel")
"""
    
# Reprojectttttt
for i in maps_info.keys():
    # Revise Header (from Header Template)
    new_header = maps_info[i]["header"].copy()
    for k, v in template_header_kw.items():
        new_header[k] = v

    # Upsampling...
    upsample, _ = reproject_adaptive((maps_info[i]["unitK"], maps_info[i]["header"]), new_header)



"""
for i in range(1):
    print(1)

    # Save as FITS
    fitsOut = f'{mom0Path}/mom0_unitK_{molename}_smooth{smoothTO}as_{nsig}sigma.fits'
    # Revise Header
    header['OBJECT'] = 'Circinus Galaxy'
    header['BUNIT'] = 'K km s-1'
    header['COMMENT'] = 'Convert the intensity unit from Jy/beam to Kevlin, by qing'
    fits.writeto(fitsOut, map_K, header, overwrite=True) # 依序填入: 檔名、內餡(圖的部分)、標頭

print()
print('All mom0s are done and saved as FITS with file name "mom0_unitK_*.fits":)')
"""