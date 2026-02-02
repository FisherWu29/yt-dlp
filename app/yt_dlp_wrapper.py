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

    def __init__(self, enable_remote: bool = True):
        """
        初始化视频下载器
        :param enable_remote: 是否启用远程组件（用于绕过YouTube的n参数限制）
        """
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
            'remote_components': ['ejs:github'] if enable_remote else [],
            'timeout': 10,  # 设置超时时间为10秒
            'socket_timeout': 5,  # 设置socket超时时间为5秒
        }

        # 支持的视频网站域名列表
        self.supported_domains = {
            'youtube.com', 'youtu.be', 'youtube-nocookie.com',
            'bilibili.com', 'b23.tv',
            'vimeo.com',
            'dailymotion.com',
            'twitch.tv',
            'twitter.com', 'x.com',
            'instagram.com',
            'facebook.com',
            'tiktok.com',
            'reddit.com',
            'netflix.com',
            'disneyplus.com',
            'hulu.com',
            'primevideo.com',
        }

    def _is_supported_url(self, url_str: str) -> bool:
        """
        快速判断URL是否支持
        :param url_str: 视频URL字符串
        :return: 是否支持该URL
        """
        from urllib.parse import urlparse

        # 解析URL
        parsed_url = urlparse(url_str)
        hostname = parsed_url.hostname.lower() if parsed_url.hostname else ''

        # 检查是否在支持的域名列表中
        for domain in self.supported_domains:
            if hostname.endswith(domain):
                return True

        return False

    def _extract_video_info(self, url, enable_remote: Optional[bool] = None) -> Dict[str, Any]:
        """
        提取视频信息
        :param url: 视频URL（字符串或HttpUrl对象）
        :param enable_remote: 是否启用远程组件，如果提供则覆盖初始化设置
        :return: 视频信息字典
        """
        # 确保url是字符串类型
        url_str = str(url) if hasattr(url, '__str__') else url

        # 快速预验证URL是否支持
        if not self._is_supported_url(url_str):
            logger.error(f"不支持的URL: {url_str}")
            raise ValueError(f"不支持的URL: {url_str}")

        opts = self.ydl_opts.copy()
        if enable_remote is not None:
            opts['remote_components'] = ['ejs:github'] if enable_remote else []

        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url_str, download=False)
            return info

    def get_raw_info(self, url, enable_remote: Optional[bool] = None) -> Dict[str, Any]:
        """
        获取视频的原始信息（相当于 yt-dlp --dump-json）
        并过滤 formats 数组，只保留视频和音频对象
        :param url: 视频URL（字符串或HttpUrl对象）
        :param enable_remote: 是否启用远程组件
        :return: 原始视频信息字典
        """
        info = self._extract_video_info(url, enable_remote=enable_remote)

        # 过滤 formats 数组，只保留视频或音频
        # 在 yt-dlp 中，如果是音视频对象，通常 vcodec 或 acodec 不为 'none'
        if 'formats' in info:
            filtered_formats = []
            for fmt in info['formats']:
                vcodec = fmt.get('vcodec')
                acodec = fmt.get('acodec')
                # 只要 vcodec 或 acodec 任意一个不是 'none'，说明是视频、音频或两者都有
                if (vcodec and vcodec != 'none') or (acodec and acodec != 'none'):
                    filtered_formats.append(fmt)
            info['formats'] = filtered_formats

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

    def get_video_formats(self, url, max_quality: Optional[int] = None, enable_remote: Optional[bool] = None) -> VideoInfoResponse:
        """
        获取视频的可用格式列表
        :param url: 视频URL（字符串或HttpUrl对象）
        :param max_quality: 最大分辨率高度，如1080
        :param enable_remote: 是否启用远程组件
        :return: VideoInfoResponse响应模型
        """
        # 提取视频信息
        info = self._extract_video_info(url, enable_remote=enable_remote)

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

    def get_download_links(self, url, format_id: Optional[str] = None, max_quality: Optional[int] = None, enable_remote: Optional[bool] = None) -> Dict[str, Any]:
        """
        获取视频的最佳下载链接
        :param url: 视频URL（字符串或HttpUrl对象）
        :param format_id: 特定格式ID，可选
        :param max_quality: 最大分辨率高度，可选
        :param enable_remote: 是否启用远程组件
        :return: 包含精简视频信息和选定格式（完整字段）的字典
        """
        # 提取完整视频信息
        info = self._extract_video_info(url, enable_remote=enable_remote)

        # 获取可用格式（这里我们用原始的，不进行初步过滤，以便筛选）
        available_formats = info.get('formats', [])

        # 选择要返回的格式对象
        selected_formats = []

        if format_id:
            # 按格式ID选择
            for fmt in available_formats:
                if str(fmt.get('format_id')) == format_id:
                    selected_formats.append(fmt)
                    break
        else:
            # 自动筛选逻辑
            # 1. 查找最佳视频格式
            best_video = None
            best_height = 0
            for fmt in available_formats:
                if fmt.get('vcodec') != 'none':
                    height = fmt.get('height') or 0
                    if max_quality and height > max_quality:
                        continue
                    if height >= best_height:
                        best_height = height
                        best_video = fmt

            # 2. 查找最佳音频格式
            best_audio = None
            best_abr = 0
            for fmt in available_formats:
                if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    abr = fmt.get('abr') or 0
                    if abr >= best_abr:
                        best_abr = abr
                        best_audio = fmt

            # 3. 如果没找到分离的，找最佳综合格式
            if not best_video:
                best_combined = None
                best_combined_height = 0
                for fmt in available_formats:
                    if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                        height = fmt.get('height') or 0
                        if max_quality and height > max_quality:
                            continue
                        if height >= best_combined_height:
                            best_combined_height = height
                            best_combined = fmt
                if best_combined:
                    selected_formats.append(best_combined)
            else:
                selected_formats.append(best_video)
                if best_audio:
                    selected_formats.append(best_audio)

        # 构建最终返回对象
        # 只保留基本的视频元数据，避免返回几百行
        return {
            "title": info.get('title'),
            "id": info.get('id'),
            "duration": info.get('duration'),
            "uploader": info.get('uploader'),
            "thumbnail": info.get('thumbnail'),
            "webpage_url": info.get('webpage_url'),
            "selected_formats": selected_formats  # 这里包含选定格式的全部原始字段
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
