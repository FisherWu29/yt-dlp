# yt-dlp 开发调试和部署步骤

## 一、开发调试步骤

### 1. 环境准备

#### 1.1 系统要求
- Windows 10/11 (64位)
- Python 3.10+（推荐3.13）

#### 1.2 安装Python依赖

```powershell
# 进入项目目录
cd d:\MyProject\Crawler\yt-dlp

# 安装开发依赖
python devscripts/install_deps.py
```

#### 1.3 安装额外推荐工具
- **FFmpeg**：用于视频合并和后期处理
  - 下载地址：https://ffmpeg.org/download.html
  - 将ffmpeg.exe和ffprobe.exe添加到系统PATH
- **Deno**：JavaScript运行时，用于处理YouTube签名
  - 下载地址：https://deno.com/download

### 2. 项目结构

```
yt-dlp/
├── app/             # 视频下载链接服务API
│   ├── app.py       # FastAPI应用入口
│   ├── models.py    # Pydantic模型定义
│   ├── yt_dlp_wrapper.py # yt-dlp封装器
│   ├── requirements.txt   # API依赖
│   └── Dockerfile   # Docker构建文件
├── yt_dlp/          # yt-dlp主源码目录
│   ├── extractor/   # 各网站提取器（包含bilibili.py）
│   ├── downloader/  # 下载器实现
│   └── YoutubeDL.py # 核心逻辑
├── devscripts/      # 开发脚本
├── test/            # 测试用例
└── README.md        # 项目说明
```

### 3. 运行和调试

#### 3.1 基本运行方式

```powershell
# 直接运行yt-dlp命令（推荐）
python -m yt_dlp [OPTIONS] URL

# 示例：模拟下载B站视频
python -m yt_dlp --simulate https://www.bilibili.com/video/BV1Gx411w7oE

# 示例：列出可用格式
python -m yt_dlp -F https://www.bilibili.com/video/BV1Gx411w7oE
```

#### 3.2 API服务运行

```powershell
# 进入app目录
cd app

# 安装API依赖
python -m pip install -r requirements.txt

# 运行API服务
python app.py
```

API服务启动后，可通过以下地址访问：
- 健康检查：http://localhost:8000/health
- API文档：http://localhost:8000/docs
- 测试获取视频格式：http://localhost:8000/formats?url=https://www.bilibili.com/video/BV1Gx411w7oE

#### 3.3 调试模式

```powershell
# yt-dlp详细日志输出
python -m yt_dlp --verbose [OPTIONS] URL

# 调试特定提取器
python -m yt_dlp --verbose --extractor-args bilibili:debug=1 URL

# API服务调试（VS Code）
# 1. 打开app目录
# 2. 创建调试配置文件 `.vscode/launch.json`
# 3. 配置内容：
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "API Service Debug",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/app.py",
            "cwd": "${workspaceFolder}",
            "console": "integratedTerminal"
        }
    ]
}
```

4. 设置断点（如在`app.py`或`yt_dlp_wrapper.py`中）
5. 按F5开始调试

### 4. 测试

#### 4.1 运行单元测试

```powershell
# 运行所有测试
python -m pytest test/ -xvs

# 运行特定测试
python -m pytest test/test_download.py -xvs

# 运行B站提取器测试
python -m pytest test/test_all_urls.py::TestAllURLs::test_bilibili -xvs
```

#### 4.2 手动测试

```powershell
# 测试B站视频下载
python -m yt_dlp --simulate https://www.bilibili.com/video/BV1Gx411w7oE

# 测试B站番剧
python -m yt_dlp --simulate https://www.bilibili.com/bangumi/play/ep21495

# 测试B站直播
python -m yt_dlp --simulate https://live.bilibili.com/196
```

### 5. 常见问题处理

#### 5.1 依赖问题
```powershell
# 重新安装依赖
python devscripts/install_deps.py --reinstall
```

#### 5.2 WBI签名失败
```powershell
# 清除cookie缓存
rm -rf %APPDATA%/yt-dlp/cookies

# 重新生成WBI密钥
python -m yt_dlp --verbose --no-cache-dir URL
```

#### 5.3 提取器调试
```powershell
# 查看提取器详细信息
python -m yt_dlp --list-extractors | grep -i bilibili

# 调试特定提取器
python -m yt_dlp --verbose --extractor-args bilibili:debug=1 URL
```

