# Run this script on feifei, due to the file structure.
# Works on mom0 and error maps.
'''
Reproject mom0 maps and error maps for the next step fitting.

Tech ref:
- reproject-Regular celestial images and cubes: 
    https://reproject.readthedocs.io/en/stable/celestial.html
- reproject_adaptive:
    https://reproject.readthedocs.io/en/stable/api/reproject.reproject_adaptive.html#reproject.reproject_adaptive

update: 2026-07-07, Seperate steps from convert2KReproj.py to 1. unit convetsion (cube_convert2K.py)
                                                              2. map_regrid.py   (this script)
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
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
mom0Path = f'{projectRoot}/data/mom0_map'
emapPath = f'{projectRoot}/data/error_map'
regridPath = f'{projectRoot}/data/regrid_map' # put everything togetherrr

# --------------------------- Constants & Variables ------------------------------- #
count = 1 # for counting...
maps_fn = []
maps_info = {}

# -------------------------- Load Maps andGet Maps' Files **Name** ----------------------------- #
'''
Due to emaps and mom0 are in different folder,
this step should be like this...
And I also need the original filename to name new files. (after regrid)
'''
for i in glob.glob(f'{mom0Path}/mom0_*.fits'): # get mom0_map filename
    fn = i[len(mom0Path)+1 : -5] # Path(i).stem also works :)
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

# ---------------------------- Reproject to Template ------------------------------ #
# Make Reprojt Template
template_header = fits.open(f'{mom0Path}/mom0_co-21_smooth3.2as_3.0sigma.fits')[0].header # use CO(2-1) as template
template_wcs2 = WCS(template_header).celestial # Make Sure Only RA/Dec, so wcs**2**

"""
# Show CDELT (header keyword, n arcsec per pixel)
print('Before reprojecting: ')
print('I known TMI but i dont car ;))')
for i in maps_info.keys():
    cdelt = abs(maps_info[i]["header"]['CDELT1'] * 3600)
    print(f"{i}: {cdelt:.3f} arcsec/pixel")
print()
"""

# Reproject to CO(2-1)
for fn in maps_info.keys():
    # Prepare Meterial
    the_map = maps_info[fn]["data"]
    the_wcs2 = WCS(maps_info[fn]["header"]).celestial

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

print('Done.')