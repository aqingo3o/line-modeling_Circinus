# from github: Hello_Circinus/miniscripts
# A script for full CASA
'''
Crop datacubes into smaller pieces.
因為還有計算噪音的需求所以會留下線兩端的空白區間哈哈屁眼
'''
import glob
import shutil

projectRoot = '/home/aqing/Documents/line-modeling_Circinus'
dataPath = f'{projectRoot}/data/alma_cube'
cubes = glob.glob(f'{dataPath}/ori_cube/cube_*.fits')

wanted = [ # (mole, channels(casaForm, check from CARTA))
    ('13co-10', '200~1200',  '3a'),
    ('13co-21', '500~2200',  '6a'),
    ('c18o-21', '2100~3500', '6a'),
    ('co-21',   '2300~3700', '6a'),
    ('co-10',   '1700~2700', '3b'),
    ('c18o-10', '2600~3800', '6a'), # 按照 cubes 的順序的啊
]

for i in range(len(cubes)):
    pathIN = cubes[i]
    importfits(fitsimage=pathIN, imagename='casaIN.im', overwrite=True)
    print('Successfully import a datacube.')
    filename = wanted[i][0]
    channs = wanted[i][1]
    band = wanted[i][2]
    outfile = f'{dataPath}/cropped_cube/cube_Band{band}_{filename}_cropped.fits'
    imsubimage(imagename='casaIN.im', outfile='casaOUT.im', chans=channs)
    exportfits(imagename='casaOUT.im', fitsimage=outfile, overwrite=True)
    shutil.rmtree('casaOUT.im')
    print(f'{outfile} was done.')
    shutil.rmtree('casaIN.im')

print('All finish :)')
