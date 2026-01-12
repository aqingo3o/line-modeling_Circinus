# Installation hint for RADEX
在仔細的閱讀 Eltha 女士的源碼之後，發現人家用的建模方法不是 `pyradex` 而是 `RADEX` 本人。  
安裝 `RADEX` 的過程非常之輕鬆寫意，我使用的設備是
- fiefei: MacOS 15
- Lab MAchine: Ubuntu20.04

兩者都在 20 分鐘內取得了安裝的成功，官網的教學十分的精確且夠用。  
其中需要特別注意的地方應該是記得重新設定 `RADEX` 尋找 .dat files 的路徑。
## Locate the .dat files
需要修改的文件是 radex.inc
```
nano Radex/src/radex.inc
```
將裡面的這行 (about ln24) 修改成你認識的路徑 (原本應該是一個以作者命名的資料夾...一定是他自己電腦上的位置)  
```
parameter(radat   = '/Users/aqing/Radex/moledat/')
```
改了 radex.inc 裡的東西，需要重新編譯才會生效。所以再做一次編譯
```
make
```

## Add RADEX to PATH
這邊另外記錄一下將 `RADEX` 加到環境變數的過程，以防我忘記。畢竟這個步驟是官網比較沒有 cover 到的地方。  
Open the resource file (並不確定是不是叫這個)
```
nano ~/.zshrc   # for MacOS
nano ~/.bashrc  # for Ubuntu
```
This kind of commandd is for zsh and bash,  
similar command like `set path = ( $path $HOME/Radex/bin )` that provided by RADEX官網 is for C shell.  
Since I work on the machine that run zsh or bash, I apply this command.
```
export PATH="$PATH:$HOME/Radex/bin"
```
And don't forget to refresh the shell file :)
```
source ~/.zshrc
source ~/.bashrc
```
