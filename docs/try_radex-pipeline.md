# Record of trying radex-pipeline_*.py
`radex-pipeline_*.py` 系列腳本的演化以及使用指示(程式層面)，以及在試跑他們時發生的錯誤的紀錄。  

## Document History
(20260112) 在實驗室電腦和 feifei 都失敗了，發生類似的錯誤。綜合判斷應該是 `13co.dat` 的問題。  
(20260125) Update current state

## Previous Events
### (caseclose)
[exp/byQing](../exp/byQing/) 裡的東西如下，大概可以理解成 Lite 分割成了後三個:
- radex-pipeline_Lite.py
- radex-pipeline_writeInput.py
- radex-pipeline_runRadex.py
- radex-pipeline_constructFlux.py  

因為這些東西被本人很大程度地改過，所以連我都有點不敢信任...  
已經標示為 **(caseclose)** 所以就不要再去用它們了。  

在 [exp](../exp) 之下還有這個
- radex-pipeline_modiPath.py
  
這幾乎是 Eltha 的原作，我就改檔案位置路徑而已，避免我因為省掉一些精細步驟造成他媽的報錯。但是這個的源碼湯底來自 ngc3351，因為一些檔案結構的關係和 bayesian 的有些許不同，所以也標示成 **(caseclose)**。

### useable
在 [scripts/radex-pipeline](../scripts/radex-pipeline) 下的都是精選...可以用的 
- [radex-pipeline_setFolder-modiPath-add6d.py](../scripts/radex-pipeline)
- [radex-pipeline_modiPath-add6d.py](../scripts/radex-pipeline)
   
他們插在 [radex-pipeline_setFolder-modiPath-add6d.py](../scripts/radex-pipeline/radex-pipeline_setFolder-modiPath-add6d.py) 多一個 **setFolder** 的功能，就是把 [make-folders.py](../scripts/make-folders.py) 外掛上去，其餘均相同。  

## Testing Result
### (20260112)
use scripts in [exp/byQing](../exp/byQing/)  

- feifei
  - radex-pipeline_writeInput.py   : 用時 270 秒，寫完 4992+94848+1802112
  - radex-pipeline_runRadex.py     : 用時 3333 秒，做完一堆 RADEX
  - radex-pipeline_constructFlux.py: 卡住力  

我也用實驗室的電腦跑過這些，但是耗時巨他媽久，大概是 10 倍的時間，不知道為什麼會這樣...? 它 cpu 好歹也是 xeon, 那不是伺服器嗎？ 
等學弟回來我要問他能不能借他的超高級運算單元跑跑看，嘿嘿。  

回歸正題，運行 `radex-pipeline_constructFlux.py` 時卡住的終端訊息部分如下:  
```
Traceback (most recent call last):
  File "/Users/aqing/Documents/1004/line-modeling_Circinus/exp/radex-pipelind_constructFlux.py", line 92, in <module>
    flux_results = Parallel(n_jobs=cores)(
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/joblib/parallel.py", line 2072, in __call__
    return output if self.return_generator else list(output)
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/joblib/parallel.py", line 1682, in _get_outputs
    yield from self._retrieve()
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/joblib/parallel.py", line 1784, in _retrieve
    self._raise_error_fast()
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/joblib/parallel.py", line 1859, in _raise_error_fast
    error_job.get_result(self.timeout)
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/joblib/parallel.py", line 758, in get_result
    return self._return_or_raise()
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/joblib/parallel.py", line 773, in _return_or_raise
    raise self._result
FileNotFoundError: /Users/aqing/Documents/1004/line-modeling_Circinus/data/radex_io/output_co/Tkin-1.0e1_nH2-1.0e2_Nco-1.0e15.out not found.
```
簡單來說就是 **FileNotFoundError**, 用終端命令
```
cd ~/Documents/1004/line-modeling_Circinus/data/radex_io/input_co
ls | wc -l
```
發現 `output_*/` 的檔案數和 `input_*/` 的不一樣，而且 `output_13co/` 裡面完全沒有東西寫入，  
`output_co/` 最正常，io 組有相同的 file numbers, `output_c18o` 不知道是意外終止還是怎樣，`.out` < `.inp`。  

- Linux machine (Lab)
一模一樣的 **FileNotFoundError**, 但用時更久...應該是電腦性能的關係？  
完全的一樣，就只有 `output_13co/` 裡什麼東西都沒有。

