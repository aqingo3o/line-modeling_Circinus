# pyradex Installation handbook for arm-64 arch
I hope this could help you deal with the OLD language tool that widly use in radical trandfer modeling.  
I have no idea why x86 is (maybe) better than arm arch, I would prefer working on x86 because it's more similar to Linux.  
But I have already done this on arm, just share it if you want pyradex run on Apple Silicon chips.  

All the 功德屬於寫出 radex, 寫出 wapper, 在 stackOverflow 上幫助我的 brillirant brain and GenAI.  
(怎麼標注別人的 repo 啊)


很大的參考了「Installation procedure for the f2py-wrapped version」的部分

基於一些對使用人口的觀察，建議在 x86 arch 下進行您的天文學工作，  
但我因為一開始沒意識到編譯器是 arm 的，於是做了以下工作，  
所以還是丟上來供大家參考，搞不好有人很完全的馴服了arm arch 呢  

相信大家都已經有了arm 的 homebrew, 沒有的話裝一個，總之可以下載東西的工具隨便什麼應該都可以  
所以直接用這個東東  
gfortran, g++及各種編譯器都打包在 gcc裡面了，所以就 install 這個  
```brew install gcc```

進入一個虛擬環境，是**conda**的話最好，但其實你方便用應該都行  
python=3.10  
numpy=1.26.2  
astropy=(看人家的github)  
因為 raedx 是一個 fortran 湯底的東西，所以numpy的版本很重要  
再新一點的（numpy2.0）好像不行，總之我用**1.26**成功了，供大家參考  

確認真裝上了  
```which gfortran```  
```which f2py```
(f2py 是在裝了 numpy後會出現的樣子)  
有顯示路徑就是有裝了  

接下來的步驟絕對標準應該參考 k 的github  
這邊只是提供一些經驗之談，大家斟酌相信（因為我只是一個沒畢業的瓠瓜）  
接下來要 clone 別人的repo，所以先確定有git工具  
```git —version```   
好像 mac會自帶，但就是確認一下，出現版本好就是有裝了  
```git clone —recursive http://……… ```  
完全就是從k的github複製的，具體網址應該參考他，搞不好網址會變（之後馬上就要遇到這個問題辣！）

cd 進去那個資料夾，要到裡面有 setup.py, install_radex.py這些的那層

接下來請查收我為您打包的patch
我的建議是 出了問題再用！也就是，先嘗試執行k提供的安裝步驟，出了問題再使用我的補丁  
（雖然改的都是一些語法之類的，但因為我對 fortran 完全的新手，不能確定我一定做了最好的操作  
做的所有事情絕大部分都是在 stack overFlow, K的issue, GenAI等多方參考下引用的，特此警告）  
改過的地方會有「modi by qing」的標註  

```python3 setup.py install_radex install_myradex install```
(python or pyhton3 depend on your computer setting)
先執行看看，但應該會遇到第一個錯：... fail to resolve ‘personal.sron.nl’ 之類的
這是因為 radex 的下載點網址好像改過
install_radex.py 裡面大概30行那邊，有一個網址，那個要改成現在(2025.10)能用的
you can find and use pyradex_installation_patch/install_radex.py in my github or find the usable url through browser(“radex install” in google and 去radex官網找，搞不好他網址又改過哩？)
恭喜，這個是所有補丁中我最有自信的，因偉這是 python:))) 請安心使用

換了新的install_radex.py(或您很幸運地沒遇到上個問題)
do it again 
python3 setup.py install_radex install_myradex install
than you may come into tons of message爆破你的terminal like
Found shared object files=[] for RADEX.  (if that is a blank, it means radex didn't install successfully) 
Found shared object files=[] for RADEX.  (if that is a blank, it means fjdu's myradex didn't install successfully)
…
eval() arg1 must be a string, or something like that
seems like nothing success hahapy
that’s because some version issue
make sure the python version and numpy version ur using is not too new(yes, TOO NEW TO WORK)

如果版本什麼的都確定之後，
再進行一次
會出現一些作者給的提示（這是在尋寶嗎）
或是你在之前的步驟可能就看過這些抱歉，我有點忘記我當時的試錯順序了
Try running the command manually:

cd Radex/src/
f2py -c -m radex --f77flags="-fPIC -fno-automatic" --fcompiler=gfortran  -I/Users/aqing/pyradex/Radex/src  *.f
cd -
mv Radex/src/*so pyradex/radex/

See also Github issues 39 and 40

嘗試這個 （請記得將（Users/aqing/pyradex_arm）那串改成你自己的path, 或是作者的提示應該會生成符合你正使用路徑的指令，總之就是不要直接拷我的這段，這只是一個演示）
cd Radex/src/
f2py -c -m radex --f77flags="-fPIC -fno-automatic" --fcompiler=gfortran  -I/Users/aqing/pyradex_arm/pyradex/Radex/src  *.f
會獲得一個看起來比較熟悉的東西
ModuleNotFoundError: No module named 'distutils.msvccompiler'
f2py 開頭那行以我的有線知識看起來應該是手動編譯的指令, whatever.
I’ve do some searching and I think the problem is because distutils 這個東西剛好在2025.10 從<3.11的pyhon版本中移除了（while python3.12+根本就沒有這種東西）

經過大概一萬年的搜尋，在stack overFlow上找到解方了
不得不承認在 GenAI盛行的年代，把error message 直接貼在 google 上 also work. thank overFlow 老哥
需要特定版本的 setuptools 代替 distutlis 的功能，透過 conda 下載
conda install “setuptools <65”
然後接著再試一次
f2py -c -m radex --f77flags="-fPIC -fno-automatic" --fcompiler=gfortran  -I/Users/aqing/pyradex_arm/pyradex/Radex/src  *.f
做完著個之後，應該會出現

不確定在下載完 setuptools 之後直接做
python3 setup.py install_radex install_myradex install
會不會達到一樣的結果，總之，大家這邊都要再做一次這個喔
python3 setup.py install_radex install_myradex install

這時候應該會出現很多很多行長得像這個的
Line #49 in radex.inc:"      parameter(hplanck = 6.6260963d-27)   "
	get_parameters: got "eval() arg 1 must be a string, bytes or code object" on 4
以及一些 red Error
‘got "eval() arg 1 must be’ is because in radex.inc, it used to use ‘d’ 代表次方
但現在的 python or something else that work on translating 只認e as the notation of power
這大體來說不影響，但因為超多行超煩，所以可以使用 patch 中的 radex.inc
將原本的 ~/ppyradex_arm/pyradex/Radex/src/radex.inc 換成補丁中的 radex.inc
就可以解決這個問題 你當然可以自己修改radex.inc，就是把裡面能找到的代表指數的d都換成ｅ
不知道會又什麼後果，但改寫了之後世界安靜多了

紅色的error 是需要處理的！
應該會說像是


 

