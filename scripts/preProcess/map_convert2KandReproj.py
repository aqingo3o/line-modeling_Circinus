# Run this script on feifei, due to the file structure.
# Works on mom0 and error maps.
'''
Convert the flux density unit of mom0 and error maps from Jy/beam to Kelvin, 
2 = to ;)
And reproject maps to CO(2-1)'s grid, for the next step fitting.

from mom0_convert2K_fulComment.py, 但已將 converting 的迴圈改成了矩陣相乘
因為加上 reproject 的動作所以新開一個檔,
並且這會取代 scripts/mom0_convert2K.py as scripts/map_convert2KandReproj.py

Tech ref:
- astropy.Units, Brightness Temperature and Surface Brightness Equivalency: 
    https://docs.astropy.org/en/stable/units/equivalencies.html#built-in-equivalencies
- the equivakency -- brightness_temperature():
    https://docs.astropy.org/en/stable/api/astropy.units.brightness_temperature.html#astropy.units.brightness_temperature
- <Tools>: 
    並無, 因爲老子根他媽本看不懂
- reproject-Regular celestial images and cubes: 
    https://reproject.readthedocs.io/en/stable/celestial.html
- reproject_adaptive:
    https://reproject.readthedocs.io/en/stable/api/reproject.reproject_adaptive.html#reproject.reproject_adaptive
'''

# --------------------------------- Import Module -------------------------------- #
from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS
import glob
import numpy as np
from reproject import reproject_adaptive
import warnings

# ---------------------------- 因為噴一堆東西有點煩煩的 ------------------------------- #
warnings.filterwarnings('ignore', message='.*PV2.*')
warnings.filterwarnings('ignore', message='*FITSFixedWarning:*')

# ------------------------------- Path Variables ---------------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
mom0Path = f'{projectRoot}/data/mom0_map'
emapPath = f'{projectRoot}/data/error_map'
mom0npyPath = f'{projectRoot}/data/mom0_npy'

# --------------------------- Constants & Variables ------------------------------- #
smoothTO = 3.2
fwhm2sigma = 1. / (8 * np.log(2))**0.5 # Gaussian beam 的常數
z = 0.001448 * u.dimensionless_unscaled # red shift of the Circinus
count = 1 # for counting...
maps_info = {}

# -------------------------- Read Mom0 Files **Name** ----------------------------- #
mom0_fn = [] # fn for fileName
for i in glob.glob(f'{mom0Path}/mom0_*.fits'):
    mom0_fn.append(i[len(mom0Path)+1:])
mom0_fn.sort() # 整理一下, 下個檢查點會比較方便

files_info = [] # split filename into elements
for i in mom0_fn:
    sub_fns = i.split('_')
    if 'unitK' in sub_fns:
        mom0_fn.remove(i) # fuck it doesn't work
    files_info.append((sub_fns[0], sub_fns[1], sub_fns[3][:3]))

# ------------------ Add Emaps' Files **Name** into files_info --------------------- #
emap_fn = [] # fn for fileName
for i in glob.glob(f'{emapPath}/emap_*.fits'):
    emap_fn.append(i[len(emapPath)+1:])
emap_fn.sort()

for i in emap_fn:
    sub_fns = i.split('_')
    files_info.append((sub_fns[0], sub_fns[1], 0.0)) # emap don't have nsig

# ---------------- 1. Convert the Intensity Unit (Jy/beam -> K) -------------------- #
for maptype, molename, nsig in files_info:
    if maptype == 'emap':
        # Get Data from Error Map
        hdu = fits.open(f'{emapPath}/emap_{molename}_smooth{smoothTO}as.fits')[0] # astropy.io
    elif maptype == 'mom0': 
        # Get Data from mom0s
        hdu = fits.open(f'{mom0Path}/mom0_{molename}_smooth{smoothTO}as_{nsig}sigma.fits')[0] # astropy.io

    map_Jb = hdu.data.squeeze() # Jy/beam 簡稱他嗎雞ㄅ, 這個是可以 imshow() 的那個部分, ssp 時期好像叫他 ima
    map_K = np.full_like(map_Jb, np.nan)

    header = hdu.header
    f0 = header['RESTFRQ'] * u.Hz
    freq = f0 / (1+z) # shifted frequency
    bmaj, bmin = header['BMAJ'] * u.deg, header['BMAJ'] * u.deg # fwhm 的部分
    OmegaB = (2 * np.pi) * (bmaj * fwhm2sigma) * (bmin * fwhm2sigma)
    
    # Unit Convertion
    cvFactor = (1 * u.Jy/OmegaB).to(u.K, equivalencies=u.brightness_temperature(freq)).value
    print(f"Converting intensity unit of {molename}'s mom0... ({count}/{len(files_info)})")
    map_K = map_Jb * cvFactor # matrix <3
    count += 1

    # Revise Header (Intensity Unit)
    hdu.header['OBJECT'] = 'Circinus Galaxy'
    hdu.header['COMMENT'] = 'Convert the intensity unit from surface brightness to brightness temperature, by qing'

    # Save into maps_info
    if maptype == 'emap':
        hdu.header['BUNIT'] = 'Kelvin'
        maps_info[f'{maptype}_{molename}'] = {
            "header_K" : hdu.header,
            "unitK": map_K,
            }
    elif maptype == 'mom0':
        hdu.header['BUNIT'] = 'K km s-1'
        maps_info[f'{maptype}_{molename}_{nsig}'] = {
            "header_K" : hdu.header,
            "unitK": map_K,
            }

count = 1 # recycle:))    

# ---------------------------- 2. Reproject to CO(2-1) ------------------------------ #
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
"""
    
# Reproject to CO(2-1)
for i in maps_info.keys():
    # Prepare Meterial
    the_map = maps_info[i]["unitK"]
    the_wcs2 = WCS(maps_info[i]["header_K"]).celestial

    # Upsampling (Reprojecting) ...
    upsample, _ = reproject_adaptive((the_map, the_wcs2), template_wcs2)

    # Revise Header (WCS, by reproject)
    the_header = maps_info[i]["header_K"].copy()
    the_header.update(template_wcs2.to_header())

    # Save Up-Sampled Info (data + WCS(header)) into maps_info
    maps_info[i]["upsample"] = upsample # upsample is numpy.ndarray object
    maps_info[i]["header_reproj"] = the_header


# ------------------------ 3. Save FINAL DATA as FITS ------------------------------ #
for i in maps_info.keys():
    # Get the File Name Keyword...
    key = i.split('_')
    molename = key[1]

    # Load 內餡
    reproj_map = maps_info[i]["upsample"]
    reproj_header = maps_info[i]["header_reproj"]

    # Decide the Output File Name
    if key[0] == 'emap':
        maptype = 'error map'
        fitsOut = f'{emapPath}/emap_unitK_reproj_{molename}_smooth{smoothTO}as.fits'
    elif key[0] == 'mom0':
        maptype = 'moment0 map'
        nsig = key[2]
        fitsOut = f'{mom0Path}/mom0_unitK_reproj_{molename}_smooth{smoothTO}as_{nsig}sigma.fits'
        np.save(f'{mom0npyPath}/mom0_unitK_reproj_{molename}_smooth{smoothTO}as_{nsig}sigma.npy',
                 reproj_map) # Only mom0 Need .npy Files
    
    # Saveee
    fits.writeto(fitsOut, reproj_map, reproj_header, overwrite=True) # 依序填入: 檔名、內餡(圖的部分)、標頭
    print(f"Saved {key[1]}'s reprojected {maptype} as FITS in unit of brightness temperature. ({count}/{len(files_info)})")
    count += 1

print('Done.')