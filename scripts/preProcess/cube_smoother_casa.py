# Mainly from github: Hello_Circinus/miniscripts
# A script for full CASA
'''
又來到的熟悉的 convole to the same beam 
'''
#from casatasks import importfits, imsmooth, exportfits
import shutil

# File and path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # for feifei
#projectRoot = '/home/aqing/Documents/line-modeling_Circinus' # for Lab Machine
dataPath = f'{projectRoot}/data/alma_cube'

# Parameters
kernel = 'gauss'
targetBeam = {'major': '3.2arcsec', 'minor': '3.2arcsec', 'pa': '0deg'} # 大一點點
wanted = [  # (mole, band, restFrequency(Hz))
    ('13co-10', '3a'), ('c18o-10', '3a'), ('co-10', '3b'),
    ('13co-21', '6a'), ('c18o-21', '6a'), ('co-21', '6a'),
]

# Smoothing
for mole, band in wanted:
    pathIN = f'{dataPath}/cropped_cube/cube_Band{band}_{mole}_cropped.fits'
    pathOUT = f'{dataPath}/smoothed_cube/cube_Band{band}_{mole}_smoothTO13co-10.fits'

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
