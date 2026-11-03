"""Descrizione della run di stadio 1 su tutti i protocolli (5 run per protocollo, solo conteggi, nessuna stima).
Uso: python descrizione_run.py [--tag pubblicazione_v1_2] [--tutti-i-file]
Output: risultati/descrizione_run_stadio1_v2.xlsx (240 documenti: esclusi fuori ambito e copie di campione/frame_esclusioni_v1.csv); con --tutti-i-file: _v1, 249 file
Presenza di un ente: numero di run (su 5) in cui compare, con il confronto tollerante dei nomi di stabilita_tollerante.py.
I cluster si formano in ordine deterministico (run 1..5, nomi ordinati); le varianti di nome non unite contano come enti diversi."""
import argparse, itertools, json, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MICRODATI  # noqa: E402
from stabilita_tollerante import NOME, formato_v2, jaccard, norm, norm_stretta, uguali  # noqa: E402

RADICE = Path(__file__).resolve().parent.parent.parent
BASE = MICRODATI / "ai_v2" / "stadio1"
RUOLI = ["firmatario", "componente_rete", "solo_citato"]


def cluster(per_run, campo):
    """per_run: {run: [voci]}. Restituisce lista di cluster {rep, runs:set, ruoli:Counter, tipi:Counter}."""
    cl = []
    for r in sorted(per_run):
        viste = set()
        for v in sorted(per_run[r], key=lambda x: norm(x[campo])):
            n = norm(v[campo])
            if not n:
                continue
            c = next((c for c in cl if c["rep"] == n or uguali(c["rep"], n)), None)
            if c is None:
                c = {"rep": n, "nome": v[campo], "runs": set(), "ruoli": Counter(), "tipi": Counter()}
                cl.append(c)
            c["runs"].add(r)
            if (id(c), r) not in viste:  # un solo voto di ruolo per cluster e per run
                c["ruoli"][v.get("ruolo_nel_documento")] += 1
                c["tipi"][v.get("tipo_menzione")] += 1
                viste.add((id(c), r))
    return cl


