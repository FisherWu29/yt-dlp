#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频下载链接服务
基于FastAPI的API服务，用于获取视频的真实下载链接
"""

import logging
import sys
import os

# 添加项目根目录到Python路径，以便正确导入yt_dlp
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, Query
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

@app.get("/formats", summary="获取视频可用格式", tags=["视频"], response_model=VideoInfoResponse)
def get_video_formats(
    url: HttpUrl = Query(..., description="视频URL"),
    max_quality: Optional[int] = Query(None, description="最大分辨率高度，如1080")
):
    """获取视频的可用格式列表"""
    try:
        logger.info(f"获取视频格式: {url}")
        video_info = downloader.get_video_formats(url, max_quality)
        return video_info
    except Exception as e:
        logger.error(f"获取视频格式失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取视频格式失败: {str(e)}")

@app.post("/download-link", summary="获取视频下载链接", tags=["视频"], response_model=DownloadLinkResponse)
def get_download_link(request: VideoUrlRequest):
    """获取视频的真实下载链接"""
    try:
        logger.info(f"获取下载链接: {request.url}, 格式: {request.format_id}")
        download_links = downloader.get_download_links(
            request.url,
            format_id=request.format_id,
            max_quality=request.max_quality
        )
        return {
            "status": "success",
            "message": "获取下载链接成功",
            "video_info": download_links["video_info"],
            "download_links": download_links["download_links"]
        }
    except Exception as e:
        logger.error(f"获取下载链接失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取下载链接失败: {str(e)}")

@app.get("/download-link", summary="获取视频下载链接(GET)", tags=["视频"], response_model=DownloadLinkResponse)
def get_download_link_get(
    url: HttpUrl = Query(..., description="视频URL"),
    format_id: Optional[str] = Query(None, description="特定格式ID") ,
    max_quality: Optional[int] = Query(None, description="最大分辨率高度，如1080")
):
    """通过GET请求获取视频的真实下载链接"""
    try:
        logger.info(f"GET获取下载链接: {url}, 格式: {format_id}")
        download_links = downloader.get_download_links(
            url,
            format_id=format_id,
            max_quality=max_quality
        )
        return {
            "status": "success",
            "message": "获取下载链接成功",
            "video_info": download_links["video_info"],
            "download_links": download_links["download_links"]
        }
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