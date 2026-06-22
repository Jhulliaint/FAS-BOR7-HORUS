#!/usr/bin/env python3
"""
parse_bl.py — Parse a Corthay / MAGE delivery note (Bon de Livraison) PDF and emit the
STOCK entry rows for the Volney 'Main products' sheet (cross-check / harness for the
bl-corthay-stock-entry skill).

It extracts: BL date + number, store, the shoe-pair articles (ignoring boxes/soles/
heels/laces/etc.), the internal BAR CODE nomenclature, and the client names in the
'Commande client' bracket zone.

Normalisation of Material/Color/Piping/Patina/Model/Last must ultimately be done against
the workbook lists at runtime; here we keep the raw BL strings + a light built-in map so
the logic is verifiable offline.

Usage:  python3 parse_bl.py BL.pdf            (requires: pip install pdfminer.six)
"""
import re, sys, json

IGNORE_REF_PREFIX = ("BTE",)
IGNORE_WORDS = ("shoe box", "boite", "boîte", "semelle", "sole", "talon", "heel",
                "lacet", "lace", "elastique", "élastique", "bout fer", "bouts fer",
                "patin", "buckle only", "shoe bag")
# barcode prefix exceptions (normalised model -> prefix)
PREFIX_EXCEPTIONS = {"BELT C": "BTC"}
STRIP_FROM_MODEL = ("pullman", "sevres", "sévres", "sevre", "sévre", "sp", "spe",
                    "calf", "suede", "ardillat", "pp", "mb")

# The workbook lists (PIPING, COLOR, MATERIAL...) are in ENGLISH; the BL is in French.
# Map common FR piping terms to the English PIPING list. Unknown -> confirm vs the list.
PIPING_FR_EN = {
    "noir": "BLACK", "bordeaux": "BURGUNDY", "marron fonce": "DARK BROWN",
    "or": "GOLD", "vert anis": "GREEN ANIS", "gris": "GREY", "lila": "LILA",
    "lilas": "LILA", "marron moyen": "MIDDLE BROWN", "violet": "PURPLE",
    "rouge": "RED", "blanc": "WHITE", "jaune neon": "NEON YELLOW",
    "rose neon": "NEON PINK", "cuivre": "BRONZE", "creme": "CREAM",
}


def _ascii(s):
    import unicodedata
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


def norm_piping(raw):
    """'Passepoil Cuivre' -> ('BRONZE', True). Returns (value, confident)."""
    if not raw:
        return None, True
    t = _ascii(re.sub(r"(?i)passepoil/?(piping)?\s*", "", raw))
    return (PIPING_FR_EN.get(t, raw.strip().upper()), t in PIPING_FR_EN)


def norm_material_color(ensemble):
    """'Box Calf Ardillat' -> ('CALF', 'ARDILLAT') (preview; confirm vs workbook lists)."""
    if not ensemble:
        return None, None
    low = _ascii(ensemble)
    mat = "CALF" if "calf" in low else ("SUEDE" if ("suede" in low or "daim" in low) else None)
    color = ensemble.strip().split()[-1].upper()  # trailing token = leather color
    return mat, color


def extract_text(path):
    from pdfminer.high_level import extract_text
    return extract_text(path)


def bl_header(txt):
    date = re.search(r"du\s+(\d{2})/(\d{2})/(\d{4})", txt)
    num = re.search(r"Bon de livraison\s*\n+\s*\n*\s*([\d\s]{3,8})", txt) or re.search(r"\*0*(\d+)\*", txt)
    d = "".join(date.groups()) if date else None            # DDMMYYYY
    dd = "/".join(date.groups()) if date else None           # DD/MM/YYYY
    n = re.sub(r"\s", "", num.group(1)) if num else None
    store = "VOLNEY" if re.search(r"volney", txt, re.I) else None
    return {"date_ddmmyyyy": d, "date_slash": dd, "bl_number": n, "store": store}


def client_names(txt):
    """Names inside brackets in the 'Commande client' zone; drop non-person entries."""
    names = []
    for m in re.finditer(r"\[\s*([^\]]+?)\s*\]", txt):
        raw = re.sub(r"\s+", " ", m.group(1)).strip()
        if not raw:
            continue
        low = raw.lower()
        if any(w in low for w in IGNORE_WORDS) or low in ("shoe boxes", "shoe box"):
            continue
        if not re.search(r"[A-Za-zÀ-ÿ]", raw):
            continue
        names.append(raw)
    return names


def model_prefix(model):
    m = model.upper().strip()
    if m in PREFIX_EXCEPTIONS:
        return PREFIX_EXCEPTIONS[m]
    words = m.split()
    if len(words) >= 2:
        return (words[0][:2] + words[1][:1])
    return m[:3]


