import os
import psycopg2

conn = psycopg2.connect('postgresql://postgres.mtyfrgnufymefmpclkjt:Jesuislemeilleur2021.@aws-1-eu-west-1.pooler.supabase.com:5432/postgres')
cur = conn.cursor()

def audit_query(query):
    print(f"--- Query: {query} ---")
    cur.execute(query)
    results = cur.fetchmany(5)
    for r in results:
        print(r)
    print()

# Check some anomalies
audit_query("SELECT COUNT(*) FROM profiles WHERE email IS NULL OR email NOT LIKE '%@%';")
audit_query("SELECT COUNT(*) FROM listings WHERE price < 0;")
audit_query("SELECT COUNT(*) FROM listings WHERE profile_id NOT IN (SELECT id FROM profiles);")

