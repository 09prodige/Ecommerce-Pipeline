# Cartographie et Matrice de Contrôles Qualité (TP3)

## 1. Cartographie Mise à Jour (Schéma Cible)

Le modèle de données cible réside dans PostgreSQL (Supabase) et comprend les entités suivantes :
- **profiles** : Informations des utilisateurs (vendeurs ou acheteurs).
- **categories** : Hiérarchie des catégories de produits/services.
- **listings** : Annonces déposées par les vendeurs (reliées à `profiles` via `seller_id` et à `categories`).
- **deals** : Transactions validées entre un acheteur et un vendeur.
- **reviews** : Avis laissés post-transaction.

### Schéma relationnel simplifié :
`profiles(id)` <- `listings(seller_id)`
`categories(id)` <- `listings(category_id)`
`listings(id)` <- `deals(listing_id)`

---

## 2. Matrice des Contrôles Qualité

Afin d'assurer la fiabilité des données, nous définissons la matrice d'audit suivante :

| Entité | Attribut | Dimension Qualité | Règle Métier (Contrôle) | Gravité |
|--------|----------|--------------------|-------------------------|---------|
| `profiles` | `display_name` | Complétude | Le nom ne doit pas être NULL ni vide. | Haute |
| `profiles` | `phone` | Validité | Le téléphone doit être valide (longueur, pas de caractères étranges) ou NULL. | Moyenne |
| `listings` | `id` | Unicité | Il ne doit pas y avoir de doublons d'annonces strictes. | Haute |
| `listings` | `price` | Validité | Le prix doit être supérieur ou égal à 0 (`>= 0`). | Haute |
| `listings` | `seller_id` | Intégrité référentielle | Chaque annonce doit appartenir à un profil existant. | Critique |
| `listings` | `status` | Cohérence | Le statut doit faire partie d'une liste finie (`active`, `sold`, etc.). | Moyenne |
| `deals` | `agreed_price`| Validité | Le prix de la transaction doit être `>= 0`. | Haute |
| `deals` | `status` | Cohérence | Le statut d'un deal doit être `pending`, `accepted`, `completed` ou `cancelled`. | Moyenne |
| `reviews` | `rating` | Validité | La note doit être comprise entre 1 et 5. | Haute |
