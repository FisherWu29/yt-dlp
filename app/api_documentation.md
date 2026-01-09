# 视频下载服务 - API文档

## 一、概述

视频下载服务提供RESTful API接口，用于获取视频的可用格式和真实下载链接。该服务基于yt-dlp，支持多种视频平台，包括Bilibili、YouTube等。

## 二、基础信息

- **服务地址**：http://localhost:8000
- **API文档**：http://localhost:8000/docs（Swagger UI）
- **健康检查**：http://localhost:8000/health
- **请求格式**：JSON
- **响应格式**：JSON

## 三、接口列表

| 接口名称 | 请求方法 | 请求路径 | 功能描述 |
|----------|----------|----------|----------|
| 健康检查 | GET | /health | 检查服务是否正常运行 |
| 获取视频格式 | GET | /formats | 获取视频的可用格式列表 |
| 获取下载链接 | POST | /download-link | 获取视频的真实下载链接（POST方式） |
| 获取下载链接 | GET | /download-link | 获取视频的真实下载链接（GET方式） |

## 四、详细接口说明

### 1. 健康检查

#### 接口描述

检查服务是否正常运行。

#### 请求信息

- **请求方法**：GET
- **请求路径**：/health
- **请求参数**：无

#### 响应信息

- **响应状态码**：200 OK
- **响应格式**：JSON
- **响应字段**：
  | 字段名 | 类型 | 描述 |
  |--------|------|------|
  | status | string | 服务状态，固定为"ok" |
  | message | string | 服务状态描述 |
  | timestamp | string | 响应时间戳 |

#### 示例响应

```json
{
  "status": "ok",
  "message": "视频下载链接服务运行正常",
  "timestamp": "2026-01-09 10:00:00,000"
}
```

### 2. 获取视频格式

#### 接口描述

获取指定视频的可用格式列表，包括分辨率、码率、文件大小等信息。

#### 请求信息

- **请求方法**：GET
- **请求路径**：/formats
- **请求参数**：
  | 参数名 | 类型 | 位置 | 必填 | 描述 |
  |--------|------|------|------|------|
  | url | string | Query | 是 | 视频URL，如https://www.bilibili.com/video/BV1Gx411w7oE |
  | max_quality | integer | Query | 否 | 最大分辨率高度，如1080 |

#### 响应信息

- **响应状态码**：200 OK
- **响应格式**：JSON
- **响应字段**：
  | 字段名 | 类型 | 描述 |
  |--------|------|------|
  | title | string | 视频标题 |
  | formats | array | 可用格式列表 |
  | best_format | object | 最佳格式信息 |
  | thumbnail | string | 视频缩略图URL（可选） |
  | description | string | 视频描述（可选） |
  | webpage_url | string | 视频网页URL |
  | duration | float | 视频时长（秒，可选） |
  | uploader | string | 视频上传者（可选） |

- **formats数组项**：
  | 字段名 | 类型 | 描述 |
  |--------|------|------|
  | format_id | string | 格式ID |
  | format_note | string | 格式说明 |
  | ext | string | 文件扩展名 |
  | resolution | string | 分辨率 |
  | fps | float | 帧率（可选） |
  | filesize | integer | 文件大小（字节，可选） |
  | filesize_approx | integer | 预估文件大小（字节，可选） |
  | url | string | 直接下载链接（可选） |

#### 示例请求

```bash
curl "http://localhost:8000/formats?url=https://www.bilibili.com/video/BV1Gx411w7oE&max_quality=1080"
```

#### 示例响应

```json
{
  "title": "【原神】璃月港夜景",
  "formats": [
    {
      "format_id": "1080p60",
      "format_note": "1080P 60fps",
      "ext": "mp4",
      "resolution": "1920x1080",
      "fps": 60,
      "filesize": 123456789,
      "filesize_approx": 120000000,
      "url": null
    },
    {
      "format_id": "720p",
      "format_note": "720P",
      "ext": "mp4",
      "resolution": "1280x720",
      "fps": 30,
      "filesize": 67890123,
      "filesize_approx": 65000000,
      "url": null
    }
  ],
  "best_format": {
    "format_id": "1080p60",
    "format_note": "1080P 60fps",
    "ext": "mp4",
    "resolution": "1920x1080",
    "fps": 60,
    "filesize": 123456789,
    "filesize_approx": 120000000,
    "url": null
  },
  "thumbnail": "https://i0.hdslb.com/bfs/archive/abc123.jpg",
  "description": "璃月港夜景真美",
  "webpage_url": "https://www.bilibili.com/video/BV1Gx411w7oE",
  "duration": 120.5,
  "uploader": "旅行者"
}
```

