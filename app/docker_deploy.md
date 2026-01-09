# 视频下载服务 - Docker部署指南

## 一、概述

本文档提供了视频下载服务的Docker部署指南，包括镜像构建、容器运行、更新流程和常见问题解决。该服务基于yt-dlp，支持自动更新，提供RESTful API接口。

## 二、前置条件

- 安装Docker（版本20.04+）
- 可用的网络连接
- 足够的磁盘空间（建议至少1GB）

## 三、部署步骤

### 1. 构建Docker镜像

```bash
# 进入app目录
cd /path/to/yt-dlp/app

# 构建镜像（会自动克隆最新yt-dlp）
docker build -t video-download-service .
```

### 2. 运行Docker容器

```bash
# 运行容器
docker run -d -p 8000:8000 --name video-download-service video-download-service
```

### 3. 验证部署

```bash
# 检查容器状态
docker ps -a

# 访问健康检查端点
curl http://localhost:8000/health

# 访问API文档
# 在浏览器中打开：http://localhost:8000/docs
```

## 四、更新流程

### 1. 更新Docker镜像

```bash
# 进入app目录
cd /path/to/yt-dlp/app

# 构建新镜像
docker build -t video-download-service .

# 停止并删除旧容器
docker stop video-download-service
docker rm video-download-service

# 运行新容器
docker run -d -p 8000:8000 --name video-download-service video-download-service
```

### 2. 自动更新（推荐）

**使用Docker Compose**：

创建 `docker-compose.yml`：

```yaml
version: '3'

services:
  video-download-service:
    build: .
    ports:
      - "8000:8000"
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**使用计划任务**：

```bash
# Linux系统（使用cron）
crontab -e

# 添加以下内容（每天凌晨2点更新）
0 2 * * * cd /path/to/yt-dlp/app && docker build -t video-download-service . && docker stop video-download-service && docker rm video-download-service && docker run -d -p 8000:8000 --name video-download-service video-download-service
```

## 五、API使用说明

### 1. 核心API端点

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /formats | 获取视频可用格式 |
| POST | /download-link | 获取视频下载链接 |
| GET | /download-link | 获取视频下载链接（GET方式） |

### 2. 示例请求

```bash
# 获取视频格式
curl "http://localhost:8000/formats?url=https://www.bilibili.com/video/BV1Gx411w7oE"

# 获取下载链接
curl -X POST -H "Content-Type: application/json" -d '{"url": "https://www.bilibili.com/video/BV1Gx411w7oE"}' http://localhost:8000/download-link
```

## 六、常见问题和解决方案

### 1. 构建镜像失败

**问题**：构建过程中出现网络错误

**解决方案**：
```bash
# 检查网络连接
ping github.com

# 使用代理构建
docker build --build-arg HTTP_PROXY=http://proxy.example.com:7890 -t video-download-service .
```

### 2. 容器启动失败

**问题**：容器启动后立即退出

**解决方案**：
```bash
# 查看容器日志
docker logs video-download-service

# 检查端口占用
netstat -tuln | grep 8000
```

### 3. API访问失败

**问题**：无法访问API端点

**解决方案**：
```bash
# 检查容器状态
docker ps -a

# 检查防火墙设置
sudo ufw status

# 检查端口映射
docker port video-download-service
```

## 七、最佳实践

1. **使用Docker Compose**：便于管理和扩展
2. **配置日志管理**：限制日志大小，避免磁盘空间耗尽
3. **定期更新镜像**：确保获取最新的yt-dlp版本和安全修复
4. **使用反向代理**：添加Nginx或Traefik作为反向代理，提供HTTPS支持
5. **监控服务状态**：使用Prometheus和Grafana监控服务健康
6. **备份重要配置**：定期备份Docker Compose文件和配置

## 八、卸载步骤

```bash
# 停止并删除容器
docker stop video-download-service
docker rm video-download-service

# 删除镜像
docker rmi video-download-service
```

## 九、联系方式

如有问题或建议，请联系开发团队。

---

**更新日期**：2026-01-08
**版本**：1.0.0
**适用环境**：Docker 20.04+
