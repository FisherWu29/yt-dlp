# 使用官方Python镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 更新系统包并安装git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 克隆最新的yt-dlp仓库
RUN git clone https://github.com/FisherWu29/yt-dlp.git /app/yt-dlp

# 复制API服务代码到容器中
COPY . /app/app

# 安装API服务依赖
RUN pip install --no-cache-dir -r /app/app/requirements.txt

# 将yt-dlp添加到Python路径
ENV PYTHONPATH=/app/yt-dlp

# 暴露API服务端口
EXPOSE 8000

# 启动API服务
CMD ["python", "/app/app/app.py"]