### 3. 获取下载链接（POST方式）

#### 接口描述

通过POST请求获取指定视频的真实下载链接。

#### 请求信息

- **请求方法**：POST
- **请求路径**：/download-link
- **请求头**：Content-Type: application/json
- **请求体**：
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | url | string | 是 | 视频URL |
  | format_id | string | 否 | 特定格式ID，如"1080p60" |
  | max_quality | integer | 否 | 最大分辨率高度，如1080 |

#### 响应信息

- **响应状态码**：200 OK
- **响应格式**：JSON
- **响应字段**：
  | 字段名 | 类型 | 描述 |
  |--------|------|------|
  | status | string | 请求状态，"success"或"error" |
  | message | string | 请求结果描述 |
  | video_info | object | 视频基本信息 |
  | download_links | array | 下载链接列表 |

- **download_links数组项**：
  | 字段名 | 类型 | 描述 |
  |--------|------|------|
  | format_id | string | 格式ID |
  | format_note | string | 格式说明 |
  | ext | string | 文件扩展名 |
  | url | string | 真实下载链接 |

#### 示例请求

```bash
curl -X POST -H "Content-Type: application/json" -d '{"url": "https://www.bilibili.com/video/BV1Gx411w7oE", "format_id": "1080p60"}' http://localhost:8000/download-link
```

#### 示例响应

```json
{
  "status": "success",
  "message": "获取下载链接成功",
  "video_info": {
    "title": "【原神】璃月港夜景",
    "formats": [...],
    "best_format": {...},
    "thumbnail": "https://i0.hdslb.com/bfs/archive/abc123.jpg",
    "description": "璃月港夜景真美",
    "webpage_url": "https://www.bilibili.com/video/BV1Gx411w7oE",
    "duration": 120.5,
    "uploader": "旅行者"
  },
  "download_links": [
    {
      "format_id": "1080p60",
      "format_note": "1080P 60fps",
      "ext": "mp4",
      "url": "https://example.com/video_1080p60.mp4"
    }
  ]
}
```

### 4. 获取下载链接（GET方式）

#### 接口描述

通过GET请求获取指定视频的真实下载链接。

#### 请求信息

- **请求方法**：GET
- **请求路径**：/download-link
- **请求参数**：
  | 参数名 | 类型 | 位置 | 必填 | 描述 |
  |--------|------|------|------|------|
  | url | string | Query | 是 | 视频URL |
  | format_id | string | Query | 否 | 特定格式ID，如"1080p60" |
  | max_quality | integer | Query | 否 | 最大分辨率高度，如1080 |

#### 响应信息

- **响应状态码**：200 OK
- **响应格式**：JSON
- **响应字段**：与POST方式相同

#### 示例请求

```bash
curl "http://localhost:8000/download-link?url=https://www.bilibili.com/video/BV1Gx411w7oE&format_id=1080p60"
```

#### 示例响应

```json
{
  "status": "success",
  "message": "获取下载链接成功",
  "video_info": {
    "title": "【原神】璃月港夜景",
    "formats": [...],
    "best_format": {...},
    "thumbnail": "https://i0.hdslb.com/bfs/archive/abc123.jpg",
    "description": "璃月港夜景真美",
    "webpage_url": "https://www.bilibili.com/video/BV1Gx411w7oE",
    "duration": 120.5,
    "uploader": "旅行者"
  },
  "download_links": [
    {
      "format_id": "1080p60",
      "format_note": "1080P 60fps",
      "ext": "mp4",
      "url": "https://example.com/video_1080p60.mp4"
    }
  ]
}
```

## 五、错误处理

### 1. 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### 2. 常见错误码

