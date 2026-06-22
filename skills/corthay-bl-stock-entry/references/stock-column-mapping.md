# Correspondance colonnes — onglet « Main products » (tableau STOCK, A:AC)

En-têtes **ligne 6**, données à partir de la **ligne 7**. **Une paire = une ligne.**

| Col | Champ | Quoi écrire |
|---|---|---|
| **A** | STORE | **NE PAS écrire** — formule `=$I$1` |
| **B** | Category | **NE PAS écrire** — XLOOKUP automatique (depuis Model) |
| **C** | Choice | `First` (sauf indication contraire du BL) |
| **D** | BAR CODE | nomenclature interne `<préfixe><JJMMAAAA><###>` (cf. `bl-parsing.md`) |
| **E** | Model | modèle **normalisé** via liste **MODEL** (« ARCA BOUCLE Pullman SP » → `ARCA BOUCLE`). *Pullman / Sévre / SP / SPE* ne font **pas** partie du Model |
| **F** | Material | depuis « Ensemble/Set », normalisé via **MATERIAL** (« Box Calf » → `CALF`) |
| **G** | Color | couleur du cuir depuis « Ensemble/Set », via **COLOR** (« …Ardillat » → `ARDILLAT`) |
| **H** | Last | la forme — généralement `PULLMAN` (souvent dans la réf/nom) ; `SEVRES` si indiqué |
| **I** | Patina | **vide** sauf patine **explicite** (liste **PATINA**). Une couleur de cuir tannée (« Ardillat ») n'est **pas** une patine |
| **J** | Piping | couleur du passepoil (FR dans le BL), normalisée via **PIPING** |
| **K** | Size | taille numérique du BL |
| **L** | CS/STOCK/BESPOKE | `STOCK` (→ `CS` si la ligne est affectée à un client à l'étape 6) |
| **M** | Customer Name | affecté à l'étape 6 |
| **N** | — | vide |
| **O** | Entry QTY | **NE PAS écrire** — formule |
| **P** | Entry date | date du BL au format `jj/mm/aaaa` |
| **Q** | From | `FACTORY` (toujours, BL Corthay = manufacture, pas un achat) |
| **R** | Reason | **NE PAS écrire** — XLOOKUP (donnera « Order ») |
| **S, T** | release info | vides |
| **U** | (release) | **NE PAS écrire** — formule |
| **V** | Stock Qty | **NE PAS écrire** — formule (doit donner 1) |
| **W** | Eshop | vide |
| **X** | Purchase price | **TOUJOURS VIDE** pour les BL Corthay |
| **Y** | Amount | **NE PAS écrire** — formule |
| **Z, AA** | Comment | vides — ne rien écrire |
| **AB** | — | vide |
| **AC** | BF number | vide |

## Colonnes FORMULES — ne JAMAIS écrire dedans

**A, B, O, R, U, V, Y** contiennent des formules de la table qui se propagent
automatiquement. Y écrire casserait la table.

## Normalisation (via les listes du classeur)

Toujours convertir les libellés du BL vers les **valeurs exactes des listes** du classeur
(onglet de listes / validation) **avant d'écrire** :
- **MODEL** : retirer matière/forme/finition du nom (« ARCA CALF Pullman Ardillat pp MB »
  → `ARCA`).
- **MATERIAL** : « Box Calf » → `CALF`, etc.
- **COLOR** : « Ardillat » → `ARDILLAT`, etc.
- **PIPING** : passepoil FR → valeur PIPING (ex. « Marron Moyen », « Cuivre »).
- **PATINA** : uniquement si une patine est explicitement nommée.

Si une valeur du BL ne correspond à **aucune** entrée de la liste : **proposer la plus
proche et demander confirmation** (ne pas inventer). Si le **modèle** est absent de MODEL :
**demander** avant d'écrire.

## Après écriture

- Vérifier **Category** (B) non vide (sinon le Model n'est pas dans MODEL), **Stock Qty**
  (V) = 1, **Entry date** en `jj/mm/aaaa`.
- **Ne pas** ajouter de Claude log / onglet / mise en forme.
- Si **Detailed sales** est ouvert et connecté : reporter la **date de réception** dans la
  colonne **AR** de l'onglet *Detailed sales* sur les lignes de commande correspondantes.
