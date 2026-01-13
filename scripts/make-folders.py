# You MUST put this script under /line-modeling/scripts/ or other subfolder
# For Linxs and MacOS
'''
這是可以自動偵測有沒有符合 radex-pipeline_modiPath-add6d.py 所需檔案結構的一隻程式，
並且修補不符合部分 :)
'''

from pathlib import Path
import os

projectRoot = Path(__file__).resolve().parents[1]
dataPath = f'{projectRoot}/data/radex_io'
productPath = f'{projectRoot}/products'

under_radex_io = ['input_5d-coarse_co', 'input_5d-coarse_13co', 'input_5d-coarse_c18o', 
                  'output_5d-coarse_co', 'output_5d-coarse_13co', 'output_5d-coarse_18co']
under_products = ['from_radex-pipeline']

print('Start building suitable folder structure...')
for i in under_radex_io:
    dataPath_sub = f'{dataPath}/{i}'
    if not os.path.exists(dataPath_sub):
        os.makedirs(dataPath_sub)

for i in under_products:
    productPath_sub = f'{productPath}/{i}'
    if not os.path.exists(productPath_sub):
        os.makedirs(productPath_sub)

print('Done.')