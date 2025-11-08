# 我這麼改源碼的理由
因為從中受到太多幫助了，所以覺得一定要記一下  
還有我搞這些花了一個禮拜吧，累死  
希望大家都有要不要經過這個痛苦的階段的選擇權


## install_radex.py
會遇到第一個錯：... fail to resolve ‘personal.sron.nl’ 之類的，這是因為 radex 的下載點網址好像改過  
install_radex.py 裡面大概30行那邊，有一個網址，那個要改成現在(2025.10)能用的   
you can find and use pyradex_installation_patch/install_radex.py in my github or find the usable url through browser(“radex install” in google) and 去radex官網找，搞不好他網址又改過哩？)  
恭喜，這個是所有補丁中我最有自信的，因偉這是 python:))) 請安心使用

## radex.inc
這時候應該會出現很多很多行長得像這個的  
```
Line #49 in radex.inc:" parameter(hplanck = 6.6260963d-27) " get_parameters: got "eval() arg 1 must be a string, bytes or code object" on 4
以及一些 red Error ‘got "eval() arg 1 must be...’
```
is because in radex.inc, it used to use ‘d’ 代表次方  
但現在的 python or something else that work on translating 只認e as the notation of power   
這大體來說不影響，但因為超多行超煩，所以可以使用 patch 中的 radex.inc   
將原本的 ~/ppyradex_arm/pyradex/Radex/src/radex.inc 換成補丁中的 radex.inc 就可以解決這個問題   
你當然可以自己修改radex.inc，就是把裡面能找到的代表指數的d都換成ｅ   
不知道會又什麼後果，但改寫了之後世界安靜多了

## sub_global_variables.f90 && sub_trivials.f90
紅色的error 是需要處理的！ 應該會說像是 
```
sub_global_variables.f90:41:54:

41 | double precision, parameter :: phy_NaN = transfer(X'FFFFFFFFFFFFFFFF', 0D0) | 1 Error: Hexadecimal constant at (1) uses nonstandard X instead of Z [see '-fallow-invalid-boz'] make: *** [sub_global_variables.o] Error 1 gfortran -O3 -fPIC -c sub_global_variables.f90
```
這樣的東西 就是說應該要用Z而不是用X，可以直接進到~/ppyradex_arm/pyradex/myradex/sub_global_variables.f90中對應的行數(for example, here is line 41) 把Z改成X 但先不要急，因為會發現改完這個後還有另一個也出現在 /sub_global_variables.f90 中的問題 我一起做了補丁，如果對於細節不感興趣的話請直接跳到下下一步驟

承上，解決Z,X 之後執行 python3 setup.py install_myradex install 會出現新的問題，像是 Error: BOZ literal constant at (1) cannot be an actual argument to 'transfer' 大意是 BOZ(二進位八進位十六進位？)不能放在 transsfer() 中

看這個error message 發現他是試圖要定義一個 NAN 用一些新語法改寫就可以拯救這些問題 找到報錯的那行程式（文件名稱和行數都會在error message 中顯示，應該都在 myradex/之下） 先定義一個變數叫NaN_bits，型態是整數(-225.... is IEEE nan pattern) integer(8), parameter :: NaN_bits = -2251799813685248_8 然後transfer 中傳入剛定義的整數變數，取代原本的BOZ double precision, parameter :: phy_NaN = transfer(NaN_bits, 0D0)

其實我也是做得膽戰心驚的，除了 sub_global_variables.f90 sub_trivials.f90也會有類似的問題 我把我改過的這倆.f90 都放在補丁中了 可以直接斤他們取代原本的檔案使用

## linalg_nleg1.f
```
1513 | CALL XERBLA('DGER ',INFO) | 1 Warning: Character length of actual argument shorter than of dummy argument 'srname' (5/6) at (1)
```
想讚嘆 fortran 真嚴格，第1513行少一個空格，無傷大雅但我依然附上了相應的補丁，可以直接使用

## opkda1.f
這邊除了很多警告之外，在 feifei 上弄的時候還給我報一個巨大解不了錯  
真沒招了才去大電腦裝的（啊其實最後建模肯定不會用筆電）  
但就是說減少一點警告佔屏也是爽的  
這真的超多 我他媽改到直接睡在機房，希望能幫到大家啦哈哈  
簡單來說就是 DO 和什麼東西回圈的寫法在語法更新中出現的問題  
具體來說我還要回去翻一下某些紙質的東西，但是在這邊先暫個做因為我好想把這個樹枝推上去  
```
opkda1.f:123:72:

123 | 110 PC(I) = PC(I-1) + FNQM1*PC(I) | 1 Warning: Fortran 2018 deleted feature: DO termination statement which is not END DO or CONTINUE with label 110 at (1)
```
