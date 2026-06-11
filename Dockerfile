# ── Build ──────────────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

# Installer les dépendances Python en premier (layer mis en cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Répertoire pour la base de données SQLite (monté en volume)
RUN mkdir -p /data

EXPOSE 5000

# ── Entrée : Gunicorn pour la prod, main.py reste accessible ──
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
