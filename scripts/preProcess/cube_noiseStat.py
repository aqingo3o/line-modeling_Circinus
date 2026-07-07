# Script for feifei (hard-coded path)
'''
How much Jy/beam of noise should be masked when generating mom0.

update: 2026-06-28, Inspire by new error maps' procedure.
'''

from astropy import units as u
import numpy as np
from regions import Regions
from spectral_cube import SpectralCube
import time
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')
warnings.filterwarnings('ignore', message='.*Stokes cube.*')

# ------------------------------- Path ------------------------------- #
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus'
cubePath = f'{projectRoot}/data/alma_cube/smoothed_cube'

# (molename, band_fileName, line-free(channel range pair))
moles_info = [('co-10',   '3b', (10, 975, 1420, 2375)),
              ('13co-10', '3a', (10, 535, 920, 1830)),
              ('co-21',   '6a', (10, 1100, 1866, 2310)),
              ('13co-21', '6a', (10, 619, 1465, 2980)),
              ('c18o-21', '6a', (127, 1426, 2283, 2386)),
              ('co-32',   '7',  (10, 92, 240, 340)), # Izumi
              ]

# ------------------------------- Main ------------------------------- #
reg_co32fov = Regions.read(f'{projectRoot}/data/region/co32-fov.crtf', format='crtf')
reg_co32nopb = Regions.read(f'{projectRoot}/data/region/co32-nopb.crtf', format='crtf')
moles_sigma = {}

for molename, band, lf_rang in moles_info: # lf for line-free
    print(f'---------- [{molename}] ----------')

    # Load and crop the cubes (spatial)
    cube = SpectralCube.read(f'{cubePath}/cube_Band{band}_{molename}_smooth3.2as.fits')
    subcube_co32fov = cube.subcube_from_regions(reg_co32fov)
    subcube_co32nopb = cube.subcube_from_regions(reg_co32nopb)
    print('Two spatial sub-cubes are ready.')

    # Line-free channels of sub-cubes
    print('Please wait for array concatenation...', end='')
    timei = time.time()
    linefree_co32fov = np.concatenate([subcube_co32fov[lf_rang[0]:lf_rang[1], :, :],
                                       subcube_co32fov[lf_rang[2]:lf_rang[3], :, :]],
                                       axis=0)
    linefree_co32nopb = np.concatenate([subcube_co32nopb[lf_rang[0]:lf_rang[1], :, :],
                                        subcube_co32nopb[lf_rang[2]:lf_rang[3], :, :]],
                                        axis=0)
    timef = time.time()
    print(f' ({(timef - timei):.1f} sec)')

    # sigma for mom0 making...
    sigma_co32fov = np.nanstd(linefree_co32fov, axis=None) # None: std. for flatten array
    sigma_co32nopb = np.nanstd(linefree_co32nopb, axis=None)

    print('Result of mom0 map cutoff base: (one sigma, just for preview)')
    print(f'{sigma_co32fov:.2f} Jy/beam (co32-fov)')
    print(f'{sigma_co32nopb:.2f} Jy/beam (co32-nopb)')
    moles_sigma[molename] = {
        "sigma_co32fov" : sigma_co32fov,
        "sigma_co32nopb" : sigma_co32nopb
    }
print()
print('Finish statistics of cutoff base for mom0 maps, please check the result in projectRoot/docs :)')
    
# --------------------------- Write Result to .txt --------------------------- #
sigmarec = open(f'{projectRoot}/docs/mom0_sigma_cutoff_base.txt', 'w')
sigmarec.write('format: (molename, sigma_co32fov, sigma_co32nopb)\n')
sigmarec.write(f'and the unit of sigma is {cube.unit}\n\n') # 殘留的 cube, 單位應該大家一樣

for molename in moles_sigma.keys():
    sigma_co32fov = moles_sigma[molename]["sigma_co32fov"]
    sigma_co32nopb = moles_sigma[molename]["sigma_co32nopb"]
    sigmarec.write(f'{molename:<8}: ({sigma_co32fov:.6f}, {sigma_co32nopb:.6f})\n')
sigmarec.close()
