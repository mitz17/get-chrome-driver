import argparse
import sys
from get_chrome_driver.core import GetChromeDriver

def main():
    parser = argparse.ArgumentParser(description="get-chrome-driver: ChromeDriver を自動取得・管理するツール")
    parser.add_argument("--check", action="store_true", help="現在インストールされている Chrome のバージョンを表示する")
    parser.add_argument("--no-validate", action="store_true", help="インストール後の動作確認（Selenium）をスキップする")
    
    args = parser.parse_args()
    
    installer = GetChromeDriver()
    
    if args.check:
        from get_chrome_driver.utils import get_chrome_version
        v = get_chrome_version()
        print(f"Detected Chrome Version: {v}")
        sys.exit(0)
    
    # ドライバーのインストール
    driver_path = installer.install()
    
    if driver_path:
        # 動作検証
        if not args.no_validate:
            success = installer.validate(driver_path)
            if success:
                print("ChromeDriver は正常に動作しています。")
            else:
                print("ChromeDriver の動作確認に失敗しました。")
                sys.exit(1)
        else:
            print("動作確認をスキップしました。")
        
        print(f"Driver Path: {driver_path}")
    else:
        print("インストールに失敗しました。")
        sys.exit(1)

if __name__ == "__main__":
    main()
