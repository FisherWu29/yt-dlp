#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频下载链接服务
基于FastAPI的API服务，用于获取视频的真实下载链接
"""

import logging
import sys
import os
import time

# 添加项目根目录到Python路径，以便正确导入yt_dlp
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import HttpUrl
from typing import Dict, List, Optional
from yt_dlp_wrapper import VideoDownloader
from models import VideoUrlRequest, FormatInfo, VideoInfoResponse, DownloadLinkResponse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('video-download-service')

# 创建FastAPI应用
app = FastAPI(
    title="视频下载链接服务",
    description="获取视频真实下载链接的API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    请求日志中间件
    记录请求方法、路径、状态码以及处理时间
    """
    start_time = time.time()
    
    # 获取客户端IP
    client_host = request.client.host if request.client else "unknown"
    
    # 继续处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}ms".format(process_time)
    
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} IP: {client_host} "
        f"Duration: {formatted_process_time}"
    )
    
    return response

# 创建视频下载器实例
downloader = VideoDownloader()

# API接口
@app.get("/health", summary="健康检查", tags=["系统"])
def health_check():
    """检查服务是否正常运行"""
    return {
        "status": "ok",
        "message": "视频下载链接服务运行正常",
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(None, None, None, None, None, None, None, None, None))
    }

@app.get("/formats", summary="获取视频可用格式", tags=["视频"])
def get_video_formats(
    url: HttpUrl = Query(..., description="视频URL"),
    enable_remote: Optional[bool] = Query(None, description="是否启用远程组件（绕过YouTube限制），默认仅在YouTube请求时启用")
):
    """获取视频的可用格式列表（返回原始JSON数据）"""
    try:
        # 判断是否为YouTube链接
        url_str = str(url)
        is_youtube = "youtube.com" in url_str or "youtu.be" in url_str

        # 仅当enable_remote为None时，根据是否为YouTube链接自动设置
        final_enable_remote = is_youtube if enable_remote is None else enable_remote

        logger.info(f"获取原始视频信息: {url}, 是YouTube链接: {is_youtube}, 启用远程组件: {final_enable_remote}")
        video_info = downloader.get_raw_info(url, enable_remote=final_enable_remote)
        return video_info
    except Exception as e:
        logger.error(f"获取视频格式失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取视频格式失败: {str(e)}")

@app.post("/download-link", summary="获取视频下载链接", tags=["视频"])
def get_download_link(request: VideoUrlRequest):
    """获取视频的真实下载链接（返回原始JSON数据）"""
    try:
        # 判断是否为YouTube链接
        url_str = str(request.url)
        is_youtube = "youtube.com" in url_str or "youtu.be" in url_str

        # 仅当enable_remote为None时，根据是否为YouTube链接自动设置
        final_enable_remote = is_youtube if request.enable_remote is None else request.enable_remote

        logger.info(f"获取下载链接(原始): {request.url}, 是YouTube链接: {is_youtube}, 启用远程组件: {final_enable_remote}")
        video_info = downloader.get_raw_info(
            request.url,
            enable_remote=final_enable_remote
        )
        return video_info
    except Exception as e:
        logger.error(f"获取下载链接失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取下载链接失败: {str(e)}")

@app.get("/download-link", summary="获取视频下载链接(GET)", tags=["视频"])
def get_download_link_get(
    url: HttpUrl = Query(..., description="视频URL"),
    enable_remote: Optional[bool] = Query(None, description="是否启用远程组件（绕过YouTube限制），默认仅在YouTube请求时启用")
):
    """通过GET请求获取视频的真实下载链接（返回原始JSON数据）"""
    try:
        # 判断是否为YouTube链接
        url_str = str(url)
        is_youtube = "youtube.com" in url_str or "youtu.be" in url_str

        # 仅当enable_remote为None时，根据是否为YouTube链接自动设置
        final_enable_remote = is_youtube if enable_remote is None else enable_remote

        logger.info(f"GET获取下载链接(原始): {url}, 是YouTube链接: {is_youtube}, 启用远程组件: {final_enable_remote}")
        video_info = downloader.get_raw_info(
            url,
            enable_remote=final_enable_remote
        )
        return video_info
    except Exception as e:
        logger.error(f"GET获取下载链接失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取下载链接失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发环境启用自动重载
        log_level="info"
    )
