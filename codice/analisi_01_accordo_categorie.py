"""Accordo questionario vs AI per categoria, gruppo e ruolo. Output: risultati/accordo_categorie_v1.xlsx"""
import sys; sys.dont_write_bytecode = True
import pandas as pd
from common import load, stats, ROLES
from config import RISULTATI

out = {}
for mp in ["base", "alt"]:
    mm, a, h, prot, cats = load(mp)
    mm = mm.merge(cats[["codice", "etichetta", "gruppo10"]], left_on="cod", right_on="codice")
    out[f"totale_{mp}"] = mm.groupby("rm").apply(stats).reset_index()
    out[f"cat30_{mp}"] = mm.groupby(["rm", "cod", "etichetta"]).apply(stats).reset_index()
    # 10 gruppi: presente se almeno una categoria del gruppo
    g = mm.groupby(["k", "rm", "gruppo10"])[["hu", "ai"]].max().reset_index()
    out[f"gruppi10_{mp}"] = g.groupby(["rm", "gruppo10"]).apply(stats).reset_index()
    if mp == "alt":
        p = mm.groupby(["k", "rm"]).apply(stats).reset_index().merge(prot[["k", "regione", "tot_soggetti"]], on="k")
        out["per_regione_alt"] = p.groupby(["rm", "regione"]).apply(lambda d: pd.Series(dict(
            protocolli=len(d), jaccard_medio=round(d.jaccard.mean(), 3))) ).reset_index()
RISULTATI.mkdir(exist_ok=True)
with pd.ExcelWriter(RISULTATI / "accordo_categorie_v1.xlsx") as w:
    for k, v in out.items(): v.to_excel(w, sheet_name=k[:31], index=False)
for k in ["totale_base", "totale_alt"]: print(k); print(out[k].to_string(index=False))
