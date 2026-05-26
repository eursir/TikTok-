import os

# AdsPower API 地址
ADSPOWER_API_HOST = os.environ.get("ADSPOWER_API_HOST", "http://localhost:50325")

# Flask 配置
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("FLASK_PORT", "9866"))
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

# 上传文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

# TikTok Studio URL
TIKTOK_STUDIO_URL = "https://www.tiktok.com/tiktokstudio/upload?from=creator_center"

# 日志文件夹
LOG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

# 最大并行环境数
MAX_ENVIRONMENTS = 10