### (20260125)
use scripts in [scripts](../scripts/radex-pipeline/)  
修好了所有的報錯，記錄一下跑的時間。 但實驗室的電腦要跑一個他媽巨久我真的不知道為什麼。  
- feifei
  - Write all .inp files: 374.19 seconds
  - Finish rinning RADEX: 10603.73 seconds
  - miss
  - miss
  - Finish "flux_model_6d.py, Eitha": 6.82 seconds  

- Linux machine (Lab)
  - Write all .inp files: 20565.66 seconds
  - Finish rinning RADEX: 67497.53 seconds
  - Save fiux models: 24426.92 seconds
  - Everything in "radex_pipeline.py, Eitha": 112490.38 seconds
  - Finish "flux_model_6d.py, Eitha": 112502.21 seconds

## whyyyyyy
### (20260112)
如果真的是因為路徑造成有些檔案寫不進去的話 `output_c18o/` 應該也會要是全空, 因為老子寫的迴圈有重複的部分都是從 co, 13co, c18o 這樣的順序複製下去的（比手畫腳），進行一個大沿用。  
如果只有 13co 出事的話，那應該就是因為 `13co.dat` 是我自己從 [EMAA](https://emaa.osug.fr) 抓的，下載的時候後綴是 .radex, not .dat  
這是唯一可以想到的不同了。 

## Problem
將會分點紀錄跑 `radex-pipeline_*.py` 系列的問題。就當成可悲的紀錄在看就好了。

### 13co.dat ?
我覺得是 `13co.dat` 的問題，這是在大電腦上跑的結果  
co 就跑得出來, 13co 就不行  
```
(eltha_py310) aqing@megamaser3-Precision-3650-Tower:~/Documents/line-modeling_Circinus/exp$ radex

    Welcome to Radex, version of 30nov2011          

Molecular data file ? co.dat
Name of output file ? ee.out
Minimum and maximum output frequency [GHz] ? 50 500
Kinetic temperature [K] ?  20
Number of collision partners ?  1
Type of partner 1 ? H2
Density of collision partner  1 [cm^-3] ? 1e4
Background temperature [K] ?  2,73
Molecular column density [cm^-2] ?  1e13
Line width [km/s] ?  15
 Starting calculations ...
 *** Warning: Assuming thermal o/p ratio for H2 of    1.7770941869968250E-003
 Finished in           10  iterations.
  Another calculation [0/1] ? 1
Molecular data file ? 13co.dat
Name of output file ? ee2.out
Minimum and maximum output frequency [GHz] ? 40 100
Kinetic temperature [K] ?  20
Number of collision partners ?  1
Type of partner 1 ? H2
Density of collision partner  1 [cm^-3] ? 1e4
Background temperature [K] ?  2.73
Molecular column density [cm^-2] ?  1e16
Line width [km/s] ?  15
 Starting calculations ...
 *** Warning: No rates found for any collision partner
Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG
```
觀察其他已知正確（？）的 .dat files (co.dat and c18o.dat)  
在描述碰撞夥伴的時候都有這幾句  
```
!NUMBER OF COLL PARTNERS
2
!COLLISIONS BETWEEN
2 CO-pH2 from Yang et al. (2010)
```
pH2 應該是 para-H2 的意思？  
是因為這個原因嗎？ 還在研究  

研究回來了！就是因為我的 `13co.dat` 是從 EMAA 下載的，他的格式就是不太對啦屁眼。  
參考 [where-to-get-dat.md](where-to-get-dat.md), 請從 LAMDA 下載格式符合 RADEX 的 .dat files :)  
feifei 用了 8000 秒完成了 `radex-pipeline_runRadex.py`  
output_13co/, output_c18o/ 的檔名都他媽很怪，我覺得是檔名超過一定長度之後就會他媽很怪。 
就像這樣：`Tkin-1.0e1_nH2-1.0e3_Nco-1.0e17_X1213-90_X1`，後面直接斷掉是三小啦。
難怪 Eltha 女士要使用不明確的檔名。  
好欸，果然什麼事都有他的原因。

(20260125)  
所以最後放棄了 [exp/byQing](../exp/byQing/) 裡，經過本人大量修改的東西，包括但不限於檔名。  
總之事情應該是一定程度上的解決了。  