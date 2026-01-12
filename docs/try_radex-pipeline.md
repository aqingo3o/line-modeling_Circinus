# Record when trying radex-pipeline_*.py
試跑的非常奇怪事件，當回圈大到一定程度之後就有點難以預測他接下來的情況了...  
雖然說 `radex-pipeline_*.py`  的迴圈不是什麼困難的大迴圈  

## 前情提要
參考 [exp](../exp), 我總共提供了這些腳本，都是從 Eltha 女士的 `radex_pipeline.py` 改的 (注意細微的檔名差異)，但是有改動程度的不同。  
(後見之明：並不是真的檔案路徑寫錯的問題。)    
- radex-pipeline_Lite.py
- radex-pipeline_writeInput.py
- radex-pipeline_runRadex.py
- radex-pipeline_constructFlux.py
- radex-pipeline_modiPath.py

_writeInput.py, _runRadex.py, _constructFlux.py 依序是 _Lite.py 的切片，我讓 feifei 這三個。  
_modiPath.py 幾乎是 Eltha 的原作，我就改檔案位置路徑而已，避免說我因為省掉一些精細步驟造成他媽的報錯，我讓實驗室的 Linux 跑這個。  

## Result
### feifei
- radex-pipeline_writeInput.py   : 用時 270 秒，寫完 4992+94848+1802112
- radex-pipeline_runRadex.py     : 用時 3333 秒，做完一堆 RADEX
- radex-pipeline_constructFlux.py: 卡住力  

啊就是我也用實驗室的電腦跑過這些其實，但是耗時巨他媽久，大概是 10 倍的時間，不知道為什麼會這樣...? 他好歹也是 xeon 的那個 cpu 
噢我知道了，等學弟回來我要問他能不能借他的超高級運算單元，嘿嘿。  

回歸正題，運行 `radex-pipeline_constructFlux.py` 時卡住的終端訊息如下:  
```
joblib.externals.loky.process_executor._RemoteTraceback: 
"""
Traceback (most recent call last):
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/joblib/externals/loky/process_executor.py", line 490, in _process_worker
    r = call_item()
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/joblib/externals/loky/process_executor.py", line 291, in __call__
    return self.fn(*self.args, **self.kwargs)
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/joblib/parallel.py", line 607, in __call__
    return [func(*args, **kwargs) for func, args, kwargs in self.items]
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/joblib/parallel.py", line 607, in <listcomp>
    return [func(*args, **kwargs) for func, args, kwargs in self.items]
  File "/Users/aqing/Documents/1004/line-modeling_Circinus/exp/radex-pipelind_constructFlux.py", line 74, in radex_flux
    if np.loadtxt(outfile_0, skiprows=10, max_rows=1, dtype='str')[3] == '****':
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/numpy/lib/_npyio_impl.py", line 1395, in loadtxt
    arr = _read(fname, dtype=dtype, comment=comment, delimiter=delimiter,
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/numpy/lib/_npyio_impl.py", line 1022, in _read
    fh = np.lib._datasource.open(fname, 'rt', encoding=encoding)
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/numpy/lib/_datasource.py", line 192, in open
    return ds.open(path, mode, encoding=encoding, newline=newline)
  File "/Users/aqing/miniconda3_arm/envs/eltha_py310/lib/python3.10/site-packages/numpy/lib/_datasource.py", line 529, in open
    raise FileNotFoundError(f"{path} not found.")
FileNotFoundError: /Users/aqing/Documents/1004/line-modeling_Circinus/data/radex_io/output_co/Tkin-1.0e1_nH2-1.0e2_Nco-1.0e15.out not found.
"""

The above exception was the direct cause of the following exception:

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
簡單來說就是 **FileNotFoundError**, 從 Finder 裡面查看 (或用終端命令)
```
ls | wc -l
```
發現 `output_*/` 的檔案數和 `input_*/` 的不一樣，而且 `output_13co` 裡面完全沒有東西寫入。  

### Linux machine
一樣的 **FileNotFoundError**, 但用時更久...應該是電腦性能的關係？  

## whyyyyyy
如果真的是因為路徑造成有些檔案寫不進去的話... c18o 應該也會失敗, 因為老子寫的迴圈是從 co, 13co, c18o 這樣進行一個大沿用。  
如果只有 13co 出事的話那應該就是因為 13co.dat 是我自己從 [EMAA](https://emaa.osug.fr) 抓的，下載的時候後綴是 .radex  
他媽的會是這種問題嗎？我將會進行一些常識然後回報  

## 額外的奇怪之處
眾所周知，RADEX 會去指定的路徑(寫在 radex.inc) 找到 .dat files 
他媽的重點是在我指定的地方根本就沒有 .dat, (檔案直接放錯地方)  
為什麼他還跑得動啊？
