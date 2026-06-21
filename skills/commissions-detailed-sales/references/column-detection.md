# Détection dynamique des colonnes (par en-tête)

Les fichiers « Detailed sales » partagent les **mêmes TYPES de colonnes** mais pas les
mêmes **positions**, ni la même **ligne d'en-têtes**. **Ne jamais coder une position en
dur** (« colonne W », « colonne AP »…). Toujours localiser par le **texte de l'en-tête**.

## 1. Localiser la ligne d'en-têtes

Les premières lignes contiennent des bannières (« NOT TO FILL », « Mandatory »,
« General info »…). La vraie ligne d'en-têtes est celle qui contient à la fois
`Staff`, un en-tête `Bespoke/Stock/...` et `First payment ...`.

Règle : balayer les 20 premières lignes, prendre la 1re ligne où **au moins 2** de ces
repères sont présents. (Vérifié : London → ligne **5**, Hong Kong → ligne **7**,
Volney → ligne **7**.)

## 2. Normaliser avant de comparer

Comparer en **minuscules, sans accents, espaces/retours-à-la-ligne compressés**
(`"First payment  amount"` et `"first payment amount"` doivent matcher).

## 3. Dictionnaire de correspondance (mots-clés → champ logique)

| Champ logique | L'en-tête (normalisé) doit… | Requis ? |
|---|---|---|
| `staff` (vendeur) | `== "staff"` ou contient `vendeur` ou `== "seller"` | **Oui** |
| `date` (date de vente) | `== "date"` ou `== "date de vente"` | non |
| `type` (Bespoke/PAP) | contient `bespoke` **et** `stock` | **Oui** |
| `category` | `== "category"`/`"categorie"` | non |
| `model` | `== "model"`/`"modele"` | non |
| `p1date` | contient `first payment` **et** `date` | **Oui** |
| `p1amt` | contient `first payment` **et** (`amount`/`montant`) | **Oui** |
| `p1mode` | contient `first payment` **et** `mode` | recommandé |
| `p2date` | contient `second payment` **et** `date` | si présent |
| `p2amt` | contient `second payment` **et** (`amount`/`montant`) | si présent |
| `p2mode` | contient `second payment` **et** `mode` | si présent |
| `p1type` | contient `first payment` **et** `type` | si présent |
| `export` | contient `export` **et** (`not` **ou** en-tête == `export or not`) | si présent |
| `currency` | `== "currency"`/`"devise"` | si présent |

> ⚠️ **Piège export** : ne PAS matcher `export` seul. La colonne « Total price… »
> a pour en-tête *« Total price after disc. (Qty*Unit price) (VAT incl.) **(VAT excl.
> for export)** »* — elle contient « export » mais **n'est pas** le drapeau export.
> Le vrai drapeau est la colonne dont l'en-tête est **`Export or not`** (valeur `EXPORT`).

## 4. Si une colonne REQUISE est introuvable → DEMANDER

Si `staff`, `type`, ou une paire `p1date`+`p1amt` ne peut pas être identifiée avec
certitude, **demander à l'utilisateur de confirmer la colonne** plutôt que de deviner.

## 5. Preuve de généricité — positions réelles résolues (3 boutiques)

Même logique, 3 colonnages différents (lettres résolues automatiquement) :

| Champ | London (en-têtes l.5) | Hong Kong (l.7) | Volney (l.7) |
|---|---|---|---|
| staff | D | D | D |
| date | B | B | B |
| type | H | H | H |
| p1 date / amt / mode | V / W / X | V / W / X | V / W / X |
| p2 date / amt / mode | Y / Z / AA | Y / Z / AA | Y / Z / AA |
| p1 type | AU | AU | **AT** |
| **export** | **AP** | **AP** | **AO** |
| currency | **T** (=GBP) | *(absente)* | *(absente)* |

Les deux dernières lignes montrent pourquoi la détection par en-tête est obligatoire :
`export` et `p1type` bougent, et la colonne `currency` n'existe pas partout.
