#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yt-dlp包装器
封装yt-dlp的核心功能，用于处理视频下载链接的获取
"""

import logging
import sys
import os

# 添加项目根目录到Python路径，以便正确导入yt_dlp
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from yt_dlp import YoutubeDL
from typing import Dict, List, Optional, Any
from models import VideoInfoResponse, FormatInfo

logger = logging.getLogger('yt-dlp-wrapper')

class VideoDownloader:
    """视频下载器类，封装yt-dlp的核心功能"""
    
    def __init__(self):
        """初始化视频下载器"""
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
            'force_json': True,
            'simulate': True,
            'verbose': False,
            'logger': logger,
            'merge_output_format': 'mp4',
        }
    
    def _extract_video_info(self, url) -> Dict[str, Any]:
        """
        提取视频信息
        :param url: 视频URL（字符串或HttpUrl对象）
        :return: 视频信息字典
        """
        # 确保url是字符串类型
        url_str = str(url) if hasattr(url, '__str__') else url
        with YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url_str, download=False)
            return info
    
    def _format_info_to_response(self, format_info: Dict[str, Any]) -> FormatInfo:
        """
        将yt-dlp格式信息转换为响应模型
        :param format_info: yt-dlp格式信息
        :return: FormatInfo响应模型
        """
        # 解析分辨率
        width = format_info.get('width', 0)
        height = format_info.get('height', 0)
        resolution = f"{width}x{height}" if width and height else "N/A"
        
        return FormatInfo(
            format_id=str(format_info.get('format_id', 'N/A')),
            format_note=format_info.get('format_note', 'N/A'),
            ext=format_info.get('ext', 'N/A'),
            resolution=resolution,
            fps=format_info.get('fps'),
            filesize=format_info.get('filesize'),
            filesize_approx=format_info.get('filesize_approx'),
            url=format_info.get('url')
        )
    
    def get_video_formats(self, url, max_quality: Optional[int] = None) -> VideoInfoResponse:
        """
        获取视频的可用格式列表
        :param url: 视频URL（字符串或HttpUrl对象）
        :param max_quality: 最大分辨率高度，如1080
        :return: VideoInfoResponse响应模型
        """
        # 提取视频信息
        info = self._extract_video_info(url)
        
        # 处理格式列表
        formats = []
        best_format = None
        best_height = 0
        
        for fmt in info.get('formats', []):
            # 跳过纯音频格式（vcodec为none）
            if fmt.get('vcodec') == 'none':
                continue
            
            # 过滤分辨率
            height = fmt.get('height', 0)
            if max_quality and height > max_quality:
                continue
            
            # 转换为响应格式
            format_response = self._format_info_to_response(fmt)
            formats.append(format_response)
            
            # 找到最佳格式
            if height > best_height:
                best_height = height
                best_format = format_response
        
        # 如果没有找到最佳格式，尝试使用第一个格式
        if not best_format and formats:
            best_format = formats[0]
        
        # 构建响应
        return VideoInfoResponse(
            title=info.get('title', 'N/A'),
            formats=formats,
            best_format=best_format,
            thumbnail=info.get('thumbnail'),
            description=info.get('description'),
            webpage_url=info.get('webpage_url', str(url)),
            duration=info.get('duration'),
            uploader=info.get('uploader')
        )
    
    def get_download_links(self, url, format_id: Optional[str] = None, max_quality: Optional[int] = None) -> Dict[str, Any]:
        """
        获取视频的真实下载链接
        :param url: 视频URL（字符串或HttpUrl对象）
        :param format_id: 特定格式ID，可选
        :param max_quality: 最大分辨率高度，可选
        :return: 包含视频信息和下载链接的字典
        """
        # 提取视频信息
        info = self._extract_video_info(url)
        
        # 获取可用格式
        available_formats = info.get('formats', [])
        
        # 选择要下载的格式
        selected_formats = []
        
        if format_id:
            # 按格式ID选择
            for fmt in available_formats:
                if str(fmt.get('format_id')) == format_id:
                    selected_formats.append(fmt)
                    break
        else:
            # 选择最佳质量的视频和音频
            # 1. 查找最佳视频格式
            best_video = None
            best_height = 0
            
            for fmt in available_formats:
                # 跳过音频格式
                if fmt.get('vcodec') == 'none':
                    continue
                
                height = fmt.get('height', 0)
                # 过滤分辨率
                if max_quality and height > max_quality:
                    continue
                
                if height > best_height:
                    best_height = height
                    best_video = fmt
            
            # 2. 查找最佳音频格式
            best_audio = None
            best_abr = 0
            
            for fmt in available_formats:
                # 跳过视频格式
                if fmt.get('acodec') != 'none':
                    abr = fmt.get('abr', 0)
                    if abr > best_abr:
                        best_abr = abr
                        best_audio = fmt
            
            # 3. 添加选定的格式
            if best_video:
                selected_formats.append(best_video)
            if best_audio:
                selected_formats.append(best_audio)
        
        # 如果没有选择到格式，使用默认最佳格式
        if not selected_formats:
            # 查找最佳综合格式
            best_combined = None
            best_score = 0
            
            for fmt in available_formats:
                # 综合格式既有视频又有音频
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                    height = fmt.get('height', 0)
                    # 过滤分辨率
                    if max_quality and height > max_quality:
                        continue
                    
                    # 简单评分：高度 + 码率
                    score = height + (fmt.get('tbr', 0) / 1000)
                    if score > best_score:
                        best_score = score
                        best_combined = fmt
            
            if best_combined:
                selected_formats.append(best_combined)
        
        # 构建下载链接列表
        download_links = []
        for fmt in selected_formats:
            format_url = fmt.get('url')
            if format_url:
                download_links.append({
                    'format_id': str(fmt.get('format_id')),
                    'format_note': fmt.get('format_note', 'N/A'),
                    'ext': fmt.get('ext', 'N/A'),
                    'url': format_url
                })
        
        # 构建视频信息响应
        video_info = self.get_video_formats(url, max_quality)
        
        return {
            "video_info": video_info,
            "download_links": download_links
        }
    
    def get_best_download_link(self, url, max_quality: Optional[int] = None) -> Dict[str, Any]:
        """
        获取最佳质量的下载链接
        :param url: 视频URL（字符串或HttpUrl对象）
        :param max_quality: 最大分辨率高度，如1080
        :return: 包含视频信息和最佳下载链接的字典
        """
        # 获取下载链接
        result = self.get_download_links(url, max_quality=max_quality)
        
        # 找到最佳下载链接
        best_link = None
        if result['download_links']:
            best_link = result['download_links'][0]  # 第一个通常是最佳视频格式
        
        return {
            "video_info": result['video_info'],
            "best_download_link": best_link
        }