# Installation Hints for RADEX
在仔細地閱讀 Eltha 女士的源碼之後，發現人家用的建模方法不是 `pyradex` 而是 `RADEX` 本人啊哈。  
安裝 `RADEX` 的過程非常之輕鬆寫意，RADEX 本人也超輕量。  
我使用的設備是：
- fiefei: MacOS 15
- Lab MAchine: Ubuntu 20.04
- Server (blackhole): Ubuntu 24.04 (?)

以上都在 20 分鐘內安裝成功，[官網](https://sronpersonalpages.nl/~vdtak/radex/index.shtml)的指示十分精確且夠用，其中需要特別注意的地方應該是要記得**重新設定 `RADEX` 尋找 .dat files 的路徑**。  
還有一些有的沒的可能會忘記的東西，總之這是一個逐個步驟的筆記 :) 

## Step1  
把從[官網](https://sronpersonalpages.nl/~vdtak/radex/index.shtml)的第一步那個連結下載的**壓縮檔** (`radex_public.tar.gz` or `radex_public.tar`)，放在**家目錄** (`/Users/aqing/` or `/home/aqing/`)下面。  
放的位置算是個人習慣，感覺應用程式放在這種層級很河狸。另外的好處是，在設定環境變數的時候，我只知道**家目錄**的關鍵字怎麼寫啊哈。  

## Step2
依照壓縮檔的副檔名選擇解壓縮的方式，就如同[官網](https://sronpersonalpages.nl/~vdtak/radex/index.shtml)所說。  
然後就會自動產生一個叫做 `Radex/` 的資料夾，with sub folders: `src/`, `bin/` and `data/`(<- data/ 以後可能會改成一些順手的名字。)  

## Step3
編譯前的一些個人化調整，總共兩處。  
### Select compiler
RADEX 是用 fortran 寫的，要編譯過後才能用（之類的）。這不需要修改的文件是 `Makefile`。  
可以用 nano 或是 vsCode 打開 `Makefile`，反正文字編輯器都可以，也可以用記事本;)  
```bash
cd ~/Radex/src
nano Makefile
```
裡面會有很多行寫著不同編譯器名稱的Option，把想要選用的選項下面的 **FC** 和 **FFLAGS** 這兩行前面的井字刪掉（取消註解）。  
如果是 Mac 的話，我選的是 **`gfortran`**。總而言之改完的 `Makefile`(部分) 大概會像這樣：  
```fortran
...
...
# Uncomment the FC/FFLAGS combination of your choice
# Option 1:
#FC      = g77
#FFLAGS += -fno-automatic -Wall -O2
# Option 2:
FC = gfortran
FFLAGS += -O2
# Option 3:
#FC      = ifort
#FFLAGS += -O2
# Option 4:
#FC = g95
#FFLAGS += -Wall -O2
# there may be other options of course ...
...
...
```
好像 Mac 會自帶 gfortran 這個編譯器，可以用這個命令確定一下：  
執行後不是寫 `command ont found` 就代表已經安裝。  
```
gfortran --version
```  

### Locate the .dat files
RADEX 在工作的時候需要去另外的資料夾中找分自資料的文件 `.dat`，我們要告訴他應該去哪兒找這些東西。     
如同官網所述，需要修改的文件是 `radex.inc`，用任何文字編輯器打開他。  
```bash
nano Radex/src/radex.inc
```
將裡面的這行 (about ln24) 修改成你電腦上的 **`data/` 所在的位置** (原本應該是一個以作者命名的資料夾...一定是他自己電腦上的位置!)  
```
parameter(radat   = '/Users/aqing/Radex/moledat/')
```
所謂 **`data/` 所在的位置**就是 Step2 解壓縮後，自動在 `~/Radex` 下生成的那個 `data/`。  
這裡我寫的 `/Users/aqing/Radex/moledat/`，而不是 `/Users/aqing/Radex/data/`，是因為我已經有一桶其他的資料夾都叫做 `data`，怕搞混了，所以換一個名字。  
其實要叫什麼都可以，也可以叫 `lana/` :D

## Step4
編譯。  
編譯的指令是 `make`，確定當前處在的環境是 `~/Radex/src`。
```
cd Radex/src
make
```

## Step5
將 `RADEX` 加到環境變數的方法，以防我忘記。畢竟這個步驟和[官網](https://sronpersonalpages.nl/~vdtak/radex/index.shtml)比較不一樣。  
環境變數就是告訴電腦，你要找的東西有可能在哪裡。簡單來說就是建立一個「有可能清單」。  
Open the resource file (並不確定是不是叫這個)
```bash
nano ~/.zshrc   # for MacOS
nano ~/.bashrc  # for Ubuntu
```
This kind of command is for zsh and bash,  
similar command like `set path = ( $path $HOME/Radex/bin )` that provided by [官網](https://sronpersonalpages.nl/~vdtak/radex/index.shtml) is for C shell.  
Since I work on the machine that run zsh or bash, I apply this command.
```bash
export PATH="$PATH:$HOME/Radex/bin"
```
`$HOME` 就是**家目錄**的關鍵字，在 resource file 裡面不太建議用 `~/` 這種縮寫。  
And don't forget to refresh the shell file :)
```bash
source ~/.zshrc
source ~/.bashrc
```

## 旗魚
剩下就是一些測試啊什麼的，總之需要記得的是，呼叫 RADEX 的指令是 `radex`。  
只打這樣的話，會進入互動式的環境，就是 RADEX 問一句你回答一句。
```bash
radex
```
把 RADEX 的問答內容事先寫進 input file (`.inp`) 的話，就這樣寫:
```bash
radex < inputfile.inp
```
.inp 的格式可以參考官網的 [Running Radex](https://sronpersonalpages.nl/~vdtak/radex/index.shtml#top) 這部分。  
如果是寫成 python script 的話，在程式裡面大概會是這個樣子的一段:
```python
import os
# generate an input file
file = open('inputfile.inp', 'w')
file.write('13co.dat\n')
file.write('outfile.out\n')
file.write('100 400\n')
file.write('1.5e2\n')
file.write('1\n')
file.write('H2\n')
file.write('2e15\n')
file.write('2.73\n')
file.write('6e23\n')
file.write('300\n')
file.write('0\n')
file.close()

# run radex
os.system(f'radex < inputfile.inp')
```
詳盡一點可以參考[這裡](../scripts/radex_fluxModel.py)（需要找一下...很多不相關部分啊哈）
