---
name: corthay-bl-stock-entry
description: >-
  Traite un PDF de Bon de Livraison (BL) Corthay / MAGE SAS (Mage Paris) et l'enregistre
  automatiquement comme entrée en stock VOLNEY dans l'onglet « Main products » (tableau
  STOCK, A6:AC) du classeur Excel ouvert. À utiliser dès que l'utilisateur soumet un BL
  Corthay / bon de livraison et veut une entrée en stock (« traite ce BL », « entrée en
  stock », « réception Corthay »). Process a Corthay/MAGE delivery-note PDF into a VOLNEY
  stock entry in the Main products sheet. Détection par en-tête ; normalisation via les
  listes du classeur (MODEL, MATERIAL, COLOR, PATINA, PIPING).
---

# Corthay BL → entrée en stock (Main products)

Quand l'utilisateur **soumet un PDF de BL Corthay** (MAGE SAS / Mage Paris), le traiter
**automatiquement** comme une **entrée en stock VOLNEY** dans l'onglet **« Main products »**
(tableau STOCK, colonnes **A:AC**, en-têtes ligne 6, données à partir de la ligne 7).
Procéder **sans reposer de questions**, sauf les cas explicitement listés (« Cas où
demander »).

Une **paire de chaussures = une ligne**. Ignorer les boîtes, semelles, talons, lacets,
élastiques, bouts fer, patins.

## When to use

- L'utilisateur fournit un **BL Corthay / bon de livraison MAGE** (PDF) et veut l'**entrée
  en stock**.
- Déclencheurs : « traite ce BL », « entrée en stock Corthay », « réception », « BL 3895 ».
- Ne PAS utiliser pour : un achat fournisseur tiers (≠ Corthay), une sortie/vente, un
  inventaire.

## Références (à lire avant d'agir)

- `references/bl-parsing.md` — extraction du BL (articles, à ignorer, nomenclature BAR
  CODE, zone « Commande client »), avec l'exemple **vérifié** du BL #3895.
- `references/stock-column-mapping.md` — correspondance **colonnes A:AC**, colonnes
  **formules à ne jamais toucher**, normalisation via les listes du classeur, règles
  techniques.

## Outil d'extraction (recommandé)

Quand l'exécution de code est disponible, extraire le BL de façon fiable avec :

```bash
python3 scripts/parse_bl.py "BL.pdf"      # nécessite : pip install pdfminer.six
```

Il renvoie : date + n° de BL, magasin, les lignes chaussures (réf, modèle, Ensemble/Set,
Passepoil, taille), le **BAR CODE** interne par ligne, et les **noms clients** de la zone
« Commande client ». Sortie validée sur le BL #3895 :

```
BL #3895  date=30/04/2026 (30042026)  store=VOLNEY
Clients: ['DAVID KNAFO', 'THIERRY AKA', 'MINA OFORIOKUMA']
ARB30042026001  ARCA BOUCLE  10.5  Box Calf Ardillat  Passepoil Cuivre        ARB299SPE
ARC30042026001  ARCA          9    Box Calf Ardillat  Passepoil Marron Moyen  ARC201ARD001
BEL30042026001  BELLA         9.5  Box Calf Ardillat  Passepoil Cuivre        BEL299SPE
```
(Toujours **normaliser** Model/Material/Color/Piping/Patina/Last contre les **listes du
classeur** — cf. `stock-column-mapping.md` — avant d'écrire.)

## Procédure

### Étape 1 — Lire le BL
Extraire pour chaque article : référence fournisseur (ex. `ARB299SPE`), nom de modèle,
**date** du BL (« du JJ/MM/AAAA »), **numéro** de BL, description (Ensemble/Set = matériau
+ couleur ; Patine si mentionnée ; Passepoil ; taille). **Ignorer** : boîtes (`BTE…`,
« Shoe Box »), semelles, talons, lacets, élastiques, bouts fer, patins.
**Done when:** la liste des paires (modèle, matériau, couleur, passepoil, taille) + date +
n° de BL est extraite, sans aucune ligne « accessoire ».

### Étape 2 — Trouver la première ligne vide
Lire la colonne **E (Model)** à partir de la **ligne 7** ; le premier index où Model est
vide = ligne de départ.
**Done when:** l'index de la première ligne vide est identifié.

### Étape 3 — Remplir une ligne par paire
Renseigner les colonnes selon `references/stock-column-mapping.md`. Points clés :
**C**=`First` ; **D**=BAR CODE `<préfixe><JJMMAAAA><###>` ; **E**=Model normalisé ;
**F/G**=Material/Color depuis Ensemble/Set ; **H**=Last (PULLMAN, ou SEVRES si indiqué) ;
**I**=Patina (vide sauf patine explicite) ; **J**=Piping ; **K**=Size ; **L**=`STOCK` ;
**P**=date BL `jj/mm/aaaa` ; **Q**=`FACTORY` ; **X**=**toujours vide**. **Ne JAMAIS écrire**
dans **A, B, O, R, U, V, Y** (colonnes formules). Ne rien écrire dans Comment (Z, AA).
**Done when:** chaque paire a une ligne remplie, sans avoir touché aux colonnes formules.

### Étape 4 — Vérification finale
Relire la plage saisie : **Category** (B) remplie (XLOOKUP a trouvé le modèle), **Stock
Qty** (V) = 1 par ligne, **Entry date** en JJ/MM/AAAA.
**Done when:** les 3 contrôles passent, sans `#N/A` en Category.

### Étape 5 — Compte-rendu
Tableau récapitulatif compact : ligne, BAR CODE, Model, Last, Color, Piping, Size, + la
plage de citation `Main products!A####:AC####`.
**Done when:** le récap est affiché avec la plage exacte.

### Étape 6 — Commande spéciale (affectation client)
Pour **chaque nom prénom de client entre crochets** dans la zone « Commande client » du
BL, demander à l'utilisateur (sous forme de **sélection**) à quelle ligne d'entrée
l'affecter. Ignorer les entrées qui ne sont pas des noms (ex. « SHOE BOXES »). Quand une
ligne est affectée : **L** devient `CS` et **M (Customer Name)** = le nom.
**Done when:** chaque nom client a été proposé à l'affectation et les lignes choisies
passent en `CS` + nom renseigné.

## Cas où demander AVANT d'écrire

- Le **modèle** extrait n'existe pas dans la liste **MODEL**.
- Une **couleur / matériau / patine** ne correspond à aucune valeur des listes
  (proposer la plus proche et **confirmer**).
- Le BL **n'est pas un BL Corthay** → demander la **source/raison** à utiliser.

## Règles techniques

- **Ne JAMAIS écrire** dans **A, B, O, R, U, V, Y** (formules de la table qui se
  propagent automatiquement).
- **X (Purchase price)** : toujours **vide** (produits manufacturés, pas achetés).
- **Q (From)** : toujours `FACTORY` pour les BL Corthay.
- N'ajouter **ni** Claude log, **ni** onglet, **ni** mise en forme supplémentaire.
- Si le fichier **Detailed sales** est ouvert et connecté : mettre à jour les lignes de
  commande correspondantes avec la **date de réception** (colonne **AR**, onglet
  *Detailed sales*).
