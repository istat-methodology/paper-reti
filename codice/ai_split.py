"""Spezza il JSON unico della pipeline AI in un file per questionario: microdati/ai/ai_<codice>.json

Input : microdati/ai/3.0_risultati_enriched_merged_geo_2.5.json   (output AI + arricchimento geografico/RUNTS, senza dati del questionario)
        microdati/rif_anagrafica_v1.xlsx                          (codice, nome originale del protocollo)
Output: microdati/ai/ai_<codice>.json                             (il record del protocollo, invariato)
        microdati/rif_ai_abbinamento_v1.csv                       (codice; file AI; metodo)

Si usa la versione 2.5: la 2.6 aggiunge un blocco 'questionario' copiato dal questionario, che non e' output AI.
Abbinamento AI file -> codice: 1) timestamp nel nome (= ultima modifica del questionario, stessa regione);
2) nome del file senza prefissi tecnici = nome del protocollo o allegato indicato in 3.9, stessa regione.
Un protocollo condiviso da piu' questionari produce piu' file identici.
"""
import sys; sys.dont_write_bytecode = True
import json, re, unicodedata
import pandas as pd
from config import MICRODATI

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    for _ in range(2): s = re.sub(r"\.(txt|pdf)$", "", s.strip())
    return re.sub(r"[^a-z0-9]", "", s)
def ts(b):
    m = re.match(r"^\d+_\d+_rta_\d+_(\d{12})_\d+---", b); return m.group(1) if m else None
def senza_prefisso(b):
    m = re.match(r"^\d+_\d+_rta_\d+_\d{12}_\d+---(.*)$", b)
    return m.group(1) if m else re.sub(r"^\d{2}_(?:(?:ex|bat|bar|bari|brindisi|foggia|lecce|taranto|terreg)_)?", "", b)

an = pd.read_excel(MICRODATI / "rif_anagrafica_v1.xlsx", sheet_name="Anagrafica", dtype=str).fillna("")
an["base"] = an.protocollo_originale.str.split("/").str[-1].str.replace(r"\.txt$", "", regex=True)
an["ts"] = an.base.map(ts)
an["n_prot"] = an.base.map(lambda b: norm(senza_prefisso(b))); an["n_all"] = an.allegato_gino_3_9.map(norm)

src = json.load(open(MICRODATI / "ai/3.0_risultati_enriched_merged_geo_2.5.json"))
righe, non_usati = [], []
for reg, v in src["regioni"].items():
    for rec in v["files"]:
        f = rec["file"]; b = re.sub(r"\.txt$", "", f)
        if "Test_rta" in f: non_usati.append((f, "file di prova")); continue
        c = an[(an.codice_regione == reg) & (an.ts == ts(b))] if ts(b) else an.iloc[0:0]; metodo = "timestamp"
        if len(c) == 0:
            n = norm(senza_prefisso(b)); c = an[(an.codice_regione == reg) & ((an.n_prot == n) | (an.n_all == n))]; metodo = "nome"
        if len(c) == 0: non_usati.append((f, "nessun questionario")); continue
        for cod in c.codice:
            (MICRODATI / "ai" / f"ai_{cod}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            righe.append(dict(codice=cod, file_ai=f, metodo=metodo, condiviso=len(c) > 1))
m = pd.DataFrame(righe).sort_values("codice")
assert m.codice.is_unique, "un questionario ha piu' file AI"
m.to_csv(MICRODATI / "rif_ai_abbinamento_v1.csv", sep=";", index=False, encoding="utf-8-sig")
print(len(m), "file ai_<codice>.json scritti su", len(an), "questionari; metodo:", m.metodo.value_counts().to_dict())
print("senza output AI:", sorted(set(an.codice) - set(m.codice)))
print("file AI non usati:", non_usati)
