# You MUST put this script on feifei,
# because of the hard-coded folder path
### from *fullComment.py, improved the algorithm.
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
mom0_fn = []
for i in glob.glob(f'{mom0Path}/mom0_*.fits'):
    mom0_fn.append(i[len(mom0Path)+1:])
mom0_fn.sort()

files_info = []
for i in mom0_fn:
    if 'unitK' in i.split('_'): # fuckkkkkkk it doesn't work well
        mom0_fn.remove(i)
    files_info.append((i.split('_')[1], i.split('_')[3][:3]))
    
# Constants
smoothTO = 3.2 # part of file name
fwhm2sigma = 1. / (8 * np.log(2))**0.5 
z = 0.001448 * u.dimensionless_unscaled # red shift of the Circinus

# Main
count = 1
for molename, nsig in files_info:
    # Get Data from mom0s
    hdul = fits.open(f'{mom0Path}/mom0_{molename}_smooth{smoothTO}as_{nsig}sigma.fits')

    mom0_Jb = hdul[0].data.squeeze()
    header = hdul[0].header
    f0 = header['RESTFRQ'] * u.Hz
    freq = f0 / (1+z) # shifted frequency
    bmaj, bmin = header['BMAJ'] * u.deg, header['BMAJ'] * u.deg
    OmegaB = (2 * np.pi) * (bmaj * fwhm2sigma) * (bmin * fwhm2sigma)
    
    # Converting
    cvFactor = (1 * u.Jy/OmegaB).to(u.K, equivalencies=u.brightness_temperature(freq)).value
    print(f"Converting intensity unit of {molename}'s mom0...")
    mom0_K = mom0_Jb * cvFactor
    print(f'Finish the convertion! ({count}/{len(files_info)})')
    count += 1

    # Save as FITS
    fitsOut = f'{mom0Path}/mom0_unitK_{molename}_smooth{smoothTO}as_{nsig}sigma.fits'
    # Write(revise) Header
    header['OBJECT'] = 'Circinus Galaxy'
    header['BUNIT'] = 'K km s-1'
    header['COMMENT'] = 'Convert the intensity unit from Jy/beam to Kevlin, by qing'
    fits.writeto(fitsOut, mom0_K, header, overwrite=True) # cannot write Quantities to file.
print()
print('All mom0s are done and saved as FITS with file name "mom0_unitK_*.fits":)')