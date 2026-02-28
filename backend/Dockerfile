FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 初始化数据文件
RUN echo '{"historical_data": {}, "performance_ranking": [], "eliminated_methods": [], "next_period": "2026017", "data_source": "", "last_update": "", "evaluation_periods": 0, "evaluation_note": ""}' > ssq_data.json

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "2", "--timeout", "120", "app:app"]
