# line-modeling_Circinus
> [!CAUTION]
> This repo mainly serves as a personal log of the research process and may contain contain many imperfect operations .   
>
**👾 Current Progress:** Masuring noise in each cubes.  
>
---
## Quick Start
I am not really sure but [radex-pipeline](scripts/radex-pipeline/) should be done first.

## Repository Structure
|Folder|Description|Rating
|---|---|---|
[envs/](envs)|Environment configuration files (.yml or something like that)        |8
[docs/](docs)|Documentation, notes, and something human-facing.                    |-
[data/](data)|There are `.dat` files that used for modeling.                       |-
[exp/](exp)|Test pipelines, and exploratory code.                                  |0
[scripts/](scripts)|Something good...?                                             |7
[products/](scripts)|(if any...)                                                   |? 

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

### scripts/
從 [exp/](../exp) 來的東西，相對稍微經過測試的好版  
也包含一些有用小工具，總之是推薦的一個好物聚集。  
</details>