### 6. API服务使用说明

#### 6.1 API端点

| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | /health | 健康检查 | 无 |
| GET | /formats | 获取视频可用格式 | url: 视频URL<br>max_quality: 最大分辨率高度（可选） |
| POST | /download-link | 获取视频下载链接 | url: 视频URL<br>format_id: 特定格式ID（可选）<br>max_quality: 最大分辨率高度（可选） |
| GET | /download-link | 获取视频下载链接（GET方式） | url: 视频URL<br>format_id: 特定格式ID（可选）<br>max_quality: 最大分辨率高度（可选） |

#### 6.2 示例请求

```powershell
# 健康检查
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# 获取视频格式
Invoke-WebRequest -Uri "http://localhost:8000/formats?url=https://www.bilibili.com/video/BV1Gx411w7oE" -UseBasicParsing

# 获取下载链接（GET方式）
Invoke-WebRequest -Uri "http://localhost:8000/download-link?url=https://www.bilibili.com/video/BV1Gx411w7oE" -UseBasicParsing

# 获取下载链接（POST方式）
Invoke-WebRequest -Uri "http://localhost:8000/download-link" -Method POST -ContentType "application/json" -Body '{"url": "https://www.bilibili.com/video/BV1Gx411w7oE"}' -UseBasicParsing
```

#### 6.3 API响应格式

**视频格式响应**：
```json
{
  "title": "视频标题",
  "formats": [
    {
      "format_id": "1080p60",
      "format_note": "1080P 60fps",
      "ext": "mp4",
      "resolution": "1920x1080",
      "fps": 60,
      "filesize": 123456789
    }
  ],
  "best_format": {
    "format_id": "1080p60",
    "format_note": "1080P 60fps",
    "ext": "mp4",
    "resolution": "1920x1080"
  },
  "webpage_url": "https://www.bilibili.com/video/BV1Gx411w7oE",
  "uploader": "UP主名称"
}
```

**下载链接响应**：
```json
{
  "status": "success",
  "message": "获取下载链接成功",
  "video_info": {
    "title": "视频标题",
    "formats": [...],
    "best_format": {...}
  },
  "download_links": [
    {
      "format_id": "1080p60",
      "format_note": "1080P 60fps",
      "ext": "mp4",
      "url": "https://example.com/video.mp4"
    }
  ]
}
```

#### 6.4 客户端集成

您可以使用任何HTTP客户端库来调用API，例如Python的requests库：

```python
import requests

# 获取视频格式
response = requests.get("http://localhost:8000/formats", params={"url": "https://www.bilibili.com/video/BV1Gx411w7oE"})
if response.status_code == 200:
    data = response.json()
    print(f"视频标题: {data['title']}")
    print(f"最佳格式: {data['best_format']['resolution']}")

# 获取下载链接
response = requests.post("http://localhost:8000/download-link", json={"url": "https://www.bilibili.com/video/BV1Gx411w7oE"})
if response.status_code == 200:
    data = response.json()
    download_url = data['download_links'][0]['url']
    print(f"下载链接: {download_url}")
```

#### 6.5 API文档

API服务提供了自动生成的Swagger文档，可通过以下地址访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

通过API文档，您可以：
- 查看所有API端点的详细信息
- 测试API调用
- 查看请求和响应示例
- 下载API规范

#### 6.6 自定义配置

您可以通过修改`app.py`文件中的配置来自定义API服务：

```python
# 修改服务端口
uvicorn.run(
    "app:app",
    host="0.0.0.0",
    port=8000,  # 修改此处端口
    reload=True,
    log_level="info"
)

# 修改yt-dlp配置
# 在yt_dlp_wrapper.py中修改self.ydl_opts
self.ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    # 添加其他配置选项
}
```

#### 6.7 监控和日志

API服务会生成详细的日志，您可以通过以下方式查看：

```powershell
# 实时查看日志（在运行服务的终端中）
# 或在Docker容器日志中查看

docker logs -f <container_id>
```

日志级别可以在`app.py`中配置：

```python
logging.basicConfig(
    level=logging.INFO,  # 修改此处日志级别：DEBUG, INFO, WARNING, ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 二、线上部署步骤

### 1. 部署方式

#### 1.1 Docker部署（推荐）

适合生产环境，支持自动更新yt-dlp，便于管理和扩展：

```powershell
# 进入app目录
cd app

