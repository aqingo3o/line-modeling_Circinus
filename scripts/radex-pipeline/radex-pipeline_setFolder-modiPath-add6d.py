'''# radex-pipeline_setFolder-modiPath-add6d.py
radex-pipeline_modiPath-add6d.py 加上 make-folders.py (for Linxs and MacOS)
一站解決所有需求 (?)
'''

# Module
import numpy as np
import os
import time
from joblib import Parallel, delayed
from pathlib import Path

start_time = time.time()

# Path
projectRoot = Path(__file__).resolve().parents[1] # .../line-modeling_Circinus, no slash at the end
dataPath = f'{projectRoot}/data/radex_io'
productPath = f'{projectRoot}/products'
model = '5d-coarse2'
sou_model = 'from_radex-pipeline/' # modi by qing (20260113), filename of flux&&ratio model

# Make folders
'''# You MUST put this script under /line-modeling/scripts/ or other subfolder
'''
under_radex_io = ['input_5d-coarse2_co', 'input_5d-coarse2_13co', 'input_5d-coarse2_c18o', 
                  'output_5d-coarse2_co', 'output_5d-coarse2_13co', 'output_5d-coarse2_c18o']
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
print('Folders are ok.')

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

# def write_inputs_m*():
def write_inputs_m0(i,j,k):
    powi = str(i//cycle_temp + int(Tkin[0]))
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    powj = j//cycle_dens + int(nH2[0])
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prei = str(Tk_dex[i%cycle_temp])
    prej = str(co_dex[j%cycle_dens])
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    prek = str(co_dex[k%cycle_dens])
    codex = str(round(co_dex[k%cycle_dens], round_dens))

    file = open(dataPath+'/input_'+model+'_'+molecule_0+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'.inp','w')
    file.write(molecule_0+'.dat\n')
    file.write(dataPath+'/output_'+model+'_'+molecule_0+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'.out\n')
    file.write('100'+' '+'400'+'\n')
    file.write(prei+'e'+powi+'\n')
    file.write('1\n')
    file.write('H2\n')
    file.write(prej+'e'+n_h2+'\n')
    file.write('2.73'+'\n')
    file.write(prek+'e'+N_co+'\n')
    file.write(str(linewidth)+'\n')
    file.write('0\n')
    file.close() 

def write_inputs_m1(i,j,k,m):
    powi = str(i//cycle_temp + int(Tkin[0]))
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    powj = j//cycle_dens + int(nH2[0])
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prei = str(Tk_dex[i%cycle_temp])
    prej = str(co_dex[j%cycle_dens])
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    prek = str(round(factors_13co[m]*co_dex[k%cycle_dens],4))
    x13co = str(X_13co[m])
    codex = str(round(co_dex[k%cycle_dens], round_dens))

    file = open(dataPath+'/input_'+model+'_'+molecule_1+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'_'+x13co+'.inp','w')
    file.write(molecule_1+'.dat\n')
    file.write(dataPath+'/output_'+model+'_'+molecule_1+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'_'+x13co+'.out\n')
    file.write('100'+' '+'400'+'\n')
    file.write(prei+'e'+powi+'\n')
    file.write('1\n')
    file.write('H2\n')
    file.write(prej+'e'+n_h2+'\n')
    file.write('2.73'+'\n')
    file.write(prek+'e'+N_co+'\n')
    file.write(str(linewidth)+'\n')
    file.write('0\n')
    file.close()   

def write_inputs_m2(i,j,k,m,n):
    powi = str(i//cycle_temp + int(Tkin[0]))
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    powj = j//cycle_dens + int(nH2[0])
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prei = str(Tk_dex[i%cycle_temp])
    prej = str(co_dex[j%cycle_dens])
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    prek = str(round(factors_c18o[n]*factors_13co[m]*co_dex[k%cycle_dens],6))
    x13co = str(X_13co[m])
    xc18o = str(X_c18o[n])
    codex = str(round(co_dex[k%cycle_dens], round_dens))

    file = open(dataPath+'/input_'+model+'_'+molecule_2+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'_'+x13co+'_'+xc18o+'.inp','w')
    file.write(molecule_2+'.dat\n')
    file.write(dataPath+'/output_'+model+'_'+molecule_2+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'_'+x13co+'_'+xc18o+'.out\n')
    file.write('100'+' '+'400'+'\n')
    file.write(prei+'e'+powi+'\n')
    file.write('1\n')
    file.write('H2\n')
    file.write(prej+'e'+n_h2+'\n')
    file.write('2.73'+'\n')
    file.write(prek+'e'+N_co+'\n')
    file.write(str(linewidth)+'\n')
    file.write('0\n')
    file.close()

# def run_rADEX_m*():
def run_radex_m0(i,j,k):
    powj = j//cycle_dens + int(nH2[0])
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    codex = str(round(co_dex[k%cycle_dens], round_dens))
    run = os.system('radex < '+dataPath+'/input_'+model+'_'+molecule_0+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'.inp')
    return run

def run_radex_m1(i,j,k,m):
    powj = j//cycle_dens + int(nH2[0])
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))
    x13co = str(X_13co[m])
    codex = str(round(co_dex[k%cycle_dens], round_dens)) 
    run = os.system('radex < '+dataPath+'/input_'+model+'_'+molecule_1+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'_'+x13co+'.inp')
    return run

def run_radex_m2(i,j,k,m,n):
    powj = j//cycle_dens + int(nH2[0])
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))    
    x13co = str(X_13co[m])
    xc18o = str(X_c18o[n])
    codex = str(round(co_dex[k%cycle_dens], round_dens))  
    run = os.system('radex < '+dataPath+'/input_'+model+'_'+molecule_2+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'_'+x13co+'_'+xc18o+'.inp')
    return run

