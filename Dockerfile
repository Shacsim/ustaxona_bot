FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# pg_dump — bazaning kunlik zaxirasini adminga yuborish uchun
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Migratsiya + bot (docker-compose command orqali ham override qilinadi)
CMD ["sh", "-c", "alembic upgrade head && python main.py"]
