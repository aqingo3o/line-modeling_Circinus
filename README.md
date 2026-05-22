# line-modeling_Circinus
** **This repo mainly serves as a personal log of the research process and may contain contain many imperfect operations.** **
> 
**👾 Current Progress:** Just have a meet with Eltha, nearly all of works need redo :(  
But a lot of valiable comments <3
>
---
## Quick Start
comming soon...  
> [!CAUTION]
>  Before this block disappear, don't trust any script in this repo.  

## Repository Structure
|Folder|Description|Rating
|---|---|---|
[envs/](envs)|Environment configuration files (.yml or .txt)       |8
[docs/](docs)|Documentation, notes, and something human-facing.    |-
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
- **what-is-wrong00.md**  
Basically a manual for scripts in [wrong00](exp/wrong00).
Actually scripts in that directory is technically correct, they just don't conform to the correct data processing flow (astronomy).  
I put all they in single folder for layout neatness.  
You might see files with the same names in [scripts](scripts), because, as I said, these code are technically correct:)

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

