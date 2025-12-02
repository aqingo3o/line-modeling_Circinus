# Installation hint for RADEX
在仔細的閱讀 Eltha 女士的源碼之後，發現人家用的建模方法不是 `pyradex` 而是 `RADEX` 本人。  
安裝 `RADEX` 的過程非常之輕鬆寫意，我使用的設備是
- fiefei: MacOS 15
- Lab MAchine: Ubuntu20.04

兩者都在 20 分鐘內取得了安裝的成功，官網的教學十分的精確且夠用。  
所以這邊只是要記錄一下將 `RADEX` 加到環境變數的過程，以防我忘記  
畢竟這個步驟是官網比較沒有 cover 到的地方。

## Command
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


