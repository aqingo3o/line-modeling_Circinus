# You should put this script on feifei,
# because of the hard-coded folder path
# use matplotlib<3.8 (3.7.5 here) to avoid "ImportError: cannot import name 'AnchoredEllipse' from 'mpl_toolkits.axes_grid1.anchored_artists'"
'''
Make the error map of datacubes, which had been cropped by CASA ({projectRoot}/data/alma_cube/cropped_cube)
Ever ring of **dr** have different noise level.
Error map is for modeling.
'''

from astropy.io import fits
from astropy import units as u
import matplotlib.pyplot as plt
import numpy as np
from spectral_cube import SpectralCube
import warnings

warnings.filterwarnings('ignore', message='.*PV2.*')
warnings.filterwarnings('ignore', message='Degrees of freedom <= 0 for slice')

# Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus'
dataPath = f'{projectRoot}/data/alma_cube/smoothed_cube'
emapPath = f'{projectRoot}/data/errormap'

# (mole_fileName, band_fileName, (blankChannel))
moles_info = [('co-10',   '3b', (113, 320, 727, 906)),
              ('13co-10', '3a', (56, 316, 721, 900)),
              ('c18o-10', '3a', (182, 475, 893, 1094)),
              ('co-21',   '6a', (86, 327, 1036, 1323)),
              ('13co-21', '6a', (41, 257, 1012, 1544)),
              ('c18o-21', '6a', (65, 275, 1043, 1200)),
              ]
cube_info = {} 

dr = 0.2 * u.arcsec
for molename, band, _ in moles_info:
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
        "cube":  cube,
        "wcs2":   cube.wcs.celestial,
        "rmask": ringMaskList_mole,
        "emap":  np.full_like(dist_mat.value, np.nan),
    }

# ----------- Measure an d Filling Noise (std.) in Each Ring-Shaped Mask ------------ #
for molename, _, cblank in moles_info:
    # Measuring Noise
    for ringMask in cube_info[molename]['rmask']:
        cube_masked = cube_info[molename]['cube'].with_mask(ringMask)
        noise = 0 * (u.Jy/u.beam) # 歸零, 放個單位
        for c in cblank:
            noise += (np.nanstd(cube_masked[c].filled_data[:])) / (len(cblank))
    # Filling Noise
        cube_info[molename]['emap'][ringMask] = noise.value

    print(f"{molename}'s error map was done :)")
    # Go to Next Molecule :)

# --------------------------------- Save as FITS -------------------------------- #
for molename, _, _  in moles_info:
    fitsOut = f'{emapPath}/emap_{molename}_smooth3.2as.fits'
    errorMap = cube_info[molename]['emap']
    # Write Header
    header = cube_info[molename]['wcs2'].to_header()
    header['OBJECT'] = 'Circinus_galaxy'
    header['BUNIT'] = 'Jy/beam'
    header['COMMENT'] = 'Radial ring-shaped noise map, by aqing via SpectralCube, numpy'
    fits.writeto(fitsOut, errorMap, header, overwrite=True)
print('All error maps are saved as FITS.')

# ------------------------------- Plot Error Maps ------------------------------- #
fig = plt.figure(figsize=(15, 11))
fig_pos = 231
for molename, _, _ in moles_info:
    errorMap = cube_info[molename]['emap']
    plt.subplot(fig_pos, projection=cube_info[molename]['wcs2'])
    plt.imshow(errorMap, origin='lower', cmap='gray', vmin=0, vmax=np.nanmax(errorMap))
    plt.xlabel('RA')
    plt.ylabel('Dec')
    plt.title(f"{molename}'s error map")
    plt.colorbar(label='Noise (Jy/beam)', fraction=0.046, pad=0.04)
    fig_pos += 1 # 超噁爛超危險寫法但我有點懶得改了啦哈哈屁眼

plt.tight_layout()
plt.show()
