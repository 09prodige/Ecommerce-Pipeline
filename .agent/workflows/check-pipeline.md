---
description: Vérifie l'état du pipeline SOKO sans rien redémarrer (lecture seule)
---

// turbo-all
1. `docker ps --format "table {{.Names}}\t{{.Status}}"`
2. `docker logs soko_consumer --tail 10`
3. `docker logs soko_spark --tail 15`
4. `curl -m 10 -s "http://localhost:9090/api/v1/targets" | Select-String -Pattern '"health":"(up|down)"' -AllMatches | ForEach-Object { $_.Matches.Value }`
5. `(Get-ChildItem datalake/raw/api_events | Measure-Object Length -Sum).Sum / 1MB`
6. Rendre un tableau : service → état ✓/✗, dernière activité, anomalie. Ne rien corriger sans demande.
