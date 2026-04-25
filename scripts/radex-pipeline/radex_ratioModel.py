# Only run this script after running radex_fluxModel.py
# Construct 5D Ratio Models, and save them as .npy files
'''
程式湯底來自 Eltha 女士的 radex_pipeline.py, flux_model_6d.py, 
flux model 的部分在 radex_fluxModel.py 中已經處理好了,
這邊是要讀取存成 .npy 的 5d flux model, 計算出 ratio model 並也存成 .npy
所以必須先跑過 radex_fluxModel.py 才行, 不然會找不到這邊需要的原料
'''

# Import Module
import numpy as np

# Path Variables
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
npyPath = f'{projectRoot}/data/model_npy'  # flux 原料的地址

# Set Containers
flux5d = {} # 放 5d flux 的字典
ratio_model = {}

# Get Ratio's Material (Load 5d Flux Model (.npy))
moles_name = ['co-10', '13co-10', 'c18o-10',
              'co-21', '13co-21', 'c18o-21',]

for molename in moles_name:
    flux5d[molename] = np.load(f'{npyPath}/flux_5d-coarse2_{molename}.npy') # Eltha 就用的 5d

# Ratio
'''
這樣寫可能會有點冗員, 但總之就是先決定是這樣了
'''
for numer in moles_name:
    for denomi in moles_name:
        if numer != denomi:
            np.save(f'{npyPath}/ratio_{numer}-over-{denomi}.npy', flux5d[numer] / flux5d[denomi])

print('Ratio models saved.')