import requests

KNOWN_GOOD_URL = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
LAST_KNOWN_GOOD_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"


def _extract_from_versions(entries, major_version, platform_name):
    """known-good の versions 配列から目的のプラットフォームを探す"""
    if not isinstance(entries, list):
        return None, None

    # API の entries は時系列昇順なので、末尾から探索して最新を優先する
    for entry in reversed(entries):
        version = entry.get("version", "")
        if not version.startswith(f"{major_version}."):
            continue
        downloads = entry.get("downloads", {}).get("chromedriver", [])
        for download in downloads:
            if download.get("platform") == platform_name:
                return version, download.get("url")
    return None, None


def _extract_from_channels(channels, major_version, platform_name):
    """last-known-good の channels 情報から取得する"""
    preferred = ["Stable", "Beta", "Dev", "Canary"]
    for name in preferred:
        channel = (channels or {}).get(name)
        if not channel:
            continue
        version = channel.get("version", "")
        if not version.startswith(f"{major_version}."):
            continue
        downloads = channel.get("downloads", {}).get("chromedriver", [])
        for download in downloads:
            if download.get("platform") == platform_name:
                return version, download.get("url")
    return None, None


def get_driver_download_url(chrome_version, platform_name):
    """
    指定された Chrome バージョンとプラットフォームに対応する ChromeDriver のダウンロード URL を取得する
    platform_name: 'linux64', 'mac-arm64', 'mac-x64', 'win32', 'win64'
    """
    major_version = chrome_version.split('.')[0]

    # known-good (全バージョン) を優先して検索し、任意のメジャー番号に追随する
    try:
        response = requests.get(KNOWN_GOOD_URL, timeout=30)
        response.raise_for_status()
        version, url = _extract_from_versions(response.json().get('versions', []), major_version, platform_name)
        if url:
            return url
    except Exception as e:
        print(f"CfT known-good 取得中にエラーが発生しました: {e}")

    # 念のため last-known-good からチャネル情報と versions を探索する
    try:
        response = requests.get(LAST_KNOWN_GOOD_URL, timeout=30)
        response.raise_for_status()
        payload = response.json()

        version, url = _extract_from_versions(payload.get('versions', []), major_version, platform_name)
        if url:
            return url

        version, url = _extract_from_channels(payload.get('channels', {}), major_version, platform_name)
        if url:
            return url
    except Exception as e:
        print(f"CfT last-known-good 取得中にエラーが発生しました: {e}")

    return None

def get_platform_string():
    import platform
    import sys
    
    os_name = platform.system()
    arch = platform.machine()
    
    if os_name == "Linux":
        return "linux64"
    elif os_name == "Darwin":
        if arch == "arm64":
            return "mac-arm64"
        return "mac-x64"
    elif os_name == "Windows":
        if sys.maxsize > 2**32:
            return "win64"
        return "win32"
    return None
