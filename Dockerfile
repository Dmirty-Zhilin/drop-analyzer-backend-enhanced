# Dockerfile для Drop Analyzer Backend
# Оптимизированный для Coolify

FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание директории для базы данных (если используется SQLite)
RUN mkdir -p /app/instance

# Открытие порта
EXPOSE 5000

# Команда запуска
CMD ["python", "src/main.py"]