# 构建Docker镜像（会自动克隆最新yt-dlp）
docker build -t video-download-service .

# 运行Docker容器
docker run -d -p 8000:8000 --name video-download-service video-download-service

# 查看容器状态
docker ps -a

# 查看容器日志
docker logs -f video-download-service
```

#### 1.2 二进制部署

适合简单场景，无需Python依赖：

```powershell
# 下载Windows二进制文件
Invoke-WebRequest -Uri https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe -OutFile yt-dlp.exe

# 运行
./yt-dlp.exe --version
```

#### 1.3 pip安装

适合需要频繁更新的场景：

```powershell
# 安装（支持升级）
python -m pip install -U yt-dlp

# 运行
yt-dlp --version
```

#### 1.4 源码部署

适合需要自定义修改的场景：

```powershell
# 克隆仓库
git clone https://github.com/yt-dlp/yt-dlp.git
cd yt-dlp

# 安装依赖
python devscripts/install_deps.py

# 运行
python -m yt_dlp --version
```

### 2. 配置文件

创建配置文件 `yt-dlp.conf`，放在以下位置之一：
- 系统级：`%APPDATA%/yt-dlp/config.txt`
- 用户级：`~/.config/yt-dlp/config.txt`
- 项目级：与yt-dlp.exe同目录

示例配置：

```
# 保存路径
-o D:/Downloads/%(title)s.%(ext)s

# 默认格式选择
-f bestvideo+bestaudio/best

# 自动合并视频音频
--merge-output-format mp4

# 嵌入字幕
--embed-subs

# 嵌入缩略图
--embed-thumbnail

# 下载速度限制（10MB/s）
--limit-rate 10M
```

### 3. 服务化部署

#### 3.1 Docker服务化部署（推荐）

使用Docker Compose或Kubernetes进行服务化部署：

**Docker Compose示例**：

在app目录下创建 `docker-compose.yml`：

```yaml
version: '3'

services:
  video-download-service:
    build: .
    ports:
      - "8000:8000"
    restart: always
    environment:
      - PYTHONPATH=/app/yt-dlp
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

运行：
```powershell
cd app
docker-compose up -d
```

#### 3.2 系统服务部署

在Linux系统上，可以使用systemd将API服务注册为系统服务：

```bash
# 创建systemd服务文件
cat > /etc/systemd/system/video-download-service.service <<EOF
[Unit]
Description=Video Download Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/yt-dlp/app
ExecStart=/usr/bin/python3 app.py
Restart=always
Environment="PYTHONPATH=/path/to/yt-dlp"

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
systemctl daemon-reload
systemctl enable video-download-service
systemctl start video-download-service

# 查看服务状态
systemctl status video-download-service
```

#### 3.3 计划任务

使用计划任务定期更新yt-dlp或执行批量下载：

```powershell
# 更新Docker镜像的计划任务
$trigger = New-JobTrigger -Daily -At 2am
$action = New-ScheduledTaskAction -Execute "powershell" -Argument "cd d:\MyProject\Crawler\yt-dlp\app; docker build -t video-download-service .; docker stop video-download-service; docker rm video-download-service; docker run -d -p 8000:8000 --name video-download-service video-download-service"
Register-ScheduledTask -TaskName "UpdateVideoDownloadService" -Trigger $trigger -Action $action
```

### 4. 更新和维护

#### 4.1 Docker镜像更新（推荐）

更新Docker镜像会自动克隆最新的yt-dlp仓库：

```powershell
# 进入app目录
cd app

# 构建新镜像
docker build -t video-download-service .

# 停止并删除旧容器
docker stop video-download-service
docker rm video-download-service

# 运行新容器
docker run -d -p 8000:8000 --name video-download-service video-download-service
```

#### 4.2 二进制更新

```powershell
./yt-dlp.exe -U
```

#### 4.3 pip更新

```powershell
python -m pip install -U yt-dlp
```

#### 4.4 源码更新

```powershell
cd d:\MyProject\Crawler\yt-dlp
git pull
python devscripts/install_deps.py
```

#### 4.5 API服务更新

如果需要更新API服务代码，只需重新构建Docker镜像：

