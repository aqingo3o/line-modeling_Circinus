# You MUST put this script on feifei,
# because of the hard-coded folder path
# use matplotlib<3.8 (3.7.5 here) to avoid "ImportError: cannot import name 'AnchoredEllipse' from 'mpl_toolkits.axes_grid1.anchored_artists'"
'''
make mom0 with different noise, 意外的很成功欸?
Tech ref:
- spectral axis unit convertion: https://spectral-cube.readthedocs.io/en/latest/moments.html#moment-maps
- noise masking on cubes:        https://spectral-cube.readthedocs.io/en/latest/masking.html#getting-started
- generate and show moment maps: https://learn.astropy.org/tutorials/FITS-cubes.html#display-the-moment-maps
程式碼的瘋狂抄抄之旅
'''

from astropy import units as u
import matplotlib.pyplot as plt
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')

# Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus'
dataPath = f'{projectRoot}/data/alma_cube/smoothed_cube'
mom0Path = f'{projectRoot}/data/mom0'

# (mole_fileName, band_fileName, restFrequency(GHz), spectralLine_freq(GHz), noise(Jy/beam))
moles_info = [('co-10',   '3b', 115.271, (115.041660, 115.172025), 0.00525),] # for test
'''
moles_info = [('co-10',   '3b', 115.271, (115.041660, 115.172025), 0.00525), # [freq]:GHz !!
              ('13co-10', '3a', 110.201, (109.974831, 110.108133), 0.00366),
              ('c18o-10', '3a', 109.782, (109.561252, 109.665745), 0.00381),
              ('co-21',   '6a', 230.538, (), 0.00378), # 幹這個壞掉
              ('13co-21', '6a', 220.399, (219,936696, 220.215985), 0.00383),
              ('c18o-21', '6a', 219.560, (219.126176, 219.364939), 0.00407),
              ]
'''
'''# moles_info
- mole_fileName, band_fileName: cube 的檔名,  mole_fileName 附帶 mom0.fits 命名功能
- restFrequency (GHz):          轉頻率軸單位 (Hz ---> km/s) 的時候要用的
- spectralLine_freq (GHz):      mom0 要積分的頻率範圍, 單位是 **GHz** (因為我 cube 的頻率軸單位是 Hz, 要用 velocoty 的話再自己寫轉換哈)
                                單位可以直接把 cube = SpectralCube.read() 的 cube print 出來, 或是 print(cube.spectral_axis.unit)
- noise (Jy/beam):              做 mom0 時 mask 掉的那個 sigma, 從 cube_noiseStat.py 來的, 和 error map 好像不是一個意思?
'''

Nsigma = [3.0, 3.5, 4.0, 4.5, 5.0] # masked 掉幾個 sigma 的「幾」
# Main
for molename, band, f0, freqrange, noise in moles_info:
    # Load the Cube
    cube = SpectralCube.read(f'{dataPath}/cube_Band{band}_{molename}_smooth3.2as.fits')
    print(f'cube_Band{band}_{molename}_smooth3.2as.fits was loaded.')

    # Extract Spefic Freq Range
    slab = cube.spectral_slab(freqrange[0]*u.GHz, freqrange[1]*u.GHz)
    '''
    像是切 cube 的概念 (casatasks.imsubimage())
    因為 SpectralCube 的 moment() 沒有範圍參數, 
    積分範圍就是整個 cube 物件, 所以要切
    '''

    # Unit Convert: Hz ---> km/s
    slab = slab.with_spectral_unit(u.km/u.s, velocity_convention='radio', rest_value=f0*u.GHz)

    # Making Moment Zero Maps
    for n in Nsigma:
        # Noise Masking
        noiseMask = slab > (n*noise) * (u.Jy/u.beam) 
        slab_masked = slab.with_mask(noiseMask) # 分開寫啦, 比較沒有那麼一坨糊在一起
        # Integrating
        mom0 = slab_masked.moment(order=0) 
        # Save as FITS
        mom0.write(f'{mom0Path}/mom0_{molename}_smooth3.2as_{n}sigma.fits', overwrite=True)
        print(f"{molename}'s moment zero map (masked {n} sigma) was saved as FITS.")

print(':))')
    
# Plot (for preview)
# 真正的東西就是開 CARTA 看吧