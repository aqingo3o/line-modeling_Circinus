# Maybe can't run this on feifei because RAM...
# Still working on this problem.
# !! First $pip install reproject
'''
reproject (resampling) on smoothed 
This time I do this work on cube, instead of on moment map.
Because error maps, which are generate from cube, need to be spatial align, too.

Tech ref:
- reproject-Regular celestial images and cubes: 
    https://reproject.readthedocs.io/en/stable/celestial.html
- reproject_adaptive:
    https://reproject.readthedocs.io/en/stable/api/reproject.reproject_adaptive.html#reproject.reproject_adaptive
- spectral_cube Reprojection:
    https://spectral-cube.readthedocs.io/en/latest/reprojection.html
'''

# --------------------------------- Import Module -------------------------------- #
import matplotlib.pyplot as plt
import numpy as np
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
#warnings.filterwarnings('ignore', message='.*PV2.*')

# ------------------------------- Path Variables ---------------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
cubeinPath = f'{projectRoot}/data/alma_cube/smoothed_cube' # cube-in
reprojPath = f'{projectRoot}/data/alma_cube/reprojed_cube' # reprojected

# -------------------------------- Basic Variables -------------------------------- #
moles_info = [('co-10',   '3b', ), # (mole_fileName, band_fileName, )
              ('13co-10', '3a', ),
              #('c18o-10', '3a', ),
              #('co-21',   '6a', ),
              #('13co-21', '6a', ),
              #('c18o-21', '6a', ),
              ]

# ------------------------------------- Main -------------------------------------- #
template_cube = SpectralCube.read(f'{cubeinPath}/cube_Band6a_co-21_smooth3.2as.fits') # use CO(2-1) as template
'''
All cube wiil be reproject with THIS template
選擇 CO(2-1) 因為他的網格比較細 (一個 pixel 對應到的 arcsec 最少)

之後可能會做類似: 視野以 CO(1-0) 為準, 網格大小以 CO(2-1) 為準的新投影
但因為現在主打的是一個跑出來就好, 所以就先犧牲外圈的視野了
'''
template_header = template_cube.header
revise_header_kw = ['NAXIS1', 'NAXIS2', 'CDELT1', 'CDELT2', 'CRPIX1', 'CRPIX2'] # to revise these header keywords
template_header_kw = {}
for i in revise_header_kw:
    template_header_kw[i] = template_header[i]
'''
因為想說這樣就只要讀一次 header,
走訪字典應該比走訪 spectral cube object 要省時間?
'''

print('Before reprojecting: ')
for molename, band in moles_info:
    # Show CDELT (header keyword, n arcsec per pixel)
    cube = SpectralCube.read(f'{cubeinPath}/cube_Band{band}_{molename}_smooth3.2as.fits')
    cdelt = abs(cube.header['CDELT1'] * 3600)
    print(f"{molename}: {cdelt:.3f} arcsec/pixel") # 看一下哈
    '''
    一看發現他媽有點不妙...
    from reproject Docs:
    (Interpolation) will not return optimal results if the input and output pixel sizes are very different.
    然後我覺得 10 倍滿 different 的啊操
    那怎麼辦
    '''

    # Generate Target Header from Original Header
    new_header = cube.header.copy()

    # Up Sampling...
    '''
    有點爆 RAM 了靠北
    ValueError: This function (<function BaseSpectralCube.reproject at 0x13e4845e0>) 
    requires loading the entire cube into memory, and the cube is large (113126400 pixels),
    so by default we disable this operation. To enable the operation,
    set `cube.allow_huge_operations=True` and try again.
    '''
    for k, v in template_header_kw.items():
        new_header[k] = v
    upsample_cube = cube.reproject(new_header)
    
    # Save as FITS
    upsample_cube.write(f'{reprojPath}/cube_Band{band}_{molename}_smooth3.2as_upsamp2co-21.fits',
                        overwrite=True)
    '''
    再加一個後綴:
    up sampling to CO(2-1)
    shorten >> upsamp2co-21
    '''
print('Done.')
