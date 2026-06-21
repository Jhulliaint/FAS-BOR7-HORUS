# Pièges réels rencontrés (3 fichiers : London / Hong Kong / Volney)

Chaque point ci-dessous a été observé dans les fichiers d'exemple et est géré par la
méthode (formules + `verify_commissions.py`).

1. **La ligne d'en-têtes bouge.** London = ligne 5 ; Hong Kong & Volney = ligne 7.
   → détecter la ligne d'en-têtes, ne pas la supposer.

2. **Les positions de colonnes bougent.** `Export or not` = AP (London/HK) mais **AO**
   (Volney) ; `First payment type` = AU (London/HK) mais **AT** (Volney). → par en-tête.

3. **Piège « export » dans un en-tête de prix.** La colonne « Total price… » contient
   *« (VAT excl. for export) »*. Ne matcher le drapeau export que sur **`Export or not`**.

4. **La devise n'est pas toujours une colonne.** Seul London a une colonne `Currency`
   (=GBP). Hong Kong (HKD) et Volney (EUR) n'en ont **pas**, et le format de nombre **ne
   contient pas** de symbole monétaire. → utiliser la colonne `Currency` si présente,
   sinon **demander/confirmer la devise**. **Ne jamais convertir** entre devises.

5. **La TVA dépend de la zone.** London 20 % (GBP), Volney 20 % (EUR), **Hong Kong 0 %**
   (HKD, pas de TVA → diviseur = 1). Proposer un taux mais **confirmer**, surtout hors €.

6. **Gift vouchers à DEUX endroits.** Dans le mode (`GIFT VOUCHER-ADMIN`,
   `LANDMARK GIFT VOUCHER`, `GIFT VOUCHER-HK-015`, `GIFT VOUCHER-Volney-060`) **et** dans
   la colonne `First payment type` = `GIFT VOUCHER` (HK : 202 lignes, Volney : 452).
   → exclure si l'un OU l'autre l'indique. (Sur HK juillet 2025, 6 gift vouchers
   admin s'annulent : −12096/−11940/−16947 et +14943/+13440/+12600 = **net 0** — c'est
   correct, pas un bug.)

7. **« No VAT » encodé dans le mode (Volney).** `VISA NOT VAT`, `AMEX NO VAT`,
   `STRIPE NO VAT`, `TRANSFER NO VAT`, `CASH NO VAT`… signifient « ne pas retirer la
   TVA ». → traiter comme l'export : montant **tel quel**.

8. **Types de vente avec fautes de frappe** (Volney) : `serv`, `sevice`, `servcie`, `st`.
   Sans importance pour le partage Bespoke/PAP : tout ce qui **n'est pas** `bespoke`
   tombe en **PAP**. → robuste par construction.

9. **`Petite mesure` (Hong Kong, 86 lignes).** Catégorie sur-mesure ambiguë. **Sans objet
   pour Hong Kong** (profil hk = CA combiné, aucun partage PAP/Bespoke). Ne concerne que
   le profil **Europe** : par défaut **PAP**, mais **signalée** (demander si taux Bespoke).

10. **Noms de vendeurs incohérents** : casse (`SONY`/`Sony`/`sony`/`sONY`,
    `Rodolphe`/`RODOLPHE`/`rODOLPHE`) et doubles espaces (`Samuel  Volney`). Sans
    normalisation → lignes en double et **totaux doublés** (le `=` d'Excel est
    insensible à la casse). → colonne `Staff (clean) = TRIM(...)` + liste dédupliquée
    insensible à la casse. (Volney : 28 graphies → **13** vendeurs réels.)

11. **Bespoke parfois suivi HORS du fichier.** L'onglet `Commissions` de Volney porte des
    CA Bespoke (Sony 7 500, Samuel Volney 14 417) qui **n'existent pas** dans la colonne
    `Type` du journal (1 seule ligne `bespoke` dans tout le fichier). → la commission
    Bespoke calculée depuis « Detailed sales » peut être **incomplète** ; le **signaler**
    comme limite dans le rapport de contrôle.

12. **Dates parasites** (`1900-01-11`, cellules vides/texte) : neutralisées par le filtre
    mois/année et `IFERROR(...,FALSE)`.

13. **Fichiers volumineux & colonnes fantômes.** Volney s'étend jusqu'à la colonne XFD
    (16384). En lecture programmatique, **limiter** le balayage (≈ 80 colonnes) et
    itérer **séquentiellement** (`iter_rows`) — l'accès cellule-par-cellule aléatoire en
    `read_only` est extrêmement lent.
