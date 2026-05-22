Scripts manual in [wrong00/](../exp/wrong00)

### For Data Reduction
0. **Crop the data cubes FIRST!**  
Use this script: [cube_cropper_casa.py](exp/wrong00/preProcess/cube_cropper_casa.py). This scripts was design to run within full CASA on machines with enough RAM. (do not use feifei)  
Module casa is *okay*, add these in script before running.
```python
from casatasks import importfits, imsubimage, imhead, exportfits
```

1. **Convolve to common beam**.
Use [cube_smoother_casa.py](exp/wrong00/preProcess/cube_smoother_casa.py).  
Similarly, this should be run with CASA on big computer.  
*If the script is killed or crashes mid-process, try limiting the threads with the following command:*  
```bash
export OMP_NUM_THREADS=4
```

2. **Measure noise** (for making mom0, not for chi2)  
Use this script: [cube_noiseStat.py](exp/wrong00/preProcess/cube_noiseStat.py), here need the smoothed cubes from previous step.

3. **Make mom0 and error maps** (<- for fitting)  
Use these scripts: [cube_mom0Maker.py](exp/wrong00/preProcess/cube_mom0Maker.py) for making moment zero maps and [cube_errorMap.py](exp/wrong00/preProcess/cube_errorMap.py) for making error maps.  

4. **Unit conversion and reproject**  
For RADEX modeling, maps' unit should be **K** (or K* km/s), not **Jy/beam** (or Jy/beam* km/s), so we need this step.
Reprojection template is **CO(2-1)**, after imsmooth().
Thought CO(3-2) has smaller FoV, CO(2-1) has 900x900 in pixel while CO(3-2) has only 864x864.

### For Building Model Grid
0. Run [radex_fluxModel.py](scripts/radex-pipeline/radex_fluxModel.py) in your projectRoot folder.  
It will first establish folder structure for the coming work, and build the physical condition grid, and extract flux data from model for fitting.  
WARNING: This step take lots time, run this script on server maybe a good choice...   

1. Run [radex_ratioModel.py](scripts/radex-pipele/radex_ratioModel.py), not sure for what now :(

### For Fitting
1. Try [fit_fitONEpix](exp/wrong00/fit_fitONEpix.py) to fit one pixel.
Check the informations such as chi2 contribution, NaN in flux model... before fit over the whole map.  

2. Use [fit_fitMANYpix_parallel.py](exp/wrong00/fit_fitMANYpix_parallel.py) to fit pixel-by-pixel over whole map with parallel processing.  
Don't occupy all threads of the lab server...
