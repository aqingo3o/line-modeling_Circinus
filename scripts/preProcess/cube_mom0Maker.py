# You MUST put this script on feifei,
# because of the hard-coded folder path
'''
make mom0 with different noise, 意外的很成功欸?
Tech ref:
- spectral axis unit convertion: https://spectral-cube.readthedocs.io/en/latest/moments.html#moment-maps
- noise masking on cubes:        https://spectral-cube.readthedocs.io/en/latest/masking.html#getting-started
- generate and show moment maps: https://learn.astropy.org/tutorials/FITS-cubes.html#display-the-moment-maps
'''

from astropy import units as u
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')

# Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus'
dataPath = f'{projectRoot}/data/alma_cube/smoothed_cube'
mom0Path = f'{projectRoot}/data/mom0'

# (mole_fileName, band_fileName, restFrequency(GHz), spectralLine_freq(GHz), noise(Jy/beam))
moles_info = [('co-10',   '3b', 115.271, (115.041660, 115.172025), 0.00525), # [freq]:GHz !!
              ('13co-10', '3a', 110.201, (109.974831, 110.108133), 0.00366),
              ('c18o-10', '3a', 109.782, (109.561252, 109.665745), 0.00381),
              #('co-21',   '6a', 230.538, (), 0.00378), # 幹這個壞掉
              ('13co-21', '6a', 220.399, (219,936696, 220.215985), 0.00383),
              ('c18o-21', '6a', 219.560, (219.126176, 219.364939), 0.00407),
              ]

Nsigma = [3.0, 3.5, 4.0, 4.5, 5.0]
# Main
for molename, band, f0, freqrange, noise in moles_info:
    # Load the Cube
    cube = SpectralCube.read(f'{dataPath}/cube_Band{band}_{molename}_smooth3.2as.fits')
    print(f'cube_Band{band}_{molename}_smooth3.2as.fits was loaded.')

    # Extract Spefic Freq Range
    slab = cube.spectral_slab(freqrange[0]*u.GHz, freqrange[1]*u.GHz)

    # Unit Convert: Hz ---> km/s
    slab = slab.with_spectral_unit(u.km/u.s, velocity_convention='radio', rest_value=f0*u.GHz)

    # Making Moment Zero Maps  & Plot 
    for n in Nsigma:
        # Noise Masking
        noiseMask = slab > (n*noise) * (u.Jy/u.beam) 
        slab_masked = slab.with_mask(noiseMask)
        # Integrating
        mom0 = slab_masked.moment(order=0)
        # Save as FITS
        mom0.write(f'{mom0Path}/mom0_{molename}_smooth3.2as_{n}sigma.fits', overwrite=True)
        print(f"{molename}'s moment zero map (masked {n} sigma) was saved as FITS.")

print(':))')
