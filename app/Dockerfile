# 使用官方的 Python 运行时作为父镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 文件到容器中
COPY requirements.txt .

# 安装项目依赖
RUN pip install --default-timeout=600 -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制项目文件到容器中
COPY . .

# 设置时区为中国标准时间
ENV TZ=Asia/Shanghai

# 挂载路径（在运行容器时通过 -v 参数挂载）
VOLUME /app/data
VOLUME /app/log

# 运行应用
CMD ["python", "main.py"]