def normalise_model(name):
    # drop material/last/finish words to keep the model name (e.g. 'ARCA BOUCLE Pullman SP' -> 'ARCA BOUCLE')
    toks = re.split(r"\s+", name.strip())
    keep = []
    for t in toks:
        if t.lower() in STRIP_FROM_MODEL:
            break  # model words come first; stop at the first material/last/finish token
        keep.append(t)
    return " ".join(keep).strip() or name.strip()


def parse_articles(txt):
    lines = [l.rstrip() for l in txt.splitlines()]
    # article header: "<REF> - <model name>"   e.g. "ARB299SPE - ARCA BOUCLE Pullman SP"
    art_re = re.compile(r"^([A-Z]{2,4}\d[A-Z0-9]*)\s*-\s*(.+)$")
    arts = []
    idxs = [(i, m) for i, l in enumerate(lines) for m in [art_re.match(l)] if m]
    for k, (i, m) in enumerate(idxs):
        ref, name = m.group(1), m.group(2).strip()
        end = idxs[k + 1][0] if k + 1 < len(idxs) else len(lines)
        block = lines[i:end]
        low_name = name.lower()
        if ref.upper().startswith(IGNORE_REF_PREFIX) or any(w in low_name for w in IGNORE_WORDS):
            continue  # boxes etc.
        def grab(label):
            for l in block:
                mm = re.search(label + r"\s*-\s*(.+)$", l, re.I)
                if mm:
                    return mm.group(1).strip()
            return None
        ensemble = grab(r"Ensemble/Set")
        piping = grab(r"Passepoil/Piping")
        patina = grab(r"Patine/Patina")
        buckle = grab(r"Boucle/Buckle")
        # size = first standalone number AFTER the materials block (Ensemble/Doublure/
        # Passepoil/Semelle/Talon/Lacets/ELASTIQUES/BOUTS FER/PATINS), e.g. 9, 9.5, 10.5
        mat_re = re.compile(r"(Ensemble/Set|Doublure|Boucle/Buckle|Passepoil|Semelle|"
                            r"Talon|Lacets|ELASTIQUE|BOUTS|PATIN)", re.I)
        last_mat = max((j for j, l in enumerate(block) if mat_re.search(l)), default=-1)
        size = None
        for l in block[last_mat + 1:]:
            mm = re.match(r"^\s*(\d{1,2}(?:[.,]\d)?)\s*$", l)
            if mm:
                size = mm.group(1).replace(",", ".")
                break
        model = normalise_model(name)
        arts.append({"ref": ref, "bl_name": name, "model": model,
                     "ensemble_set": ensemble, "piping_raw": piping, "patina_raw": patina,
                     "buckle": buckle, "size": size})
    return arts


def build_rows(path):
    txt = extract_text(path)
    h = bl_header(txt)
    arts = parse_articles(txt)
    counter = {}
    for a in arts:
        pfx = model_prefix(a["model"])
        counter[pfx] = counter.get(pfx, 0) + 1
        a["prefix"] = pfx
        a["barcode"] = f"{pfx}{h['date_ddmmyyyy']}{counter[pfx]:03d}"
        # preview normalisation (confirm against workbook lists at runtime)
        a["material"], a["color"] = norm_material_color(a["ensemble_set"])
        a["piping"], a["piping_confident"] = norm_piping(a["piping_raw"])
        a["last"] = "PULLMAN"  # default; SEVRES only if the BL says so
    return {"header": h, "clients": client_names(txt), "articles": arts}


if __name__ == "__main__":
    res = build_rows(sys.argv[1] if len(sys.argv) > 1 else "BL.pdf")
    h = res["header"]
    print(f"BL #{h['bl_number']}  date={h['date_slash']} ({h['date_ddmmyyyy']})  store={h['store']}")
    print(f"Clients (Commande client): {res['clients']}")
    print(f"\nColonnes à écrire (E,F,G,H,J,K + D barcode ; normalisation à confirmer vs listes du classeur):")
    print(f"{'D BARCODE':<16}{'E MODEL':<13}{'F MAT':<6}{'G COLOR':<10}{'H LAST':<8}{'J PIPING':<12}{'K SIZE':<6}REF")
    for a in res["articles"]:
        warn = "" if a.get("piping_confident", True) else "  ⚠piping?"
        print(f"{a['barcode'] or '?':<16}{a['model'][:13]:<13}{(a['material'] or '?'):<6}"
              f"{(a['color'] or '?'):<10}{a['last']:<8}{(a['piping'] or '?'):<12}{(a['size'] or '?'):<6}{a['ref']}{warn}")
    print(f"\n{len(res['articles'])} stock line(s).  JSON:")
    print(json.dumps(res, ensure_ascii=False))
