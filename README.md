# COCOA ログチェック

cocoaログをExcelやグラフで表示して、接触状況を確認します。

## Phase

開発・テスト中

## 参考にさせていただいた情報

<a href="https://cocoalog.jp/?" target="_blank" rel="noopener noreferrer">COCOAログ.jp</a>  
<a href="https://cocoa-log-checker.com/#/beforeUseNote" target="_blank" rel="noopener noreferrer">COCOAログチェッカー2.0 (β)</a>  


## 準備

python 3.10.6 で開発テストしました。    
pipで必要なライブラリを導入  

```text
pip install -r requirements.txt
```

## 実行方法

```text
usage: cocoa.py [-h] [-l COCOA_LOGFILE] [--graph]

Cocoa Log Checker

options:
  -h, --help            show this help message and exit
  -l COCOA_LOGFILE, --cocoa_log COCOA_LOGFILE
                        cocoa log file name
  --graph               just show COCOA charts. Excel will not be created.
              
```
### example

```text
python cocoa.py --cocoa_log /Users/mbam2/Downloads/exposure_data.json
```

### COCOAログの入手方法

iPhoneの場合
- COCOA アプリをオープン
- 情報を保存クリック
- AirDrop, Mail等で exposure_data.json を入手する
  