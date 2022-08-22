# COCOA ログチェック

cocoaログから陽性者との接触状況を確認します。  
『陽性者との接触は確認されませんでした』の状況でも、細かい接触履歴が確認できます。  
どれくらいの距離で、どのくらいの時間、回数、陽性者と接触があったかが確認できます。  
日常の行動リスク評価、感染予測に利用できます。  
接触状況(COCOAスコア)は日々更新されています。直近の日では、まだ陽性登録者数は少ないです。

## 参考にさせていただいた情報

<a href="https://cocoalog.jp/?" target="_blank" rel="noopener noreferrer">COCOAログ.jp</a>  
<a href="https://cocoa-log-checker.com/#/beforeUseNote" target="_blank" rel="noopener noreferrer">COCOAログチェッカー2.0 (β)</a>  

## Phase

開発・テスト中  
Androidデータ入手中

## Input

厚生労働省提供アプリCOCOAの陽性登録者との接触結果のログ  
- exposure_data.json

ログ入手方法  

iPhone, Android
- COCOA アプリをオープン
- 陽性登録者との接触結果を確認をクリック
- 情報を保存クリック
- 共有方法を指定（AirDrop, メール等） exposure_data.json を入手する

## Output

### GUI

<img width="1300" alt="GUI" src="https://user-images.githubusercontent.com/19845464/185816885-b3b6426a-f272-41d2-a346-926b18113025.png">

### 接触履歴(Excel Table)  

<img width="751" alt="excel table" src="https://user-images.githubusercontent.com/19845464/185004074-f2d90444-b5b4-488d-89d7-83e4ad070158.png">

### COCOA Charts(Excel)  

<img width="510" alt="execl charts" src="https://user-images.githubusercontent.com/19845464/185004084-45af3735-54d2-47c2-9ec8-6cf37c4175f8.png">

### COCOA Charts(Matplotlib)

<img width="957" alt="cocoa chart" src="https://user-images.githubusercontent.com/19845464/185004089-c5808971-a3bd-4907-871e-f92d598ce891.png">


## 準備

実行に必要なモジュールは以下の通りです。
```text
cocoa.py
cocoaChart.py
cocoaConfig.py
cocoaExcel.py
cocoaGui.py
* requirements.txt
```

pipで必要なライブラリを導入   
python 3.10.6 で開発テストしています。    

```text
pip install -r requirements.txt
```

## 実行方法

コマンド形式
```text
usage: cocoa.py [-h] [-l COCOA_LOGFILE] [--graph]

Cocoa Log Checker

options:
  -h, --help            show this help message and exit
  -l COCOA_LOGFILE, --cocoa_log COCOA_LOGFILE
                        cocoa log file name
              
```
Windowsでは、`cocoa.pyw`をダブルクリックで実行

### 実行例

`-l` は指定せず、GUI環境でファイルの選択も可能です。  
同じフォルダにexposure_data.jsonがある場合は、`--cocoa_log xxxx.json`は省略できます。  

```text
python cocoa.py --cocoa_log /Users/mbam2/Downloads/exposure_data.json
```
