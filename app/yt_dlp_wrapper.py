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

    def _map_format_to_interface(self, fmt: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据 interfaceKey.json 的定义映射单个格式对象的字段
        """
        return {
            "format_id": str(fmt.get('format_id', '')),
            "format_note": fmt.get('format_note', ''),
            "height": fmt.get('height'),
            "width": fmt.get('width'),
            "ext": fmt.get('ext', ''),
            "vcodec": fmt.get('vcodec', ''),
            "acodec": fmt.get('acodec', ''),
            "dynamic_range": fmt.get('dynamic_range', ''),
            "container": fmt.get('container', ''),
            "protocol": fmt.get('protocol', ''),
            "video_ext": fmt.get('video_ext', 'none'),
            "audio_ext": fmt.get('audio_ext', 'none'),
            "resolution": fmt.get('resolution', ''),
            "aspect_ratio": fmt.get('aspect_ratio'),
            "filesize": fmt.get('filesize'),
            "filesize_approx": fmt.get('filesize_approx'),
            "http_headers": fmt.get('http_headers', {}),
            "format": fmt.get('format', ''),
            "url": fmt.get('url', '')
        }

    def _map_to_interface_format(self, info: Dict[str, Any], formats: List[Dict[str, Any]], best_formats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        根据 interfaceKey.json 的定义映射顶层响应字段
        """
        # 确定 media_type
        # 如果有视频流则是 video，否则是 audio
        has_video = any(f.get('vcodec') != 'none' and f.get('vcodec') is not None for f in formats)
        media_type = "video" if has_video else "audio"

        return {
            "id": info.get('id', ''),
            "title": info.get('title', ''),
            "thumbnail": info.get('thumbnail', ''),
            "channel_id": info.get('channel_id', ''),
            "channel_url": info.get('channel_url', ''),
            "duration": info.get('duration'),
            "webpage_url": info.get('webpage_url', ''),
            "media_type": media_type,
            "needs_merge": any(f.get('needs_merge') for f in formats if f.get('vcodec') != 'none'),
            "original_url": info.get('original_url', info.get('webpage_url', '')),
            "formats": [self._map_format_to_interface(f) for f in formats],
            "best_formats": [self._map_format_to_interface(f) for f in best_formats]
        }

    def get_raw_info(self, url, enable_remote: Optional[bool] = None) -> Dict[str, Any]:
        """
        获取视频的原始信息（相当于 yt-dlp --dump-json）
        并过滤 formats 数组：只保留所有视频轨道 + 一个最佳音频轨道
        同时按照 interfaceKey.json 定义的格式返回
        """
        info = self._extract_video_info(url, enable_remote=enable_remote)

        if 'formats' in info:
            video_formats = []
            audio_formats = []

            # 1. 分类视频和音频并添加 needs_merge 标记
            for fmt in info['formats']:
                vcodec = fmt.get('vcodec')
                acodec = fmt.get('acodec')

                is_video = vcodec and vcodec != 'none'
                is_audio = acodec and acodec != 'none'

                if is_video:
                    fmt['needs_merge'] = not is_audio
                    video_formats.append(fmt)
                elif is_audio:
                    audio_formats.append(fmt)

            # 2. 筛选最佳音频 (优先考虑 m4a 且码率最高)
            best_audio = None
            if audio_formats:
                audio_formats.sort(key=lambda x: (1 if x.get('ext') == 'm4a' else 0, x.get('abr') or 0), reverse=True)
                best_audio = audio_formats[0]

            # 3. 找出最佳视频
            best_video = None
            if video_formats:
                video_formats.sort(key=lambda x: (x.get('height') or 0, x.get('tbr') or 0), reverse=True)
                best_video = video_formats[0]

            # 4. 重新构建 formats 列表：所有视频 + 1个最佳音频
            final_formats = video_formats
            if best_audio:
                final_formats.append(best_audio)

            # 5. 构建 best_formats 列表
            best_formats_list = []
            if best_video:
                best_formats_list.append(best_video)
                if best_video.get('needs_merge') and best_audio:
                    best_formats_list.append(best_audio)

            # 6. 映射到 interfaceKey.json 格式
            return self._map_to_interface_format(info, final_formats, best_formats_list)

        return info

    def get_download_links(self, url, format_id: Optional[str] = None, max_quality: Optional[int] = None, enable_remote: Optional[bool] = None) -> Dict[str, Any]:
        """
        获取视频的最佳下载链接
        按照 interfaceKey.json 定义的格式返回
        """
        info = self._extract_video_info(url, enable_remote=enable_remote)
        available_formats = info.get('formats', [])

        selected_formats = []
        best_audio = None

        # 预先找到最佳音频
        audio_only = [f for f in available_formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
        if audio_only:
            audio_only.sort(key=lambda x: (1 if x.get('ext') == 'm4a' else 0, x.get('abr') or 0), reverse=True)
            best_audio = audio_only[0]

        if format_id:
            for fmt in available_formats:
                if str(fmt.get('format_id')) == format_id:
                    # 标记 needs_merge
                    fmt['needs_merge'] = (fmt.get('vcodec') != 'none' and fmt.get('acodec') == 'none')
                    selected_formats.append(fmt)
                    # 如果选中的是纯视频且需要合并，则自动加上最佳音频
                    if fmt['needs_merge'] and best_audio:
                        selected_formats.append(best_audio)
                    break
        else:
            # 自动筛选最佳
            best_video = None
            video_only = [f for f in available_formats if f.get('vcodec') != 'none']
            if video_only:
                if max_quality:
                    video_only = [f for f in video_only if (f.get('height') or 0) <= max_quality]
                if video_only:
                    video_only.sort(key=lambda x: (x.get('height') or 0, x.get('tbr') or 0), reverse=True)
                    best_video = video_only[0]

            if best_video:
                best_video['needs_merge'] = (best_video.get('acodec') == 'none' or not best_video.get('acodec'))
                selected_formats.append(best_video)
                if best_video['needs_merge'] and best_audio:
                    selected_formats.append(best_audio)

        # 返回统一的 interface 格式，其中 formats 数组只包含选中的链接
        return self._map_to_interface_format(info, selected_formats, selected_formats)

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
