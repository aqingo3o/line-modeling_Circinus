# Mainly from github: Hello_Circinus/miniscripts
# A script for full CASA
'''
又來到的熟悉的 convole to the same beam 
依然選擇了熟悉的 CASA

!! 如果這個腳本運行到一半 CASA 就被 killed
可能是因為 ram 爆炸了 (Linux terminal: )
在終端先輸入 export OMP_NUM_THREADS=4
再進入 casa 就可以解決ヽ(｀▽´)ノ 但運行時間當然會加倍啦
總之不要塞滿執行緒, Lab 那台好像有 12 緒吧, 全塞滿的話大 cube 會爆 ram

!! 非常之建議做完 smooth 之後要用 CARTA 或是其他可以看光譜軸的方法確認 cube 有沒有壞掉,
(有前科的) 可能會有譜線強度在某個 channel 之後全部歸零的情況, 個人猜測很高機率是硬體的鍋
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
    pathOUT = f'{dataPath}/smoothed_cube/cube_Band{band}_{mole}_smooth3.2as.fits'

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
