"""
独立测试脚本：启动 AdsPower 浏览器环境并打印 Selenium 连接信息。
用于验证 AdsPower API 是否正常工作。
"""

import sys
import requests

ADSPOWER_API = "http://localhost:50325/api/v1/browser/start"


def start_browser(environment_id: str):
    resp = requests.get(ADSPOWER_API, params={"user_id": environment_id}, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 0:
        raise RuntimeError(f"启动失败: {data.get('msg')}")

    selenium_url = data["data"]["ws"]["selenium"]
    webdriver_path = data["data"]["webdriver"]
    print(f"Selenium URL : {selenium_url}")
    print(f"WebDriver    : {webdriver_path}")
    return selenium_url, webdriver_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: python {sys.argv[0]} <environment_id>")
        sys.exit(1)
    start_browser(sys.argv[1])
