# You should put this script on feifei,
# because of the hard-coded folder path
# use matplotlib<3.8 (3.7.5 here) to avoid 
# "ImportError: cannot import name 'AnchoredEllipse' from 'mpl_toolkits.axes_grid1.anchored_artists'"
'''
Make the error map of datacubes, which had been cropped by CASA ({projectRoot}/data/alma_cube/cropped_cube)
Ever ring of **dr** have different noise level.
Error map is for modeling.

* Here are updates that "cube_errorMap_fullComment.py" doesn't have! *
'''

from astropy import constants as const
from astropy import units as u
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from spectral_cube import SpectralCube
import warnings

warnings.filterwarnings('ignore', message='.*PV2.*')
warnings.filterwarnings('ignore', message='Degrees of freedom <= 0 for slice')

# Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus'
dataPath = f'{projectRoot}/data/alma_cube/smoothed_cube'
emapPath = f'{projectRoot}/data/error_map'

# (mole_fileName, band_fileName, blank_channel(#), integral_range(GHz))
moles_info = [('co-10',   '3b', (15, 86, 445, 483),    (115.041660, 115.172025)),
              ('13co-10', '3a', (56, 316, 721, 900),   (109.974831, 110.108133)),
              ('c18o-10', '3a', (182, 475, 893, 1094), (109.561252, 109.665745)),
              ('co-21',   '6a', (86, 327, 1036, 1323), (230.053556, 230.360676)),
              ('13co-21', '6a', (41, 257, 1012, 1544), (219.936696, 220.215985)),
              ('c18o-21', '6a', (65, 275, 1043, 1200), (219.126176, 219.364939)),
              ]
cube_info = {} 
header_ref_kw = ['BMAJ', 'BMIN', 'BPA', 'RESTFRQ']

dr = 0.2 * u.arcsec
for molename, band, _, _ in moles_info:
    # --------------------------- Get Info from Cube --------------------------- #
    # Load the Cube
    cube = SpectralCube.read(f'{dataPath}/cube_Band{band}_{molename}_smooth3.2as.fits')
    print(f'cube_Band{band}_{molename}_smooth3.2as.fits was loaded.')
    
    # Find the **Center** of the Observation
    ra_crval  = cube.wcs.wcs.crval[0] * u.deg
    dec_crval = cube.wcs.wcs.crval[1] * u.deg
    dec_cr_rad = dec_crval.to(u.rad) # 用來修正投影用的所以單位是 rad

    # Length-related and Distance Matrix
    dec_mat, ra_mat = cube.spatial_coordinate_map
    delta_dec = (dec_mat - dec_crval)
    delta_ra = (ra_mat - ra_crval) * np.cos(dec_cr_rad)
    dist_mat = np.sqrt(delta_ra**2 + delta_dec**2).to(u.arcsec) # 就是計算距離, 一次性算完

    rfov = (0.5 * (dec_mat.max()-dec_mat.min())).to(u.arcsec)

    # --------------------------- Make Ring-like Masks --------------------------- #
    # Initilize
    ringMaskList_mole = [] 
    radius_inner = 0 * u.arcsec 
    radius_outer = 0.2 * u.arcsec

    while radius_outer < rfov:
        ringMask = (dist_mat > radius_inner) & (dist_mat <= radius_outer)
        ringMaskList_mole.append(ringMask.copy())
        # Next Ring
        radius_inner = radius_outer.copy()
        radius_outer += dr

    # Save Cube Information and Ring Masks into dict.
    cube_info[molename] = {
        "cube":   cube,
        "wcs2":   cube.wcs.celestial,
        "header": cube.header,
        "cdelt3": (cube.header['CDELT3'] * u.Hz).to(u.GHz), # channel width
        "rmask": ringMaskList_mole,
        "emap":  np.full_like(dist_mat.value, np.nan),
    }

# ----------- Measure and Filling Noise (std.) in Each Ring-Shaped Mask ------------ #
for molename, _, cblank, mom0range in moles_info:
    cdelt3 = cube_info[molename]["cdelt3"] # GHz
    Nchann = (mom0range[1]-mom0range[0])*u.GHz / cdelt3

    # Measuring Noise
    for ringMask in cube_info[molename]['rmask']:
        cube_masked = cube_info[molename]['cube'].with_mask(ringMask)
        chann_noise = 0 * (u.Jy/u.beam) # 歸零, 放個單位
        noise = 0 * ((u.Jy/u.beam)*(u.km/u.s))
        for c in cblank:
            chann_noise = (np.nanstd(cube_masked[c].filled_data[:]))

            # Make the Unit Match with mom0 (chann_noise --> mom0_noise)
            ref_freq = (cube_info[molename]["cube"].spectral_axis[c]).to(u.GHz)
            velo_resolution = const.c.to(u.km/u.s) * cdelt3 / ref_freq

            noise += chann_noise * velo_resolution * np.sqrt(Nchann.value)
    # Filling Noise (the average of 4 blank channels' noise)
        cube_info[molename]['emap'][ringMask] = noise.value / (len(cblank))

    print(f"{molename}'s error map was done :)")
    # Go to Next Molecule :)

# --------------------------------- Save as FITS -------------------------------- #
for molename, _, _, _  in moles_info:
    fitsOut = f'{emapPath}/emap_{molename}_smooth3.2as.fits'
    errorMap = cube_info[molename]['emap']
    # Write Header
    header_ref = cube_info[molename]['header']
    header_emap = cube_info[molename]['header'].copy()
    for i in header_ref_kw:
        header_emap[i] = header_ref[i]
    header_emap['OBJECT'] = 'Circinus_galaxy'
    header_emap['BUNIT'] = 'Jy.km.beam-1.s-1' # match with mom0s' unit :)
    header_emap['COMMENT'] = 'Radial ring-shaped noise map, by aqing via SpectralCube, numpy'
    fits.writeto(fitsOut, errorMap, header_emap, overwrite=True)
print('All error maps are saved as FITS.')

# ------------------------------- Plot Error Maps ------------------------------- #
fig = plt.figure(figsize=(15, 11))
fig_pos = 231
for molename, _, _, _ in moles_info:
    errorMap = cube_info[molename]['emap']
    plt.subplot(fig_pos, projection=cube_info[molename]['wcs2'])
    plt.imshow(errorMap, origin='lower', cmap='gray', vmin=0, vmax=np.nanmax(errorMap))
    plt.xlabel('RA')
    plt.ylabel('Dec')
    plt.title(f"{molename}'s error map")
    plt.colorbar(label='Noise (Jy/beam * km/s)', fraction=0.046, pad=0.04)
    fig_pos += 1 # 超噁爛超危險寫法但我有點懶得改了啦哈哈屁眼

plt.tight_layout()
plt.savefig(f'{projectRoot}/products/figure/fig_errorMap.png', dpi=300)
plt.show()