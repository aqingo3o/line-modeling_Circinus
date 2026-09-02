# Script for feifei (plt.show()),
# Also work on server (blackhole), but no figure will show.
'''
Make mom0 (.fits) with different noise, and show the spectral line with integral range by mpl.
Recommand not to dispire the ploting part because it can help ypu check the unint, freq... correction.

Tech ref:
- spectral axis unit convertion: https://spectral-cube.readthedocs.io/en/latest/moments.html#moment-maps
- noise masking on cubes:        https://spectral-cube.readthedocs.io/en/latest/masking.html#getting-started
- generate and show moment maps: https://learn.astropy.org/tutorials/FITS-cubes.html#display-the-moment-maps

update: 2026-06-29, new sigma values from cube_noiseStat.py
        2026-07-07, Revise the hard-code part of intensity unit.
        2026-08-19, A new version (_resolve), separate from original one.
                    Make mom0 from cubes that BMAJ ~= 0.3 - 0.4 aresec.
'''

from astropy import units as u
import matplotlib.pyplot as plt
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')
warnings.filterwarnings('ignore', message='.*Stokes cube.*')

# ------------------------------- Path ------------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # fei
dataPath = f'{projectRoot}/data/alma_cube/smoothed_cube'
mom0Path = f'{projectRoot}/data/mom0_map'

# (molename, band, restfreq(GHz), integral_range(channel), noise(Kelvin))
'''
- Noise is stdDev in CARTA
- Integral range should be the same as that in cube_errorMap.py !
'''
moles_info = [ ################# Noise is for 3.2as cubes ##############
              ('co-10',   '3b', 115.271, (1057, 1338), 0.075768),
              ('13co-10', '3a', 110.201, (573, 844),   0.036418),
              ('co-21',   '6a', 230.538, (1125, 1799), 0.070404),
              ('13co-21', '6a', 220.399, (759, 1278),  0.070139),
              ('co-32',   '7',  345.796, (100, 233),   0.073305), # Izumi
              ('c18o-21', '6a', 219.560, (1640, 2100), 0.004495),
              ################# Noise for 0.41as cubes ##################
              ('co-21',   '6a', 230.538, (1125, 1799), 0.8556), ##### NOT GOOD MEASURE NOISE
              ('13co-21', '6a', 220.399, (759, 1278),  0.8119),
              ('co-32',   '7',  345.796, (100, 233),   0.1084),
              ('co-65',   '9h', 219.560, (305, 1640),  1.0439),
              ]

bsize = 0.41 # BMAJ in file name after smoothing,
             # the unii is arcsec.
             # Now we have [3.2, 0.41]
z = 0.001448 * u.dimensionless_unscaled # Circinus redshift
Nsigma = [1.0, 3.0, 5.0, 8.0]

#'''
# ------------------------- Making Moment Zero -------------------------- #
for molename, band, f0, mom0rang, sigma in moles_info:
    # Load the Cube
    cube = SpectralCube.read(f'{dataPath}/cube_Band{band}_{molename}_smooth{bsize}as.fits')
    print(f'cube_Band{band}_{molename}_smooth{bsize}as.fits was loaded.')

    # Extract Spefic Freq Range
    slab = cube[mom0rang[0]:mom0rang[1], :, :]

    # Unit Convert: Hz ---> km/s
    slab = slab.with_spectral_unit(u.km/u.s, velocity_convention='radio', rest_value=f0*u.GHz)

    # Making Moment Zero Maps  & Plot 
    for n in Nsigma:
        # Noise Masking
        cutoffMask = slab > (n*sigma) * (u.K) 
        slab_masked = slab.with_mask(cutoffMask)
        # Integrating
        mom0 = slab_masked.moment(order=0)
        # Save as FITS
        mom0.write(f'{mom0Path}/mom0_{molename}_smooth{bsize}as_{n}sigma.fits', overwrite=True)
        print(f"{molename}'s moment zero map (masked {n} sigma) was saved as FITS.")
#'''

# ------------------------- Show Spectral Figures -------------------------- #
fig, ax2 = plt.subplots(3, 2, figsize=(12, 8)) # facecolor='#eeeeee'
ax = ax2.flatten()

for fig_idx, (molename, band, f0, mom0rang, _) in enumerate(moles_info):
    f0 = f0 * u.GHz
    # Load the Cube and Turn it into Velocity Unit
    cube_velo = SpectralCube.read(
        f'{dataPath}/cube_Band{band}_{molename}_smooth{bsize}as.fits'
        ).with_spectral_unit(
        u.km/u.s, velocity_convention='radio', rest_value=f0) # spectral axis is now in velo-unit
    
    # Get Axes Info
    samplePix = int(cube_velo.header['CRPIX1'])
    subcube_velo = cube_velo[:, samplePix, samplePix] # for intensity
    spaxis_velo = subcube_velo.spectral_axis

    # Plot the Spectrum
    ax[fig_idx].plot(spaxis_velo, subcube_velo , lw=1, color='k')
    ax[fig_idx].axhline(0, lw=0.5, linestyle='--', color='k')
    ax[fig_idx].set_title(f'{molename} spectrum pix({samplePix}, {samplePix})')
    if fig_idx > 3:
        ax[fig_idx].set_xlabel(f'Radio Velocity ({spaxis_velo.unit})')
    if (fig_idx % 2) == 0:
        ax[fig_idx].set_ylabel(f'Flux Density ({subcube_velo.unit})')

    # Mark the Spectral Line (shifted, in velo-unit) 
    moleline = f0 / (1+z) # shifted freq.
    moleline_velo = moleline.to(spaxis_velo.unit, 
                                equivalencies=u.doppler_radio(f0)).value
    ax[fig_idx].axvline(moleline_velo, lw=0.7, color='r')
    ax[fig_idx].text(moleline_velo, min(subcube_velo.value), f'{molename}',
                     rotation=90, color='r', fontsize=8, ha='right', va='bottom')

    # Mark the Intergral Range (in velo-unit)
    for chann in mom0rang:
        rangline_velo = cube_velo.spectral_axis[chann].value
        ax[fig_idx].axvline(rangline_velo, lw=0.5, color='b')
        ax[fig_idx].text(rangline_velo, max(subcube_velo.value)*0.5, 
                         f'{rangline_velo:.2f} {spaxis_velo.unit}', color='b',
                         rotation=90, fontsize=8, ha='right', va='bottom')

plt.tight_layout()
plt.savefig(f'{projectRoot}/products/figure/fig_mom0-integralRange-{bsize}as.png', dpi=300)
plt.show()