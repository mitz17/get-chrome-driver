import os
import zipfile
import requests
import io
import shutil
import subprocess
import re
from pathlib import Path
from .utils import get_chrome_version
from .api import get_driver_download_url, get_platform_string

class GetChromeDriver:
    def __init__(self):
        self.save_dir = Path.home() / ".get-chrome-driver"
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.driver_name = "chromedriver.exe" if os.name == "nt" else "chromedriver"
        self.driver_path = self.save_dir / self.driver_name

    def install(self):
        """Chrome バージョンを検出し、最適なドライバーをインストールする"""
        version = get_chrome_version()
        if not version:
            print("Chrome がインストールされていないか、バージョンを特定できませんでした。")
            return None
        
        print(f"検出された Chrome バージョン: {version}")

        existing_version = self._get_installed_driver_version()
        target_major = version.split('.')[0]
        if existing_version:
            existing_major = existing_version.split('.')[0]
            if existing_major == target_major and self.driver_path.exists():
                print(f"既存の ChromeDriver (バージョン {existing_version}) は互換性があります。")
                return str(self.driver_path)
            else:
                print(f"ChromeDriver を更新します: 現在 {existing_version} -> 目標メジャー {target_major}")
        
        platform_str = get_platform_string()
        if not platform_str:
            print("対応していないプラットフォームです。")
            return None
        
        url = get_driver_download_url(version, platform_str)
        if not url:
            print(f"バージョン {version} に対応する ChromeDriver が見つかりませんでした。")
            return None
        
        print(f"ダウンロード中: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                driver_member = None
                for member in z.infolist():
                    member_path = os.path.normpath(member.filename)
                    if os.path.isabs(member_path) or member_path.startswith("..") or member_path.startswith("/") or member_path.startswith("\\"):
                        print(f"警告: 不正なパスを含むファイルをスキップしました: {member.filename}")
                        continue
                    if os.path.basename(member_path) == self.driver_name:
                        driver_member = member
                        break

                if not driver_member:
                    print("アーカイブ内に ChromeDriver 実行ファイルが見つかりませんでした。")
                    return None

                with z.open(driver_member) as source, open(self.driver_path, "wb") as target:
                    shutil.copyfileobj(source, target)

            # 実行権限の付与 (Linux/macOS)
            if os.name != "nt":
                self.driver_path.chmod(0o755)

            print(f"インストール完了: {self.driver_path}")
            return str(self.driver_path)

        except Exception as e:
            print(f"ダウンロードまたは展開中にエラーが発生しました: {e}")
            return None

    def validate(self, driver_path):
        """Selenium を使って動作確認を行う"""
        if not driver_path:
            return False
        
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        print("動作確認中 (Selenium)...")
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            driver.get("https://google.com")
            title = driver.title
            print(f"接続成功: ページタイトル - {title}")
            driver.quit()
            return True
        except Exception as e:
            print(f"動作確認中にエラーが発生しました: {e}")
            return False

    def _get_installed_driver_version(self):
        """保存済み ChromeDriver のバージョンを取得する"""
        if not self.driver_path.exists():
            return None

        try:
            output = subprocess.check_output([str(self.driver_path), "--version"], stderr=subprocess.DEVNULL).decode().strip()
            match = re.search(r"ChromeDriver ([\d\.]+)", output)
            if match:
                return match.group(1)
        except Exception:
            return None
        return None
