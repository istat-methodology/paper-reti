"""Stabilità tra run con confronto dei nomi tollerante (senza 'Comune di', 'Azienda', articoli; inclusione; difflib>=0.85).
Uso: python stabilita_tollerante.py --tag v1_1_testo [--contenitore enti_identificati|menzioni_generiche]"""
import argparse, difflib, itertools, json, re, sys, unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MICRODATI  # noqa: E402

BASE = MICRODATI / "ai_v2" / "stadio1"
NOME = {"enti_identificati": "nome", "menzioni_generiche": "espressione"}


def formato_v2(d):
    """i run del prompt v0 hanno una lista unica 'enti' con il flag 'generico': li porta ai due contenitori"""
    if "enti" in d and "enti_identificati" not in d:
        d["enti_identificati"] = [e for e in d["enti"] if not e.get("generico")]
        d["menzioni_generiche"] = [dict(e, espressione=e["nome"], ente_di_appartenenza=None) for e in d["enti"] if e.get("generico")]
    return d


def norm_stretta(s):
    s = unicodedata.normalize("NFKD", (s or "").lower().replace("’", "'"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\W+", " ", s).strip()


def norm(s):
    s = re.sub(r"\b(comune|citta|azienda|di|del|della|dei|degli|delle|dell|e|il|la|lo|le|l|d|presso|per|asl|usl)\b", " ", norm_stretta(s))
    return re.sub(r"\s+", " ", s).strip()


def uguali(x, y):
    return bool(x and y) and (x == y or x in y or y in x or difflib.SequenceMatcher(None, x, y).ratio() >= 0.85)


def jaccard(A, B, eq):
    """Jaccard tra due insiemi di nomi con abbinamento uno-a-uno, deterministico:
    nomi ordinati; prima gli abbinamenti identici, poi quelli per somiglianza (eq)."""
    A, B = sorted(A), sorted(B)
    usati_a, usati_b, m = set(), set(), 0
    for passo in (lambda x, y: x == y, eq):
        for i, a in enumerate(A):
            if i in usati_a:
                continue
            for j, b in enumerate(B):
                if j not in usati_b and passo(a, b):
                    usati_a.add(i); usati_b.add(j); m += 1; break
    u = len(A) + len(B) - m
    return m / u if u else 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--contenitore", default="enti_identificati", choices=NOME)
    a = ap.parse_args()
    runs = defaultdict(dict)
    for f in sorted((BASE / a.tag).glob("*_run*.json")):
        d = formato_v2(json.loads(f.read_text(encoding="utf-8")))
        runs[d["meta"]["codice"]][d["meta"]["run"]] = {x[NOME[a.contenitore]] for x in d[a.contenitore]}
    print(f"{a.tag} / {a.contenitore}\ncodice  n_run  jaccard_stretto  jaccard_tollerante")
    tot = [[], []]
    for c, r in sorted(runs.items()):
        coppie = list(itertools.combinations(sorted(r), 2))
        if not coppie:
            continue
        s = sum(jaccard({norm_stretta(x) for x in r[i]}, {norm_stretta(x) for x in r[j]}, lambda p, q: p == q) for i, j in coppie) / len(coppie)
        t = sum(jaccard({norm(x) for x in r[i]}, {norm(x) for x in r[j]}, uguali) for i, j in coppie) / len(coppie)
        tot[0].append(s); tot[1].append(t)
        print(f"{c}    {len(r)}      {s:.3f}            {t:.3f}")
    if tot[0]:
        print(f"media            {sum(tot[0])/len(tot[0]):.3f}            {sum(tot[1])/len(tot[1]):.3f}")


if __name__ == "__main__":
    main()
