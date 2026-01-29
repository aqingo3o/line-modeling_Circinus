# line-modeling_Circinus
> [!CAUTION]
> This repo mainly serves as a personal log of the research process and may contain contain many imperfect operations .   
>
**👾 Current Progress:** `radex_pipeline.py` and `flux_model_6d.py` are technically working, but I don't know why we should do like that.
>
---
## Repository Structure
This repo is organized as follows:
```
.
├── data/                     # .dat files used in RADEX
├── docs/                     # Documentation, notes, and something human-facing
│   └── pyradex_patches/      # Patches for pyradex installation.
├── envs/                     # Environment configuration files (.yml or something like that)
├── exp/                      # Test pipelines, and exploratory code
├── products/                 # Products. (if have :)
├── pyradex_at-first-sight/   # A bottle of shit, never use that.
├── scripts/                  # Usable scripts
├── (src/)                    # (not yet)
├── LICENSE                   # ok I know I write a piece of shit.
└── README.md                 # YOU ARE HERE ;)
```

## data/
There are `.dat` files that used for modeling.   
Data cubes from ALMA are in the local data/, I'm not sure if those are public data... so only `.dat` files here.  
To get the `.dat`s, please check [where-to-get-dat.md](../docs/where-to-get-dat.md). (just download from [LAMDA](https://home.strw.leidenuniv.nl/~moldata/), 23333)  

## docs/
Documents :)
- *pyradex_patches/*  
Since the patches comes from a fortran 大菜雞, please use it carefully with [installation-handBook_pyradex.md](../docs/installation-handBook_pyradex.md).  
Referenced from [keflavich/pyradex](https://github.com/keflavich/pyradex). Tthe repo may be updated, so please refer to keflavich's repo for the most accurate information.
- *installation-handBook_pyradex.md*  
這真的巨媽麻煩，好消息是建模主體並不會用到 `pyradex`，只是因為誤會了什麼所以才 work on installing `pyradex` :(  
- *installation-hint_RADEX.md*  
Actually, [RADEX's official website](https://sronpersonalpages.nl/~vdtak/radex/index.shtml) already explains it very clearly, so this is just a note.
- *try_radex-pipeline.md*   
The logs(natural language) of running [this series](../scripts/radex-pipeline) of programs.
Aside from lots of unnecessary details, this is quite valuable for reference, and also record the script's evolution tree. Recommended:)
- *where-to-get-dat.md*  
As the filename, it explains where and how to get `.dat` files. Please don't laugh because I genuinely didn't know where to find these files at first.
I thought RADEX would download them automaticallyt?  
