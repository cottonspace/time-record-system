[English](README.md) | [日本語](README-ja.md)

# T-RECS
![logo](static/worktime/logo.svg)

**T-RECS**: **T**ime **REC**ord **S**ystem

Django で記述された Web ベースのシンプルな勤怠管理（タイムカード）システムです。現在は日本語と日本の祝日にのみ対応しています。

## 機能
ユーザは出勤と退勤の打刻をスマートフォンや PC からおこなえます。管理者はユーザの時間記録を確認できます。

<img src="static/worktime/capture_record.png" width="50%">

## 使用方法

### 打刻
- "出勤" または "退勤" のボタンをクリックします。
- メッセージが表示されたら時刻の記録が正常に完了したことを示します。
- 同じ日の複数回クリックした場合、就業時間は最初のクリックから最後のクリックまでで計算されます。

### 勤務表
- 月単位で勤務表を確認できます。
- 管理者はすべてのユーザの勤務表を確認できます。

### パスワード変更
- ユーザは自分自身のパスワードを変更できます。

## デモ
- [https://cottonspace.pythonanywhere.com/worktime/login/](https://cottonspace.pythonanywhere.com/worktime/login/) にアクセスします。
- 位置情報の取得はデモのため OFF にしています。
- デモでは以下のユーザが使用可能です。
- デモユーザのパスワードは 1 日に 1 回、以下のデフォルト値に初期化されます。

| ID  | パスワード | 役割 |
| ------------- | ------------- | ------------- |
| demo1  | demodemo1  | 一般ユーザ |
| demo2  | demodemo2  | 一般ユーザ |
| manage  | manemane1  | 管理者 |

## インストール方法

### ダウンロードと設定の変更
- [リポジトリ](https://github.com/cottonspace/time-record-system) からアプリケーションのソースコードを Clone またはダウンロードします。
- local_settings_template.txt を、同じディレクトリに local_settings.py の名前でコピーします。
- コピーして作成した local_settings.py の % から % の部分を、ご自身の環境にあわせて設定します。
- [T-RECS 簡易設定ツール](https://cottonspace.github.io/tools/time-record-system-local-settings.html) を利用すると簡単に local_settings.py ファイルを作成できます。

### ライブラリのインストール
- 以下のコマンドを実行し、必要なライブラリをインストールします。
```
pip install -r requirements.txt
```
- MySQL を使用する場合は、追加で以下のコマンドを実行します。
```
pip install mysqlclient
```
- PostgreSQL を使用する場合は、追加で以下のコマンドを実行します。
```
pip install psycopg2-binary
```

### アプリケーションの初期化
- 以下のコマンドを実行し、データベースを準備します。
```
python manage.py migrate
```
- 以下のコマンドでスーパーユーザを作成します。
```
python manage.py createsuperuser
```
- 以下のコマンドでマスタデータを初期化します。ここではデフォルトの設定が作成されるので、あとの作業で、適切な就業時間のルールに編集します。
```
python manage.py loaddata worktime/fixtures/standard-work-pattern.json
python manage.py loaddata worktime/fixtures/time-off-pattern.json
```
- サーバを起動します。例えば Django の機能で起動する場合は以下のコマンドを実行します。
```
python manage.py runserver
```

### 初期設定
- Web ブラウザでスーパーユーザでログインして管理画面にアクセスします。
- 最初に "勤務パターン" 画面で曜日別の就業時刻のパターンを設定します。この設定は、アプリケーションの運用を開始する前に、必ず最初におこなってください。
- 以下のコマンドで曜日別の就業時間を初期化し、営業日カレンダを作成します。
```
python manage.py create_calendar
```
- 打刻をおこなうユーザを管理画面から適宜ユーザ追加で登録します。

### 自動タスクへのコマンド追加
- crontab などの定期タスクで以下のコマンドが毎月 1 回以上実行されるように登録してください。
```
python manage.py create_calendar
```

### 営業日カレンダの削除
- `create_calendar` で作成した営業日カレンダの設定をやりなおす場合などは、以下のコマンドで指定した年月とそれ以降の営業日カレンダを削除することができます。
```
python manage.py delete_calendar 年 月
```
- 不足している月の営業日カレンダは `create_calendar` を実行することで再度作成されます。
- 営業日カレンダは月単位で管理されますので、月内の特定の日のみ削除することは出来ません。

### ユーザの一括登録
- ユーザの登録はシステム管理の画面からも行えますが、`create_users` で複数ユーザを一括で登録することができます。
```
python manage.py create_users ファイル
```
- ファイルは CSV 形式で UTF-8 で作成してください。
- 項目の並びは ID,パスワード,姓,名 の順です。

### ユーザの無効化
- 退職などでユーザを無効化する場合は、管理者画面でユーザの "有効" のチェックを外すことを推奨します。削除してしまうと、そのユーザの過去の出勤履歴を参照できなくなります。
- "有効" のチェックを外したユーザは、一覧表示の際に "氏名" のあとに * 記号がついて表示されます。

## ライセンス
[MIT](LICENSE)
