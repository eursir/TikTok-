import os
import time
import logging
from datetime import datetime

import requests
from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config

# --------------- 初始化 ---------------

app = Flask(__name__)

os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.LOG_FOLDER, exist_ok=True)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(config.LOG_FOLDER, f"{datetime.now():%Y-%m-%d}.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# --------------- AdsPower / Selenium ---------------


def start_ads_power_browser(environment_id: str) -> tuple[str, str]:
    """调用 AdsPower API 启动浏览器环境，返回 (selenium_url, webdriver_path)。"""
    url = f"{config.ADSPOWER_API_HOST}/api/v1/browser/start"
    resp = requests.get(url, params={"user_id": environment_id}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"AdsPower 启动失败: {data.get('msg')}")
    ws = data["data"]["ws"]
    return ws["selenium"], data["data"]["webdriver"]


def open_tiktok_studio(selenium_url: str) -> webdriver.Chrome:
    """连接到已启动的浏览器实例并打开 TikTok Studio。"""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", selenium_url)
    driver = webdriver.Chrome(options=options)
    driver.get(config.TIKTOK_STUDIO_URL)
    time.sleep(5)
    return driver


def upload_video(driver: webdriver.Chrome, file_path: str) -> None:
    """通过 <input type='file'> 上传视频文件。"""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"视频文件不存在: {file_path}")

    file_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(file_path)
    logger.info("视频已发送到上传控件: %s", file_path)


def enter_text_in_editor(driver: webdriver.Chrome, text: str) -> None:
    """在 TikTok Studio 的 DraftJS 编辑器中输入文本/标签。"""
    text_box = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.public-DraftEditor-content[contenteditable='true']")
        )
    )
    text_box.click()

    # 选中并清空已有内容
    driver.execute_script("""
        var el = arguments[0];
        var range = document.createRange();
        range.selectNodeContents(el);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
    """, text_box)
    text_box.send_keys(Keys.BACK_SPACE)
    driver.execute_script(
        "arguments[0].dispatchEvent(new Event('input', {bubbles: true}))", text_box
    )

    # 逐词写入（触发 DraftJS 内部状态更新）
    for word in text.split():
        driver.execute_script("arguments[0].innerHTML += arguments[1]", text_box, word)
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}))", text_box
        )
        text_box.send_keys(Keys.SPACE)

    logger.info("文本已输入编辑器")


# --------------- Flask 路由 ---------------


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/list_files", methods=["GET"])
def list_files():
    """列出 uploads/ 下的文件。"""
    try:
        files = sorted(os.listdir(config.UPLOAD_FOLDER))
        return jsonify({"status": "success", "files": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/upload", methods=["POST"])
def upload_file():
    """接收前端上传的文件。"""
    uploaded = []
    for f in request.files.getlist("files[]"):
        if f.filename:
            save_path = os.path.join(config.UPLOAD_FOLDER, f.filename)
            f.save(save_path)
            uploaded.append(f.filename)
            logger.info("文件已上传: %s", f.filename)

    if uploaded:
        return jsonify({"status": "success", "filenames": uploaded})
    return jsonify({"status": "error", "message": "未选择文件"}), 400


@app.route("/delete_file", methods=["POST"])
def delete_file():
    """删除单个文件。"""
    filename = request.form.get("filename", "")
    file_path = os.path.join(config.UPLOAD_FOLDER, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
        logger.info("文件已删除: %s", filename)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "文件不存在"}), 404


@app.route("/delete_all_files", methods=["POST"])
def delete_all_files():
    """删除 uploads/ 下所有文件。"""
    count = 0
    for name in os.listdir(config.UPLOAD_FOLDER):
        path = os.path.join(config.UPLOAD_FOLDER, name)
        if os.path.isfile(path):
            os.remove(path)
            count += 1
    logger.info("已删除全部文件，共 %d 个", count)
    return jsonify({"status": "success", "message": f"已删除 {count} 个文件"})


@app.route("/start_environments", methods=["POST"])
def start_environments():
    """
    核心接口：启动 AdsPower 环境 → 打开 TikTok Studio → 上传视频 → 填写文案。
    前端传入 environment_ids、files、editor_text。
    """
    env_ids = request.form.getlist("environment_ids[]")
    files = request.form.getlist("files[]")
    editor_text = request.form.get("editor_text", "")
    results = []

    for idx, env_id in enumerate(env_ids):
        if not env_id:
            continue
        if idx >= len(files):
            results.append(f"环境 {env_id}: 文件不足，跳过")
            continue

        try:
            logger.info("启动环境 %s ...", env_id)
            selenium_url, _ = start_ads_power_browser(env_id)
            time.sleep(2)

            driver = open_tiktok_studio(selenium_url)
            video_path = os.path.join(config.UPLOAD_FOLDER, files[idx])
            upload_video(driver, video_path)
            time.sleep(5)

            if editor_text:
                enter_text_in_editor(driver, editor_text)

            msg = f"环境 {env_id}: 启动成功，视频已上传"
            results.append(msg)
            logger.info(msg)

        except Exception as e:
            msg = f"环境 {env_id}: 失败 - {e}"
            results.append(msg)
            logger.error(msg)

    return jsonify({"status": "success", "messages": results})


# --------------- 启动 ---------------

if __name__ == "__main__":
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
