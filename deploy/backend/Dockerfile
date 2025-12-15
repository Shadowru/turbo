# ---------- build stage ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Установите зависимости сборки (gcc, headers), если нужны
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# Пример для pip:
RUN pip install --prefix=/install -r requirements.txt

COPY src ./src

# ---------- runtime stage ----------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY --from=builder /install /usr/local
COPY src ./src

# статические файлы/артефакты, если нужно
# COPY assets ./assets

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]