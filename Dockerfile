# 1. Базовый образ с Python
FROM python:3.10-slim

# 2. Рабочая директория
WORKDIR /app

# 3. Сначала копируем только requirements, чтобы кэшировать pip install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем весь код
COPY . .

# 5. По умолчанию запускаем скрипт
CMD ["python", "app.py"]