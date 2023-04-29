# mini_theater_scheduler
Webスクレイピングをしてミニシアターのスケジュールを集めるプログラム

## ファイル構成

### 設定ファイル
- `theater_settings.json`
- `settings.py`

### プログラム
#### メインのプログラム
- `scheduler.py`
#### 各映画館のクラスの定義
- `theaters.py`
#### 映画館クラス、プログラムクラス、映画クラスの定義
- `theater_class.py`
#### 映画館クラスのデータを扱うクラスの定義
- `data_manager.py`
#### その他関数の定義
- `lib.py`

### 映画館データ
- `theater_data/theater_data.json`　(`scheduler.py`を実行すると作成される)

### スケジュールデータ
= `schedule/schedule.csv`　(`scheduler.py`を実行すると作成される)

## 使用方法
`scheduler.py --help`を実行して確認できます。