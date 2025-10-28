# pyradex Installation handbook for x86-64 arch
I hope this could help you deal with the OLD language tool that widly use in radical trandfer modeling.  

請小心使用，因為我自己也裝得亂七八糟的。  
但至少近年，我做的補丁應該會有一定的作用（在進行安裝的環節可以有效減少報錯...僅此而已）



不要把東西都放在實驗室因為我常常他的忘記帶鑰匙
因為這是在裝過 arm 之後做的操作，一些人性化的廢話請見handBook_arm64


安裝x86 版的 homebrew:
Rosetta開著， unmae -m 確認 去網上搜尋homebrew install 的那串，貼到終端然後就讓他跑

裝好就確定一下
痾應該要先設路徑
原本arm 的brew是export PATH="/opt/homebrew/bin:$PATH"
現在要設成這個，把這個寫到 .zshrc
export PATH="/usr/local/bin:/usr/local/sbin:$PATH"
記得 source ~/.zshrc

然後就可以裝 x86 的編譯器了
which brew 確認一下真的是x86的brew
gfortran, g++及各種編譯器都打幫在 gcc裡面了，所以就 install 這個
brew install gcc
brew install gcc@11
各種版本的 gcc 被鼓勵（？）同時存在
不知道11版有沒有比較好用但我就會用這個哈哈

file $(which gfortran)
file $(which gfortran-11)看看是不是真的裝了x86的編譯器

打開虛擬環境
conda activate astro_py310
安裝相依的python 套件
astropy, numpy 應該這兩最要緊
還有
conda install “setuptools <65”
為麼要這麼作
的原因這邊也打一份吧！（先見之明） 
確定有git
git —version

cd 到目標資料夾
把repo clone下來
cd ~/pyradex_x86
git clone --recursive https://github.com/keflavich/pyradex.git

cd 進到 pyradex
cd ~/pyradex_x86/pyradex

執行命令
python3 setup.py install_radex install_myradex install

網址錯了 直接用補丁 install_radex.py
（也許可以補一下補丁的建議及用法）

再一次
python3 setup.py install_radex install_myradex install
>something
Line #49 in radex.inc:"      parameter(hplanck = 6.6260963d-27)   "
	get_parameters: got "eval() arg 1 must be a string, bytes or code object" on 4

>Error
sub_global_variables.f90:41:54:

   41 |   double precision, parameter :: phy_NaN = transfer(X'FFFFFFFFFFFFFFFF', 0D0)
      |                                                      1
Error: Hexadecimal constant at (1) uses nonstandard X instead of Z [see '-fallow-invalid-boz']
make: *** [sub_global_variables.o] Error 1
gfortran -O3 -fPIC -c sub_global_variables.f90
先解決error!!
這種X, Z問題，詳見handBook_arm64第n點
直接引入補丁sub_global_variables.f90 and sub_trivials.f90 解決
真的相信我 之後麻煩的事情他媽的多著呢

執行
python3 setup.py install_radex install_myradex install
這邊開始就和arm的不一樣了！
除了
>Line #49 in radex.inc:"      parameter(hplanck = 6.6260963d-27)   "
	get_parameters: got "eval() arg 1 must be a string, bytes or code object" on 4
這種
還會出現新的warning and error，請見第n步

** 當發現執行python3 開頭的那個指令，output的最開始那兩行中
Found shared object files=['radex.so'] for RADEX.  (if that is a blank, it means radex didn't install successfully)
Found shared object files=[] for RADEX.  (if that is a blank, it means fjdu's myradex didn't install successfully)
已經是 radex install successfully ([] is not blank) 的時候，就可以用 radex.inc 的補丁了
因為用了之後，下次python3... 後就不會接 install_radex（避免覆寫.inc）
所以要等 radex 裝好之後才使用這個補丁

執行
python3 setup.py install_myradex install
記得移除install_radex
發現乾淨了一點
>新的warning:
linalg_nleq1.f:1513:21:

 1513 |          CALL XERBLA('DGER ',INFO)
      |                     1
Warning: Character length of actual argument shorter than of dummy argument 'srname' (5/6) at (1)
這個就是我想讚嘆 fortran 真嚴格，第1513航少一個空格，無傷大雅但我依然附上了相應的補丁，可以直接使用

opkda1.f:123:72:

  123 |  110      PC(I) = PC(I-1) + FNQM1*PC(I)
      |                                                                        1
Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 110 at (1)
opkda1.f 裡出老多錯了，麻煩鼠，等下再修理你
>新的error:
opkda1.f:1255:72:

 1255 |      1   RWORK(LACOR), IA, JA, RWORK(LWM), RWORK(LWM), IPFLAG, F, JAC)
      |                                                                        1
Error: Type mismatch in argument 'iwk' at (1); passed REAL(8) to INTEGER(4)
opkda1.f:9499:72:

 9499 |      2   RES, JAC, ADDA)
      |                                                                        1
Error: Type mismatch in argument 'iwk' at (1); passed REAL(8) to INTEGER(4)
幹啊我真的沒招了
** 雖然在output 的最後說了 Installation has completed.
但output 最開始的那兩行，fjdu's myradex 那邊看起來就是東西沒裝好，屁眼
所以要續努力desu

Type mismatch in argument 'iwk' at (1); passed REAL(8) to INTEGER(4)
這個問題其實他描述得很清楚，就是變數的東東設錯還是怎樣
但因為我已經被python慣壞了，所以我不能理解or猜出哪些東西應該用什麼變數
還有這是我生命中首次接觸 fortran 的第三天，我真的不知道怎麼改
所以這個補丁（如果有的話）請小心使用，或是請教善於 fortran 的人類
好吧，依然進到 opkda1.f 去看看哩
