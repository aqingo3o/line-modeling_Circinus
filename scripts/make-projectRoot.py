# Put this script in a clean folder (called projectRoot) 
# and it can create a suitable structure for next scripts ;)
# For Linxs and MacOS
'''
創造 data/, scripts/, exp/, 那些東西
算是前置中的大前置
'''

from pathlib import Path
import os

projectRoot = Path(__file__).resolve() # line-modeling_Circinus/
projectRoot_member = ['data', 'docs', 'exp', 'products', 'scripts', 'src']

print('Start building suitable folder structure...')
for i in projectRoot_member:
    projectRoot_sub = f'{projectRoot}/{i}'
    if not os.path.exists(projectRoot_sub):
        os.makedirs(projectRoot_sub)
print('Done.')