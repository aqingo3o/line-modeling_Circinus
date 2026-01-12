# Record of trying radex-pipeline_*.py
試跑 `radex-pipeline_*.py` 發生的錯誤紀錄。

## History
(20260112) 在實驗室電腦和 feifei 都失敗了，發生類似的錯誤。綜合判斷應該是 `13co.dat` 的問題。

## 前情提要
參考 [exp](../exp), 我總共提供了這五個腳本，都是從 Eltha 女士的 `radex_pipeline.py` 改的 (注意細微的檔名差異)，但是有改動程度的不同。  
(後見之明：並不是真的檔案路徑寫錯的問題。)    
- radex-pipeline_Lite.py
- radex-pipeline_writeInput.py
- radex-pipeline_runRadex.py
- radex-pipeline_constructFlux.py
- radex-pipeline_modiPath.py

_writeInput.py, _runRadex.py, _constructFlux.py 依序是 _Lite.py 的切片。我讓 feifei 跑這三個。  
_modiPath.py 幾乎是 Eltha 的原作，我就改檔案位置路徑而已，避免我因為省掉一些精細步驟造成他媽的報錯。我讓實驗室的 Linux 跑這個。  

## Result
### feifei
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

### Linux machine
一模一樣的 **FileNotFoundError**, 但用時更久...應該是電腦性能的關係？  
完全的一樣，就只有 `output_13co/` 裡什麼東西都沒有。

## whyyyyyy
如果真的是因為路徑造成有些檔案寫不進去的話 `output_c18o/` 應該也會要是全空, 因為老子寫的迴圈有重複的部分都是從 co, 13co, c18o 這樣的順序複製下去的（比手畫腳），進行一個大沿用。  
如果只有 13co 出事的話，那應該就是因為 `13co.dat` 是我自己從 [EMAA](https://emaa.osug.fr) 抓的，下載的時候後綴是 .radex, not .dat  
這是唯一可以想到的不同了。 

## 13co.dat ?
我覺得是，這是在大電腦上跑的結果  
co 就跑得出來, 13co 就不行  
所以一定是 `13co.dat` 的問題！  
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
是因為這個原因嗎？  
還在研究
