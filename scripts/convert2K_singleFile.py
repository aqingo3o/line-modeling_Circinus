# You MUST put this script on feifei,
# because of the hard-coded folder path
### for single FITS file ;))
'''
從 mom0_convert2K.py 那邊複製的, 可以做非流水線的單一用途
'''

from astropy.io import fits
from astropy import units as u
import numpy as np
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')
    
# Constants
smoothTO = 3.2 # part of file name
fwhm2sigma = 1. / (8 * np.log(2))**0.5 
z = 0.001448 * u.dimensionless_unscaled # red shift of the Circinus

# Main
hdul = fits.open('/Users/aqing/Documents/1004/line-modeling_Circinus/data/mom8_co-10_smooth3.2as.fits')

mom0_Jb = hdul[0].data.squeeze()
header = hdul[0].header
f0 = header['RESTFRQ'] * u.Hz
freq = f0 / (1+z) # shifted frequency
bmaj, bmin = header['BMAJ'] * u.deg, header['BMAJ'] * u.deg
OmegaB = (2 * np.pi) * (bmaj * fwhm2sigma) * (bmin * fwhm2sigma)

# Converting
cvFactor = (1 * u.Jy/OmegaB).to(u.K, equivalencies=u.brightness_temperature(freq)).value
mom0_K = mom0_Jb * cvFactor

# Save as FITS
fitsOut = '/Users/aqing/Documents/1004/line-modeling_Circinus/data/mom8_unitK_co-10_smooth3.2as.fits'
# Write(revise) Header
header['OBJECT'] = 'Circinus Galaxy'
header['BUNIT'] = 'K' # 自己輸入正確的單位哈
header['COMMENT'] = 'Convert the intensity unit from Jy/beam to Kevlin, by qing'
fits.writeto(fitsOut, mom0_K, header, overwrite=True) # cannot write Quantities to file.
print()
print('Done.')