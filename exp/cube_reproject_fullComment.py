# Run this script on feifei, due to the file structure.
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
'''

# --------------------------------- Import Module -------------------------------- #
from astropy.io import fits
from astropy import units as u
import matplotlib.pyplot as plt
import numpy as np
from reproject import reproject_interp, reproject_adaptive
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')

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
template_cube = fits.open(f'{cubeinPath}/cube_Band6a_co-21_smooth3.2as.fits')[0] # use CO(2-1) as template
template_header_kw = ['NAXIS1', 'NAXIS2', 'CDELT1', 'CDELT2', 'CRPIX1', 'CRPIX2'] # to revise
'''
All cube wiil be reproject with THIS template
選擇 CO(2-1) 因為他的網格比較細 (一個 pixel 對應到的 arcsec 最少)

之後可能會做類似: 視野以 CO(1-0) 為準, 網格大小以 CO(2-1) 為準的新投影
但因為現在主打的是一個跑出來就好, 所以就先犧牲外圈的視野了
'''

print('Before reprojecting...')
for molename, band in moles_info:
    # Show CDELT (header keyword, n arcsec per pixel)
    hdu = fits.open(f'{cubeinPath}/cube_Band{band}_{molename}_smooth3.2as.fits')[0]
    cdelt = abs(hdu.header['CDELT1'] * 3600)
    print(f"{molename}: {cdelt:.3f} arcsec/pixel") # 看一下哈
    '''
    一看發現他媽有點不妙...
    from reproject Docs:
    (Interpolation) will not return optimal results if the input and output pixel sizes are very different.
    然後我覺得 10 倍滿 different 的啊操
    那怎麼辦
    '''
    new_header = hdu.header.copy()
    for i in template_header_kw:
        new_header[i] = template_cube.header[i]
    print(hdu.data.squeeze().shape)
    upsample_data = reproject_adaptive((hdu.data.squeeze(), hdu.header), # .squeeze() kills =1 dim, 
                                       # and here should be an HDU object or a tuple of (array, WCS) or (array, Header)
                                       new_header, return_footprint=False) 


print('here')
"""
"""
