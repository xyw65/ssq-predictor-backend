FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 初始化数据
RUN python -c "import json; json.dump({'historical_data': {}, 'performance_ranking': [], 'eliminated_methods': [], 'next_period': '2026017', 'data_source': '', 'last_update': '', 'evaluation_periods': 0, 'evaluation_note': ''}, open('ssq_data.json', 'w'), ensure_ascii=False, indent=2)"

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
