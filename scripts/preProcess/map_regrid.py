# Script for both server (blackhole) and feifei.
'''
This is the last step before fitting.
Reproject mom0 maps and error maps with Nyquist sampling.
That is, pixel size = 0.5 * beam size.
- pixel size (deg): CDELT1, CDELT2
- beam  size (deg): BMAJ (convolve to the same beam first!)

Tech ref:
- reproject-Regular celestial images and cubes: 
    https://reproject.readthedocs.io/en/stable/celestial.html
- reproject_adaptive:
    https://reproject.readthedocs.io/en/stable/api/reproject.reproject_adaptive.html#reproject.reproject_adaptive

update: 2026-07-07, Seperate steps from convert2KReproj.py
                    to 1. unit convetsion (cube_convert2K.py)
                       2. map_regrid.py   (this script)
        2026-07-27, Use Nyquist sampling instead of CO(2-1) as regrid template.
                    Aim to speed up the fitting caculation.
'''

# --------------------------------- Import Module -------------------------------- #
from astropy.io import fits
from astropy.wcs import WCS
import glob
import numpy as np
from reproject import reproject_adaptive
import warnings

# ---------------------------- 因為噴一堆東西有點煩煩的 ------------------------------- #
warnings.filterwarnings('ignore', message='.*PV2.*')
warnings.filterwarnings('ignore', message='.*made the change.*')

# ------------------------------- Path Variables ---------------------------------- #
projectRoot = '/home/aqing/Documents/line-modeling_Circinus' # blackhole
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # fei
mom0Path = f'{projectRoot}/data/mom0_map'
emapPath = f'{projectRoot}/data/error_map'
regridPath = f'{projectRoot}/data/regrid_map_nyq' # put everything togetherrr

# --------------------------- Constants & Variables ------------------------------- #
count = 1 # for counting...
maps_fn = []
maps_info = {}
cbeam = 3.2 / 3600 # common beam, unit: deg

# -------------------- Load Maps andGet Maps' Files **Name** ---------------------- #
'''
Due to emaps and mom0 are in different folder 
and i still need filename to name files after regrid...
That is why this step looks the way it does ;)
'''
for i in glob.glob(f'{mom0Path}/mom0_*.fits'): # get mom0_map filename
    fn = i[len(mom0Path)+1 : -5] # Path(i).stem also works, but need extra module.
    hdul = fits.open(f'{mom0Path}/{fn}.fits')
    maps_info[fn] = {            # super LONG index but i dont car
        "filename" : fn,
        "data" : hdul[0].data.squeeze(),
        "header" : hdul[0].header,
    }
    hdul.close()
    maps_fn.append(fn)

for i in glob.glob(f'{emapPath}/emap_*.fits'): # get error_map filename
    fn = i[len(emapPath)+1 : -5]
    hdul = fits.open(f'{emapPath}/{fn}.fits')
    maps_info[fn] = {
        "data" : hdul[0].data.squeeze(),
        "header" : hdul[0].header,
    }
    hdul.close()
    maps_fn.append(fn)

# ---------------------------- Make Regrid Template ------------------------------ #
'''
Use CO(3-2) as template's base because CO(3-2) has the smallest fov of 6 lines.
Get sky coordinate range from it and set pixel size by Nyquist sampling.

Spatial regrid template can be "wcs2" object,
that is: WCS(a_header).celestial, a kind of WCS obj. 
(some time wcs2 == WCS)

(print(WCS(co32_header).celestial) to gain some concept :P)
--------------- [Inside wcs2] ---------------
Number of WCS axes: 2
CTYPE : 'RA---SIN' 'DEC--SIN'
CRVAL : 213.2914583333 -65.33916666667
CRPIX : 433.0 433.0 
PC1_1 PC1_2  : 1.0 0.0
PC2_1 PC2_2  : 0.0 1.0
CDELT : -9.166666666667e-06 9.166666666667e-06
NAXIS : 864  864

Aside from CDELT1&2 (pixel size in degree),
NAXIS1&2 (how may pixels along two spatial axes) and
CRPIX1&2 (the centeral pixel) should also be revised!
Because these will be different b/a I change the pixel scale.
'''
co32_header = fits.open(f'{mom0Path}/mom0_co-32_smooth3.2as_3.0sigma.fits')[0].header

# Change Pixel Size (pixel scale) by Nyquist Sampling
template_header = co32_header.copy()
target_pixsize = 0.1 * cbeam #### 89*89
template_header['CDELT1'] = -target_pixsize  # RA, 向東為負, 真的相信我把 WCS(co32_header)先印出來會比較輕鬆
template_header['CDELT2'] = target_pixsize   # DEC

# Revise other WCS keywords
scale1 = abs(co32_header['CDELT1'] / target_pixsize)
scale2 = abs(co32_header['CDELT2'] / target_pixsize) # may data is not square?

template_header['NAXIS1'] = int(co32_header['NAXIS1'] * scale1)
template_header['NAXIS2'] = int(co32_header['NAXIS2'] * scale2)
template_header['CRPIX1'] = (co32_header['CRPIX1'] - 1) * scale1
template_header['CRPIX2'] = (co32_header['CRPIX2'] - 1) * scale2
print(f"New data_shape is: {(template_header['NAXIS1'], template_header['NAXIS2'])}")

# Get Regrid WCS template
template_wcs2 = WCS(template_header).celestial

# ---------------------------------- Regrid! ------------------------------------ #
#'''
for fn in maps_info.keys():
    # Prepare Meterial
    the_map = maps_info[fn]["data"]
    the_wcs2 = WCS(maps_info[fn]["header"]).celestial
    """
    print('Pixel size before regrid:', end='')
    print(f'{(abs(maps_info[fn]["header"]["cdelt1"] * 3600)):.2f} arcsec')
    """

    # Upsampling (Reprojecting) ...
    data_regrid, _ = reproject_adaptive((the_map, the_wcs2), template_wcs2)

    # Revise Header (WCS, by reproject)
    header_regrid = maps_info[fn]["header"].copy()
    header_regrid.update(template_wcs2.to_header())

    # Save as .npy
    np.save(f'{regridPath}/{fn}_regrid.npy', data_regrid) # Actually only mom0 need .npy files

    # Save as FITS
    fitsOut = f'{regridPath}/{fn}_regrid.fits'
    fits.writeto(fitsOut, data_regrid, header_regrid, overwrite=True)

    print(f'Finish regriding and save the product. ({count}/{len(maps_fn)})')
    count += 1
#'''
print('Done.')