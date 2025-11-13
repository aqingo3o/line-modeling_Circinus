# pyradex Installation handbook for Linux machine (Ubuntu)
Hope this handbook can help you work with this **legacy** tool that is still widely used in radiative transfer modeling.  
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
Release in *line-modeling_Circinus/patches*  
**ONLY apply them if you run into errors.**  Try following keflavich’s installation steps first. Your cloned repo might already be up-to-date.
Most fixes are just little syntax edits to prevent install errors and warnings. But I’m totally new to Fortran, can’t promise they’re the “best” solutions.   

Changes should be marked with **“modi by qing on (date)”**, except for warnings in *opkda1.f*  (there were like 500+ of those).  
My own installation setup is honestly quite chaotic:( so please import the patches carefully.  
Still, they should help reduce installation errors, at least for now.   

## Steps
### 0. Set the environment
The default system Python of lab machine is python3.8, which is too old to install packages like `astropy==6.1.2` and `numpy==1.26.2`.  
Since I didn’t want to risk breaking the lab’s system Python, I decided to set up a virtual environment using `miniconda`.  

I named mine `astro_py310`, but any name is okkkk.
```
conda create -n astro_py310 python=3.10
conda activate astro_py310
```

Once you’re inside the virtual environment, install the required Python packages.  
Because raedx is a Fortran-based application, the `numpy` version really matters. Newer ones (like `numpy2.0+`) seem incompatible... I use `numpy==1.26.2` and it works, so you can take that as a ref.  
Also, `conda install` doesn’t seem to find `astroquery` or `specutils`, so I installed them via `pip` instead.
```
pip install astropy==6.1.2 numpy==1.26.2
pip install astroquery
pip install specutils
```

You’ll need a working `gfortran` compiler beacuse raedx is a Fortran-based application. Check if it’s already installed on your system:
```
gfortran --version
which gfortran
```

If not, install it using:
```
sudo apt update
sudo apt install gfortran
```

Because of some issues I described in */patches/patch_ref.md*, you’ll also need to install an older version `setuptools` to ensure a smooth build process.
Special thanks to the kind souls on Stack Overflow, 人類群星閃耀時 ✨
```
conda install “setup tools<65”
```
**That’s almost all the preparation you need for setting up the environment.**


### 1. Installationnn
The following steps are based on keflavich’s repo-*pyradex*, which should be considered as the authoritative source.  
Here I’m just sharing some personal experience. You should 決定 to belive me or not because I’m just an *Lagenaria siceraria* .

Make sure you have git installed first: 
```
git —version
```
Next, we’ll clone the repository *pyradex*. This commands will create a folder named pyradex/ in the current directory, so first `cd` to wherever you want that folder to be, for example:
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

### Testing & Ensureeee
當出現了
```
Found shared object files=['radex.so'] for RADEX.  (if that is a blank, it means radex didn't install successfully)
Found shared object files=['wrapper_my_radex.cpython-310-x86_64-linux-gnu.so'] for RADEX.  (if that is a blank, it means fjdu's myradex didn't install successfully)
```
這倆 `.so` 代表大成功  
其他的測試可以使用 k 大提供的測試碼  

## Appendix
裝成功後的終端訊息，保留這個東西方便以後查查什麼東西的  
隨便，並非什麼具有參考價值的東西  
```
Found shared object files=['radex.so'] for RADEX.  (if that is a blank, it means radex didn't install successfully)
Found shared object files=['wrapper_my_radex.cpython-310-x86_64-linux-gnu.so'] for RADEX.  (if that is a blank, it means fjdu's myradex didn't install successfully)
/home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/setuptools/dist.py:530: UserWarning: Normalizing '0.4.2dev' to '0.4.2.dev0'
  warnings.warn(tmpl.format(**locals()))
running install_myradex
rm ./*.mod ./*.o
rm: cannot remove './*.mod': No such file or directory
rm: cannot remove './*.o': No such file or directory
make: *** [makefile:79: clean] Error 1
gfortran -O3 -fPIC -c sub_global_variables.f90
gfortran -O3 -fPIC -c sub_trivials.f90
gfortran -O3 -fPIC -c nleq1.f
gfortran -O3 -fPIC -c linalg_nleq1.f
gfortran -O3 -fPIC -c statistic_equilibrium.f90
gfortran -O3 -fPIC -c my_radex.f90
gfortran -O3 -fPIC -c opkda1.f
opkda1.f:2804:72:

 2804 |   6     j = j-1
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 6 at (1)
opkda1.f:1311:72:

 1311 |      4   JAC)
      |                                                                        1
Warning: Type mismatch in argument ‘iwk’ at (1); passed REAL(8) to INTEGER(4) [-Wargument-mismatch]
opkda1.f:9827:72:

 9827 |      5   ADDA)
      |                                                                        1
Warning: Type mismatch in argument ‘iwk’ at (1); passed REAL(8) to INTEGER(4) [-Wargument-mismatch]
gfortran -O3 -fPIC -c opkda2.f
opkda2.f:630:72:

  630 |       IF (INCX .EQ. INCY) IF (INCX-1) 5,20,60
      |                                                                        1
Warning: Fortran 2018 deleted feature: Arithmetic IF statement at (1)
opkda2.f:719:72:

  719 |       IF (INCX .EQ. INCY) IF (INCX-1) 5,20,60
      |                                                                        1
Warning: Fortran 2018 deleted feature: Arithmetic IF statement at (1)
opkda2.f:812:72:

  812 |       IF (INCX .EQ. INCY) IF (INCX-1) 5,20,60
      |                                                                        1
Warning: Fortran 2018 deleted feature: Arithmetic IF statement at (1)
opkda2.f:938:72:

  938 |    10 ASSIGN 30 TO NEXT
      |                                                                        1
Warning: Deleted feature: ASSIGN statement at (1)
opkda2.f:945:19:

  945 |    20    GO TO NEXT,(30, 50, 70, 110)
      |                   1
Warning: Deleted feature: Assigned GOTO statement at (1)
opkda2.f:947:72:

  947 |       ASSIGN 50 TO NEXT
      |                                                                        1
Warning: Deleted feature: ASSIGN statement at (1)
opkda2.f:957:72:

  957 |       ASSIGN 70 TO NEXT
      |                                                                        1
Warning: Deleted feature: ASSIGN statement at (1)
opkda2.f:963:72:

  963 |       ASSIGN 110 TO NEXT
      |                                                                        1
Warning: Deleted feature: ASSIGN statement at (1)
opkda2.f:997:72:

  997 |    95    SUM = SUM + DX(J)**2
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 95 at (1)
gfortran -O3 -fPIC -c opkdmain.f
opkdmain.f:1352:72:

 1352 |  80     RWORK(I+LSAVF-1) = RWORK(I+LWM-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 80 at (1)
opkdmain.f:1361:72:

 1361 |  95     RWORK(I) = 0.0D0
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 95 at (1)
opkdmain.f:1395:72:

 1395 |  115    RWORK(I+LYH-1) = Y(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 115 at (1)
opkdmain.f:1402:72:

 1402 |  120    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 120 at (1)
opkdmain.f:1426:72:

 1426 |  130    TOL = MAX(TOL,RTOL(I))
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 130 at (1)
opkdmain.f:1447:72:

 1447 |  190    RWORK(I+LF0-1) = H0*RWORK(I+LF0-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 190 at (1)
opkdmain.f:1498:72:

 1498 |  260    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 260 at (1)
opkdmain.f:1566:72:

 1566 |  410    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 410 at (1)
opkdmain.f:1636:72:

 1636 |  590    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 590 at (1)
opkdmain.f:3216:72:

 3216 |  72       RWORK(J) = RWORK(J+LYHD)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 72 at (1)
opkdmain.f:3220:72:

 3220 |  76       RWORK(I) = RWORK(I+LYHD)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 76 at (1)
opkdmain.f:3230:72:

 3230 |  82     RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 82 at (1)
opkdmain.f:3253:72:

 3253 |  95     RWORK(I) = 0.0D0
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 95 at (1)
opkdmain.f:3275:72:

 3275 |  105    RWORK(I+LYH-1) = Y(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 105 at (1)
opkdmain.f:3284:72:

 3284 |  110    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 110 at (1)
opkdmain.f:3348:72:

 3348 |  130    TOL = MAX(TOL,RTOL(I))
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 130 at (1)
opkdmain.f:3369:72:

 3369 |  190    RWORK(I+LF0-1) = H0*RWORK(I+LF0-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 190 at (1)
opkdmain.f:3420:72:

 3420 |  260    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 260 at (1)
opkdmain.f:3488:72:

 3488 |  410    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 410 at (1)
opkdmain.f:3573:72:

 3573 |  590    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 590 at (1)
opkdmain.f:4917:72:

 4917 |  95     RWORK(I) = 0.0D0
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 95 at (1)
opkdmain.f:4954:72:

 4954 |  115    RWORK(I+LYH-1) = Y(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 115 at (1)
opkdmain.f:4961:72:

 4961 |  120    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 120 at (1)
opkdmain.f:4988:72:

 4988 |  130    TOL = MAX(TOL,RTOL(I))
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 130 at (1)
opkdmain.f:5009:72:

 5009 |  190    RWORK(I+LF0-1) = H0*RWORK(I+LF0-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 190 at (1)
opkdmain.f:5065:72:

 5065 |  260    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 260 at (1)
opkdmain.f:5156:72:

 5156 |  410    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 410 at (1)
opkdmain.f:5244:72:

 5244 |  590    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 590 at (1)
opkdmain.f:6697:72:

 6697 |  95     RWORK(I) = 0.0D0
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 95 at (1)
opkdmain.f:6734:72:

 6734 |  115    RWORK(I+LYH-1) = Y(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 115 at (1)
opkdmain.f:6741:72:

 6741 |  120    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 120 at (1)
opkdmain.f:6768:72:

 6768 |  130    TOL = MAX(TOL,RTOL(I))
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 130 at (1)
opkdmain.f:6789:72:

 6789 |  190    RWORK(I+LF0-1) = H0*RWORK(I+LF0-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 190 at (1)
opkdmain.f:6873:72:

 6873 |  260    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 260 at (1)
opkdmain.f:6977:72:

 6977 |  410    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 410 at (1)
opkdmain.f:7068:72:

 7068 |  590    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 590 at (1)
opkdmain.f:8486:72:

 8486 |  80     RWORK(I+LSAVF-1) = RWORK(I+LWM-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 80 at (1)
opkdmain.f:8494:72:

 8494 |  95     RWORK(I) = 0.0D0
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 95 at (1)
opkdmain.f:8537:72:

 8537 |  115    RWORK(I+LYH-1) = Y(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 115 at (1)
opkdmain.f:8544:72:

 8544 |  120    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 120 at (1)
opkdmain.f:8568:72:

 8568 |  130    TOL = MAX(TOL,RTOL(I))
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 130 at (1)
opkdmain.f:8589:72:

 8589 |  190    RWORK(I+LF0-1) = H0*RWORK(I+LF0-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 190 at (1)
opkdmain.f:8684:72:

 8684 |  260    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 260 at (1)
opkdmain.f:8752:72:

 8752 |  410    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 410 at (1)
opkdmain.f:8835:72:

 8835 |  590    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 590 at (1)
opkdmain.f:10358:72:

10358 |  80     RWORK(I+LSAVF-1) = RWORK(I+LWM-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 80 at (1)
opkdmain.f:10366:72:

10366 |  95     RWORK(I) = 0.0D0
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 95 at (1)
opkdmain.f:10411:72:

10411 |  115    RWORK(I+LYH-1) = Y(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 115 at (1)
opkdmain.f:10418:72:

10418 |  120    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 120 at (1)
opkdmain.f:10431:72:

10431 |  190    RWORK(I+LF0-1) = H0*RWORK(I+LF0-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 190 at (1)
opkdmain.f:10554:72:

10554 |  260    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 260 at (1)
opkdmain.f:10635:72:

10635 |  410    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 410 at (1)
opkdmain.f:10723:72:

10723 |  590    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 590 at (1)
opkdmain.f:12165:72:

12165 |  80     YDOTI(I) = RWORK(I+LWM-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 80 at (1)
opkdmain.f:12174:72:

12174 |  95     RWORK(I) = 0.0D0
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 95 at (1)
opkdmain.f:12214:72:

12214 |  115        RWORK(I+LYH-1) = Y(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 115 at (1)
opkdmain.f:12219:72:

12219 |  125        RWORK(I+LYD0-1) = YDOTI(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 125 at (1)
opkdmain.f:12227:72:

12227 |  135    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 135 at (1)
opkdmain.f:12251:72:

12251 |  140    TOL = MAX(TOL,RTOL(I))
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 140 at (1)
opkdmain.f:12272:72:

12272 |  190    RWORK(I+LYD0-1) = H0*RWORK(I+LYD0-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 190 at (1)
opkdmain.f:12323:72:

12323 |  260    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 260 at (1)
opkdmain.f:12396:72:

12396 |  410    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 410 at (1)
opkdmain.f:12494:72:

12494 |  585     Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 585 at (1)
opkdmain.f:12506:72:

12506 |  592    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 592 at (1)
opkdmain.f:13964:72:

13964 |  80     YDOTI(I) = RWORK(I+LWM-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 80 at (1)
opkdmain.f:13973:72:

13973 |  95     RWORK(I) = 0.0D0
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 95 at (1)
opkdmain.f:14013:72:

14013 |   115       RWORK(I+LYH-1) = Y(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 115 at (1)
opkdmain.f:14018:72:

14018 |   125       RWORK(I+LYD0-1) = YDOTI(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 125 at (1)
opkdmain.f:14026:72:

14026 |  135    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 135 at (1)
opkdmain.f:14050:72:

14050 |  140    TOL = MAX(TOL,RTOL(I))
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 140 at (1)
opkdmain.f:14071:72:

14071 |  190    RWORK(I+LYD0-1) = H0*RWORK(I+LYD0-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 190 at (1)
opkdmain.f:14122:72:

14122 |  260    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 260 at (1)
opkdmain.f:14195:72:

14195 |  410    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 410 at (1)
opkdmain.f:14293:72:

14293 |  585     Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 585 at (1)
opkdmain.f:14305:72:

14305 |  592    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 592 at (1)
opkdmain.f:16009:72:

16009 |  72       RWORK(J) = RWORK(J+LYHD)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 72 at (1)
opkdmain.f:16013:72:

16013 |  76       RWORK(I) = RWORK(I+LYHD)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 76 at (1)
opkdmain.f:16022:72:

16022 |  82     RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 82 at (1)
opkdmain.f:16044:72:

16044 |  92     YDOTI(I) = RWORK(I+LSAVF-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 92 at (1)
opkdmain.f:16051:72:

16051 |  95     RWORK(I) = 0.0D0
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 95 at (1)
opkdmain.f:16074:72:

16074 |  105    RWORK(I+LYH-1) = Y(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 105 at (1)
opkdmain.f:16079:72:

16079 |  106    RWORK(I+LYD0-1) = YDOTI(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 106 at (1)
opkdmain.f:16085:72:

16085 |  110    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 110 at (1)
opkdmain.f:16150:72:

16150 |  140    TOL = MAX(TOL,RTOL(I))
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 140 at (1)
opkdmain.f:16171:72:

16171 |  190    RWORK(I+LYD0-1) = H0*RWORK(I+LYD0-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 190 at (1)
opkdmain.f:16222:72:

16222 |  260    RWORK(I+LEWT-1) = 1.0D0/RWORK(I+LEWT-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 260 at (1)
opkdmain.f:16296:72:

16296 |  410    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 410 at (1)
opkdmain.f:16409:72:

16409 |  585     Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 585 at (1)
opkdmain.f:16421:72:

16421 |  592    Y(I) = RWORK(I+LYH-1)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 592 at (1)
gfortran -O3 -fPIC -c wnorm.f
gfortran -O3 -fPIC -c zibconst.f
gfortran -O3 -fPIC -c zibmon.f
zibmon.f:384:55-69:

  384 |      $     'The following indices are active', (INDACT(I),I=0,IONCNT)
      |                                                       1             2
Warning: Array reference at (1) out of bounds (0 < 1) in loop beginning at (2)
zibmon.f:394:55-69:

  394 |      $     'The following indices are active', (INDACT(I),I=0,IONCNT)
      |                                                       1             2
Warning: Array reference at (1) out of bounds (0 < 1) in loop beginning at (2)
gfortran -O3 -fPIC -c zibsec.f
f2py -c -m wrapper_my_radex wrapper_for_python.f90 -L my_radex.o opkda1.o opkda2.o opkdmain.o statistic_equilibrium.o sub_global_variables.o sub_trivials.o nleq1.o linalg_nleq1.o wnorm.o zibconst.o zibmon.o zibsec.o
/home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/numpy/f2py/f2py2e.py:686: VisibleDeprecationWarning: distutils has been deprecated since NumPy 1.26.Use the Meson backend instead, or generate wrapperswithout -c and use a custom build script
  builder = build_backend(
running build
running config_cc
INFO: unifing config_cc, config, build_clib, build_ext, build commands --compiler options
running config_fc
INFO: unifing config_fc, config, build_clib, build_ext, build commands --fcompiler options
running build_src
INFO: build_src
INFO: building extension "wrapper_my_radex" sources
INFO: f2py options: []
INFO: f2py:> /tmp/tmpyqx0rlx6/src.linux-x86_64-3.10/wrapper_my_radexmodule.c
creating /tmp/tmpyqx0rlx6/src.linux-x86_64-3.10
Reading fortran codes...
Reading file 'wrapper_for_python.f90' (format:free)
Post-processing...
Block: wrapper_my_radex
Block: myradex_wrapper
Block: config_basic
In: :wrapper_my_radex:wrapper_for_python.f90:myradex_wrapper:config_basic
get_useparameters: no module my_radex info used by config_basic
Block: run_one_params
In: :wrapper_my_radex:wrapper_for_python.f90:myradex_wrapper:run_one_params
get_useparameters: no module my_radex info used by run_one_params
In: :wrapper_my_radex:wrapper_for_python.f90:myradex_wrapper:run_one_params
get_useparameters: no module statistic_equilibrium info used by run_one_params
Applying post-processing hooks...
  character_backward_compatibility_hook
Post-processing (stage 2)...
Block: wrapper_my_radex
Block: unknown_interface
Block: myradex_wrapper
Block: config_basic
Block: run_one_params
Building modules...
    Building module "wrapper_my_radex"...
Constructing F90 module support for "myradex_wrapper"...
 Variables: flag_good n_item_column about column_names molecule_name
            Constructing wrapper function "myradex_wrapper.config_basic"...
              n_levels,n_item,n_transitions = config_basic(dir_transition_rates,filename_molecule,tbg,verbose)
            Constructing wrapper function "myradex_wrapper.run_one_params"...
              energies,f_occupations,data_transitions,cooling_rate = run_one_params(tkin,dv_cgs,dens_x_cgs,ncol_x_cgs,h2_density_cgs,hi_density_cgs,oh2_density_cgs,ph2_density_cgs,hii_density_cgs,electron_density_cgs,n_levels,n_item,n_transitions,geotype)
    Wrote C/API module "wrapper_my_radex" to file "/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10/wrapper_my_radexmodule.c"
    Fortran 90 wrappers are saved to "/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10/wrapper_my_radex-f2pywrappers2.f90"
INFO:   adding '/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10/fortranobject.c' to sources.
INFO:   adding '/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10' to include_dirs.
copying /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/numpy/f2py/src/fortranobject.c -> /tmp/tmpyqx0rlx6/src.linux-x86_64-3.10
copying /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/numpy/f2py/src/fortranobject.h -> /tmp/tmpyqx0rlx6/src.linux-x86_64-3.10
INFO:   adding '/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10/wrapper_my_radex-f2pywrappers2.f90' to sources.
INFO: build_src: building npy-pkg config files
/home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/setuptools/command/install.py:34: SetuptoolsDeprecationWarning: setup.py install is deprecated. Use build and pip and other standards-based tools.
  warnings.warn(
running build_ext
INFO: customize UnixCCompiler
INFO: customize UnixCCompiler using build_ext
INFO: get_default_fcompiler: matching types: '['arm', 'gnu95', 'intel', 'lahey', 'pg', 'nv', 'absoft', 'nag', 'vast', 'compaq', 'intele', 'intelem', 'gnu', 'g95', 'pathf95', 'nagfor', 'fujitsu']'
INFO: customize ArmFlangCompiler
WARN: Could not locate executable armflang
INFO: customize Gnu95FCompiler
INFO: Found executable /usr/bin/gfortran
INFO: customize Gnu95FCompiler
INFO: customize Gnu95FCompiler using build_ext
INFO: building 'wrapper_my_radex' extension
INFO: compiling C sources
INFO: C compiler: gcc -pthread -B /home/aqing/miniconda3/envs/astro_py310/compiler_compat -Wno-unused-result -Wsign-compare -DNDEBUG -fwrapv -O2 -Wall -fPIC -O2 -isystem /home/aqing/miniconda3/envs/astro_py310/include -fPIC -O2 -isystem /home/aqing/miniconda3/envs/astro_py310/include -fPIC

creating /tmp/tmpyqx0rlx6/tmp
creating /tmp/tmpyqx0rlx6/tmp/tmpyqx0rlx6
creating /tmp/tmpyqx0rlx6/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10
INFO: compile options: '-DNPY_DISABLE_OPTIMIZATION=1 -I/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10 -I/home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/numpy/core/include -I/home/aqing/miniconda3/envs/astro_py310/include/python3.10 -c'
INFO: gcc: /tmp/tmpyqx0rlx6/src.linux-x86_64-3.10/wrapper_my_radexmodule.c
INFO: gcc: /tmp/tmpyqx0rlx6/src.linux-x86_64-3.10/fortranobject.c
INFO: compiling Fortran 90 module sources
INFO: Fortran f77 compiler: /usr/bin/gfortran -Wall -g -ffixed-form -fno-second-underscore -fPIC -O3 -funroll-loops
Fortran f90 compiler: /usr/bin/gfortran -Wall -g -fno-second-underscore -fPIC -O3 -funroll-loops
Fortran fix compiler: /usr/bin/gfortran -Wall -g -ffixed-form -fno-second-underscore -Wall -g -fno-second-underscore -fPIC -O3 -funroll-loops
INFO: compile options: '-I/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10 -I/home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/numpy/core/include -I/home/aqing/miniconda3/envs/astro_py310/include/python3.10 -c'
extra options: '-J/tmp/tmpyqx0rlx6/ -I/tmp/tmpyqx0rlx6/'
INFO: gfortran:f90: wrapper_for_python.f90
INFO: compiling Fortran sources
INFO: Fortran f77 compiler: /usr/bin/gfortran -Wall -g -ffixed-form -fno-second-underscore -fPIC -O3 -funroll-loops
Fortran f90 compiler: /usr/bin/gfortran -Wall -g -fno-second-underscore -fPIC -O3 -funroll-loops
Fortran fix compiler: /usr/bin/gfortran -Wall -g -ffixed-form -fno-second-underscore -Wall -g -fno-second-underscore -fPIC -O3 -funroll-loops
INFO: compile options: '-I/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10 -I/home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/numpy/core/include -I/home/aqing/miniconda3/envs/astro_py310/include/python3.10 -c'
extra options: '-J/tmp/tmpyqx0rlx6/ -I/tmp/tmpyqx0rlx6/'
INFO: gfortran:f90: /tmp/tmpyqx0rlx6/src.linux-x86_64-3.10/wrapper_my_radex-f2pywrappers2.f90
INFO: /usr/bin/gfortran -Wall -g -Wall -g -shared /tmp/tmpyqx0rlx6/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10/wrapper_my_radexmodule.o /tmp/tmpyqx0rlx6/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10/fortranobject.o /tmp/tmpyqx0rlx6/wrapper_for_python.o /tmp/tmpyqx0rlx6/tmp/tmpyqx0rlx6/src.linux-x86_64-3.10/wrapper_my_radex-f2pywrappers2.o my_radex.o opkda1.o opkda2.o opkdmain.o statistic_equilibrium.o sub_global_variables.o sub_trivials.o nleq1.o linalg_nleq1.o wnorm.o zibconst.o zibmon.o zibsec.o -L -L/usr/lib/gcc/x86_64-linux-gnu/9 -L/usr/lib/gcc/x86_64-linux-gnu/9 -lgfortran -o ./wrapper_my_radex.cpython-310-x86_64-linux-gnu.so
Removing build directory /tmp/tmpyqx0rlx6
make: 'sub_trivials.o' is up to date.
rm ./*.mod ./*.o
running install
/home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/setuptools/command/install.py:34: SetuptoolsDeprecationWarning: setup.py install is deprecated. Use build and pip and other standards-based tools.
  warnings.warn(
/home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/setuptools/command/easy_install.py:144: EasyInstallDeprecationWarning: easy_install command is deprecated. Use build and pip and other standards-based tools.
  warnings.warn(
running bdist_egg
running egg_info
writing pyradex.egg-info/PKG-INFO
writing dependency_links to pyradex.egg-info/dependency_links.txt
writing requirements to pyradex.egg-info/requires.txt
writing top-level names to pyradex.egg-info/top_level.txt
reading manifest file 'pyradex.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
adding license file 'LICENSE.rst'
writing manifest file 'pyradex.egg-info/SOURCES.txt'
installing library code to build/bdist.linux-x86_64/egg
running install_lib
running build_py
copying pyradex/fjdu/wrapper_my_radex.cpython-310-x86_64-linux-gnu.so -> build/lib/pyradex/fjdu
creating build/bdist.linux-x86_64/egg
creating build/bdist.linux-x86_64/egg/pyradex
copying build/lib/pyradex/base_class.py -> build/bdist.linux-x86_64/egg/pyradex
creating build/bdist.linux-x86_64/egg/pyradex/fjdu
copying build/lib/pyradex/fjdu/core.py -> build/bdist.linux-x86_64/egg/pyradex/fjdu
copying build/lib/pyradex/fjdu/wrapper_my_radex.cpython-310-x86_64-linux-gnu.so -> build/bdist.linux-x86_64/egg/pyradex/fjdu
copying build/lib/pyradex/fjdu/__init__.py -> build/bdist.linux-x86_64/egg/pyradex/fjdu
copying build/lib/pyradex/version.py -> build/bdist.linux-x86_64/egg/pyradex
creating build/bdist.linux-x86_64/egg/pyradex/tests
copying build/lib/pyradex/tests/test_fjdu.py -> build/bdist.linux-x86_64/egg/pyradex/tests
copying build/lib/pyradex/tests/test_synthspec.py -> build/bdist.linux-x86_64/egg/pyradex/tests
copying build/lib/pyradex/tests/test_grid.py -> build/bdist.linux-x86_64/egg/pyradex/tests
creating build/bdist.linux-x86_64/egg/pyradex/tests/data
copying build/lib/pyradex/tests/data/example.out -> build/bdist.linux-x86_64/egg/pyradex/tests/data
copying build/lib/pyradex/tests/test_radex_install.py -> build/bdist.linux-x86_64/egg/pyradex/tests
copying build/lib/pyradex/tests/test_radex.py -> build/bdist.linux-x86_64/egg/pyradex/tests
copying build/lib/pyradex/tests/test_radex_myradex_consistency.py -> build/bdist.linux-x86_64/egg/pyradex/tests
copying build/lib/pyradex/tests/setup_package_data.py -> build/bdist.linux-x86_64/egg/pyradex/tests
copying build/lib/pyradex/tests/__init__.py -> build/bdist.linux-x86_64/egg/pyradex/tests
creating build/bdist.linux-x86_64/egg/pyradex/radex
copying build/lib/pyradex/radex/radex.so -> build/bdist.linux-x86_64/egg/pyradex/radex
copying build/lib/pyradex/radex/__init__.py -> build/bdist.linux-x86_64/egg/pyradex/radex
copying build/lib/pyradex/core.py -> build/bdist.linux-x86_64/egg/pyradex
copying build/lib/pyradex/grid_wrapper.py -> build/bdist.linux-x86_64/egg/pyradex
copying build/lib/pyradex/synthspec.py -> build/bdist.linux-x86_64/egg/pyradex
copying build/lib/pyradex/read_radex.py -> build/bdist.linux-x86_64/egg/pyradex
copying build/lib/pyradex/utils.py -> build/bdist.linux-x86_64/egg/pyradex
copying build/lib/pyradex/__init__.py -> build/bdist.linux-x86_64/egg/pyradex
copying build/lib/pyradex/despotic_interface.py -> build/bdist.linux-x86_64/egg/pyradex
byte-compiling build/bdist.linux-x86_64/egg/pyradex/base_class.py to base_class.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/fjdu/core.py to core.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/fjdu/__init__.py to __init__.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/version.py to version.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/tests/test_fjdu.py to test_fjdu.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/tests/test_synthspec.py to test_synthspec.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/tests/test_grid.py to test_grid.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/tests/test_radex_install.py to test_radex_install.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/tests/test_radex.py to test_radex.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/tests/test_radex_myradex_consistency.py to test_radex_myradex_consistency.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/tests/setup_package_data.py to setup_package_data.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/tests/__init__.py to __init__.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/radex/__init__.py to __init__.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/core.py to core.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/grid_wrapper.py to grid_wrapper.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/synthspec.py to synthspec.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/read_radex.py to read_radex.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/utils.py to utils.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/__init__.py to __init__.cpython-310.pyc
byte-compiling build/bdist.linux-x86_64/egg/pyradex/despotic_interface.py to despotic_interface.cpython-310.pyc
creating build/bdist.linux-x86_64/egg/EGG-INFO
copying pyradex.egg-info/PKG-INFO -> build/bdist.linux-x86_64/egg/EGG-INFO
copying pyradex.egg-info/SOURCES.txt -> build/bdist.linux-x86_64/egg/EGG-INFO
copying pyradex.egg-info/dependency_links.txt -> build/bdist.linux-x86_64/egg/EGG-INFO
copying pyradex.egg-info/not-zip-safe -> build/bdist.linux-x86_64/egg/EGG-INFO
copying pyradex.egg-info/requires.txt -> build/bdist.linux-x86_64/egg/EGG-INFO
copying pyradex.egg-info/top_level.txt -> build/bdist.linux-x86_64/egg/EGG-INFO
writing build/bdist.linux-x86_64/egg/EGG-INFO/native_libs.txt
creating 'dist/pyradex-0.4.2.dev0-py3.10.egg' and adding 'build/bdist.linux-x86_64/egg' to it
removing 'build/bdist.linux-x86_64/egg' (and everything under it)
Processing pyradex-0.4.2.dev0-py3.10.egg
removing '/home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/pyradex-0.4.2.dev0-py3.10.egg' (and everything under it)
creating /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/pyradex-0.4.2.dev0-py3.10.egg
Extracting pyradex-0.4.2.dev0-py3.10.egg to /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
pyradex 0.4.2.dev0 is already the active version in easy-install.pth

Installed /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages/pyradex-0.4.2.dev0-py3.10.egg
Processing dependencies for pyradex==0.4.2.dev0
Searching for requests==2.32.5
Best match: requests 2.32.5
Adding requests 2.32.5 to easy-install.pth file

Using /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
Searching for astropy==6.1.2
Best match: astropy 6.1.2
Adding astropy 6.1.2 to easy-install.pth file
Installing fits2bitmap script to /home/aqing/miniconda3/envs/astro_py310/bin
Installing fitscheck script to /home/aqing/miniconda3/envs/astro_py310/bin
Installing fitsdiff script to /home/aqing/miniconda3/envs/astro_py310/bin
Installing fitsheader script to /home/aqing/miniconda3/envs/astro_py310/bin
Installing fitsinfo script to /home/aqing/miniconda3/envs/astro_py310/bin
Installing samp_hub script to /home/aqing/miniconda3/envs/astro_py310/bin
Installing showtable script to /home/aqing/miniconda3/envs/astro_py310/bin
Installing volint script to /home/aqing/miniconda3/envs/astro_py310/bin
Installing wcslint script to /home/aqing/miniconda3/envs/astro_py310/bin

Using /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
Searching for certifi==2025.10.5
Best match: certifi 2025.10.5
Adding certifi 2025.10.5 to easy-install.pth file

Using /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
Searching for urllib3==2.5.0
Best match: urllib3 2.5.0
Adding urllib3 2.5.0 to easy-install.pth file

Using /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
Searching for idna==3.11
Best match: idna 3.11
Adding idna 3.11 to easy-install.pth file

Using /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
Searching for charset-normalizer==3.4.4
Best match: charset-normalizer 3.4.4
Adding charset-normalizer 3.4.4 to easy-install.pth file
Installing normalizer script to /home/aqing/miniconda3/envs/astro_py310/bin

Using /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
Searching for packaging==25.0
Best match: packaging 25.0
Adding packaging 25.0 to easy-install.pth file

Using /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
Searching for pyyaml==6.0.3
Best match: pyyaml 6.0.3
Adding pyyaml 6.0.3 to easy-install.pth file

Using /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
Searching for astropy-iers-data==0.2025.10.20.0.39.8
Best match: astropy-iers-data 0.2025.10.20.0.39.8
Adding astropy-iers-data 0.2025.10.20.0.39.8 to easy-install.pth file

Using /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
Searching for pyerfa==2.0.1.5
Best match: pyerfa 2.0.1.5
Adding pyerfa 2.0.1.5 to easy-install.pth file

Using /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
Searching for numpy==1.26.2
Best match: numpy 1.26.2
Adding numpy 1.26.2 to easy-install.pth file
Installing f2py script to /home/aqing/miniconda3/envs/astro_py310/bin

Using /home/aqing/miniconda3/envs/astro_py310/lib/python3.10/site-packages
Finished processing dependencies for pyradex==0.4.2.dev0
Installation has completed.  Make sure to set your RADEX_DATAPATH variable!
```


