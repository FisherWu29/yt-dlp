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

获取指定视频的完整信息及过滤后的可用格式列表。格式列表仅保留视频轨道和最佳音频轨道，字段已精简。

#### 请求信息

- **请求方法**：GET
- **请求路径**：/formats
- **请求参数**：
  | 参数名 | 类型 | 位置 | 必填 | 描述 |
  |--------|------|------|------|------|
  | url | string | Query | 是 | 视频URL |
  | enable_remote | boolean | Query | 否 | 是否启用远程组件绕过限制（默认true） |

#### 响应信息

- **响应状态码**：200 OK
- **响应格式**：JSON
- **响应字段**：
  | 字段名 | 类型 | 描述 |
  |--------|------|------|
  | id | string | 视频唯一标识 |
  | title | string | 视频标题 |
  | thumbnail | string | 视频缩略图URL |
  | channel_id | string | 频道ID |
  | channel_url | string | 频道URL |
  | duration | float | 视频时长（秒） |
  | webpage_url | string | 视频网页URL |
  | media_type | string | 媒体类型 ("video" 或 "audio") |
  | needs_merge | boolean | 是否需要合并音视频（针对DASH流） |
  | original_url | string | 原始请求URL |
  | formats | array | 过滤后的格式列表（所有视频轨道 + 1个最佳音频） |
  | best_formats | array | 最佳画质组合（包含最佳视频和配套音频） |

- **formats/best_formats 数组项**：
  | 字段名 | 类型 | 描述 |
  |--------|------|------|
  | format_id | string | 格式ID |
  | format_note | string | 格式说明（如 "1080p"） |
  | height | integer | 高度 |
  | width | integer | 宽度 |
  | ext | string | 文件扩展名 |
  | vcodec | string | 视频编码器 |
  | acodec | string | 音频编码器 |
  | dynamic_range | string | 动态范围 |
  | container | string | 容器格式 |
  | protocol | string | 传输协议 |
  | video_ext | string | 视频扩展名 |
  | audio_ext | string | 音频扩展名 |
  | resolution | string | 分辨率字符串 |
  | aspect_ratio | float | 宽高比 |
  | http_headers | object | 下载所需的HTTP头信息 |
  | url | string | 真实下载链接 |

#### 示例响应

```json
{
  "id": "Mb6H7trzMfI",
  "title": "Driving Xiaomi's Electric Car: Are we Cooked?",
  "thumbnail": "https://i.ytimg.com/vi/Mb6H7trzMfI/maxresdefault.jpg",
  "channel_id": "UC...",
  "channel_url": "https://www.youtube.com/@...",
  "duration": 925.0,
  "webpage_url": "https://www.youtube.com/watch?v=Mb6H7trzMfI",
  "media_type": "video",
  "needs_merge": true,
  "original_url": "https://www.youtube.com/watch?v=Mb6H7trzMfI",
  "formats": [
    {
      "format_id": "313",
      "format_note": "2160p",
      "height": 2160,
      "width": 3840,
      "ext": "webm",
      "vcodec": "vp9",
      "acodec": "none",
      "url": "https://...",
      "http_headers": { "User-Agent": "..." }
    },
    {
      "format_id": "140",
      "format_note": "medium",
      "ext": "m4a",
      "vcodec": "none",
      "acodec": "mp4a.40.2",
      "url": "https://..."
    }
  ],
  "best_formats": [
    { "format_id": "313", ... },
    { "format_id": "140", ... }
  ]
}
```

### 3. 获取下载链接

#### 接口描述

自动筛选最佳下载链接，或根据指定的 `format_id` 获取下载链接。返回结构与 `/formats` 保持一致，但 `formats` 数组仅包含选中的链接。

#### 请求信息

- **请求方法**：POST / GET
- **请求路径**：/download-link
- **请求参数 (Query 或 JSON)**：
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | url | string | 是 | 视频URL |
  | format_id | string | 否 | 特定格式ID |
  | max_quality | integer | 否 | 最大允许分辨率高度（自动筛选时生效） |

#### 响应信息

响应字段与 `/formats` 完全一致。

- 若请求指定了 `format_id` 且该格式为纯视频，返回的 `formats` 将包含该视频和 1 个最佳音频。
- 若未指定 `format_id`，将自动返回最佳视频和最佳音频。

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

### 1. Android (Java) 示例

假设使用 `OkHttp` 处理请求，并已集成 `ffmpeg-kit-android`。

