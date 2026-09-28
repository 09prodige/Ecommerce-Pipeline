# Architecture SOKO COMMERCE - Pipeline Data (TP2)

## 1. Schéma de l'Architecture

```mermaid
flowchart TD
    %% Définition des sources
    subgraph Sources ["1. Sources de Données"]
        API[API Actions Utilisateurs\n(Python/FastAPI)]
        DB_REF[(PostgreSQL - SOKO)\nDonnées de référence]
    end

    %% Ingestion
    subgraph Ingestion ["2. Ingestion & Streaming"]
        PROD[Kafka Producer\n(Python)]
        KAFKA[Apache Kafka\nTopic: user_actions]
    end

    %% Stockage Brut
    subgraph DataLake ["3. Data Lake (Stockage Brut)"]
        DL_RAW_API[📁 /datalake/raw/api_events/]
        DL_RAW_REF[📁 /datalake/raw/reference_data/]
    end

    %% Traitement
    subgraph Traitement ["4. Traitement & Agrégation"]
        SPARK[Apache Spark / PySpark\nNettoyage & Agrégation]
    end

    %% Stockage Propre
    subgraph Serving ["5. Stockage Analytique"]
        DB_ANALYTICS[(PostgreSQL - SOKO)\nSchéma 'analytics']
    end

    %% Restitution & Observabilité
    subgraph DataViz ["6. Restitution & Observabilité"]
        METABASE[Metabase\nDashboard Métier]
        GRAFANA[Grafana\nDashboard Infrastructure]
        PROM[Prometheus\nCollecte de métriques]
    end

    %% Flux de données
    API -- "Événements JSON (clics, vues)" --> PROD
    PROD -- "Streaming" --> KAFKA
    
    KAFKA -- "Consommateur périodique" --> DL_RAW_API
    DB_REF -- "Export initial/périodique" --> DL_RAW_REF
    
    DL_RAW_API --> SPARK
    DL_RAW_REF --> SPARK
    
    SPARK -- "Jointure (Enrichissement)\nÉcriture JDBC" --> DB_ANALYTICS
    
    DB_ANALYTICS -- "Requêtes SQL" --> METABASE
    
    %% Monitoring
    KAFKA -. "Métriques" .-> PROM
    SPARK -. "Métriques" .-> PROM
    DB_ANALYTICS -. "Métriques" .-> PROM
    PROM --> GRAFANA
```

## 2. Description des Composants

1. **Source 1 (API)** : Un script Python simulant une API qui génère un flux continu d'événements (JSON). Exemple : `{ "user_id": "...", "listing_id": "...", "action_type": "view", "timestamp": "..." }`.
2. **Source 2 (Référence)** : Les données métier du TP1 (`profiles`, `categories`, `listings`, `offers`, `deals`, `reviews`). Ces données peuvent être exportées dans le Data Lake sous forme CSV/JSON, ou lues directement par Spark en JDBC.
3. **Ingestion (Kafka)** : Le flux API est envoyé dans un topic Kafka `user_actions` par un Producer Python.
4. **Data Lake** : Un volume monté en local dans Docker (dossier partagé).
   - Les événements Kafka y sont sauvegardés sous forme de fichiers.
   - Les données de référence s'y trouvent pour le traitement "à froid".
5. **Traitement (PySpark)** : Un script lit les événements bruts du Data Lake, croise ces données avec les informations des listings et des profils, effectue des nettoyages et des agrégations (ex. *nombre de vues et d'offres par annonce/catégorie*), puis sauvegarde le résultat propre dans PostgreSQL.
6. **Stockage (PostgreSQL)** : La donnée propre atterrit dans un schéma dédié `analytics` au sein de la base existante.
7. **Data Viz & Monitoring** : 
   - **Metabase** permet d'exploiter les tables du schéma `analytics` via des dashboards interactifs (Dashboard Métier).
   - **cAdvisor** (L'espion) : Outil Google monté sur l'hôte Docker (via des volumes `/var/run` et `/var/lib/docker/`) pour mesurer en temps réel la consommation (CPU, RAM) de chaque conteneur.
   - **Prometheus** (Le carnet de santé) : Base de données temporelle configurée (via `prometheus.yml`) pour requêter cAdvisor (`http://cadvisor:8080/metrics`) toutes les 15 secondes. Il conserve l'historique des métriques du pipeline.
   - **Grafana** (Le tableau de bord) : Connecté à Prometheus en interne (`http://prometheus:9090`), il permet de visualiser les courbes de santé de l'infrastructure (ex: consommation mémoire avec la requête PromQL `container_memory_usage_bytes / 1024 / 1024`). Tout transite par le réseau virtuel fermé `soko_network`.
