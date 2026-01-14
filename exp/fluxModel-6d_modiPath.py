'''# fluxModel-6d_modiPath.py
radex-pipeline_modiPath-add6d.py 跑到一半爆炸的話可以從這邊接著下去哈哈屁眼
缺點就是沒有寫入 radex-pipeline_timeRecord.txt 的環節

這個湯底是 flux_model_6d.py(Eltha), 用的是 bayes 那版的
和同樣 _modiPath 的來自不同的 repo, 不能混用幹您娘
'''

# Module
import numpy as np
import time
from pathlib import Path

start_time = time.time()
# Path
projectRoot = Path(__file__).resolve().parents[1] # .../line-modeling_Circinus, no slash at the end
dataPath = f'{projectRoot}/data/radex_io'
productPath = f'{projectRoot}/products'
sou_model = 'from_radex-pipeline/' # modi by qing (20260113), filename of flux&&ratio model

# Variable
num_cores = 20 # joblib
linewidth = 15 # km/s

molecule_0 = 'co'
molecule_1 = '13co'
molecule_2 = 'c18o'

# Physical Conditions Grid
Nco = np.arange(15., 20.1, 0.2)
Tkin = np.arange(1., 2.8, 0.1)
nH2 = np.arange(2., 5.1, 0.2) # step size for Nco and nH2 should be the same
X_13co = np.arange(10, 205, 10)
X_c18o = np.arange(2, 21, 1)
round_dens = 1
round_temp = 1

# Pre-processing
incr_dens = round(Nco[1] - Nco[0],1)
incr_temp = round(Tkin[1] - Tkin[0],1)
diff_Tk = Tkin[1] - Tkin[0]
co_dex = np.round(10**np.arange(0.,1.,incr_dens), 4)
Tk_dex = np.round(10**np.arange(0.,1.,incr_temp), 4)
factors_13co = 1./X_13co  
factors_c18o = 1./X_c18o
num_Nco = Nco.shape[0]
num_Tk = Tkin.shape[0]
num_nH2 = nH2.shape[0]
cycle_dens = co_dex.shape[0]
cycle_temp = Tk_dex.shape[0]
num_X12to13 = X_13co.shape[0]
num_X13to18 = X_c18o.shape[0]

# flux_model_6d.py, Eltha
print('Start doing flux_model_6d.py...')
base_model = '5d-coarse2' # modi by qing (20260114), '5d_coarse2' 沒有這種檔名啊？
model6 = '6d-coarse2'     # modi by qing (20260113), change the variablename from 'model' to 'model6'
beam_fill = 10**np.arange(-1.3, 0.1, 0.1)

# import flux data
flux_co10 =      np.load(f'{productPath}/{sou_model}flux_{base_model}_co-10.npy')
flux_co21 =      np.load(f'{productPath}/{sou_model}flux_{base_model}_co-21.npy')
flux_co32 =      np.load(f'{productPath}/{sou_model}flux_{base_model}_co-32.npy') 
flux_13co10 =    np.load(f'{productPath}/{sou_model}flux_{base_model}_13co-10.npy')
flux_13co21 =    np.load(f'{productPath}/{sou_model}flux_{base_model}_13co-21.npy')
flux_13co32 =    np.load(f'{productPath}/{sou_model}flux_{base_model}_13co-32.npy')
flux_c18o10_5d = np.load(f'{productPath}/{sou_model}flux_{base_model}_c18o-10.npy')
flux_c18o21_5d = np.load(f'{productPath}/{sou_model}flux_{base_model}_c18o-21.npy')
flux_c18o32_5d = np.load(f'{productPath}/{sou_model}flux_{base_model}_c18o-32.npy')

temp =         np.repeat(flux_co21[:, :, :, np.newaxis], num_X12to13, axis=3)
flux_co21_5d = np.repeat(temp[:, :, :, :, np.newaxis], num_X13to18, axis=4)
temp2 =        np.repeat(flux_co10[:, :, :, np.newaxis], num_X12to13, axis=3)
flux_co10_5d = np.repeat(temp2[:, :, :, :, np.newaxis], num_X13to18, axis=4)
temp3 =        np.repeat(flux_co32[:, :, :, np.newaxis], num_X12to13, axis=3)                                                      
flux_co32_5d = np.repeat(temp3[:, :, :, :, np.newaxis], num_X13to18, axis=4)
flux_13co10_5d = np.repeat(flux_13co10[:, :, :, :, np.newaxis], num_X13to18, axis=4)
flux_13co21_5d = np.repeat(flux_13co21[:, :, :, :, np.newaxis], num_X13to18, axis=4)
flux_13co32_5d = np.repeat(flux_13co32[:, :, :, :, np.newaxis], num_X13to18, axis=4) 

# Construct 6d-flux models from 5d by adding the beam filling factor dimension
flux_co10_6d = flux_co10_5d.reshape(num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18,1) * beam_fill.reshape(1,1,1,1,1,beam_fill.shape[0])
flux_co21_6d = flux_co21_5d.reshape(num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18,1) * beam_fill.reshape(1,1,1,1,1,beam_fill.shape[0])
flux_co32_6d = flux_co32_5d.reshape(num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18,1) * beam_fill.reshape(1,1,1,1,1,beam_fill.shape[0]) 
flux_13co10_6d = flux_13co10_5d.reshape(num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18,1) * beam_fill.reshape(1,1,1,1,1,beam_fill.shape[0])
flux_13co21_6d = flux_13co21_5d.reshape(num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18,1) * beam_fill.reshape(1,1,1,1,1,beam_fill.shape[0])
flux_13co32_6d = flux_13co32_5d.reshape(num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18,1) * beam_fill.reshape(1,1,1,1,1,beam_fill.shape[0])
flux_c18o10_6d = flux_c18o10_5d.reshape(num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18,1) * beam_fill.reshape(1,1,1,1,1,beam_fill.shape[0])
flux_c18o21_6d = flux_c18o21_5d.reshape(num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18,1) * beam_fill.reshape(1,1,1,1,1,beam_fill.shape[0])
flux_c18o32_6d = flux_c18o32_5d.reshape(num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18,1) * beam_fill.reshape(1,1,1,1,1,beam_fill.shape[0])

# Save 6d-flux models
np.save(f'{productPath}/{sou_model}flux_{model6}_co-10.npy',   flux_co10_6d)
np.save(f'{productPath}/{sou_model}flux_{model6}_co-21.npy',   flux_co21_6d)
np.save(f'{productPath}/{sou_model}flux_{model6}_co-32.npy',   flux_co32_6d)
np.save(f'{productPath}/{sou_model}flux_{model6}_13co-10.npy', flux_13co10_6d)
np.save(f'{productPath}/{sou_model}flux_{model6}_13co-21.npy', flux_13co21_6d)
np.save(f'{productPath}/{sou_model}flux_{model6}_13co-32.npy', flux_13co32_6d)
np.save(f'{productPath}/{sou_model}flux_{model6}_c18o-10.npy', flux_c18o10_6d)
np.save(f'{productPath}/{sou_model}flux_{model6}_c18o-21.npy', flux_c18o21_6d)
np.save(f'{productPath}/{sou_model}flux_{model6}_c18o-32.npy', flux_c18o32_6d)
end6d_time = time.time()
print('Done with flux_model_6d.py.')
print(f'It took {(end6d_time - start_time):.2f} seconds to finish "flux_model_6d.py, Eitha".\n')