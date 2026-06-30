# A script for full CASA
'''
Cut datacubes into smaller pieces and revise the header keyword 'RESTFRQ' by casatools (.setrestfrequency())
Leave at least 1x width as the spectral line in both sides for error estimation.

update: 2026-06-30, Use casatools to modify header key ['restfreq']
                    and increase the recognition of status hints.
'''
import glob
import shutil

# Files and Path
projectRoot = '/home/aqing/Documents/line-modeling_Circinus' # for Lab Machine or blackhole
dataPath = f'{projectRoot}/data/alma_cube'
cubes = glob.glob(f'{dataPath}/ori_cube/cube_*.fits')
cubes.sort() # make sure the order is the same in every computer!

# (molename, band, sub-image's channel(casaForm, check from CARTA), restFrequency(Hz))
wanted = [
    #('c18o-10', '3a', '0~1', 1.09782E+11), # c18o-10 is not used in modeling
    ('13co-10', '3a', '10~1870',   1.10201E+11),
    ('co-10',   '3b', '1035~3440', 1.15271E+11),
    ('c18o-21', '6a', '1000~3810', 2.19560E+11),
    ('13co-21', '6a', '20~3070',   2.20399E+11),
    ('co-21',   '6a', '1510~3830', 2.30538E+11),
    ('co-32',   '7',  '70~415',    3.45796E+11),
]

# Main
for i in range(len(cubes)):
    pathIN = cubes[i]
    mole = wanted[i][0]
    band = wanted[i][1]
    spchanns = wanted[i][2]
    f0 = wanted[i][3]
    pathOUT = f'{dataPath}/cropped_cube/cube_Band{band}_{mole}_cropped.fits'

    importfits(fitsimage=pathIN, imagename='casaIN.im', overwrite=True)
    print(f">>aqing : Successfully load {mole}'s cube.")

    # Crop
    imsubimage(imagename='casaIN.im', outfile='casaCUT.im', chans=spchanns)

    # Change Restfreequency, by casatools
    ia.open('casaCUT.im')
    csys = ia.coordsys()
    csys.setrestfrequency(value=f0)
    ia.setcoordsys(csys.torecord())
    ia.done()

    print(f">>aqing : Finish cropping {mole} and the header keyWord 'RESTFRQ' now is {f0} Hz.")

    exportfits(imagename='casaCUT.im', fitsimage=pathOUT, overwrite=True)
    shutil.rmtree('casaCUT.im')
    shutil.rmtree('casaIN.im')
    print(f">>aqing : Finish processing {mole}'s original cube and metafiles are cleaned.")

print('All done :)')