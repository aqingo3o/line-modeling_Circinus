# You MUST put this script on feifei,
# because of the hard-coded folder path
# 因為差勁的算法, 所以運行速度極慢
'''
Convert the flux density unit from Jy/beam to Kelvin
2 = to ;)
和 cube_mom0Maker.py 分開, 因為這是在 mom0 上的操作, 比較沒有 cube 的事了

Tech ref:
- astropy.Units, Brightness Temperature and Surface Brightness Equivalency: 
  https://docs.astropy.org/en/stable/units/equivalencies.html#built-in-equivalencies
- the equivakency -- brightness_temperature():
  https://docs.astropy.org/en/stable/api/astropy.units.brightness_temperature.html#astropy.units.brightness_temperature
- <Tools>: 並無, 因爲老子根他媽本看不懂

** 這邊用了雙層回圈進行計算, 非常之缺乏效率
   比較優良的寫法請見 scripts/
'''

from astropy.io import fits
from astropy import units as u
import glob
import numpy as np
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')

# Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
mom0Path = f'{projectRoot}/data/mom0'

# Read Mom0 Files **Name**
'''
用了讀檔案之術, 因為有些 sigma 的 mom0 之後可能會刪掉...
還是直接讀比較直觀吧
'''
mom0_fn = [] #fn for fileName
for i in glob.glob(f'{mom0Path}/mom0_*.fits'):
    mom0_fn.append(i[len(mom0Path)+1:])
mom0_fn.sort() # 整理一下, 下個檢查點會比較方便
'''
簡化到有點噁心了, 全部展開來寫應該是這樣

mom0FULL = glob.glob(f'{mom0Path}/mom0_*.fits')
# mom0FULL 是一個串列, 裡面會像是
# 這樣 '/Users/aqing/Documents/1004/line-modeling_Circinus/data/mom0/mom0_co-21_smooth3.2as_5.0sigma.fits'
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
    if 'unitK' in i.split('_'):
        mom0_fn.remove(i) # 因為轉換前後的 mom0 是放在同一個資料夾下, 轉換後的檔名會帶有'unitK', 避免複寫問題...
    files_info.append((i.split('_')[1], i.split('_')[3][:3]))
    '''
    因為 mom0 的檔名規範是 mom0_13co-21_smooth3.2as_5.0sigma.fits 這樣
    以 '_' 為分隔符切出來的串列會是 ['mom0', '13co-21', 'smooth3.2as', '5.0sigma.fits']
    這邊將 molecule 以及存在的 Nsigma 版本存成 tuple, 並塞進 mom0_info
    繞很大一圈只希望有些版本的 sigma 刪掉後腳本仍然能自己運行...
    '''

'''# 容器總結 (有用到的)
- mom0_fn:    字串餡兒的串列, 從 folder 裡讀未轉換亮度單位的 mom0.fits 檔名, 
- files_info: 大串列包小元組, 切分後的檔名關鍵字, 以 tuple 儲存, i.e. [('co-10', '3.0'), (13co-21, '4.5'), ...]
- mom0_info:  大字典包小字典, 儲存 FITS 開出來的資料, 第一層索引是 [f'{molename}_{nsig}'], 
              i.e. co-21_3.5, nsig 代表積分時 masked 掉了幾個 sigma
'''

# Constants
smoothTO = 3.2 # 因為之後可能會 smooth 到不同 beam size... 早該這麼幹了
fwhm2sigma = 1. / (8 * np.log(2))**0.5 # Gaussian beam 的常數
z = 0.001448 * u.dimensionless_unscaled # red shift of the Circinus
count = 1 # 顯示計數用的, 因為這個要跑 30 分鐘以上

# Main
for molename, nsig in files_info:
    # Get Data from mom0s
    hdul = fits.open(f'{mom0Path}/mom0_{molename}_smooth{smoothTO}as_{nsig}sigma.fits') # astropy.io

    mom0_Jb = hdul[0].data.squeeze() # Jy/beam 簡稱他嗎雞ㄅ, 這個是可以 imshow() 的那個部分, ssp 時期好像叫他 ima
    mom0_K = np.full_like(mom0_Jb, np.nan) # 先畫一張空白的圖

    header = hdul[0].header
    f0 = header['RESTFRQ'] * u.Hz
    freq = f0 / (1+z) # shifted frequency
    bmaj, bmin = header['BMAJ'] * u.deg, header['BMAJ'] * u.deg # fwhm 的部分
    OmegaB = (2 * np.pi) * (bmaj * fwhm2sigma) * (bmin * fwhm2sigma) # ()是好看用的
    
    # Converting
    print(f"Converting intensity unit of {molename}'s mom0...")
    print('It takes time, pleasse wait...') # 幹這真的要一段時間欸, 但不是很想寫平行處理
    for x in range(mom0_Jb.shape[0]):
        for y in range(mom0_Jb.shape[1]):
            fluxD = mom0_Jb[x, y] * (u.Jy/OmegaB)
            T_B = fluxD.to(u.K, equivalencies=u.brightness_temperature(freq))
            mom0_K[x, y] = T_B.value
    print(f'Finish the convertion! ({count}/{len(files_info)})')
    count += 1

    # Save as FITS
    fitsOut = f'{mom0Path}/mom0_unitK_{molename}_smooth{smoothTO}as_{nsig}sigma.fits'
    # Write(revise) Header
    header['OBJECT'] = 'Circinus Galaxy'
    header['BUNIT'] = 'Kelvin km/s' # 大便般的格式
    header['COMMENT'] = 'Convert the intensity unit from Jy/beam to Kevlin, by qing'
    fits.writeto(fitsOut, mom0_K, header, overwrite=True) # 依序填入: 檔名、內餡(圖的部分)、標頭

print()
print('All mom0s are done and saved as FITS with file name "mom0_unitK_*.fits":)')