```java
import com.arthenica.ffmpegkit.FFmpegKit;
import com.arthenica.ffmpegkit.ReturnCode;
import okhttp3.*;
import org.json.*;
import java.io.*;

public class VideoDownloader {
    private final OkHttpClient client = new OkHttpClient();
    private static final String BASE_URL = "http://localhost:8000";

    /**
     * 获取下载链接并处理合并逻辑
     */
    public void downloadAndProcess(String videoUrl, String formatId) {
        try {
            // 1. 请求下载链接
            JSONObject json = new JSONObject();
            json.put("url", videoUrl);
            json.put("format_id", formatId);

            Request request = new Request.Builder()
                    .url(BASE_URL + "/download-link")
                    .post(RequestBody.create(json.toString(), MediaType.parse("application/json")))
                    .build();

            Response response = client.newCall(request).execute();
            JSONObject data = new JSONObject(response.body().string());

            boolean needsMerge = data.getBoolean("needs_merge");
            JSONArray formats = data.getJSONArray("formats");

            if (needsMerge && formats.length() >= 2) {
                // 需要合并 (通常第一个是视频，第二个是音频)
                String videoLink = formats.getJSONObject(0).getString("url");
                String audioLink = formats.getJSONObject(1).getString("url");
                
                // 下载到临时文件
                File videoFile = downloadFile(videoLink, "temp_video.mp4");
                File audioFile = downloadFile(audioLink, "temp_audio.m4a");
                File outputFile = new File(getExternalFilesDir(null), "final_video.mp4");

                // 使用 FFmpeg 合并
                String cmd = String.format("-i %s -i %s -c copy -map 0:v:0 -map 1:a:0 %s",
                        videoFile.getAbsolutePath(), audioFile.getAbsolutePath(), outputFile.getAbsolutePath());
                
                FFmpegKit.executeAsync(cmd, session -> {
                    if (ReturnCode.isSuccess(session.getReturnCode())) {
                        Log.d("FFmpeg", "合并成功: " + outputFile.getPath());
                    }
                });
            } else {
                // 直接下载单文件
                String downloadLink = formats.getJSONObject(0).getString("url");
                downloadFile(downloadLink, "video.mp4");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private File downloadFile(String url, String fileName) throws IOException {
        Request request = new Request.Builder().url(url).build();
        Response response = client.newCall(request).execute();
        File file = new File(getExternalFilesDir(null), fileName);
        try (BufferedSink sink = Okio.buffer(Okio.sink(file))) {
            sink.writeAll(response.body().source());
        }
        return file;
    }
}
```

### 2. iOS (Swift) 示例

假设使用 `URLSession` 处理请求，并已集成 `ffmpeg-kit-ios`。

```swift
import Foundation
import ffmpegkit

class VideoService {
    let baseURL = "http://localhost:8000"
    
    /**
     * 获取下载链接并处理合并逻辑
     */
    func fetchAndProcess(videoURL: String, formatID: String?) {
        guard let apiURL = URL(string: "\(baseURL)/download-link") else { return }
        
        var request = URLRequest(url: apiURL)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = ["url": videoURL, "format_id": formatID ?? ""]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, _, error in
            guard let data = data, error == nil else { return }
            
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let formats = json["formats"] as? [[String: Any]],
               let needsMerge = json["needs_merge"] as? Bool {
                
                if needsMerge && formats.count >= 2 {
                    // 需要合并
                    let vURL = formats[0]["url"] as! String
                    let aURL = formats[1]["url"] as! String
                    
                    self.processMerge(videoURL: vURL, audioURL: aURL)
                } else {
                    // 直接下载
                    let downloadURL = formats[0]["url"] as! String
                    print("直接下载地址: \(downloadURL)")
                }
            }
        }.resume()
    }
    
    private func processMerge(videoURL: String, audioURL: String) {
        let docPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let vPath = docPath.appendingPathComponent("temp_v.mp4").path
        let aPath = docPath.appendingPathComponent("temp_a.m4a").path
        let outPath = docPath.appendingPathComponent("final.mp4").path
        
        // 步骤：1. 下载视频 2. 下载音频 3. 调用 FFmpeg (此处简化为 FFmpeg 执行)
        let command = "-i \(vPath) -i \(audioURL) -c copy -map 0:v:0 -map 1:a:0 \(outPath)"
        
        FFmpegKit.executeAsync(command) { session in
            let returnCode = session?.getReturnCode()
            if ReturnCode.isSuccess(returnCode) {
                print("iOS 合并成功: \(outPath)")
            }
        }
    }
}
```

## 七、最佳实践

1. **合并音视频**：如果接口返回 `needs_merge: true`，客户端应下载 `formats` 中的所有链接（通常是一个视频流和一个音频流），并使用 FFmpeg 等工具进行合并。
2. **选择最佳画质**：可以直接使用 `best_formats` 中的链接，它们已经是系统自动筛选出的最佳组合。
3. **使用HTTPS**：在生产环境中，建议使用HTTPS协议保护API通信。
4. **定期更新yt-dlp**：确保支持最新的视频平台和格式。

## 八、更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-02-09 | 1.1.0 | 精简接口返回字段，统一 `/formats` 和 `/download-link` 的响应结构，增加 `needs_merge` 和 `best_formats` 字段 |
| 2026-01-09 | 1.0.0 | 初始版本，包含健康检查、获取视频格式、获取下载链接接口 |

