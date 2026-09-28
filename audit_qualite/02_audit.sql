-- ==============================================================
-- 02_audit.sql : Détection des anomalies dans les données brutes
-- ==============================================================

-- 1. Complétude : Détecter les profils sans nom ou avec nom vide
SELECT id, display_name 
FROM profiles 
WHERE display_name IS NULL OR TRIM(display_name) = '';

-- 2. Validité : Détecter les annonces avec des prix négatifs
SELECT id, title, price 
FROM listings 
WHERE price < 0;

-- 3. Intégrité Référentielle : Détecter les annonces orphelines (seller_id inexistant)
SELECT l.id, l.title, l.seller_id
FROM listings l
LEFT JOIN profiles p ON l.seller_id = p.id
WHERE p.id IS NULL;

-- 4. Cohérence : Détecter des statuts non standards dans les annonces
SELECT id, status 
FROM listings 
WHERE status NOT IN ('active', 'reserved', 'sold', 'archived', 'na');

-- 5. Validité : Détecter les deals avec des montants négatifs
SELECT id, agreed_price 
FROM deals 
WHERE agreed_price < 0;

-- 6. Unicité : Détecter les annonces postées en double (même vendeur, même titre, même prix)
SELECT seller_id, title, price, COUNT(*) as nb_doublons
FROM listings
GROUP BY seller_id, title, price
HAVING COUNT(*) > 1;

-- 7. Validité : Détecter les reviews avec un rating hors limites (1 à 5)
SELECT id, rating 
FROM reviews 
WHERE rating < 1 OR rating > 5;
