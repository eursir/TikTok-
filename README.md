# TikTok 批量发布工具

基于 Flask + Selenium + AdsPower 指纹浏览器的 TikTok 批量视频发布工具。

## 功能

- 🎬 批量上传视频文件
- 🤖 自动启动 AdsPower 浏览器环境
- 📝 自动填写 TikTok Studio 文案和标签
- 🚀 一键发布到多个 TikTok 账号
- 📋 Web 管理界面，支持拖拽上传

## 架构

```
┌─────────────┐     HTTP      ┌─────────────┐    API     ┌──────────────┐
│  浏览器前端  │ ──────────── │  Flask 后端  │ ──────── │  AdsPower    │
│  (jQuery)   │              │  (app.py)    │          │  指纹浏览器   │
└─────────────┘              └─────────────┘          └──────────────┘
                                    │ Selenium
                                    ▼
                             ┌─────────────┐
                             │ TikTok Studio│
                             └─────────────┘
```

## 前置条件

1. **Python 3.9+**
2. **AdsPower 浏览器** — 本地运行，API 默认端口 `50325`
3. **ChromeDriver** — 版本需与 AdsPower 内置 Chrome 匹配

## 安装

```bash
# 克隆仓库
git clone https://github.com/<your-username>/tiktok-batch-uploader.git
cd tiktok-batch-uploader

# 安装依赖
pip install -r requirements.txt
```

## 配置

通过环境变量覆盖默认配置（可选）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ADSPOWER_API_HOST` | `http://localhost:50325` | AdsPower API 地址 |
| `FLASK_PORT` | `9866` | Web 服务端口 |
| `FLASK_HOST` | `0.0.0.0` | 监听地址 |
| `FLASK_DEBUG` | `false` | 调试模式 |

## 使用

1. **启动 AdsPower 浏览器**，确保 API 可访问（默认 `http://localhost:50325`）

2. **运行程序**：
   ```bash
   python app.py
   ```

3. **打开浏览器**访问 `http://localhost:9866`

4. 在页面上：
   - 填写 AdsPower 环境 ID（最多 10 个）
   - 输入文案 / 标签
   - 拖拽上传视频文件
   - 点击「启动批量发布」

### 测试 AdsPower 连接

```bash
python startAdsP.py <environment_id>
```

## 项目结构

```
├── app.py              # Flask 主程序
├── config.py           # 配置管理
├── startAdsP.py        # AdsPower 连接测试脚本
├── requirements.txt    # Python 依赖
├── .gitignore
├── templates/
│   └── index.html      # Web 管理界面
├── uploads/            # 上传的视频文件（已 gitignore）
└── logs/               # 运行日志（已 gitignore）
```

## 注意事项

- 需要先在 AdsPower 中创建好浏览器环境（指纹配置文件）
- 上传的视频文件会临时存放在 `uploads/` 目录
- 日志按日期存储在 `logs/` 目录
- 请确保 TikTok 账号已在 AdsPower 环境中登录

## License

MIT
