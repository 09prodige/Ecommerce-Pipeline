# TP2 — Pipeline Data temps rÃ©el & plateforme Data : SOKO COMMERCE

Bienvenue dans le dÃ©pÃ´t de notre plateforme de donnÃ©es de bout en bout pour SOKO COMMERCE. Ce projet s'inscrit dans la suite de l'audit et de la cartographie des donnÃ©es rÃ©alisÃ©s lors du TP1.

L'objectif de ce projet est de construire une architecture Data complÃ¨te, automatisÃ©e et observable, intÃ©grant l'ingestion de donnÃ©es en streaming, le stockage dans un Data Lake, le traitement par lots (micro-batching), la persistance dans un Data Warehouse et l'exposition via des dashboards BI.

---

## 1. Architecture DÃ©taillÃ©e

Le pipeline de donnÃ©es est conÃ§u autour d'une architecture orientÃ©e streaming et traitement par micro-batch :

```mermaid
flowchart LR
    subgraph Sources
        A[API Soko Commerce] 
        B[Reference Data CSV]
    end

    subgraph Ingestion & Streaming
        P[Producer Python]
        K[Apache Kafka]
        C[Consumer Python]
    end

    subgraph Stockage Datalake
        DL[(Data Lake Local\n/raw)]
    end

    subgraph Traitement Spark
        S[Apache Spark\nMicro-batch]
    end

    subgraph Stockage & Data Warehouse
        PG[(PostgreSQL\nSupabase)]
    end

    subgraph Visualisation & BI
        M[Metabase]
    end

    subgraph ObservabilitÃ©
        Prom[Prometheus]
        Graf[Grafana]
        cAdv[cAdvisor]
    end

    %% Flux de donnÃ©es
    A --> P
    P -->|Envoi Ã©vÃ©nements| K
    K -->|Consommation| C
    C -->|Ã‰criture JSON bruts| DL
    B -->|MÃ©tadonnÃ©es| DL
    DL -->|Lecture donnÃ©es brutes| S
    S -->|AgrÃ©gation & Clean| PG
    PG -->|RequÃªtes SQL| M

    %% Monitoring
    cAdv -.->|MÃ©triques conteneurs| Prom
    Prom -.->|Visualisation MÃ©triques| Graf
```

### Explication des composants :
- **API SOKO COMMERCE (Source 1)** : GÃ©nÃ¨re en continu des Ã©vÃ©nements de ventes, clics et activitÃ© des utilisateurs.
- **DonnÃ©es de rÃ©fÃ©rence (Source 2)** : Fichiers statiques (ex: profils utilisateurs) prÃ©sents dans le Data Lake, servant Ã  enrichir les donnÃ©es en temps rÃ©el.
- **Kafka (Broker)** : Agit comme un tampon (buffer) absorbant les pics de charge de l'API.
- **Consumer** : Lit les messages Kafka et les sauvegarde sous forme de fichiers bruts dans le **Data Lake**.
- **PySpark** : ExÃ©cute des micro-batchs pour lire les donnÃ©es brutes (Raw), appliquer des rÃ¨gles de qualitÃ© (typage, gestion des doublons, agrÃ©gation) et produire des donnÃ©es propres (Clean).
- **Supabase (PostgreSQL)** : Sert d'entrepÃ´t de donnÃ©es (Data Warehouse) hÃ©bergeant les tables structurÃ©es prÃªtes Ã  l'analyse.
- **Metabase** : Outil de Data Visualization connectÃ© Ã  PostgreSQL pour l'analyse mÃ©tier.
- **Prometheus & Grafana (avec cAdvisor)** : Stack d'observabilitÃ© surveillant l'infrastructure (consommation RAM/CPU des conteneurs) et le pipeline.

---

## 2. Structure du DÃ©pÃ´t

```text
TP2/
â”œâ”€â”€ docker-compose.yml       # Orchestration de l'ensemble des services
â”œâ”€â”€ README.md                # Documentation complÃ¨te du projet
â”œâ”€â”€ api/                     # Code source de l'API FastAPI et du Producer Kafka
â”œâ”€â”€ kafka/                   # Code du Consumer Kafka
â”œâ”€â”€ spark/                   # Scripts de traitement de donnÃ©es PySpark
â”œâ”€â”€ datalake/                # RÃ©pertoire local stockant les donnÃ©es brutes (raw)
â”œâ”€â”€ postgres/                # Scripts d'initialisation de la base de donnÃ©es (DDL)
â””â”€â”€ monitoring/              # Configuration Prometheus (et autres outils de monitoring)
```

---

## 3. PrÃ©requis et DÃ©ploiement

Pour lancer le projet, vous devez avoir installÃ© **Docker** et **Docker Compose** sur votre machine.

### Instructions de dÃ©marrage :

1. Clonez ce dÃ©pÃ´t.
2. Assurez-vous qu'aucun autre service n'occupe les ports utilisÃ©s (8000, 9092, 3000, 3001, 9090, etc.).
3. Lancez l'ensemble de la stack avec la commande suivante :
   ```bash
   docker compose up -d
   ```
4. VÃ©rifiez que tous les conteneurs sont `Up` avec la commande `docker ps`.

### AccÃ¨s aux services :
- **API Soko** : `http://localhost:8000/docs` (Interface Swagger pour interagir avec l'API)
- **Metabase (BI)** : `http://localhost:3000` (Setup initial requis lors du premier lancement)
- **Grafana (Monitoring)** : `http://localhost:3001` (Credentials: `admin` / `admin`)
- **Prometheus** : `http://localhost:9090`

---

## 4. Exploitation et ObservabilitÃ©

### Data Visualization (Metabase)
Le dashboard Metabase permet de suivre les KPIs de la plateforme SOKO Commerce. Connectez Metabase Ã  la base PostgreSQL (Supabase) pour visualiser :
- L'activitÃ© quotidienne de la plateforme.
- Le top des vendeurs et l'engagement des annonces.

### Infrastructure Monitoring (Grafana + Prometheus)
GrÃ¢ce Ã  l'intÃ©gration de cAdvisor et Prometheus, vous pouvez observer les ressources de votre infrastructure depuis Grafana.
Dans Grafana, configurez `http://prometheus:9090` comme source de donnÃ©es et utilisez ces requÃªtes PromQL :
- **Utilisation CPU par conteneur** : `rate(container_cpu_usage_seconds_total{name!=""}[1m])`
- **Utilisation MÃ©moire par conteneur** : `container_memory_usage_bytes{name!=""} / 1024 / 1024`

### Raw vs Clean
L'indicateur Raw vs Clean peut Ãªtre dÃ©duit en mesurant le volume des fichiers stockÃ©s dans le Data Lake (Raw) comparÃ© au volume de lignes intÃ©grÃ©es rÃ©guliÃ¨rement dans les tables de la base PostgreSQL (Clean).

---
*Projet rÃ©alisÃ© dans le cadre du TP2 - Nowledgeable*
