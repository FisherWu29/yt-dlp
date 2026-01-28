#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的 VideoDownloader 类对不支持 URL 的处理
"""

import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from yt_dlp_wrapper import VideoDownloader

def test_url_support():
    """测试不同 URL 的支持情况和处理时间"""
    urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # 有效的 YouTube URL
        'http://example.com/not-a-video',  # 无效的 URL
        'https://www.baidu.com',  # 有效的网站，但不是视频网站
    ]
    
    # 创建 VideoDownloader 实例
    downloader = VideoDownloader()
    
    for url in urls:
        print(f"\n测试 URL: {url}")
        start_time = time.time()
        
        try:
            # 尝试获取视频格式
            video_info = downloader.get_video_formats(url, enable_remote=False)
            print(f"获取成功: {video_info.title}")
        except Exception as e:
            print(f"错误: {type(e).__name__}: {e}")
        finally:
            end_time = time.time()
            print(f"处理时间: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    test_url_support()
