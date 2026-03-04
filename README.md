# get-chrome-driver

Google Chrome のバージョンに合わせた ChromeDriver を自動取得・管理する Python ツール。

## 特徴
- インストールされている Chrome バージョンの自動検知
- Chrome for Testing (CfT) API を使用した最新ドライバーの取得
- Selenium による動作確認バリデーション機能
- PyInstaller による単一実行ファイル形式へのビルド対応

## セットアップ

このプロジェクトは Python 3.8 以上を対象としています。

```bash
# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate  # Windows の場合は venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

## 使い方

```bash
# ドライバーのインストールと動作確認を実行
python main.py

# Chrome バージョンの確認のみ
python main.py --check

# 動作確認（Selenium）をスキップ
python main.py --no-validate
```

## ビルド手順 (EXE/バイナリ作成)

PyInstaller を使用して、依存関係を含んだ単体実行ファイルを作成できます。

```bash
pip install pyinstaller
pyinstaller --onefile main.py --name get-chrome-driver
```

