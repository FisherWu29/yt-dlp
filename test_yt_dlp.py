#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 yt-dlp 对不支持 URL 的处理
"""

import time
from yt_dlp import YoutubeDL

def test_url_support():
    """测试不同 URL 的支持情况和处理时间"""
    urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # 有效的 YouTube URL
        'http://example.com/not-a-video',  # 无效的 URL
        'https://www.baidu.com',  # 有效的网站，但不是视频网站
    ]

    for url in urls:
        print(f"\n测试 URL: {url}")
        start_time = time.time()

        try:
            # 创建 yt-dlp 实例
            ydl = YoutubeDL({
                'quiet': True,
                'no_warnings': True,
                'timeout': 5,  # 设置超时时间为 5 秒
                'skip_download': True,
                'extract_flat': False,
                'force_json': True,
                'simulate': True,
            })

            # 尝试提取信息
            info = ydl.extract_info(url, download=False)
            print(f"提取成功: {info.get('title', '无标题')}")
        except Exception as e:
            print(f"错误: {type(e).__name__}: {e}")
        finally:
            end_time = time.time()
            print(f"处理时间: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    test_url_support()
