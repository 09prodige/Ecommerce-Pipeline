-- ==============================================================
-- 03_nettoyage.sql : Script de nettoyage et correction (DML)
-- ==============================================================

-- 1. Complétude : Correction des profils sans nom ou nom vide
-- Substitution par un nom générique "Utilisateur Anonyme"
UPDATE profiles 
SET display_name = 'Utilisateur Anonyme'
WHERE display_name IS NULL OR TRIM(display_name) = '';

-- 2. Validité : Correction des prix négatifs dans les annonces
-- Imputation de la valeur absolue ou mise à zéro selon la règle métier
UPDATE listings 
SET price = ABS(price)
WHERE price < 0;

-- 3. Intégrité Référentielle : Suppression des annonces orphelines
-- Il est préférable de supprimer les annonces sans vendeur référencé
DELETE FROM listings 
WHERE seller_id NOT IN (SELECT id FROM profiles);

-- 4. Cohérence : Correction des statuts non standards dans les annonces
-- Mise par défaut à 'active' ou 'archived' pour les valeurs absurdes
UPDATE listings 
SET status = 'active'
WHERE status NOT IN ('active', 'reserved', 'sold', 'archived');

-- 5. Validité : Correction des deals avec montants négatifs
UPDATE deals 
SET agreed_price = ABS(agreed_price)
WHERE agreed_price < 0;

-- 6. Unicité : Suppression des doublons stricts dans listings
-- Nous conservons l'annonce la plus récente (MAX id ou MAX created_at)
DELETE FROM listings
WHERE id IN (
    SELECT id
    FROM (
        SELECT id,
               ROW_NUMBER() OVER (
                   PARTITION BY seller_id, title, price 
                   ORDER BY created_at DESC
               ) as rnum
        FROM listings
    ) t
    WHERE t.rnum > 1
);

-- 7. Validité : Correction des ratings invalides dans reviews
-- Plafonnement du rating entre 1 et 5
UPDATE reviews 
SET rating = 5 WHERE rating > 5;

UPDATE reviews 
SET rating = 1 WHERE rating < 1;
