# from github: Hello_Circinus/miniscripts
# A script for full CASA
'''
Cut datacubes into smaller pieces and revise the header keyword 'RESTFREQ'
因為還有計算噪音的需求所以會留下線兩端的空白區間
'''
#from casatasks import importfits, imsubimage, imhead, exportfits
import glob
import shutil

# Files and Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # for feifei
#projectRoot = '/home/aqing/Documents/line-modeling_Circinus'       # for Lab Machine
dataPath = f'{projectRoot}/data/alma_cube'
cubes = glob.glob(f'{dataPath}/ori_cube/cube_*.fits')
cubes.sort() # make sure the order is the same in every computer!

# (mole, band, specLine's channels(casaForm, check from CARTA), restFrequency(Hz))
wanted = [ 
    ('c18o-10', '3a', '2600~3800', 1.09782E+11),
    ('13co-10', '3a', '200~1200',  1.10201E+11),
    ('co-10',   '3b', '1700~2700', 1.15271E+11),
    ('c18o-21', '6a', '2100~3500', 2.19560E+11),
    ('13co-21', '6a', '500~2200',  2.20399E+11),
    ('co-21',   '6a', '2300~3700', 2.30538E+11),
]

# Cropping
for i in range(len(cubes)):
    pathIN = cubes[i]
    mole = wanted[i][0]
    band = wanted[i][1]
    spchanns = wanted[i][2]
    f0 = wanted[i][3]
    pathOUT = f'{dataPath}/cropped_cube/cube_Band{band}_{mole}_cropped.fits'

    importfits(fitsimage=pathIN, imagename='casaIN.im', overwrite=True)
    print('Successfully import a datacube.')

    imsubimage(imagename='casaIN.im', outfile='casaCUT.im', chans=spchanns)
    imhead(imagename='casaCUT.im',
           mode='put', hdkey='restfreq', hdvalue=str(f0)) # 資料型態竟然要是字串，不客氣，幫轉了
    print(f"Finish cropping of {mole} and the header keyWord 'RESTFREQ' now is {f0} Hz") 

    exportfits(imagename='casaCUT.im', fitsimage=pathOUT, overwrite=True)
    shutil.rmtree('casaCUT.im')
    shutil.rmtree('casaIN.im')
    print(f"Finish processing {mole}'s original cube and metafiles are cleaned")

print('All done :)')