def jaccard_medio(sets):
    coppie = list(itertools.combinations(sorted(sets), 2))
    if not coppie:
        return None
    return sum(jaccard({norm(x) for x in sets[i]}, {norm(x) for x in sets[j]}, uguali) for i, j in coppie) / len(coppie)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="pubblicazione_v1_2")
    ap.add_argument("--tutti-i-file", action="store_true")
    a = ap.parse_args()
    cartella = BASE / a.tag
    dati = defaultdict(dict)
    for f in sorted(cartella.glob("*_run*.json")):
        d = formato_v2(json.loads(f.read_text(encoding="utf-8")))
        dati[d["meta"]["codice"]][d["meta"]["run"]] = d

    if not a.tutti_i_file:
        esc = set(pd.read_csv(RADICE / "campione" / "frame_esclusioni_v1.csv", sep=";", dtype=str, encoding="utf-8-sig").codice)
        dati = {c: r for c, r in dati.items() if c not in esc}
    anag = pd.read_excel(MICRODATI / "rif_anagrafica_v2.xlsx", dtype=str)[["codice", "regione"]].drop_duplicates("codice")
    regione = dict(zip(anag.codice, anag.regione))

    righe, presenze = [], []
    tok_in = tok_out = secondi = 0
    cit_tot = cit_mancanti = 0
    for c, runs in sorted(dati.items()):
        txt = MICRODATI / "protocolli" / f"protocollo_{c}.txt"
        car = len(txt.read_text(encoding="utf-8", errors="ignore")) if txt.exists() else None
        r = {"codice": c, "regione": regione.get(c), "caratteri": car, "n_run": len(runs),
             "n_pezzi": max(d["meta"].get("n_pezzi", 1) for d in runs.values())}
        for d in runs.values():
            tok_in += d["meta"].get("token_input") or 0
            tok_out += d["meta"].get("token_output") or 0
            secondi += d["meta"].get("secondi") or 0
            for cont in NOME:
                for x in d[cont]:
                    cit_tot += 1
                    cit_mancanti += not x.get("citazione_trovata_nel_testo", True)
        for cont, sigla in (("enti_identificati", "nucleo"), ("menzioni_generiche", "periferia")):
            per_run = {k: d[cont] for k, d in runs.items()}
            n = [len(v) for v in per_run.values()]
            cl = cluster(per_run, NOME[cont])
            pres = [len(x["runs"]) for x in cl]
            r[f"{sigla}_mediana_run"] = statistics.median(n)
            r[f"{sigla}_min_run"], r[f"{sigla}_max_run"] = min(n), max(n)
            r[f"{sigla}_cluster"] = len(cl)
            r[f"{sigla}_in_5_run"] = sum(p == len(runs) for p in pres)
            r[f"{sigla}_in_3plus_run"] = sum(p >= 3 for p in pres)
            r[f"{sigla}_in_1_run"] = sum(p == 1 for p in pres)
            r[f"{sigla}_jaccard_tollerante"] = jaccard_medio({k: {x[NOME[cont]] for x in v} for k, v in per_run.items()})
            for p in pres:
                presenze.append({"contenitore": sigla, "n_run_presente": p, "codice": c})
            maggioranza = [x for x in cl if len(x["runs"]) >= 3]
            ruoli = Counter(x["ruoli"].most_common(1)[0][0] for x in maggioranza)
            for ruolo in RUOLI:
                r[f"{sigla}_3plus_{ruolo}"] = ruoli.get(ruolo, 0)
            r[f"{sigla}_ruolo_instabile"] = sum(len([k for k in x["ruoli"] if k]) > 1 for x in maggioranza)
            if cont == "menzioni_generiche":
                tipi = Counter(x["tipi"].most_common(1)[0][0] for x in maggioranza)
                for t in ("tipologia", "struttura_senza_nome", "istituzione_senza_riferimento"):
                    r[f"periferia_3plus_{t}"] = tipi.get(t, 0)
        righe.append(r)

    P = pd.DataFrame(righe)
    Z = pd.DataFrame(presenze)

    def q(s):
        return [s.min(), s.quantile(.25), s.median(), s.quantile(.75), s.max(), s.mean()]

    voci = []
    for sigla in ("nucleo", "periferia"):
        for col, et in ((f"{sigla}_mediana_run", "voci per run (mediana delle 5 run), per protocollo"),
                        (f"{sigla}_in_3plus_run", "voci in almeno 3 run su 5, per protocollo"),
                        (f"{sigla}_jaccard_tollerante", "Jaccard tollerante tra run, per protocollo")):
            voci.append([sigla, et] + q(P[col].dropna()))
    D = pd.DataFrame(voci, columns=["contenitore", "misura", "min", "q1", "mediana", "q3", "max", "media"])

    T = []
    for sigla in ("nucleo", "periferia"):
        z = Z[Z.contenitore == sigla]
        tot = len(z)
        for k in range(1, 6):
            T.append([sigla, k, int((z.n_run_presente == k).sum()), (z.n_run_presente == k).mean()])
        T.append([sigla, "totale cluster", tot, 1.0])
    T = pd.DataFrame(T, columns=["contenitore", "n_run_presente", "cluster", "quota"])

    reg = P.groupby("regione").agg(protocolli=("codice", "count"), caratteri_mediana=("caratteri", "median"),
                                   nucleo_mediana_run=("nucleo_mediana_run", "sum"),
                                   nucleo_in_3plus=("nucleo_in_3plus_run", "sum"),
                                   periferia_in_3plus=("periferia_in_3plus_run", "sum"),
                                   jaccard_nucleo=("nucleo_jaccard_tollerante", "mean")).reset_index()

    P["fascia_lunghezza"] = pd.cut(P.caratteri, [0, 10000, 20000, 40000, 1e9], labels=["<=10k", "10-20k", "20-40k", ">40k (spezzati)"])
    fas = P.groupby("fascia_lunghezza", observed=True).agg(protocolli=("codice", "count"),
                                                           nucleo_in_3plus_media=("nucleo_in_3plus_run", "mean"),
                                                           periferia_in_3plus_media=("periferia_in_3plus_run", "mean"),
                                                           jaccard_nucleo=("nucleo_jaccard_tollerante", "mean"),
                                                           jaccard_periferia=("periferia_jaccard_tollerante", "mean")).reset_index()

    ruoli = pd.DataFrame([[s, ru, int(P[f"{s}_3plus_{ru}"].sum())] for s in ("nucleo", "periferia") for ru in RUOLI],
                         columns=["contenitore", "ruolo_prevalente", "voci_in_3plus_run"])
    gen = {"run": int(P.n_run.sum()), "protocolli": len(P), "tag": a.tag, "token_input": tok_in, "token_output": tok_out,
           "ore_chiamate": round(secondi / 3600, 1), "citazioni_totali": cit_tot, "citazioni_non_trovate": cit_mancanti,
           "protocolli_spezzati": int((P.n_pezzi > 1).sum())}
    G = pd.DataFrame(list(gen.items()), columns=["voce", "valore"])

    out = RADICE / "risultati" / ("descrizione_run_stadio1_v1.xlsx" if a.tutti_i_file else "descrizione_run_stadio1_v2.xlsx")
    with pd.ExcelWriter(out) as w:
        G.to_excel(w, sheet_name="generale", index=False)
        D.to_excel(w, sheet_name="distribuzioni", index=False)
        T.to_excel(w, sheet_name="presenza_tra_run", index=False)
        ruoli.to_excel(w, sheet_name="ruoli", index=False)
        fas.to_excel(w, sheet_name="per_lunghezza", index=False)
        reg.to_excel(w, sheet_name="per_regione", index=False)
        P.to_excel(w, sheet_name="per_protocollo", index=False)
    pd.set_option("display.width", 200)
    print(G.to_string(index=False)); print(D.round(2).to_string(index=False)); print(T.round(3).to_string(index=False))
    print(ruoli.to_string(index=False)); print(fas.round(2).to_string(index=False))
    print(f"scritto {out}")


if __name__ == "__main__":
    main()
