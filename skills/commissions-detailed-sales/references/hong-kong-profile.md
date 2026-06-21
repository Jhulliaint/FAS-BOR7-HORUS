# Profil Hong Kong / Asia-Pacific (schéma multi-paliers)

**Hong Kong n'utilise PAS le partage PAP/Bespoke.** La base est le **CA encaissé du mois
COMBINÉ par vendeur** (HKD, **sans taxe** → diviseur TVA = 1), gift vouchers exclus —
exactement la colonne auxiliaire `Base HT mois` (cf. `calculation-method.md`), sommée par
vendeur **sans** distinguer Bespoke. Référence : onglet `Comm MM YYYY` du fichier payroll.

> Vérifié : la base par vendeur reproduit **à l'identique** les chiffres « REAL WITH NO
> TAX » du payroll (mai 2026 : JEAN-LOUP 562 798, ARMAND 121 220, CHRIS 120 640,
> total magasin 804 658).

## Structure de commission

Trois briques :

1. **Commission personnelle** (vendeurs) = `CA perso du vendeur × taux perso du vendeur`.
   Taux **par personne** (ex. ARMAND 1,7 %, CHRIS 2,0 %).
2. **Commission pool / magasin** = `CA magasin × taux palier`, **versée à chaque
   vendeur** (pas le manager). Palier selon `CA magasin / objectif magasin` :
   | Atteinte objectif magasin | Taux pool |
   |---|---|
   | < 60 % | 0,3 % |
   | 60–79 % | 0,8 % |
   | 80–99 % | 1,5 % |
   | ≥ 100 % | 2,2 % |
3. **Commission manager (JL)** = `CA magasin ×` (1,4 % si objectif **atteint**, sinon
   0,8 %). Le manager (Jean-Loup) reçoit **ceci à la place** du personnel + pool.

**Total par personne** :
- Vendeur : `commission personnelle + commission pool`.
- Manager : `commission manager (JL)` seule.

## Paramètres (à fournir chaque mois)

Hors du fichier « Detailed sales » → bloc d'hypothèses (issu de la légende du payroll +
saisie mensuelle) :

| Paramètre | Source | Ex. mai 2026 |
|---|---|---|
| Objectif magasin | saisi | 728 000 |
| Taux perso par vendeur | légende payroll | ARMAND 1,7 % · CHRIS 2,0 % |
| Objectif par vendeur (info) | saisi | ARMAND 290 000 · CHRIS 198 000 |
| Paliers pool | légende (stable) | 0,3 / 0,8 / 1,5 / 2,2 % |
| Taux manager (atteint / non) | légende (stable) | 1,4 % / 0,8 % |
| Manager | configuré | JEAN-LOUP |

Un gabarit JSON est fourni : `scripts/hk_config.example.json`.

## Formules Excel (placer dans un onglet `Comm`)

Bloc d'hypothèses (exemple) : `C1`=Mois, `C2`=Année, `C5`=**Diviseur TVA = 1** (HKD),
`C7`=Objectif magasin, `C8`=Manager (nom), `C9..C12`=paliers pool (0,003/0,008/0,015/
0,022), `C14`=JL atteint (0,014), `C15`=JL non atteint (0,008).

Colonne auxiliaire `Base HT mois` (identique à Europe ; avec `C5=1`, aucun retrait de
taxe). **Pas** de colonne `Bespoke?` ici.

- **CA par vendeur** (ligne vendeur en `$B r`, `CLEAN`/`BASE` = colonnes *Staff (clean)* /
  *Base HT mois*) :
  ```
  =SUMPRODUCT((CLEAN=$Br)*BASE)
  ```
- **CA magasin** : `=SUM(<colonne CA par vendeur>)`  *(ou `=SUM(BASE)`)*
- **% atteinte** : `=CA_magasin/$C$7`
- **Taux pool** : `=IF(%>=1,$C$12,IF(%>=0.8,$C$11,IF(%>=0.6,$C$10,$C$9)))`
- **Commission pool** (commune) : `=CA_magasin*Taux_pool`
- **Commission manager** : `=CA_magasin*IF(%>=1,$C$14,$C$15)`
- **Total par personne** (`CA r` = CA du vendeur, `Tauxperso r`, `Manager`=`$C$8`) :
  ```
  =IF(EXACT(UPPER(TRIM($Br)),UPPER(TRIM($C$8))),
      Commission_manager,
      CA r * Tauxperso r + Commission_pool)
  ```

## Exemple VÉRIFIÉ — Hong Kong, mai 2026

CA magasin 804 658 / objectif 728 000 = **110,5 %** → palier pool **2,2 %** (atteint).
Pool (par vendeur) = 17 702,48 ; commission manager = 11 265,21.

| Vendeur | CA (no tax) | Personnel | Pool / Manager | **Total** |
|---|---|---|---|---|
| JEAN-LOUP (manager) | 562 798 | — | 11 265,21 (JL 1,4 %) | **11 265,21** |
| ARMAND | 121 220 | 2 060,74 (1,7 %) | 17 702,48 | **19 763,22** |
| CHRIS | 120 640 | 2 412,80 (2,0 %) | 17 702,48 | **20 115,28** |
| **TOTAL** | **804 658** | | | **51 143,70** |

Identique à l'onglet `Comm 05 2026` du payroll (51 143,704) et au script
`verify_commissions.py --profile hk`.

## Vérification croisée

```bash
python3 scripts/verify_commissions.py "Hongkong_DETAILED_SALES.xlsx" \
    --month 5 --year 2026 --profile hk --hk-config scripts/hk_config.example.json
```
