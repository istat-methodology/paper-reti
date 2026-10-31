"""Ricalcola la verifica delle citazioni su run già fatte (senza chiamare il modello).
Una citazione è 'trovata' se almeno l'80% delle sue sequenze di 3 parole compare nel testo del protocollo
(confronto senza accenti e senza punteggiatura, perché il testo OCR perde accenti e ha errori sparsi).
Uso: python codice/pipeline_ai_v2/verifica_citazioni.py [--tag v1_pdf]"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import MICRODATI  # noqa: E402
from stadio1_estrazione import norm, copertura, CONTENITORI  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--tag", default="v1_pdf"); o = ap.parse_args()
cache, tot = {}, {c: [0, 0] for c in CONTENITORI}
per = {}
for f in sorted((MICRODATI / "ai_v2" / "stadio1" / o.tag).glob("*_run*.json")):
    d = json.loads(f.read_text(encoding="utf-8")); c = d["meta"]["codice"]
    if c not in cache:
        cache[c] = norm((MICRODATI / "protocolli" / f"protocollo_{c}.txt").read_text(encoding="utf-8", errors="ignore"))
    for cont in CONTENITORI:
        for e in d[cont]:
            e["citazione_copertura"] = round(copertura(e["citazione"], cache[c]), 2)
            e["citazione_trovata_nel_testo"] = e["citazione_copertura"] >= 0.8
            tot[cont][0] += 1; tot[cont][1] += not e["citazione_trovata_nel_testo"]
            p = per.setdefault((c, cont), [0, 0]); p[0] += 1; p[1] += not e["citazione_trovata_nel_testo"]
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"tag {o.tag}: citazioni NON trovate (soglia 0,8)")
for cont, (n, x) in tot.items():
    print(f"  {cont}: {x} su {n} ({100 * x / max(n, 1):.1f}%)")
print("per protocollo (quota non trovate: identificati / generiche):")
for c in sorted({k[0] for k in per}):
    a, b = per.get((c, "enti_identificati"), [0, 0]), per.get((c, "menzioni_generiche"), [0, 0])
    print(f"  {c}: {a[1] / max(a[0], 1):.2f} / {b[1] / max(b[0], 1):.2f}")
