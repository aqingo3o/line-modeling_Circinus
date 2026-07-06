# Script for both server (blackhole) and feifei
'''
Convert flux unit from Jy/beam to Kelvin **before** cube smoothing.

ref:
- map_convert2Kandreproj.py
Tech ref:
- the equivakency -- brightness_temperature():
    https://docs.astropy.org/en/stable/api/astropy.units.brightness_temperature.html#astropy.units.brightness_temperature

update: 2026-07-05, Do the unit conversion in cube state and before smoothing.
'''

# --------------------------------- Import Module -------------------------------- #
from astropy.io import fits
from astropy import units as u
import numpy as np
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*Cube is a Stokes cube.*')
warnings.filterwarnings('ignore', message='.*PV2_.*')

# ------------------------------- Path Variables ---------------------------------- #
projectRoot = '/home/aqing/Documents/line-modeling_Circinus' # blackhole
#projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei, for testing
dataPath = f'{projectRoot}/data/alma_cube/cropped_cube'
KPath = f'{projectRoot}/data/alma_cube/K_cube'
 
# --------------------------- Constants & Variables ------------------------------- #
fwhm2sigma = 1. / (8 * np.log(2))**0.5  # constant of Gaussian beam
z = 0.001448 * u.dimensionless_unscaled # red shift of the Circinus
moles_info = [('co-10',    '3b'),
              #('13co-10', '3a'),
              #('co-21',   '6a'),
              #('13co-21', '6a'),
              #('c18o-21', '6a'),
              #('co-32',   '7'),
              ]

# ------------------------- Conversion & Save as FITS ----------------------------- #
count = 1
for molename, band in moles_info:
    # Load the cube
    hdul = fits.open(f'{dataPath}/cube_Band{band}_{molename}_cropped.fits')
    data_Jb = hdul[0].data.squeeze() # Jy/beam 簡稱他嗎雞ㄅ, 但其實這個 array 不帶有單位
    header = hdul[0].header
    hdul.close()

    # Prepare parameter (OmegaB & frequency)
    bmaj, bmin = header['BMAJ'] * u.deg, header['BMIN'] * u.deg      # fwhm
    OmegaB = (2 * np.pi) * (bmaj * fwhm2sigma) * (bmin * fwhm2sigma) # Beam area

    freq_axis = SpectralCube.read(
        f'{dataPath}/cube_Band{band}_{molename}_cropped.fits'
        ).spectral_axis # array with unit (header['CUNIT3'])
    '''
    Usually call it 'spec_axis',
    but i'll put this into brightness_temperature equivalency,
    so i want to name it as 'freq_axis'.
    '''

    # Unit Convertion
    cvFactor = (1 * u.Jy/OmegaB).to(u.K, equivalencies=u.brightness_temperature(freq_axis))
    cvFactor = cvFactor.value
    print(f"Converting intensity unit of {molename}'s cube from {header['BUNIT']} to Kelvin...")
    data_K = data_Jb * cvFactor[:, None, None]
    print(f'Finish conversion. ({count}/{len(moles_info)})')

    # Revise Header
    header['BUNIT'] = 'K'
    header['HISTORY'] = "Convert cube's unit from surface brightness(Jy/beam) into "
    header['HISTORY'] = "brightness temperature(Kelvin), by qing, 2026-07-06"

    # Save as FITS
    fitsOut = f'{KPath}/cube_Band{band}_{molename}_K.fits'
    fits.writeto(fitsOut, data_K, header, overwrite=True) # cannot write Quantities to file.
    print(f'Saved cube_Band{band}_{molename}_K.fits to K_cube/.')

    count += 1
print('All Done :)')