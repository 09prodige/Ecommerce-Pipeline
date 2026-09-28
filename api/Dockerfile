FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances systèmes nécessaires pour psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY producer.py .

# Par défaut on lance l'API, mais le docker-compose peut surcharger la commande pour le producer
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