| 状态码 | 错误类型 | 错误描述 |
|--------|----------|----------|
| 400 | Bad Request | 请求参数错误 |
| 500 | Internal Server Error | 服务器内部错误 |

### 3. 错误示例

```json
{
  "detail": "获取视频格式失败: expected string or bytes-like object, got 'HttpUrl'"
}
```

```json
{
  "detail": "获取视频格式失败: [BiliBili] 1xx411c7mN: This video may be deleted or geo-restricted"
}
```

## 六、使用示例

### 1. Python示例

```python
import requests

# 健康检查
def check_health():
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        print("服务健康状态:", response.json())
    else:
        print("服务异常:", response.text)

# 获取视频格式
def get_video_formats(url, max_quality=None):
    params = {"url": url}
    if max_quality:
        params["max_quality"] = max_quality
    response = requests.get("http://localhost:8000/formats", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("获取视频格式失败:", response.text)
        return None

# 获取下载链接（POST方式）
def get_download_link(url, format_id=None, max_quality=None):
    data = {"url": url}
    if format_id:
        data["format_id"] = format_id
    if max_quality:
        data["max_quality"] = max_quality
    response = requests.post("http://localhost:8000/download-link", json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print("获取下载链接失败:", response.text)
        return None

# 示例使用
if __name__ == "__main__":
    check_health()
    
    video_url = "https://www.bilibili.com/video/BV1Gx411w7oE"
    
    # 获取视频格式
    formats = get_video_formats(video_url, max_quality=1080)
    if formats:
        print(f"视频标题: {formats['title']}")
        print(f"可用格式数: {len(formats['formats'])}")
        print(f"最佳格式: {formats['best_format']['resolution']}")
    
    # 获取下载链接
    download_info = get_download_link(video_url, format_id="1080p60")
    if download_info:
        print(f"下载链接: {download_info['download_links'][0]['url']}")
```

### 2. JavaScript示例

```javascript
// 健康检查
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => console.log('服务健康状态:', data))
  .catch(error => console.error('服务异常:', error));

// 获取视频格式
const getVideoFormats = async (url, maxQuality) => {
  const params = new URLSearchParams({ url });
  if (maxQuality) {
    params.append('max_quality', maxQuality);
  }
  
  try {
    const response = await fetch(`http://localhost:8000/formats?${params}`);
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error('获取视频格式失败');
    }
  } catch (error) {
    console.error(error);
    return null;
  }
};

// 获取下载链接
const getDownloadLink = async (url, formatId, maxQuality) => {
  const data = { url };
  if (formatId) data.format_id = formatId;
  if (maxQuality) data.max_quality = maxQuality;
  
  try {
    const response = await fetch('http://localhost:8000/download-link', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error('获取下载链接失败');
    }
  } catch (error) {
    console.error(error);
    return null;
  }
};

// 示例使用
const videoUrl = 'https://www.bilibili.com/video/BV1Gx411w7oE';

getVideoFormats(videoUrl, 1080)
  .then(formats => {
    if (formats) {
      console.log(`视频标题: ${formats.title}`);
      console.log(`可用格式数: ${formats.formats.length}`);
      console.log(`最佳格式: ${formats.best_format.resolution}`);
    }
  });

getDownloadLink(videoUrl, '1080p60')
  .then(downloadInfo => {
    if (downloadInfo) {
      console.log(`下载链接: ${downloadInfo.download_links[0].url}`);
    }
  });
```

## 七、最佳实践

1. **使用HTTPS**：在生产环境中，建议使用HTTPS协议保护API通信
2. **添加缓存**：对于频繁请求的视频，可以添加缓存机制，减少API调用次数
3. **设置请求频率限制**：防止恶意请求导致服务过载
4. **使用CDN**：对于大文件下载，建议使用CDN加速
5. **定期更新yt-dlp**：确保支持最新的视频平台和格式
6. **监控API性能**：使用Prometheus和Grafana等工具监控API性能和可用性

## 八、更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-01-09 | 1.0.0 | 初始版本，包含健康检查、获取视频格式、获取下载链接接口 |

## 九、联系方式

如有问题或建议，请联系开发团队。

---

**文档更新日期**：2026-01-09
**API版本**：1.0.0
**适用环境**：所有支持HTTP/HTTPS的客户端
