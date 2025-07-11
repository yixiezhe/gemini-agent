# 使用一个官方的 Python 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /usr/src/app

# 复制依赖文件并安装
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY ./app .

# 暴露端口，以便从 Windows 访问
EXPOSE 5000

# 容器启动时运行的命令
CMD ["python", "main.py"]