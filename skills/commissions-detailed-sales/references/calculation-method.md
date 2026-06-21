# Méthode de calcul + modèles de formules Excel (vérifiés)

Base de commission = **encaissement DU MOIS, net de TVA**, raisonné **paiement par
paiement** (jamais sur le total de la commande).

## Règles, par paiement retenu

Pour chaque ligne, on examine séparément le **1er paiement** (date/montant/mode) et le
**2e paiement** (date/montant/mode s'il existe) :

1. **Retenir** le paiement seulement si sa **date tombe dans le mois/année cible**.
2. **Exclure les gift vouchers** : si le mode contient `gift voucher`
   (ex. `GIFT VOUCHER-ADMIN`, `LANDMARK GIFT VOUCHER`, `GIFT VOUCHER-HK-015`), ou si
   la colonne « First payment type » = `GIFT VOUCHER`, le paiement **n'entre pas** dans
   la commission.
3. **Passage en HT** :
   - si **EXPORT**, **ou** mode contenant `no vat`/`not vat`, **ou** diviseur TVA = 1
     → montant **tel quel** (déjà HT / hors champ TVA) ;
   - sinon → **montant ÷ (1 + taux TVA)** (diviseur, ex. 1,20 pour 20 %).
4. **Inclure** services, frais de port et **lignes négatives** (retours/avoirs).
5. **Affecter au bon taux** selon le type de la ligne : `Bespoke` → taux Bespoke ;
   sinon → taux PAP.

Par vendeur : `CA PAP HT` et `CA Bespoke HT` séparés.
`Commission = CA PAP HT × taux PAP + CA Bespoke HT × taux Bespoke`.

> **Cas à signaler (ne pas trancher seul)** : frais de port / shipping sur une ligne
> **export** peuvent contenir de la TVA → à reconvertir. Les **lister** dans le rapport
> pour validation manuelle.

## Bloc d'hypothèses (cellules labellisées, référencées par les formules)

Sur l'onglet de sortie `Comm` (ou « Commissions [Mois Année] ») :

| Cellule | Libellé | Exemple |
|---|---|---|
| C1 | Mois (1–12) | 4 |
| C2 | Année | 2026 |
| C3 | Taux PAP | 0,05 |
| C4 | Taux Bespoke | 0,025 |
| C5 | Diviseur TVA (1 + taux) | 1,20  *(mettre **1** si HT / HKD)* |

## Colonnes auxiliaires (1 par ligne du journal — tout est traçable)

Ajouter 3 colonnes à droite du tableau « Detailed sales ». Remplacer les lettres
`{STAFF} {TYPE} {P1DATE} {P1AMT} {P1MODE} {P2DATE} {P2AMT} {P2MODE} {P1TYPE} {EXPORT}`
par les colonnes **détectées** (voir `column-detection.md`). `r` = n° de ligne.

**A. `Staff (clean)`** — neutralise casse/espaces (TRIM compresse aussi les espaces
internes ; la comparaison `=` d'Excel est insensible à la casse) :
```
=TRIM(${STAFF}r)
```

**B. `Bespoke?`** (1 = Bespoke, 0 = PAP) :
```
=IF(ISNUMBER(SEARCH("bespoke",${TYPE}r&"")),1,0)
```

**C. `Base HT mois (calc)`** — encaissement HT du mois pour la ligne (les 2 paiements,
gift vouchers exclus) :
```
=IF(AND(IFERROR(AND(YEAR(${P1DATE}r)=Comm!$C$2,MONTH(${P1DATE}r)=Comm!$C$1),FALSE),
       NOT(OR(ISNUMBER(SEARCH("gift voucher",${P1MODE}r&"")),
              EXACT(UPPER(TRIM(${P1TYPE}r&"")),"GIFT VOUCHER"))),
       ISNUMBER(${P1AMT}r)),
    IF(OR(ISNUMBER(SEARCH("export",${EXPORT}r&"")),
          ISNUMBER(SEARCH("no vat",${P1MODE}r&"")),
          ISNUMBER(SEARCH("not vat",${P1MODE}r&"")),
          Comm!$C$5=1),
       ${P1AMT}r, ${P1AMT}r/Comm!$C$5), 0)
+IF(AND(IFERROR(AND(YEAR(${P2DATE}r)=Comm!$C$2,MONTH(${P2DATE}r)=Comm!$C$1),FALSE),
        NOT(ISNUMBER(SEARCH("gift voucher",${P2MODE}r&""))),
        ISNUMBER(${P2AMT}r)),
    IF(OR(ISNUMBER(SEARCH("export",${EXPORT}r&"")),
          ISNUMBER(SEARCH("no vat",${P2MODE}r&"")),
          ISNUMBER(SEARCH("not vat",${P2MODE}r&"")),
          Comm!$C$5=1),
       ${P2AMT}r, ${P2AMT}r/Comm!$C$5), 0)
```
Le `&""` évite les `#VALEUR!` sur cellules vides/numériques ; `IFERROR(...,FALSE)`
neutralise les dates invalides (cellules vides, `1900-01-…`, texte).

> Si le fichier n'a **qu'un seul paiement** (pas de colonnes `Second payment`),
> supprimer le second bloc `+IF(...)`.

## Tableau Commissions (1 ligne par vendeur)

Lister les vendeurs **dédupliqués** (insensible casse/espaces — utiliser
`UNIQUE(TRIM(plage staff))` si disponible, sinon construire la liste à partir de
`Staff (clean)`). Plages : `CLEAN` = colonne *Staff (clean)*, `BASE` = *Base HT mois*,
`BES` = *Bespoke?*. Vendeur en `$B r`.

| Colonne | Formule |
|---|---|
| CA PAP HT | `=SUMPRODUCT((CLEAN=$Br)*(BES=0)*BASE)` |
| CA Bespoke HT | `=SUMPRODUCT((CLEAN=$Br)*(BES=1)*BASE)` |
| Taux PAP | `=$C$3` |
| Taux Bespoke | `=$C$4` |
| Commission | `=Cr*$C$3+Dr*$C$4` |

Ligne **Total** : `=SUM(...)` sur chaque colonne.

## Exemple concret VÉRIFIÉ — Volney, Avril 2026 (TVA 20 %, diviseur 1,20)

Colonnes détectées : STAFF=D, TYPE=H, P1=V/W/X, P2=Y/Z/AA, P1TYPE=AT, EXPORT=AO.
Résultats reproduits **à l'identique** par (a) le moteur Python `verify_commissions.py`,
(b) l'évaluateur de formules Excel indépendant `formulas`, et (c) l'onglet
`Commissions` existant du fichier client :

| Vendeur | CA PAP HT | Commission (×5 %) |
|---|---|---|
| Sony | 26 720,83 | 1 336,04 |
| Rodolphe | 20 700,01 | 1 035,00 |
| Alexandra | 9 812,50 | 490,63 |
| **TOTAL** | **57 233,34** | **2 861,67** |

(Onglet client : Sony 26 700 / Rodolphe 20 700 / Alexandra 9 813 — l'écart ≈ 0,08 %
vient d'arrondis manuels, justement ce que les formules auditables permettent de tracer.)
