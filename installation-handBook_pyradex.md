# pyradex Installation handbook for Linux machine (Ubuntu)
I hope this handbook can help you work with this **legacy** tool that is still widely used in radiative transfer modeling.  
I tried to install pyradex on my laptop (macOS 15, named feifei:)), but sadly I failed on both arm64 and x86-64 (via Rosetta2) architectures due to compilation issues with `myRadex`.  
Later, I switched to a Linux machine and FINALLY got it working!  
So here, I’ll share the installation steps and the patch I used, hoping it can help others facing the same problem <3

All the credit and reputation goes to the brilliant minds who wrote RADEX, developed its python wrapper, answered related questions on stackOverflow.  
Much of this work also refers to **keflavich**’s repo `pyradex`.

This handbook mainly focuses on the installation tutorial.  
For details on the modifications and references of patches, please see `patch_ref.md`.

## Environment info
- **OS**: Ubuntu20.04
- **gfortran**: GNU Fortran 9.4.0 (Ubuntu 9.4.0-1ubuntu1~20.04.2)
- **venv**: miniconda
- **python** 3.10
- **astropy** 6.1.2
- **numpy** 1.26.2

## Patches
應該有在同個資料夾中釋出  
使用的大原則是，出現了問題(error)再用，搞不好你克隆下來的 repo 是 k大 更新過的了  
請小心使用，因為我自己也裝得亂七八糟的。  
但至少近年，我做的補丁應該會有一定的作用（在進行安裝的環節可以有效減少報錯...僅此而已  

請查收我為您打包的patch 
**我的建議是 出了問題再用！** 也就是，先嘗試執行k提供的安裝步驟，出了問題再使用我的補丁
（雖然改的都是一些語法之類的，但因為我對 fortran 完全的新手，不能確定我一定做了最好的操作  
做的所有事情絕大部分都是在 stack overFlow, K的issue, GenAI等多方參考下引用的，特此警告）
改過的地方（應該）會有「modi by qing」的標註，除了 op1的warning，因為那大概有500+

## Steps
### Set the environment
Because 系統的python是python3.8, which is too old to 裝 astropy==6.1.2 numpy==1.26.2  
並且我害怕爆破實驗室的電腦，所以開了個虛擬環境，我用了 miniconda  
這邊我叫他 astro_py310，或是隨便的名字，all depends on you
```
conda create -n astro_py310 python=3.10
conda activate astro_py310
```

進入虛擬環境，安裝相依的 python 套件  
因為 raedx 是一個 fortran 湯底的東西，所以numpy的版本很重要
再新一點的（numpy2.0）好像不行，總之我用1.26成功了，供大家參考
conda install seems can't find `astroqurey` and `spec`, so I use pip
```
pip install astropy==6.1.2 numpy==1.26.2
pip install astroquery
pip install specutils
```

接下來安裝編譯器，因爲 `RADEX` 是 fortran 湯底的，所以需要 `gfortran`  
可以先用倆command這個看看電腦裡裝過`gfortran`沒
```
gfortran --version
which gfortran
```

安裝 `gfortran`
```
sudo apt update
sudo apt install gfortran
```

因為某些原因 i describe in `installation-details.md`  
you also need this for 編譯順利  
在這邊感謝 Stack overflow 上的 ()，謝謝他的人性光輝  
```
conda install “setup tools<65”
```
**以上幾乎是環境設置的所有前置工作**

### Installationnn
接下來的步驟絕對標準應該參考 k 的github  
這邊只是提供一些經驗之談，大家斟酌相信（因為我只是一個沒畢業的瓠瓜） 

接下來要 clone 別人的repo，所以先確定有git工具  
```
git —version
```
接下來的步驟將會在當前路徑下建立一個名為`pyradex/`的資料夾，所以先 cd 到你想放這資料夾的地方  
比如
```
cd ~/astro_tools
```

將別人的 repo clone 下來
完全就是從k的github複製的，具體網址應該參考他，搞不好網址會變（之後馬上就要遇到相似這個問題辣！）
```
git clone --recursive https://github.com/keflavich/pyradex.git
```

