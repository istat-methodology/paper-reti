"""Frame e campione dopo il controllo di fine 2026-11-02: fuori ambito, copie, rimpiazzi.
Regole (docs/decisioni.md):
- fuori ambito: documenti che non sono protocolli (1701, 1702, 0201, 044103);
- copie: l'unità è il documento; di ogni coppia di testi identici resta un file (quello nel campione o nel gold; poi quello usato come pilota; poi il codice più basso);
- rimpiazzo di un'unità tolta dal campione: stessa regione, non già nel campione, lunghezza più vicina (a parità, codice più basso). Se lo strato è vuoto, nessun rimpiazzo.
Uso: python codice/campione_sostituzioni.py
Scrive campione/frame_esclusioni_v1.csv e campione/campione_pubblicazione_v2.csv. Il campione v1 e il gold v1 non si toccano."""
import pandas as pd
from config import MICRODATI, REPO

FUORI_AMBITO = {
    "1701": "presentazione programmatica della Regione Basilicata, non un protocollo (testo identico a 1702)",
    "1702": "presentazione programmatica della Regione Basilicata, non un protocollo (testo identico a 1701)",
    "0201": "legge regionale n. 4 del 25/02/2013, non un protocollo",
    "044103": "riassunto di un incontro della rete (21/03/2024), non un protocollo",
}
COPIE = {"1258": "1255", "1261": "1264", "0326": "0317", "1306": "1305", "0909": "0910"}  # copia -> documento che resta
TEDESCO = {"044102", "044104"}  # testo in tedesco o bilingue: non annotabile dagli annotatori
PILOTA = {"0901", "0902", "0903", "0904", "0905", "0906", "0907", "0908", "0910", "0911", "0912"}


def main():
    an = pd.read_excel(MICRODATI / "rif_anagrafica_v1.xlsx", dtype=str)[["codice", "regione"]]
    an["caratteri"] = [len((MICRODATI / "protocolli" / f"protocollo_{c}.txt").read_text(encoding="utf-8", errors="ignore")) for c in an.codice]
    frame1 = an[an.caratteri >= 500]
    v1 = pd.read_csv(REPO / "campione/campione_pubblicazione_v1.csv", sep=";", dtype=str, encoding="utf-8-sig")
    gold1 = pd.read_csv(REPO / "campione/campione_gold_v1.csv", sep=";", dtype=str, encoding="utf-8-sig")
    gold = set(gold1.codice)

    esc = [(c, "fuori ambito", m, "") for c, m in FUORI_AMBITO.items()]
    esc += [(c, "copia", f"testo identico a {d}", d) for c, d in COPIE.items()]
    E = pd.DataFrame(esc, columns=["codice", "tipo", "motivo", "documento_di_riferimento"]).merge(an[["codice", "regione"]], on="codice")
    E.sort_values("codice")[["codice", "regione", "tipo", "motivo", "documento_di_riferimento"]].to_csv(
        REPO / "campione/frame_esclusioni_v1.csv", sep=";", index=False, encoding="utf-8-sig")

    frame2 = frame1[~frame1.codice.isin(E.codice)]
    sel = {r.codice: r for r in v1.itertuples()}
    tolti = [c for c in sel if c in set(E.codice)]
    righe = [dict(codice=c, origine="originale", sostituisce="") for c in sel if c not in tolti]
    for c in sorted(tolti):
        reg, car = sel[c].regione, int(sel[c].caratteri)
        cand = frame2[(frame2.regione == reg) & ~frame2.codice.isin([x["codice"] for x in righe])].copy()
        if cand.empty:
            print(f"{c} ({reg}): strato vuoto, nessun rimpiazzo"); continue
        cand["d"] = (cand.caratteri - car).abs()
        r = cand.sort_values(["d", "codice"]).iloc[0]
        print(f"{c} ({reg}, {car} car.) -> rimpiazzo {r.codice} ({r.caratteri} car.)")
        righe.append(dict(codice=r.codice, origine="sostituto", sostituisce=c))
    S = pd.DataFrame(righe).merge(frame2, on="codice")
    S["rango_lunghezza"] = ""
    for reg, g in frame2.groupby("regione"):
        o = g.sort_values(["caratteri", "codice"]).codice.tolist()
        for i in S.index[S.regione == reg]:
            S.loc[i, "rango_lunghezza"] = f"{o.index(S.loc[i, 'codice']) + 1}/{len(o)}"
    S["pilota"] = S.codice.isin(PILOTA).map({True: "si", False: "no"})
    S = S.sort_values(["regione", "caratteri"])
    S[["codice", "regione", "caratteri", "rango_lunghezza", "pilota", "origine", "sostituisce"]].to_csv(
        REPO / "campione/campione_pubblicazione_v2.csv", sep=";", index=False, encoding="utf-8-sig")
    # gold: un'unità tolta è sostituita da un'unità di campione idonea al gold, non già nel gold, di lunghezza più vicina
    # (idonea: non pilota, fino a 100.000 caratteri, non in tedesco). Non si mantiene la regione: il rimpiazzo di strato (044102) è in tedesco.
    idonee = S[(S.pilota == "no") & (S.caratteri.astype(int) <= 100000) & ~S.codice.isin(TEDESCO) & ~S.codice.isin(gold)].copy()
    g2 = gold1.copy(); g2["origine"] = "originale"
    for c in sorted(gold & set(tolti)):
        car = int(sel[c].caratteri)
        idonee["d"] = (idonee.caratteri.astype(int) - car).abs()
        r = idonee.sort_values(["d", "codice"]).iloc[0]
        print(f"gold: {c} ({car} car.) -> {r.codice} ({r.regione}, {r.caratteri} car.)")
        i = g2.index[g2.codice == c][0]
        g2.loc[i, ["codice", "regione", "caratteri", "origine"]] = [r.codice, r.regione, r.caratteri, "sostituto"]
        idonee = idonee[idonee.codice != r.codice]
    g2[["codice", "regione", "caratteri", "doppia", "origine"]].to_csv(REPO / "campione/campione_gold_v2.csv", sep=";", index=False, encoding="utf-8-sig")
    print("n gold", len(g2), "; doppia", int((g2.doppia == "si").sum()))
    N, n = frame2.groupby("regione").size(), S.groupby("regione").size()
    T = pd.DataFrame({"N": N, "n": n}).fillna(0).astype(int)
    T["N_v1"] = frame1.groupby("regione").size()
    print(T.sort_values("N", ascending=False).to_string())
    print(f"frame v1 {len(frame1)} file -> frame v2 {len(frame2)} documenti; campione {len(v1)} -> {len(S)}; gold {len(gold)} invariato")


if __name__ == "__main__":
    main()
