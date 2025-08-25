FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN useradd -m -u 1000 botuser \
    && mkdir -p /app/logs \
    && touch /app/logs/bot.log \
    && chown -R botuser:botuser /app
USER botuser

CMD bash -lc "alembic upgrade head && python run.py"
