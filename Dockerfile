# FROM python:3.11
# EXPOSE 5000
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install -r requirements.txt
# COPY . .
# CMD ["flask", "run", "--host", "0.0.0.0"]

### docker build -t flask-app .

### docker run -dp 5005:5000 -w /app -v "$(pwd):/app" flask-app

# 使用 Python 3.11 作为基础镜像
FROM python:3.11

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 运行 Flask 应用，使用 Gunicorn 作为 WSGI 服务器
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]