```powershell
cd app
# 修改API代码后
docker build -t video-download-service .
docker stop video-download-service
docker rm video-download-service
docker run -d -p 8000:8000 --name video-download-service video-download-service
```

### 5. 监控和日志

#### 5.1 API服务日志

```powershell
# 查看API服务日志（本地运行）
# 在运行服务的终端中实时查看

# 查看Docker容器日志
docker logs -f video-download-service

# 查看Docker容器日志的最后100行
docker logs --tail 100 video-download-service

# 持续监控Docker容器日志
docker logs -f --tail 50 video-download-service
```

#### 5.2 日志配置

**API服务日志配置**：

在`app.py`中修改日志配置：

```python
logging.basicConfig(
    level=logging.INFO,  # 修改日志级别：DEBUG, INFO, WARNING, ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_download_service.log'),  # 保存到文件
        logging.StreamHandler()  # 输出到控制台
    ]
)
```

**Docker日志配置**：

在`docker-compose.yml`中配置日志驱动和限制：

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"  # 单个日志文件最大10MB
    max-file: "3"    # 保留3个日志文件
```

#### 5.3 监控服务状态

```powershell
# 监控API服务健康状态
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# 监控Docker容器状态
docker stats video-download-service

# 使用Prometheus和Grafana监控（高级）
# 1. 安装Prometheus和Grafana
# 2. 配置Prometheus采集Docker和API服务指标
# 3. 在Grafana中创建监控面板
```

#### 5.4 监控下载状态

```powershell
# 通过API查看视频格式和下载链接
Invoke-WebRequest -Uri "http://localhost:8000/formats?url=https://www.bilibili.com/video/BV1Gx411w7oE" -UseBasicParsing
```

## 三、B站特定配置

### 1. B站提取器位置

```
yt_dlp/extractor/bilibili.py
```

### 2. 常见B站问题

#### 2.1 地区限制
```powershell
# 使用代理
python -m yt_dlp --proxy http://127.0.0.1:7890 URL

# 模拟地区
python -m yt_dlp --xff CN URL
```

#### 2.2 大会员视频
```powershell
# 使用cookie登录
python -m yt_dlp --cookies-from-browser chrome URL

# 或者使用cookie文件
python -m yt_dlp --cookies cookies.txt URL
```

#### 2.3 下载合集/多P视频
```powershell
# 下载整个合集
python -m yt_dlp https://www.bilibili.com/video/BV1Gx411w7oE

# 下载特定P
python -m yt_dlp --playlist-items 1 https://www.bilibili.com/video/BV1Gx411w7oE

# 下载多个P
python -m yt_dlp --playlist-items 1,3,5-7 https://www.bilibili.com/video/BV1Gx411w7oE
```

## 四、性能优化

### 1. 并行下载

```powershell
# 启用10个并发片段下载
python -m yt_dlp --concurrent-fragments 10 URL
```

### 2. 缓存优化

```powershell
# 启用HTTP缓存
python -m yt_dlp --cache-dir %TEMP%/yt-dlp-cache URL

# 禁用缓存
python -m yt_dlp --no-cache-dir URL
```

### 3. 减少重试

```powershell
# 设置重试次数为3
python -m yt_dlp --retries 3 URL
```

## 五、安全最佳实践

1. **不要分享cookie文件**：包含登录信息
2. **使用HTTPS代理**：保护隐私
3. **定期更新yt-dlp**：修复安全漏洞
4. **限制下载速率**：避免被封禁
5. **使用沙箱环境**：在隔离环境中运行

## 六、故障排除

### 1. 连接错误
```powershell
# 检查网络
ping api.bilibili.com

# 检查代理
python -m yt_dlp --proxy http://127.0.0.1:7890 --verbose URL
```

### 2. 格式错误
```powershell
# 列出所有可用格式
python -m yt_dlp -F URL

# 尝试不同格式
python -m yt_dlp -f best URL
```

### 3. 权限错误
```powershell
# 检查文件权限
icacls D:/Downloads

# 以管理员身份运行
Start-Process powershell.exe -Verb RunAs -ArgumentList "python -m yt_dlp URL"
```

---

**更新日期**：2026-01-08
**版本**：yt-dlp 2025.12.08
**API服务版本**：1.0.0
**适用环境**：Windows 10/11 + PowerShell、Linux + Docker
**部署方式**：Docker、二进制、pip、源码
