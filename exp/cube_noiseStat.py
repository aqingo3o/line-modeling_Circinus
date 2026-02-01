# You MUST put this script on feifei,
# because of the hard-coded folder path
'''
How much Jy/beam of noise should be masked when generating mom0.  
the datacubes had been cropped by CASA ({projectRoot}/data/alma_cube/cropped_cube)
(can't do this on feifei due to some cubes are too big.)
'''

from astropy.io import fits
from astropy import units as u
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np
from spectral_cube import SpectralCube
from qingUtils.astroTool import saveFITS

projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # 因為不知道校本確切來說會放哪所以這樣比較順暢吧
dataPath = f'{projectRoot}/data/alma_cube/cropped_cube'

# (mole_fileName, band_fileName, blankChannel)
mole_info = [
    ('co-10', '3b'),
    ('co-21', '6a'),
    ('13co-10', '3a'),
    ('13co-21', '6a'),
    ('c18o-10', '3a'),
    ('c18o-21', '6a'),
]

for molename, band in mole_info:
    cube = (f"{dataPath}/cube_Band{band}_{molename}_cropped.fits")
    crval_ra = cube.wcs.wcs.crval[0] # 以中心為中心畫圓
    '''
    其實還沒有想好應該要用真實的物理尺寸做 mask，或是用幾個 pixel 這樣
    其實應該沒差，但是
    '''
    crval_dec = cube.wcs.wcs.crval[1] # ra&dec 的分辨方式是看數值(參考 print(cube)的輸出, 單位是 deg, 和 carta 不一樣) 
