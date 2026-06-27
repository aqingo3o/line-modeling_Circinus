'''
convole to the same beam, by full CASA
Make sure {projectRoot}/data/alma_cube/smooth_cube/ is exsist

!! If 'casa killed', it must because RAM is explore.
Use this command to fix: (in terminal)
>> export OMP_NUM_THREADS=4
Ofcourse running time would become double :(

!! Please check spectral axis by CARTA (or something like that) after smoothing.
(有前科的) 可能會有譜線強度在某個 channel 之後全部歸零的情況, 個人猜測很高機率是硬體的鍋

!! Server(blackhole) can operate even larger cubes (9 GB) <333
'''
#from casatasks import importfits, imsmooth, exportfits
import shutil

# File and path
projectRoot = '/home/aqing/Documents/line-modeling_Circinus' # for Lab Machine, server(blackhole)
dataPath = f'{projectRoot}/data/alma_cube'

# Parameters
kernel = 'gauss'
beamSize = 3.2 # arcsec
targetBeam = {'major': f'{beamSize}arcsec', 'minor': f'{beamSize}arcsec', 'pa': '0deg'} # set as round beam
wanted = [  # (mole, band, restFrequency(Hz)
    ('co-10', '3b'), ('co-21', '6a'), ('co-32', '7'),
    ('13co-10', '3a'), ('13co-21', '6a'),
    ('c18o-21', '6a'),
]

# Smoothing
for mole, band in wanted:
    pathIN = f'{dataPath}/cropped_cube/cube_Band{band}_{mole}_cropped.fits'
    pathOUT = f'{dataPath}/smoothed_cube/cube_Band{band}_{mole}_smooth{beamSize}as.fits'

    importfits(fitsimage=pathIN, imagename='casaIN.im', overwrite=True)
    print('Successfully import a datacube.')

    imsmooth(imagename='casaIN.im', outfile='casaSMOOTH.im',
             kernel=kernel, beam=targetBeam, targetres=True, overwrite=True)
    print('Finish smooth.')

    exportfits(imagename='casaSMOOTH.im', fitsimage=pathOUT, overwrite=True)
    shutil.rmtree('casaIN.im')
    shutil.rmtree('casaSMOOTH.im')
    print(f'{mole} was smoothed and metafiles are cleaned.')

print('All Done :)')