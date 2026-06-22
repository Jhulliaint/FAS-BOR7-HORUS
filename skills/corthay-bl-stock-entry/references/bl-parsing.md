# Lecture du BL Corthay / MAGE

## En-tête à extraire

- **Date** du BL : motif « du JJ/MM/AAAA » (ex. *du 30/04/2026*).
- **Numéro** du BL : ex. *3 895* / `*0003895*` → `3895`.
- **Magasin livré** : « Mage Paris … rue de Volney » → **VOLNEY**.
- Émetteur **MAGE SAS / Corthay** ⇒ BL Corthay (sinon, voir « Cas où demander »).

## Articles = paires de chaussures (une ligne de stock chacune)

Chaque article commence par une ligne `«<RÉF> - <Nom de modèle>»` (ex.
`ARB299SPE - ARCA BOUCLE Pullman SP`). Sous l'article :
- `Ensemble/Set - <matériau> <couleur>` (ex. *Box Calf Ardillat*) → Material + Color.
- `Passepoil/Piping - <couleur FR>` (ex. *Passepoil Cuivre*) → Piping.
- `Boucle/Buckle - …` (info ; n'alimente pas une colonne dédiée).
- `Patine/Patina - …` **si présent** → Patina (sinon vide).
- **Taille** : le nombre isolé **juste après** le bloc matières (Ensemble/Doublure/
  Passepoil/Semelle/Talon/Lacets/ELASTIQUES/BOUTS FER/PATINS) — ex. `10.5`, `9`, `9.5`.
  ⚠️ Ne pas confondre avec le n° de CARTON, la quantité `1`, ni le n° de page.

## À IGNORER systématiquement (ce ne sont pas des lignes de stock)

Réf commençant par `BTE…`, « Shoe Box »/boîtes, **semelles**, **talons**, **lacets**,
**élastiques**, **bouts fer**, **patins**. (Le BL #3895 contient `BTE0106 - Blue Shoe Box`
×25 → ignoré.)

## BAR CODE interne (colonne D)

Format : `<préfixe modèle><JJMMAAAA><###>`
- **JJMMAAAA** = date du BL sans séparateur (30/04/2026 → `30042026`).
- **###** = compteur `001, 002, 003…` par **modèle** et par **BL**.
- **Préfixe modèle** = 3 lettres dérivées du **nom de modèle normalisé** :
  - modèle en **un mot** → 3 premières lettres (`ARCA` → `ARC`, `BELLA` → `BEL`) ;
  - modèle en **deux mots** → 2 premières lettres du 1er mot + 1re lettre du 2e
    (`ARCA BOUCLE` → `ARB`) ;
  - **exceptions** : `BELT C` → `BTC`.

## Zone « Commande client » (étape 6)

Noms entre crochets, ex. :
```
0011350 [ DAVID KNAFO]
0011362 [ THIERRY AKA]
0011391 [ MINA OFORIOKUMA]
0011506 [ SHOE BOXES]      ← ignoré (pas un nom de personne)
```
→ noms retenus : **DAVID KNAFO, THIERRY AKA, MINA OFORIOKUMA**. Ignorer tout ce qui ne
ressemble pas à un « nom prénom » (ex. *SHOE BOXES*).

## Exemple VÉRIFIÉ — BL #3895 (30/04/2026, Mage Paris → VOLNEY)

3 paires (la boîte BTE0106 est ignorée) :

| BAR CODE | Model | Material (Ensemble/Set) | Color | Piping (Passepoil) | Size | Réf |
|---|---|---|---|---|---|---|
| `ARB30042026001` | ARCA BOUCLE | Box Calf → CALF | Ardillat → ARDILLAT | Cuivre | 10.5 | ARB299SPE |
| `ARC30042026001` | ARCA | Box Calf → CALF | Ardillat → ARDILLAT | Marron Moyen | 9 | ARC201ARD001 |
| `BEL30042026001` | BELLA | Box Calf → CALF | Ardillat → ARDILLAT | Cuivre | 9.5 | BEL299SPE |

Clients à affecter (étape 6) : DAVID KNAFO, THIERRY AKA, MINA OFORIOKUMA.

> Reproductible avec `scripts/parse_bl.py "BL.pdf"`. Les valeurs Material/Color/Piping/
> Patina/Model/Last doivent ensuite être **normalisées contre les listes du classeur**
> (cf. `stock-column-mapping.md`).
