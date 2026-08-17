# Please run this script after running radex_fluxModel.py
# Construct 5D Ratio Models, and save them as .npy files
'''
因為真沒招了, 搞不好真的是 beam-filling factor 在搞
所以試試這個?

updatae: 2026-08-17, Really use this script and do some revise...
'''

# Import Module
import numpy as np

# Path Variables
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus' # feifei
npyPath = f'{projectRoot}/data/model_npy'

moles_name = ['co-10', 'co-21', 'co-32', '13co-10', '13co-21', 'c18o-21',]
# (numer, denomi)
'''
just these 5 line ratio for ratio model
because (L2/L3) = ((L2/L1) / (L3/L1)) for chi2 fitting.
'''
ratio_set = [
    ('co-21', 'co-10'),
    ('co-32', 'co-10'),

    ('13co-10', 'co-10'),
    ('13co-21', 'co-10'),

    ('c18o-21', 'co-10'),
    ]

# Load flux models
flux_model = {}
for molename in moles_name:
    flux_model[molename] = np.load(f'{npyPath}/flux_plain-model_3para_{molename}.npy')
    '''
    load flux models without beam filling factor
    , so '3para'
    '''

# Ratio
for ratioset in ratio_set:
    line_ratio = flux_model[ratioset[0]] / flux_model[ratioset[1]]
    np.save(f'{npyPath}/ratio_plain-model_{ratioset[0]}-over-{ratioset[0]}.npy',
            line_ratio)

print('Ratio models are saved.')