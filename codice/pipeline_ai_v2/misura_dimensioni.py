"""Dimensioni dei protocolli: caratteri (testo OCR, tutti i 251), pagine e MB (dove c'è il PDF), enti AI (vecchio) e,
per i protocolli con run v1_2, enti identificati (mediana tra run). Scrive microdati/ai_v2/stadio1/dimensioni.csv"""
import csv, json, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MICRODATI  # noqa: E402
import pymupdf  # noqa: E402

import pandas as pd  # noqa: E402
reg = dict(pd.read_excel(MICRODATI / "rif_anagrafica_v1.xlsx", dtype=str)[["codice", "regione"]].values)
abb = {r["codice"]: r["file_ai"] for r in csv.DictReader(open(MICRODATI / "rif_ai_abbinamento_v1.csv", encoding="utf-8-sig"), delimiter=";")}
righe = []
for f in sorted((MICRODATI / "protocolli").glob("protocollo_*.txt")):
    c = f.stem.split("_")[1]
    pdf = MICRODATI / "protocolli_pdf" / f"protocollo_{c}.pdf"
    if not pdf.exists() and c in abb:
        pdf = MICRODATI / "protocolli_pdf" / "_originali" / (Path(abb[c]).stem + ".pdf")
    pag = mb = ""
    if pdf.exists():
        try:
            pag = len(pymupdf.open(pdf)); mb = round(pdf.stat().st_size / 1e6, 2)
        except Exception:
            pass
    enti = []
    for r in sorted((MICRODATI / "ai_v2/stadio1/v1_2_testo").glob(f"{c}_run*.json")):
        enti.append(len(json.loads(r.read_text(encoding="utf-8"))["enti_identificati"]))
    righe.append(dict(codice=c, regione=reg.get(c, ""), caratteri=len(f.read_text(encoding="utf-8", errors="ignore")),
                      pagine=pag, mb=mb, enti_v1_2=statistics.median(enti) if enti else ""))
out = MICRODATI / "ai_v2/stadio1/dimensioni.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(righe[0]), delimiter=";"); w.writeheader(); w.writerows(righe)
ch = sorted(r["caratteri"] for r in righe)
q = lambda p: ch[int(p * (len(ch) - 1))]
print(len(righe), "protocolli; caratteri: min", ch[0], "q25", q(.25), "mediana", q(.5), "q75", q(.75), "q90", q(.9), "q95", q(.95), "max", ch[-1])
for s in (50000, 100000, 150000, 200000): print(f"  > {s}: {sum(c > s for c in ch)}")
print("\nToscana (testo v1_2):"); print("codice caratteri pagine   MB enti_v1_2")
for r in righe:
    if r["enti_v1_2"] != "": print(f"{r['codice']:>6} {r['caratteri']:>9} {str(r['pagine']):>6} {str(r['mb']):>5} {r['enti_v1_2']:>5}")
print("\n10 più lunghi:")
for r in sorted(righe, key=lambda r: -r["caratteri"])[:10]: print(r["codice"], r["regione"], r["caratteri"], r["pagine"], r["mb"], r["regione"])
