# line-modeling_Circinus
**⚠️ This repo mainly serves as a personal log of the research process and may contain contain many imperfect operations .**  
>
**👾 Current Progress:** I've tried src/radex-pipeline_*.py, some failed and some is still running... 
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

## Environment (2025.12.27)
**feifei:** macOS Sequoia 15.6.1, M3 chip (arm-64)  
..  

**Lab computer:** Ubuntu20.04  
Model fitting requires computational powerrrr, so I perform those tasks on desktop.  
(But I think writing .inp files on feifei is much faster?)
Thought I may not use `pyradex` for modeling, I still need to mention that I could only make `pyradex` works on Linux now. :(  
