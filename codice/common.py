"""Caricamento e raccordo dei dati GINO (questionario, umano) e AI (output della pipeline LLM).

Costruisce la griglia protocollo x categoria (30) x ruolo (Proponente, Attore coinvolto) con due indicatori:
  hu = categoria selezionata nel questionario; ai = categoria con almeno un soggetto AI con quel ruolo.
Ruoli AI usati: proponente = 'soggetto_proponente', attore = 'attore'.
mapping='base': i soggetti AI senza categoria GINO (604) sono esclusi dal confronto.
mapping='alt' : assegnazione provvisoria, DA VALIDARE (vedi docs/decisioni.md).
"""
import sys; sys.dont_write_bytecode = True
import pandas as pd, numpy as np, warnings; warnings.filterwarnings("ignore")
from config import MICRODATI, RIFERIMENTI

ROLES = {"Proponente": "soggetto_proponente", "Attore coinvolto": "attore"}
REGIONI = {"01": "Piemonte", "02": "Valle d'Aosta", "03": "Lombardia", "04": "Trentino-AA", "05": "Veneto", "06": "FVG", "07": "Liguria",
           "08": "Emilia-Romagna", "09": "Toscana", "10": "Umbria", "11": "Marche", "12": "Lazio", "13": "Abruzzo", "14": "Molise",
           "15": "Campania", "16": "Puglia", "17": "Basilicata", "18": "Calabria", "19": "Sicilia", "20": "Sardegna"}
# etichette AI che differiscono dal testo del questionario
ALIAS = {"CAV/Centri Antiviolenza": 1, "Procura Minorile/Tribunale minorile": 17, "Altri ordini professionali": 22,
         "Regioni/Province Autonome": 10, "Ente terzo settore - ETS (iscritto al RUNTS)": 24}
# assegnazione provvisoria dei soggetti AI senza categoria GINO
ALT = {"ORGANIZZAZIONI DI VOLONTARIATO": 24, "ASSOCIAZIONI DI PROMOZIONE SOCIALE": 24, "IMPRESE SOCIALI": 24,
       "ALTRI ENTI DEL TERZO SETTORE": 24, "ENTI FILANTROPICI": 24, "Unione dei Comuni": 3,
       "Centri/Sportelli di ascolto": 1, "Consorzi": 30}

def categorie():
    return pd.read_csv(RIFERIMENTI / "categorie_gino_30.csv", sep=";", encoding="utf-8-sig")

def load(mapping="alt"):
    cats = categorie(); lab = {r.etichetta: r.codice for r in cats.itertuples()}; lab.update(ALIAS)
    prot = pd.read_excel(MICRODATI / "ai/ai_tabelle_p2_6.xlsx", sheet_name="protocolli", dtype=str)
    prot["k"] = prot.questionario_id_rispondente_rilev + "|" + prot.questionario_progressivo_quest
    prot = prot[prot.questionario_match_questionario == "True"].copy()
    prot["regione"] = prot.questionario_codice_regione.map(REGIONI)
    for c in ["tot_soggetti", "tot_firmatari"]: prot[c] = pd.to_numeric(prot[c])
    h = pd.read_excel(MICRODATI / "gino/gino_soggetti.xlsx", sheet_name=0, dtype=str)
    h["k"] = h.ID_RISPONDENTE_RILEV + "|" + h.PROGRESSIVO_QUEST
    keys = sorted(set(prot.k) & set(h.k)); prot = prot[prot.k.isin(keys)]
    h = h[h.k.isin(keys)].copy(); h["cod"] = h.SOGGETTO_PROP_VALORI.astype(int)
    a = pd.read_excel(MICRODATI / "ai/ai_tabelle_p2_6.xlsx", sheet_name="soggetti", dtype=str)
    a["k"] = a.questionario_id_rispondente_rilev + "|" + a.questionario_progressivo_quest
    a = a[a.k.isin(keys)].copy()
    a["cod_base"] = a.tipo.map(lambda t: 9 if isinstance(t, str) and t.startswith("Ambiti") else lab.get(t))
    a["cod_alt"] = a.cod_base.fillna(a.tipo.map(ALT))
    a["cod"] = a.cod_alt if mapping == "alt" else a.cod_base
    # griglia
    chk = {"Proponente": "SOGGETTO_PROP_CHECK", "Attore coinvolto": "ATTORI_COINVOLTI_CHECK"}
    parts = []
    for rn, rl in ROLES.items():
        g = pd.MultiIndex.from_product([keys, cats.codice], names=["k", "cod"]).to_frame(index=False); g["rm"] = rn
        hs = h[h[chk[rn]].notna()][["k", "cod"]].drop_duplicates().assign(hu=1)
        s = a[(a.ruolo == rl) & a.cod.notna()][["k", "cod"]].assign(cod=lambda d: d.cod.astype(int)).drop_duplicates().assign(ai=1)
        parts.append(g.merge(hs, on=["k", "cod"], how="left").merge(s, on=["k", "cod"], how="left").fillna({"hu": 0, "ai": 0}))
    mm = pd.concat(parts, ignore_index=True); mm[["hu", "ai"]] = mm[["hu", "ai"]].astype(int)
    return mm, a, h, prot, cats

def stats(g):
    b = int(((g.ai == 1) & (g.hu == 1)).sum()); ho = int(((g.ai == 0) & (g.hu == 1)).sum())
    ao = int(((g.ai == 1) & (g.hu == 0)).sum()); n = int(((g.ai == 0) & (g.hu == 0)).sum()); N = len(g)
    po = (b + n) / N; pe = ((b + ho) / N) * ((b + ao) / N) + ((ao + n) / N) * ((ho + n) / N)
    return pd.Series(dict(entrambi=b, solo_umano=ho, solo_AI=ao, nessuno=n, n_umano=b + ho, n_AI=b + ao,
                          jaccard=round(b / max(b + ho + ao, 1), 3), kappa=round((po - pe) / (1 - pe), 3) if pe < 1 else np.nan,
                          pabak=round(2 * po - 1, 3)))