# def radex_flux(): **from bayes repo**
def radex_flux(i,j,k,m,n):
    powj = j//cycle_dens + int(nH2[0])
    Tk = str(round(diff_Tk*i + int(Tkin[0]), round_temp))
    n_h2 = str(powj)
    N_co = str(k//cycle_dens + int(Nco[0]))
    
    prej_r = str(round(co_dex[j%cycle_dens], round_dens))   
    x13co = str(X_13co[m])
    xc18o = str(X_c18o[n])
    codex = str(round(co_dex[k%cycle_dens], round_dens))

    outfile_0 = dataPath+'/output_'+model+'_'+molecule_0+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'.out'
    outfile_1 = dataPath+'/output_'+model+'_'+molecule_1+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'_'+x13co+'.out'
    outfile_2 = dataPath+'/output_'+model+'_'+molecule_2+'/'+Tk+'_'+prej_r+'e'+n_h2+'_'+codex+'e'+N_co+'_'+x13co+'_'+xc18o+'.out'

    # Extract reliable flux predictions (avoid those with convergence issues)
    if np.loadtxt(outfile_0, skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_0 = np.full((3,),np.nan)
    else:
        flux_0 = np.genfromtxt(outfile_0, skip_header=13)[:,11]

    if np.loadtxt(outfile_1, skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_1 = np.full((3,),np.nan)
    else:    
        flux_1 = np.genfromtxt(outfile_1, skip_header=13)[:,11]

    if np.loadtxt(outfile_2, skiprows=10, max_rows=1, dtype='str')[3] == '****':
        flux_2 = np.full((3,),np.nan)
    else:    
        flux_2 = np.genfromtxt(outfile_2, skip_header=13)[:,11]
    
    return k,i,j,m,n,flux_0,flux_1,flux_2

# Use the functions write_inputs_m*() for molecules0,1,2
print('Start to writing .inp files...')
Parallel(n_jobs=num_cores)(
    delayed(write_inputs_m0)(i,j,k)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )              
Parallel(n_jobs=num_cores)(
    delayed(write_inputs_m1)(i,j,k,m)
    for m in range(0,num_X12to13)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )
Parallel(n_jobs=num_cores)(
    delayed(write_inputs_m2)(i,j,k,m,n)
    for n in range(0,num_X13to18)
    for m in range(0,num_X12to13)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )
input_time = time.time()
print(f'It took {(input_time - start_time):.2f} seconds to write all .inp files.') # modi by qing (20260113)

# Run RADEX for molecules 0,1,2
print('Start RADEXing ...')
Parallel(n_jobs=num_cores)(
    delayed(run_radex_m0)(i,j,k)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )  
Parallel(n_jobs=num_cores)(
    delayed(run_radex_m1)(i,j,k,m)
    for m in range(0,num_X12to13)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )          
Parallel(n_jobs=num_cores)(
    delayed(run_radex_m2)(i,j,k,m,n)
    for n in range(0,num_X13to18)
    for m in range(0,num_X12to13)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )
radex_time = time.time()
print(f'It took {(radex_time - input_time):.2f} seconds to finish running RADEX.') # modi by qing (20260113)

# Construct 3D - 5D flux models
print('Constructing flux model grids...')
results = Parallel(n_jobs=num_cores, verbose=5)(
    delayed(radex_flux)(i,j,k,m,n)
    for n in range(0,num_X13to18)
    for m in range(0,num_X12to13)
    for k in range(num_Nco)
    for j in range(num_nH2)
    for i in range(num_Tk)
    )

flux_co10 = np.full((num_Nco,num_Tk,num_nH2), np.nan)
flux_co21 = np.full((num_Nco,num_Tk,num_nH2), np.nan)
flux_co32 = np.full((num_Nco,num_Tk,num_nH2), np.nan)
flux_13co10 = np.full((num_Nco,num_Tk,num_nH2,num_X12to13), np.nan)
flux_13co21 = np.full((num_Nco,num_Tk,num_nH2,num_X12to13), np.nan)
flux_13co32 = np.full((num_Nco,num_Tk,num_nH2,num_X12to13), np.nan)
flux_c18o10 = np.full((num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18), np.nan)
flux_c18o21 = np.full((num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18), np.nan)
flux_c18o32 = np.full((num_Nco,num_Tk,num_nH2,num_X12to13,num_X13to18), np.nan)

for result in results:
    k, i, j, m, n, flux_0, flux_1, flux_2 = result
    flux_co10[k,i,j] = flux_0[0]
    flux_co21[k,i,j] = flux_0[1]
    flux_co32[k,i,j] = flux_0[2]
    flux_13co10[k,i,j,m] = flux_1[0]
    flux_13co21[k,i,j,m] = flux_1[1]
    flux_13co32[k,i,j,m] = flux_1[2]
    flux_c18o10[k,i,j,m] = flux_2[0]
    flux_c18o21[k,i,j,m,n] = flux_2[1]
    flux_c18o32[k,i,j,m,n] = flux_2[2]

np.save(productPath+'/'+sou_model+'flux_'+model+'_co-10.npy',   flux_co10) # (filename) modi by qing (20260113)
np.save(productPath+'/'+sou_model+'flux_'+model+'_co-21.npy',   flux_co21)
np.save(productPath+'/'+sou_model+'flux_'+model+'_co-32.npy',   flux_co32)
np.save(productPath+'/'+sou_model+'flux_'+model+'_13co-10.npy', flux_13co10)
np.save(productPath+'/'+sou_model+'flux_'+model+'_13co-21.npy', flux_13co21)
np.save(productPath+'/'+sou_model+'flux_'+model+'_13co-32.npy', flux_13co32)
np.save(productPath+'/'+sou_model+'flux_'+model+'_c18o-10.npy', flux_c18o10)
np.save(productPath+'/'+sou_model+'flux_'+model+'_c18o-21.npy', flux_c18o21)
np.save(productPath+'/'+sou_model+'flux_'+model+'_c18o-32.npy', flux_c18o32)
flux_time = time.time()
print('Flux models saved.')

# Construct 5D ratio models
temp = np.repeat(flux_co21[:, :, :, np.newaxis], num_X12to13, axis=3)
co21_5d = np.repeat(temp[:, :, :, :, np.newaxis], num_X13to18, axis=4)
temp2 = np.repeat(flux_co10[:, :, :, np.newaxis], num_X12to13, axis=3)
co10_5d = np.repeat(temp2[:, :, :, :, np.newaxis], num_X13to18, axis=4)
c13o_21_5d = np.repeat(flux_13co21[:, :, :, :, np.newaxis], num_X13to18, axis=4)
c13o_32_5d = np.repeat(flux_13co32[:, :, :, :, np.newaxis], num_X13to18, axis=4) 

ratio_co = co21_5d/co10_5d
ratio_13co = c13o_32_5d/c13o_21_5d
ratio_c18o = flux_c18o32/flux_c18o21
ratio_co213co = co21_5d/c13o_21_5d
ratio_co2c18o = co21_5d/flux_c18o21
ratio_13co2c18o_21 = c13o_21_5d/flux_c18o21
ratio_13co2c18o_32 = c13o_32_5d/flux_c18o32

np.save(productPath+'/'+sou_model+'ratio_'+model+'_co-21_over_co-10.npy',     ratio_co) # (filename) modi by qing (20260113)
np.save(productPath+'/'+sou_model+'ratio_'+model+'_13co-32_over_13co-21.npy', ratio_13co)
np.save(productPath+'/'+sou_model+'ratio_'+model+'_c18o-32_over_c18o-21.npy', ratio_c18o)
np.save(productPath+'/'+sou_model+'ratio_'+model+'_co-21_over_c13o-21.npy',   ratio_co213co)
np.save(productPath+'/'+sou_model+'ratio_'+model+'_co-21_over_c18o-21.npy',   ratio_co2c18o)
np.save(productPath+'/'+sou_model+'ratio_'+model+'_13co-21_over_c18o-21.npy', ratio_13co2c18o_21)
np.save(productPath+'/'+sou_model+'ratio_'+model+'_13co-32_over_c18o-32.npy', ratio_13co2c18o_32)
print('Ratio models saved.')
endpl_time = time.time()

# ----------------------------------------------------------------------------------------------------------------------------------------------- #

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
print('Done with flux_model_6d.py.')
end6d_time = time.time()

# Write Time Record
# modi by qing (20260113)
timerec = open(f'{projectRoot}/docs/radex-pipeline_timeRecord.txt', 'w')
timerec.write(f'It took {(input_time - start_time):.2f} seconds to write all .inp files.\n')
timerec.write(f'It took {(radex_time - input_time):.2f} seconds to finish running RADEX.\n')
timerec.write(f'It took {(flux_time - radex_time):.2f} seconds to save flux models.\n')
timerec.write(f'It took {(endpl_time - start_time):.2f} seconds to do everythig in "radex_pipeline.py, Eitha".\n')
timerec.write(f'It took {(end6d_time - start_time):.2f} seconds to finish "flux_model_6d.py, Eitha".\n')
timerec.close()