cd 進去`pyrdexx`那個資料夾，
ls 的話裡面應有 `setup.py`, `install_radex.py` etc...
```
cd ~/astro_tools/pyradex
ls
```

依照指示跑跑這個 (python or pyhton3 depend on your computer setting) 
```
python setup.py install_radex install_myradex install
```

先執行看看，但應該會遇到第一個錯：
```
... fail to resolve ‘personal.sron.nl’
```
具體修改請見`details`, 總之這邊可以使用補丁`install_radex.py`  
直接貼到`~/astro_tools/pyradex` （或對應路徑）就可以了，取代原有檔案


### 開始編譯
換了新的install_radex.py(或您很幸運地沒遇到上個問題) do it again 
```
python setup.py install_radex install_myradex install
```

than you may come into tons of message 爆破你的 terminal like:
```
Found shared object files=[] for RADEX.  (if that is a blank, it means radex didn't install successfully)
Found shared object files=[] for RADEX.  (if that is a blank, it means fjdu's myradex didn't install successfully)
...
Line #49 in radex.inc:" parameter(hplanck = 6.6260963d-27) " get_parameters: got "eval() arg 1 must be a string, bytes or code object" on 4
...
Error sub_global_variables.f90:41:54:
41 | double precision, parameter :: phy_NaN = transfer(X'FFFFFFFFFFFFFFFF', 0D0)  
```
or something like that seems like nothing success hahapy  

Here we got two problem, one is from`radex.inc` another is from`sub_global_variables.f90`  
I am going to fix the `sub_global_variables.f90` one because it is an **Error**
這個問題的詳細細節依然請見 `patch_ref.md` 簡單來說就是定義 null 的方式變了，新的編譯器不認識原本的寫法  
在 `~/astro_tools/pyradex/myRadex` 放入補丁 `sub_global_variables.f90` and `sub_trivials.f90` 就可以解決

再試一次
```
python setup.py install_radex install_myradex install
```

應該可以看到
```
Found shared object files=['radex.so'] for RADEX. (if that is a blank, it means radex didn't install successfully)
Found shared object files=[] for RADEX. (if that is a blank, it means fjdu's myradex didn't install successfully)
```
`radex` 成功了！恭喜一半！當`radex.so` 出現在[]之後，就可以在`~/astro_tools/pyradex/Radex/src`中放入補丁`radex.inc`  
這個個改動詳見 `patch_ref.md`, 簡單來說就是指數符號新舊的差異  
在使用了 補丁`radex.inc` 之後，安裝命令要從`python setup.py install_radex install_myradex install`改成
```
python setup.py install_myradex install
```
移除install_radex（避免覆寫.inc），所以必須等 radex 裝好之後（`radex.so` 出現）才使用這個補丁

跑了一次`python setup.py install_myradex install`之後  
出現了一大桶新的 warning
```
warning: linalg_nleq1.f:1513:21:
1513 | CALL XERBLA('DGER ',INFO) | 1 Warning: Character length of actual argument shorter than of dummy argument 'srname' (5/6) at (1) 

warning: opkda1.f:123:72:
123 | 110 PC(I) = PC(I-1) + FNQM1*PC(I) | 1 Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 110 at (1) opkda1.f 
...
warning: opkda1.f:1255:72:
1255 | 1 RWORK(LACOR), IA, JA, RWORK(LWM), RWORK(LWM), IPFLAG, F, JAC) | 1 Error: Type mismatch in argument 'iwk' at (1); passed REAL(8) to INTEGER(4) opkda1.f:9499:72:
...
9499 | 2 RES, JAC, ADDA) | 1 Error: Type mismatch in argument 'iwk' at (1); passed REAL(8) to INTEGER(4) 
```

這邊像要跟大家說的是，後兩個關於iwk的警告在 macOS 上會是錯誤！  
但，因為一些我不懂的理由（或許是gfortran版本？） Linux machine上將這些視為警告、不影響編譯  


### 測試
當出現了
```

```
這倆 `.so` 代表大成功，可以使用 k 大提供的測試碼



