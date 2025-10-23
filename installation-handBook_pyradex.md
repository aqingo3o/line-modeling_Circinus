# pyradex Installation handbook for Linux machine (Ubuntu)
I hope this could help you deal with the OLD language tool that widly use in radical trandfer modeling.  
I've try to install pyrdex on my laptop(macOS 15) but I 悲慘地 fail on both arm-64 and x86-64(via Rosetta) arch because of some compilition issue of `myradex`:(  
Then I turn to Linux machine and I get what I want, so 我將要分享我安裝的步驟以及中間用到的補丁，希望能幫到大家  

All the 功德屬於寫出 radex, 寫出 wapper, 在 stackOverflow 上幫助我的 brillirant brain and GenAI.  
(怎麼標注別人的 repo 啊)

很大的參考了 k大「Installation procedure for the f2py-wrapped version」的部分  

## Environment info
- **OS**: Ubuntu20.04
- **gfortran**: GNU Fortran 9.4.0 (Ubuntu 9.4.0-1ubuntu1~20.04.2)
- **venv**: miniconda
- **python** 3.10
- **astropy** 6.1.2
- **numpy** 1.26.2

## Patches
應該有在塗個資料夾中釋出  
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

依照指示跑跑這個

python3 setup.py install_radex install_myradex install (python or pyhton3 depend on your computer setting) 先執行看看，但應該會遇到第一個錯：... fail to resolve ‘personal.sron.nl’ 之類的 這是因為 radex 的下載點網址好像改過 install_radex.py 裡面大概30行那邊，有一個網址，那個要改成現在(2025.10)能用的 you can find and use pyradex_installation_patch/install_radex.py in my github or find the usable url through browser(“radex install” in google and 去radex官網找，搞不好他網址又改過哩？) 恭喜，這個是所有補丁中我最有自信的，因偉這是 python:))) 請安心使用

換了新的install_radex.py(或您很幸運地沒遇到上個問題) do it again python3 setup.py install_radex install_myradex install than you may come into tons of message爆破你的terminal like Found shared object files=[] for RADEX.  (if that is a blank, it means radex didn't install successfully) Found shared object files=[] for RADEX.  (if that is a blank, it means fjdu's myradex didn't install successfully) … eval() arg1 must be a string, or something like that seems like nothing success hahapy that’s because some version issue make sure the python version and numpy version ur using is not too new(yes, TOO NEW TO WORK)

如果版本什麼的都確定之後， 再進行一次 會出現一些作者給的提示（這是在尋寶嗎） 或是你在之前的步驟可能就看過這些抱歉，我有點忘記我當時的試錯順序了 Try running the command manually:

cd Radex/src/ f2py -c -m radex --f77flags="-fPIC -fno-automatic" --fcompiler=gfortran -I/Users/aqing/pyradex/Radex/src *.f cd - mv Radex/src/*so pyradex/radex/

See also Github issues 39 and 40

嘗試這個 （請記得將（Users/aqing/pyradex_arm）那串改成你自己的path, 或是作者的提示應該會生成符合你正使用路徑的指令，總之就是不要直接拷我的這段，這只是一個演示） cd Radex/src/ f2py -c -m radex --f77flags="-fPIC -fno-automatic" --fcompiler=gfortran -I/Users/aqing/pyradex_arm/pyradex/Radex/src *.f 會獲得一個看起來比較熟悉的東西 ModuleNotFoundError: No module named 'distutils.msvccompiler' f2py 開頭那行以我的有線知識看起來應該是手動編譯的指令, whatever. I’ve do some searching and I think the problem is because distutils 這個東西剛好在2025.10 從<3.11的pyhon版本中移除了（while python3.12+根本就沒有這種東西）

經過大概一萬年的搜尋，在stack overFlow上找到解方了 不得不承認在 GenAI盛行的年代，把error message 直接貼在 google 上 also work. thank overFlow 老哥 需要特定版本的 setuptools 代替 distutlis 的功能，透過 conda 下載 conda install “setuptools <65” 然後接著再試一次 f2py -c -m radex --f77flags="-fPIC -fno-automatic" --fcompiler=gfortran -I/Users/aqing/pyradex_arm/pyradex/Radex/src *.f 做完著個之後，應該會出現 .so file like ‘radex.cpython-310-darwin.so’這樣的，就是編譯完成的東西

不確定在下載完 setuptools 之後直接做 python3 setup.py install_radex install_myradex install 會不會達到一樣的結果，總之，大家這邊都要再做一次這個喔 python3 setup.py install_radex install_myradex install

這時候應該會出現很多很多行長得像這個的 Line #49 in radex.inc:" parameter(hplanck = 6.6260963d-27) " get_parameters: got "eval() arg 1 must be a string, bytes or code object" on 4 以及一些 red Error ‘got "eval() arg 1 must be’ is because in radex.inc, it used to use ‘d’ 代表次方 但現在的 python or something else that work on translating 只認e as the notation of power 這大體來說不影響，但因為超多行超煩，所以可以使用 patch 中的 radex.inc 將原本的 ~/ppyradex_arm/pyradex/Radex/src/radex.inc 換成補丁中的 radex.inc 就可以解決這個問題 你當然可以自己修改radex.inc，就是把裡面能找到的代表指數的d都換成ｅ 不知道會又什麼後果，但改寫了之後世界安靜多了 執行一次 python3 setup.py install_myradex install
檢驗成果
注意，這邊不用再下 install_radex in the command 了，不然會把redex.inc覆寫掉

紅色的error 是需要處理的！ 應該會說像是 sub_global_variables.f90:41:54:

41 | double precision, parameter :: phy_NaN = transfer(X'FFFFFFFFFFFFFFFF', 0D0) | 1 Error: Hexadecimal constant at (1) uses nonstandard X instead of Z [see '-fallow-invalid-boz'] make: *** [sub_global_variables.o] Error 1 gfortran -O3 -fPIC -c sub_global_variables.f90 這樣的東西 就是說應該要用Z而不是用X，可以直接進到~/ppyradex_arm/pyradex/myradex/sub_global_variables.f90中對應的行數(for example, here is line 41) 把Z改成X 但先不要急，因為會發現改完這個後還有另一個也出現在 /sub_global_variables.f90 中的問題 我一起做了補丁，如果對於細節不感興趣的話請直接跳到下下一步驟

承上，解決Z,X 之後執行 python3 setup.py install_myradex install 會出現新的問題，像是 Error: BOZ literal constant at (1) cannot be an actual argument to 'transfer' 大意是 BOZ(二進位八進位十六進位？)不能放在 transsfer() 中

看這個error message 發現他是試圖要定義一個 NAN 用一些新語法改寫就可以拯救這些問題 找到報錯的那行程式（文件名稱和行數都會在error message 中顯示，應該都在 myradex/之下） 先定義一個變數叫NaN_bits，型態是整數(-225.... is IEEE nan pattern) integer(8), parameter :: NaN_bits = -2251799813685248_8 然後transfer 中傳入剛定義的整數變數，取代原本的BOZ double precision, parameter :: phy_NaN = transfer(NaN_bits, 0D0)

其實我也是做得膽戰心驚的，除了 sub_global_variables.f90 sub_trivials.f90也會有類似的問題 我把我改過的這倆.f90 都放在補丁中了 可以直接斤他們取代原本的檔案使用
