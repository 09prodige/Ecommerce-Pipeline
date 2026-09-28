import os
import shutil

# Files to keep
KEEP_FILES = [
    'TP_Audit_et_Cartographie_SOKO_COMMERCE.md',
    'simulate_data_tp1.sql',
    'cleanup.py'
]

KEEP_DIRS = [
    'docs'
]

# Create new directories for TP2
TP2_DIRS = [
    'api',
    'kafka',
    'spark',
    'datalake',
    'datalake/raw',
    'datalake/raw/api_events',
    'datalake/raw/reference_data',
    'postgres',
    'postgres/init',
    'dataviz',
    'monitoring',
    'monitoring/prometheus',
    'monitoring/grafana'
]

for d in TP2_DIRS:
    os.makedirs(d, exist_ok=True)

# Delete unwanted files and directories
for item in os.listdir('.'):
    if item in KEEP_FILES or item in KEEP_DIRS or item in TP2_DIRS or item.startswith('.'):
        # Don't touch hidden files like .git or the ones we keep
        continue
        
    try:
        if os.path.isdir(item):
            shutil.rmtree(item)
        else:
            os.remove(item)
    except Exception as e:
        print(f"Could not remove {item}: {e}")

print("Workspace cleaned and TP2 structure created.")
