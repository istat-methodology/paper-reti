"""Confronta due varianti dell'input dello stadio 1 (per default: testo estratto contro PDF).
Per ogni protocollo: enti stabili (presenti in almeno 2 run su 3) trovati da entrambe le varianti, solo dal testo, solo dal PDF.
Abbinamento dei nomi tollerante: senza accenti, senza articoli, con inclusione e similarità >= 0.85.
Uso: python codice/pipeline_ai_v2/confronta_testo_pdf.py [--a v1_testo] [--b v1_pdf] [--soglia 2] [--contenitore enti_identificati|menzioni_generiche]
Output: stampa una tabella e scrive microdati/ai_v2/stadio1/confronto_<a>_<b>.csv (fuori da git)."""
import argparse, csv, difflib, json, re, sys, unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MICRODATI  # noqa: E402

BASE = MICRODATI / "ai_v2" / "stadio1"


def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").lower().replace("’", "'"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w ]", " ", s)
    s = re.sub(r"\b(comune|citta|di|del|della|dei|degli|delle|dell|e|il|la|lo|le|l|d)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def uguali(x, y):
    return x == y or x in y or y in x or difflib.SequenceMatcher(None, x, y).ratio() >= 0.85


def carica(tag, soglia, cont):
    per = defaultdict(lambda: defaultdict(lambda: dict(nome="", n=0, ruoli=[], gen=False)))
    runs = defaultdict(set)
    for f in sorted((BASE / tag).glob("*_run*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        c = d["meta"]["codice"]; runs[c].add(d["meta"]["run"])
        visti = set()
        for e in d[cont]:
            k = norm(e["nome"] if cont == "enti_identificati" else e["espressione"])
            if k in visti:
                continue
            visti.add(k)
            x = per[c][k]
            x["nome"] = x["nome"] or (e["nome"] if cont == "enti_identificati" else e["espressione"]); x["n"] += 1; x["ruoli"].append(e["ruolo_nel_documento"]); x["gen"] = cont == "menzioni_generiche"
    return {c: {k: v for k, v in ents.items() if v["n"] >= min(soglia, len(runs[c]))} for c, ents in per.items()}, runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="v1_testo"); ap.add_argument("--b", default="v1_pdf"); ap.add_argument("--soglia", type=int, default=2)
    ap.add_argument("--contenitore", default="enti_identificati", choices=["enti_identificati", "menzioni_generiche"])
    o = ap.parse_args()
    A, ra = carica(o.a, o.soglia, o.contenitore); B, rb = carica(o.b, o.soglia, o.contenitore)
    righe = []
    print(f"{o.contenitore}: elementi stabili (>= {o.soglia} run). A={o.a}, B={o.b}")
    print("codice  A    B    entrambi  solo_A  solo_B")
    for c in sorted(set(A) & set(B)):
        ka, kb = list(A[c]), list(B[c])
        ent = [k for k in ka if any(uguali(k, y) for y in kb)]
        sa = [k for k in ka if k not in ent]
        sb = [y for y in kb if not any(uguali(x, y) for x in ka)]
        print(f"{c:<7} {len(ka):<4} {len(kb):<4} {len(ent):<9} {len(sa):<7} {len(sb)}")
        for k in ent: righe.append((c, "entrambi", A[c][k]["nome"], max(set(A[c][k]["ruoli"]), key=A[c][k]["ruoli"].count), A[c][k]["gen"]))
        for k in sa: righe.append((c, f"solo_{o.a}", A[c][k]["nome"], max(set(A[c][k]["ruoli"]), key=A[c][k]["ruoli"].count), A[c][k]["gen"]))
        for k in sb: righe.append((c, f"solo_{o.b}", B[c][k]["nome"], max(set(B[c][k]["ruoli"]), key=B[c][k]["ruoli"].count), B[c][k]["gen"]))
    out = BASE / f"confronto_{o.a}_{o.b}_{o.contenitore}.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["codice", "esito", "nome", "ruolo", "generico"]); w.writerows(righe)
    print("scritto", out)


if __name__ == "__main__":
    main()
