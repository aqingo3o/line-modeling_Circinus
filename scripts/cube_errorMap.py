# Script for feifei (hard-coded path),
# use matplotlib<3.8 (3.7.5 here) to avoid
# "ImportError: cannot import name 'AnchoredEllipse' from 'mpl_toolkits.axes_grid1.anchored_artists'"
'''
Error estimation of each spectral line for modeling.
σ_mom0 = σ * Δv * sqrt(N_line)
Material: datacubes (smooth by CASA, under {projectRoot}/data/alma_cube/smooth_cube)

update: 2026-06-23, After Eltha's advice.
'''

from astropy import constants
from astropy import units as u
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from spectral_cube import SpectralCube
import time
import warnings

warnings.filterwarnings('ignore', message='.*PV2.*')
warnings.filterwarnings('ignore', message='.*Stokes cube.*')

# ------------------------------- Path ------------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus'
dataPath = f'{projectRoot}/data/alma_cube/smoothed_cube'
emapPath = f'{projectRoot}/data/error_map'

# (molename, band_fileName,
# line-free(channel range pair), integral_range(channel))
moles_info = [('co-10',   '3b', 
               (10, 975, 1420, 2375),   (1057, 1338)),
              ('13co-10', '3a', 
               (10, 535, 920, 1830),    (573, 844)),
              ('co-21',   '6a', 
               (10, 1100, 1866, 2310),  (1125, 1799)),
              ('13co-21', '6a',
               (10, 619, 1465, 2980),   (759, 1278)),
              ('c18o-21', '6a',
               (127, 1426, 2283, 2386), (1640, 2100)),
              ('co-32',   '7',
               (10, 92, 240, 340),      (100, 233)), # Izumi
              ]

# --------------------------- Get Info from Cube --------------------------- #
cube_info = {}
for molename, band, linefree_rang, _ in moles_info:
    # Load the cube
    cube = SpectralCube.read(f'{dataPath}/cube_Band{band}_{molename}_smooth3.2as.fits')
    print(f'cube_Band{band}_{molename}_cropped.fits was loaded.')

    # Line-free channels
    print('Please wait for array concatenation...', end='')
    ctimei = time.time()
    linefree_cube = np.concatenate([cube[linefree_rang[0]:linefree_rang[1], :, :],
                                   cube[linefree_rang[2]:linefree_rang[3], :, :]],
                                   axis=0) # it takes times...
    ctimef = time.time()
    print(f' ({(ctimef - ctimei):.1f} sec)')
    
    # Save cube information into dict.
    cube_info[molename] = {
        "cube":     cube,
        "wcs2":     cube.wcs.celestial,
        "header":   cube.header,
        "cdelt3":   (abs(cube.header['CDELT3']) * u.Hz).to(u.GHz), # channel width (GHz)
        "restfreq": (cube.header['RESTFRQ']* u.Hz).to(u.GHz),      # rest frequency (GHz)
        "linefree": linefree_cube,
    }

# ------------------------------- sigma_mom0 ------------------------------- #
print()
print('Start estimating error...')
for molename, band, _, mom0_rang in moles_info:
    # rms through the line free channels (σ, unit: Jy/beam)
    linefree_cube = cube_info[molename]["linefree"]
    sigma_rms = np.nanstd(linefree_cube, axis=0) # Jy/beam

    # How much channels does mom0 integraled, dim-less
    N_mom0 = mom0_rang[1] - mom0_rang[0] + 1

    # Velocity resolution (Δv, unit: km/s)
    cdelt3 = cube_info[molename]["cdelt3"] # GHz
    f0 = cube_info[molename]["restfreq"]   # GHz
    velo_resolution = constants.c.to(u.km/u.s) * cdelt3 / f0 # Not relativistic radio Doppler

    # σ_mom0 = σ * Δv * sqrt(N_line)
    sigma_mom0 = sigma_rms * velo_resolution * np.sqrt(N_mom0)

    # Put result into dict.
    cube_info[molename]['emap'] = sigma_mom0

# ---------------------------- Save Error Maps as FITS --------------------------- #
header_ref_kw = ['BMAJ', 'BMIN', 'BPA', 'RESTFRQ']
'''
Require beam information for unit convertion. (Jy/beam*km/s --> K*km/s)
'''
for molename, _, _, _  in moles_info:
    #fitsOut = f'{emapPath}/emap_{molename}_smooth3.2as.fits'
    fitsOut = f'{emapPath}/emap_{molename}.fits'
    errorMap = cube_info[molename]["emap"].value # unit: Jy/beam*km/s, but no unit in FITS

    # Revise Header
    header_ref = cube_info[molename]['header']
    header_emap = cube_info[molename]['header'].copy()
    for i in header_ref_kw:
        header_emap[i] = header_ref[i]
    header_emap['OBJECT'] = 'Circinus_galaxy'
    header_emap['BUNIT'] = 'Jy.km.beam-1.s-1' # match with mom0s' unit :)
    header_emap['COMMENT'] = 'std. in line-free channels, by qing via SpectralCube, np.nanstd'

    # write to FITS
    fits.writeto(fitsOut, errorMap, header_emap, overwrite=True)
print('All error maps are saved as FITS :D')

# ------------------------------- Plot Error Maps ------------------------------- #
fig = plt.figure(figsize=(15, 11))
fig_pos = 231
for molename, _, _, _ in moles_info:
    errorMap = cube_info[molename]['emap'].value
    plt.subplot(fig_pos, projection=cube_info[molename]['wcs2'])
    plt.imshow(errorMap, origin='lower', cmap='gray',
               vmin=0, vmax=np.nanmax(errorMap)*0.65)
    plt.xlabel('RA')
    plt.ylabel('Dec')
    plt.title(f"{molename}'s error map")
    plt.colorbar(label='Noise (Jy/beam * km/s)', fraction=0.046, pad=0.04)
    fig_pos += 1 # 超噁爛超危險寫法但我有點懶得改了啦哈哈屁眼

plt.tight_layout()
plt.savefig(f'{projectRoot}/products/figure/fig_errorMap.png', dpi=300)
plt.show()