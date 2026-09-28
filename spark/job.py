import time
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, to_date, lit, when

# Configuration Postgres
DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "soko_db")
DB_USER = os.environ.get("DB_USER", "soko_admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "soko_password")
JDBC_URL = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
JDBC_PROPERTIES = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "org.postgresql.Driver"
}

DATALAKE_ROOT = "/datalake/raw"

def process_data(spark):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Démarrage du traitement PySpark...")
    
    # 1. Lecture des événements de l'API (Source 1)
    events_path = f"{DATALAKE_ROOT}/api_events/*.jsonl"
    try:
        df_events = spark.read.json(events_path)
        # Nettoyage : suppression des doublons basés sur l'ID de l'événement
        if 'event_id' in df_events.columns:
            df_events = df_events.dropDuplicates(['event_id'])
    except Exception as e:
        print(f"Aucun événement trouvé ou erreur de lecture: {e}")
        return

    # 2. Lecture des données de référence (Source 2)
    try:
        df_listings = spark.read.csv(f"{DATALAKE_ROOT}/reference_data/listings.csv", header=True, inferSchema=True)
        df_profiles = spark.read.csv(f"{DATALAKE_ROOT}/reference_data/profiles.csv", header=True, inferSchema=True)
    except Exception as e:
        print(f"Données de référence non prêtes: {e}")
        return

    # 3. Enrichissement (Jointures)
    df_enriched = df_events.join(df_listings, df_events.listing_id == df_listings.id, "left") \
                           .drop(df_listings.id) \
                           .withColumnRenamed("title", "listing_title")

    # 4. Agrégation 1 : Métriques par Annonce (Listing)
    df_listing_metrics = df_enriched.groupBy("listing_id", "listing_title") \
        .agg(
            count(when(col("action_type") == "view_listing", True)).alias("total_views"),
            count(when(col("action_type") == "like_listing", True)).alias("total_likes"),
            count(when(col("action_type") == "create_offer", True)).alias("total_offers"),
            count(when(col("action_type") == "send_message", True)).alias("total_messages")
        )

    # 5. Agrégation 2 : Activité Globale par Jour
    df_daily_activity = df_events.withColumn("date", to_date(col("timestamp"))) \
        .groupBy("date", "action_type") \
        .agg(count("*").alias("total_actions"))

    # 6. Écriture dans PostgreSQL (Schéma 'analytics')
    try:
        # On écrase/met à jour les tables analytiques
        df_listing_metrics.write.jdbc(url=JDBC_URL, table="analytics.listing_metrics", mode="overwrite", properties=JDBC_PROPERTIES)
        df_daily_activity.write.jdbc(url=JDBC_URL, table="analytics.daily_activity", mode="overwrite", properties=JDBC_PROPERTIES)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Écriture dans PostgreSQL réussie !")
    except Exception as e:
        print(f"Erreur lors de l'écriture JDBC dans Postgres: {e}")

if __name__ == "__main__":
    print("Initialisation de PySpark...")
    # On initialise Spark avec le driver JDBC pour Postgres
    spark = SparkSession.builder \
        .appName("SokoDataPipeline") \
        .master("local[*]") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    # Boucle infinie pour simuler un traitement Micro-Batch (Toutes les 60 secondes)
    while True:
        process_data(spark)
        print("Attente de 60 secondes avant le prochain traitement...")
        time.sleep(60)
