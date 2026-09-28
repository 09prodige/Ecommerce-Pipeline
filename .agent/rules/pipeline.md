---
trigger: always_on
---

# Règles projet — SOKO Commerce Pipeline (TP2/TP3)

## Contexte
- Stack Docker Compose : zookeeper, kafka, api (FastAPI), producer, consumer, spark_job, metabase, prometheus, grafana, cadvisor.
- PostgreSQL = Supabase distant (schéma `public` = données TP1, schéma `analytics` = sorties Spark).
- Docker fonctionne : ne pas redémarrer/reconstruire la stack sans demande explicite.

## Données
- `datalake/raw/**` : fichiers > 30 Mo en croissance continue → JAMAIS lus en entier. Max `Get-Content <f> -TotalCount 5` ou `(Get-Content <f> | Measure-Object -Line).Lines`.
- Ne jamais modifier ni supprimer le Data Lake.

## Docker
- Logs : `docker logs <conteneur> --tail 50` uniquement (jamais `-f`).
- État : `docker ps --format "table {{.Names}}\t{{.Status}}"`.
- Requêtes Prometheus depuis l'hôte : `curl -m 10 "http://localhost:9090/api/v1/query?query=..."`.

## Réseau
- Entre conteneurs : nom de service (`http://prometheus:9090`, `kafka:9092`), jamais `localhost`.
- Grafana → datasource Prometheus = `http://prometheus:9090`.
- Docker Desktop Windows : cAdvisor n'expose pas le label `name` → ne pas filtrer `{name!=""}`.

## Secrets
- Identifiants Supabase dans `.env` uniquement, référencés via `${DB_PASSWORD}` dans docker-compose.
