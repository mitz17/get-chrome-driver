import subprocess
import os
import platform
import re

def get_chrome_version():
    """インストールされている Google Chrome のバージョンを取得する"""
    system = platform.system()
    version = None

    try:
        if system == "Windows":
            # Windowsの場合、レジストリまたはWMICから取得を試みる
            paths = [
                r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
                r'reg query "HKEY_LOCAL_MACHINE\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome" /v version'
            ]
            import locale
            encoding = locale.getpreferredencoding()
            for cmd in paths:
                try:
                    raw_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
                    try:
                        output = raw_output.decode(encoding)
                    except UnicodeDecodeError:
                        output = raw_output.decode('cp932', errors='replace')
                    
                    match = re.search(r'version\s+REG_SZ\s+([\d\.]+)', output)
                    if match:
                        version = match.group(1)
                        break
                except subprocess.CalledProcessError:
                    continue
            
            if not version:
                # 実行ファイルのパスから取得を試みる
                chrome_paths = [
                    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
                ]
                for path in chrome_paths:
                    if os.path.exists(path):
                        cmd = f'powershell -command "(Get-Item \'{path}\').VersionInfo.ProductVersion"'
                        output = subprocess.check_output(cmd, shell=True).decode().strip()
                        if output:
                            version = output
                            break

        elif system == "Darwin":
            # macOSの場合
            path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(path):
                output = subprocess.check_output([path, "--version"]).decode().strip()
                match = re.search(r'Google Chrome ([\d\.]+)', output)
                if match:
                    version = match.group(1)

        elif system == "Linux":
            # Linuxの場合
            commands = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]
            for cmd in commands:
                try:
                    output = subprocess.check_output([cmd, "--version"]).decode().strip()
                    match = re.search(r'[\d\.]+', output)
                    if match:
                        version = match.group(0)
                        break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

    except Exception as e:
        print(f"Chrome バージョン取得中にエラーが発生しました: {e}")

    return version

if __name__ == "__main__":
    v = get_chrome_version()
    print(f"Detected Chrome Version: {v}")
