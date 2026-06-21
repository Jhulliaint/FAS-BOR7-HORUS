---
name: commissions-detailed-sales
description: >-
  Calcule et vérifie les commissions mensuelles des vendeurs (staff) à partir d'un
  fichier « Detailed sales », dans Excel. À utiliser quand l'utilisateur veut
  calculer / vérifier / contrôler les commissions du staff pour un mois donné
  (« calcule les commissions de mars », « vérifie les commissions du staff pour
  avril 2026 », « commissions vendeurs »). Calculate / verify / check monthly
  sales-staff commissions from a Detailed sales workbook. Générique : multi-devises
  (EUR, GBP, HKD…), avec ou sans Bespoke, colonnage variable (détection par en-tête).
---

# Commissions — Detailed Sales

Construit, dans le classeur Excel ouvert, un tableau de **commissions mensuelles par
vendeur** à partir de l'onglet **« Detailed sales »**, avec des **formules auditables**
(l'utilisateur peut cliquer et tracer chaque chiffre), plus un **rapport de contrôle**.

**Générique par conception** : devises différentes, présence ou non de Bespoke, et
**colonnage variable** — les mêmes TYPES de colonnes existent toujours, mais pas aux
mêmes positions. **Toujours repérer les colonnes par leur EN-TÊTE, jamais par position.**

Base de calcul = **encaissement du mois, net de TVA**, raisonné **paiement par paiement**.

## When to use

- « Calcule / vérifie / contrôle les commissions [du mois] [des vendeurs] »
- « Commissions mensuelles / commissions staff / sales commissions » sur un fichier
  *Detailed sales*.
- Ne PAS utiliser pour : objectifs/bonus hors commission, conversion de devises,
  reporting de CA non lié aux commissions.

## Documents de référence (à lire avant d'agir)

- `references/column-detection.md` — localiser la ligne d'en-têtes + dictionnaire de
  mots-clés → colonnes (et le **piège export**).
- `references/calculation-method.md` — méthode exacte + **modèles de formules Excel
  vérifiés** (bloc d'hypothèses, colonnes auxiliaires, SUMPRODUCT par vendeur).
- `references/gotchas-from-real-files.md` — pièges réels (gift vouchers, « no vat »,
  noms de vendeurs, petite mesure, Bespoke hors fichier…).

## Procédure

### Étape 1 — Détecter dynamiquement les colonnes (par en-tête)
Localiser la ligne d'en-têtes (2 premiers repères parmi `Staff`, `Bespoke/Stock…`,
`First payment…` ; souvent ligne 1, ici 5 ou 7). Construire la correspondance en-tête →
colonne via `references/column-detection.md` (normaliser : minuscules/sans accents).
Repérer : staff, date, type (Bespoke/PAP), 1er & 2e paiement (date/montant/mode),
First payment type, Export or not, Currency. **Piège** : le drapeau export est
`Export or not`, pas la colonne « Total price… (VAT excl. for export) ».
**Done when:** chaque champ requis (staff, type, p1 date+montant) est associé à une
colonne ; toute colonne requise incertaine a été **confirmée par l'utilisateur**.

### Étape 2 — Demander les entrées
- **MOIS** : obligatoire (demander si absent).
- **ANNÉE** : optionnelle → si absente, **année en cours**.
- **TAUX** (cellules d'hypothèses) : PAP **5 %** par défaut ; Bespoke **2,5 %**
  (seulement s'il existe des lignes Bespoke) ; commission atelier/maker sur Bespoke si
  mentionnée.
- **TVA** : diviseur 1,20 (20 %) par défaut ; **1** si déjà HT / hors champ. Devise
  non-€ → proposer mais **confirmer** (ex. HKD = 0 %).
- **DEVISE** : colonne `Currency` si présente ; sinon **demander** (pas de symbole dans
  le format). **Ne jamais convertir** entre devises.
**Done when:** mois (et taux/TVA/devise) sont fixés dans des **cellules labellisées**.

### Étape 3 — Bloc d'hypothèses + colonnes auxiliaires (formules)
Créer le bloc d'hypothèses (Mois, Année, Taux PAP, Taux Bespoke, Diviseur TVA) et les
3 colonnes auxiliaires (`Staff (clean)`, `Bespoke?`, `Base HT mois`) avec les **modèles
de formules** de `references/calculation-method.md`, en substituant les lettres
**détectées**. Gère : paiement dans le mois, exclusion gift vouchers (mode OU
First payment type), HT (export / « no vat » → tel quel ; sinon ÷ diviseur), lignes
négatives incluses.
**Done when:** les colonnes auxiliaires se calculent sans `#VALEUR!`/`#REF!` sur tout le
journal.

### Étape 4 — Tableau Commissions par vendeur
Détecter **tous** les vendeurs ayant ≥ 1 encaissement dans le mois (liste **dédupliquée
insensible à la casse/espaces** — jamais de liste fixe). Une ligne par vendeur :
`CA PAP HT` | `CA Bespoke HT` | `Taux PAP` | `Taux Bespoke` | `Commission`
(SUMPRODUCT sur les colonnes auxiliaires), + ligne **Total**. Montants dans la devise du
fichier.
**Done when:** chaque vendeur a une ligne, le Total = somme des lignes, et tout référence
les colonnes auxiliaires + cellules de taux (pas de valeurs collées en dur).

### Étape 5 — Rapport de contrôle
Indiquer : nb de paiements retenus, total exclu (gift vouchers), lignes export, lignes
négatives, cas « port/shipping sur export » à valider, types ambigus (`petite mesure`),
et **taux/TVA/devise utilisés**. Signaler les limites (ex. Bespoke suivi hors du fichier).
**Done when:** le rapport est écrit à côté du tableau et liste explicitement les cas à
valider manuellement.

### Étape 6 — Contrôles qualité + vérification croisée
Vérifier l'absence de `#VALEUR!`/`#REF!` et la cohérence des totaux. Quand l'exécution
de code est disponible, **recouper** avec le script (voir ci-dessous) ; tout écart
notable est listé pour validation.
**Done when:** aucune erreur de formule, totaux cohérents, et l'écart éventuel avec le
script est expliqué.

## Vérification croisée (script Python)

`scripts/verify_commissions.py` recalcule les mêmes commissions directement depuis le
classeur (même méthode, détection par en-tête) — pour valider les formules Excel.

```bash
python3 scripts/verify_commissions.py "FICHIER.xlsx" --month 4 --year 2026 --vat 0.20
# options : --pap 0.05 --bespoke 0.025 --sheet "Detailed sales" --json
# zone sans TVA (HKD) : --vat 0
```

Sortie validée (Volney, avril 2026, TVA 20 %) — identique à l'évaluation indépendante des
formules Excel et à l'onglet `Commissions` du client :

```
STAFF                       CA_PAP_HT     CA_BESP_HT     COMMISSION
Sony                        26,720.83           0.00       1,336.04
Rodolphe                    20,700.01           0.00       1,035.00
Alexandra                    9,812.50           0.00         490.63
TOTAL                       57,233.34           0.00       2,861.67
```

## Sortie attendue

1. **Onglet/section « Commissions [Mois Année] »** : par vendeur → CA PAP HT |
   CA Bespoke HT | Taux PAP | Taux Bespoke | Commission ; + Total ; dans la devise du
   fichier.
2. **Rapport de contrôle** (cf. Étape 5).
3. **Formules auditables** référençant le journal et les cellules de taux/TVA — jamais de
   valeurs collées en dur.

## Gotchas (résumé — détails dans `references/gotchas-from-real-files.md`)

- Ligne d'en-têtes et positions de colonnes **variables** → détection par en-tête.
- **Export** : drapeau = `Export or not` (pas la colonne de prix).
- **Devise** souvent absente comme colonne → demander ; **jamais** de conversion.
- **TVA** par zone (HKD = 0 %).
- **Gift vouchers** dans le mode **et** `First payment type`.
- **« no vat »/« not vat »** dans le mode → montant tel quel.
- **Noms de vendeurs** : normaliser (casse + `TRIM`), dédupliquer.
- **`petite mesure`** : PAP par défaut, **demander** si taux Bespoke.
- **Bespoke parfois hors fichier** → le signaler comme limite.
