# PentaRange web service. Intentionally NOT hardened: runs as root so the file-upload and
# .htaccess challenges actually have something to write to and something to override.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /var/www/pentarange

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl apache2-utils \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /var/www/pentarange/uploads /var/www/pentarange/static

EXPOSE 8000

# There is no --workers flag on purpose: a single process keeps the SQLite-less state and the
# uploaded-webshell demo deterministic.
CMD ["python", "main.py"]