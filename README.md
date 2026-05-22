# line-modeling_Circinus
** **This repo mainly serves as a personal log of the research process and may contain contain many imperfect operations.** **
> 
**👾 Current Progress:** Just have a meet with Eltha, nearly all of works need redo :(  
But a lot of valiable comments <3
>
---
## Quick Start
> [!CAUTION]
>  Before this block disappear, don't trust any script in this repo.  
### For Data Reduction
0. **Crop the data cubes FIRST!**  
Use this script: [cube_cropper_casa.py](scripts/preProcess/cube_cropper_casa.py). This scripts was design to run within full CASA on machines with enough RAM. (do not use feifei)  
Module casa is *okay*, add these in script before running.
```python
from casatasks import importfits, imsubimage, imhead, exportfits
```

1. **Convolve to common beam**.
Use [cube_smoother_casa.py](scripts/preProcess/cube_smoother_casa.py).  
Similarly, this should be run with CASA on big computer.  
*If the script is killed or crashes mid-process, try limiting the threads with the following command:*  
```bash
export OMP_NUM_THREADS=4
```

2. **Measure noise** (for making mom0, not for chi2)  
Use this script: [cube_noiseStat.py](scripts/preProcess/cube_noiseStat.py), here need the smoothed cubes from previous step.

3. **Make mom0 and error maps** (<- for fitting)  
Use these scripts: [cube_mom0Maker.py](scripts/preProcess/cube_mom0Maker.py) for making moment zero maps and [cube_errorMap.py](scripts/preProcess/cube_errorMap.py) for making error maps.  

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
1. Try [fit_fitONEpix](scripts/fit_fitONEpix.py) to fit one pixel.
Check the informations such as chi2 contribution, NaN in flux model... before fit over the whole map.  

2. Use [fit_fitMANYpix_parallel.py](scripts/fit_fitMANYpix_parallel.py) to fit pixel-by-pixel over whole map with parallel processing.  
Don't occupy all threads of the lab server...


## Repository Structure
|Folder|Description|Rating
|---|---|---|
[envs/](envs)|Environment configuration files (.yml or .txt)       |8
[docs/](docs)|Documentation, notes, and something human-facing.    |-
[data/](data)|There are `.dat` files that used for modeling.       |-
[exp/](exp)|Test pipelines, and exploratory code.                  |0
[scripts/](scripts)|Something good...?                             |7

[pyradex_at-first-sight/](pyradex_at-first-sight) Is a bottle of shit, never use that.💩  

<details>
<summary>Click <kbd>here</kbd> for more folders information :)</summary>
  
### docs/  
- **pyradex_patches/**  
Since the patches comes from a fortran 大菜雞, please use it carefully with [installation-handBook_pyradex.md](../docs/installation-handBook_pyradex.md).  
Referenced from [keflavich/pyradex](https://github.com/keflavich/pyradex). Tthe repo may be updated, so please refer to keflavich's repo for the most accurate information.
- **installation-handBook_pyradex.md**  
這真的巨媽麻煩，好消息是建模主體並不會用到 `pyradex`，只是因為誤會了什麼所以才 work on installing `pyradex` :(  
- **installation-hint_RADEX.md**  
Actually, [RADEX's official website](https://sronpersonalpages.nl/~vdtak/radex/index.shtml) already explains it very clearly, so this is just a note.
- **try_radex-pipeline.md**   
The logs(natural language) of running [this series](../scripts/radex-pipeline) of programs.
Aside from lots of unnecessary details, this is quite valuable for reference, and also record the script's evolution tree. Recommended:)
- **where-to-get-dat.md**  
As the filename, it explains where and how to get `.dat` files. Please don't laugh because I genuinely didn't know where to find these files at first.
I thought RADEX would download them automaticallyt?  

### data/ 
Data cubes from ALMA are in the local data/, I'm not sure if those are public data... so only `.dat` files here.  
To get the `.dat`s, please check [where-to-get-dat.md](../docs/where-to-get-dat.md). (just download from [LAMDA](https://home.strw.leidenuniv.nl/~moldata/), 23333)

### exp/
Test pipelines, and exploratory code.  
基本上我會建議不要使用這邊的東西，因為是試驗性質的東西所以基本上都在亂改哈哈，一鍋雜湯。  
不過用來回頭查查某些過於緻密的迴圈到底是什麼的時候還算好用，  
但要用的話還是建議從 [scripts/](scripts) 中抓。  

### scripts/
Quick start 中有提到的 scripts 都算經過測試的相對好版，  
通常會是 [exp/](exp) 中，同名_fullComment.py 的變種，  
可能是刪掉一些很白痴的註解，讓程式變得比較可讀一點。  
也包含一些有用小工具，總之是推薦的一個好物聚集。  
</details>

