# FAS-BOR7-HORUS — Skills Claude (équipe)

Dépôt **source de vérité** des *Agent Skills* Claude de l'équipe, créés avec le skill
**`skill-creator`** d'Anthropic. Les membres utilisent surtout **claude.ai** et le
**complément Claude pour Excel** → la livraison se fait par **upload `.zip`** dans
*Organization settings ▸ Skills* (plan **Team/Enterprise**, **Owner** uniquement).

GitHub sert de **dépôt versionné + relu (PR)** ; la **relecture en PR est le garde-fou
qualité** (claude.ai n'a pas de workflow d'approbation natif). Un `.zip` prêt à l'emploi
est généré automatiquement à chaque release.

## Skills

| Skill | Rôle | Dossier |
|---|---|---|
| `commissions-detailed-sales` | Calcule/vérifie les commissions mensuelles des vendeurs depuis un fichier *Detailed sales* (multi-devises, colonnage variable), dans Excel. Deux profils : **Europe** (PAP/Bespoke) et **Hong Kong** (personnel + pool magasin + manager). | [`skills/commissions-detailed-sales/`](skills/commissions-detailed-sales/) |

## Structure

```
skills/<nom-du-skill>/
  SKILL.md            # instructions (frontmatter name + description = déclencheurs)
  references/         # détails chargés à la demande (méthode, formules, pièges)
  scripts/            # scripts utilitaires / vérification croisée
scripts/package_skill.sh          # construit dist/<skill>.zip pour l'upload org
.github/workflows/package-skills.yml  # zip auto à chaque release (artefacts)
```

## Publier un skill aux membres

1. **Créer / modifier** le skill (idéalement via `skill-creator` dans Claude Code, puis
   commit) et ouvrir une **Pull Request** (relecture = approbation).
2. **Empaqueter** :
   ```bash
   scripts/package_skill.sh commissions-detailed-sales   # -> dist/commissions-detailed-sales.zip
   ```
   (ou récupérer le `.zip` dans les artefacts de l'action *Package skills* après une
   release.)
3. **Uploader** : un **Owner** ouvre *claude.ai ▸ Organization settings ▸ Skills* et
   sélectionne le `.zip`. Prérequis : **Code execution** activé pour l'organisation. Le
   skill devient disponible pour tous dans *Customize ▸ Skills* (activé par défaut,
   désactivable par chacun) — y compris dans le complément **Claude pour Excel**.

> Les skills **ne se synchronisent pas** entre claude.ai et Claude Code : GitHub est la
> source unique, le `.zip` est le canal de livraison vers l'app/Excel.

## Vérifier le skill `commissions-detailed-sales`

Recalcul indépendant des commissions (utile pour valider les formules) :
```bash
pip install openpyxl
python3 skills/commissions-detailed-sales/scripts/verify_commissions.py \
    "DetailedSales.xlsx" --month 4 --year 2026 --vat 0.20
# zone sans TVA (HKD) : --vat 0   | JSON : --json
```

## Références (documentation officielle Anthropic)

- Provisionner des skills pour l'organisation (Team/Enterprise) — support.claude.com/en/articles/13119606
- Agent Skills (overview, best practices) — platform.claude.com/docs/en/agents-and-tools/agent-skills
- skill-creator — github.com/anthropics/skills
