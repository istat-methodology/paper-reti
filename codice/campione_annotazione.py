"""Campione per l'annotazione manuale (gold standard) e assegnazione agli annotatori.
- Toscana: tutti i protocolli (pilota; questionari compilati dalla responsabile del progetto).
- Altre regioni: 1 protocollo per regione + il resto in proporzione (resti maggiori).
  Dentro la regione: ordine per lunghezza e scelta sistematica (copre corti e lunghi).
- Sardegna esclusa: un solo protocollo, di 170.000 caratteri e 110 enti, troppo oneroso da annotare.
- Assegnazione: un terzo dei protocolli (spaziato per regione e lunghezza) è annotato da entrambi,
  gli altri sono divisi tra A1 e A2 bilanciando il numero di enti.
Seed fisso. Uso: python codice/campione_annotazione.py [n_totale=36]"""
import sys, json
import numpy as np, pandas as pd
from config import MICRODATI, REPO

N_TOT = int(sys.argv[1]) if len(sys.argv) > 1 else 36
SEED = 20261030
ESC = {"0909", "0326", "044101", "0507", "1612", "1613"}
REG_ESCLUSE = {"Sardegna"}
REG_TUTTI = {"Toscana"}

a = pd.read_excel(MICRODATI / "rif_anagrafica_v1.xlsx", dtype=str)
a = a[~a.codice.isin(ESC) & ~a.regione.isin(REG_ESCLUSE)].copy()
a["caratteri"] = [len((MICRODATI / "protocolli" / f"protocollo_{c}.txt").read_text(encoding="utf-8", errors="ignore")) for c in a.codice]
a["enti_AI"] = [len(json.load(open(MICRODATI / "ai" / f"ai_{c}.json")).get("soggetti", [])) for c in a.codice]

N = a.groupby("regione").size()
altre = N[~N.index.isin(REG_TUTTI)]
n_altre = N_TOT - int(N[N.index.isin(REG_TUTTI)].sum())
quota = (altre - 1) / (altre - 1).sum() * (n_altre - len(altre))
n = 1 + np.floor(quota).astype(int)
for r in (quota - np.floor(quota)).sort_values(ascending=False).index[: n_altre - n.sum()]:
    n[r] += 1
n = np.minimum(n, altre)

rng = np.random.default_rng(SEED)
scelti = []
for reg, g in a.groupby("regione"):
    g = g.sort_values("caratteri").reset_index(drop=True)
    if reg in REG_TUTTI:
        scelti.append(g); continue
    k, m = int(n[reg]), len(g)
    pos = np.floor((np.arange(k) + rng.random()) * m / k).astype(int)
    scelti.append(g.loc[pos])
s = pd.concat(scelti)[["codice", "regione", "caratteri", "enti_AI"]]
s = s.sort_values(["regione", "caratteri"]).reset_index(drop=True)

comuni = s.index % 3 == 0
s["annotatori"] = ""
s.loc[comuni, "annotatori"] = "A1+A2"
carico = {"A1": s.loc[comuni, "enti_AI"].sum(), "A2": s.loc[comuni, "enti_AI"].sum()}
for i in s[~comuni].sort_values("enti_AI", ascending=False).index:
    x = min(carico, key=carico.get)
    s.loc[i, "annotatori"] = x
    carico[x] += s.loc[i, "enti_AI"]
s = s.sort_values(["regione", "codice"])
s.to_csv(REPO / "annotazione" / "campione_v1.csv", sep=";", index=False, encoding="utf-8-sig")

tab = pd.DataFrame({"protocolli": N, "campione": s.groupby("regione").size(), "enti_AI": s.groupby("regione").enti_AI.sum()}).fillna(0).astype(int)
print(tab.sort_values("protocolli", ascending=False).to_string())
print(len(s), "protocolli;", s.enti_AI.sum(), "enti;", "comuni:", int(comuni.sum()))
for x in ("A1", "A2"):
    m = s.annotatori.isin([x, "A1+A2"])
    print(x, m.sum(), "protocolli,", s.loc[m, "enti_AI"].sum(), "enti")
