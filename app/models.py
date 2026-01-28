from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

class FormatInfo(BaseModel):
    """视频格式信息"""
    format_id: str
    format_note: str
    ext: str
    resolution: str
    fps: Optional[float] = None
    filesize: Optional[int] = None
    filesize_approx: Optional[int] = None
    url: Optional[str] = None

class VideoInfoResponse(BaseModel):
    """视频信息响应"""
    title: str
    formats: List[FormatInfo]
    best_format: Optional[FormatInfo] = None
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    webpage_url: str
    duration: Optional[float] = None
    uploader: Optional[str] = None

class VideoUrlRequest(BaseModel):
    """视频URL请求"""
    url: HttpUrl
    format_id: Optional[str] = None
    max_quality: Optional[int] = None
    enable_remote: Optional[bool] = None

class DownloadLinkResponse(BaseModel):
    """下载链接响应"""
    status: str
    message: str
    video_info: VideoInfoResponse
    download_links: List[Dict[str, str]]
