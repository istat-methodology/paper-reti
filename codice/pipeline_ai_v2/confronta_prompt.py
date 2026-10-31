"""Differenze di contenuto tra due prompt/tag (stesso input). Un ente è 'presente' se compare in >=soglia run.
Uso: python confronta_prompt.py --a v1_testo --b v1_1_testo [--contenitore ...] [--soglia 2]"""
import argparse, csv, json, sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MICRODATI  # noqa: E402
from stabilita_tollerante import norm, uguali, NOME, BASE, formato_v2  # noqa: E402


def carica(tag, cont, soglia):
    per = defaultdict(lambda: defaultdict(lambda: {"nome": "", "n": 0, "ruoli": Counter()}))
    runs = defaultdict(set)
    for f in sorted((BASE / tag).glob("*_run*.json")):
        d = formato_v2(json.loads(f.read_text(encoding="utf-8"))); c = d["meta"]["codice"]; runs[c].add(d["meta"]["run"])
        visti = set()
        for e in d[cont]:
            nome = e[NOME[cont]]; k = norm(nome)
            # aggancia a un ente già visto con nome tollerante
            for k2 in list(per[c]):
                if uguali(k, k2):
                    k = k2; break
            if k in visti: continue
            visti.add(k); x = per[c][k]; x["n"] += 1; x["nome"] = x["nome"] if len(x["nome"]) >= len(nome) else nome
            x["ruoli"][e.get("ruolo_nel_documento") or e.get("ruolo", "")] += 1
    return {c: {k: v for k, v in d.items() if v["n"] >= min(soglia, len(runs[c]))} for c, d in per.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True); ap.add_argument("--b", required=True)
    ap.add_argument("--contenitore", default="enti_identificati", choices=NOME); ap.add_argument("--soglia", type=int, default=2)
    a = ap.parse_args()
    A, B = carica(a.a, a.contenitore, a.soglia), carica(a.b, a.contenitore, a.soglia)
    righe, comuni = [], {}
    for c in sorted(set(A) & set(B)):
        ca = 0
        for ka, xa in A[c].items():
            kb = next((k for k in B[c] if uguali(ka, k)), None)
            if kb: ca += 1
            else: righe.append((c, f"solo_{a.a}", xa["nome"], dict(xa["ruoli"])))
        for kb, xb in B[c].items():
            if not any(uguali(kb, k) for k in A[c]): righe.append((c, f"solo_{a.b}", xb["nome"], dict(xb["ruoli"])))
        comuni[c] = (len(A[c]), len(B[c]), ca)
    print(f"{a.contenitore} (>= {a.soglia} run)\ncodice  {a.a}  {a.b}  comuni")
    for c, (x, y, z) in comuni.items(): print(f"{c}    {x:4d}  {y:4d}  {z:4d}")
    print("TOT", *[sum(v[i] for v in comuni.values()) for i in range(3)])
    out = BASE / f"differenze_{a.a}_{a.b}_{a.contenitore}.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["codice", "dove", "nome", "ruoli"]); w.writerows(righe)
    for r in righe: print(*r, sep=" | ")


if __name__ == "__main__":
    main()
