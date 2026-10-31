"""Ricostruisce le misure del registro esperimenti (docs/experiments.md) dai JSON in microdati/ai_v2/stadio1/.
Scrive docs/experiments_misure.csv (una riga per esperimento e protocollo) e docs/experiments_confronti.csv
(differenze di contenuto tra coppie di esperimenti). Aggiungere un esperimento = aggiungere una riga a ESPERIMENTI."""
import csv, itertools, json, statistics, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MICRODATI, REPO  # noqa: E402
from stabilita_tollerante import formato_v2, jaccard, norm, norm_stretta, uguali  # noqa: E402
from confronta_prompt import carica  # noqa: E402

BASE = MICRODATI / "ai_v2" / "stadio1"
# (id, cartella, prompt, input, nota)
ESPERIMENTI = [
    ("E1", "testo", "v0", "text", "first prompt, flat list of entities"),
    ("E2", "pdf", "v0", "pdf", "same prompt, PDF input (files <= 3 MB)"),
    ("E3", "v1_testo", "v1", "text", "two containers: identified entities / generic mentions"),
    ("E4", "v1_pdf", "v1", "pdf", "same prompt, PDF input (files <= 3 MB)"),
    ("E5", "v1_1_testo", "v1.1", "text", "excludes international bodies, programmes, networks"),
    ("E6", "v1_2_testo", "v1.2", "text", "signing mayors' conferences and national bodies back in; two-name rule"),
    ("E7", "v1_2_pdf", "v1.2", "pdf", "same prompt, PDF input (files <= 4.1 MB, 0903 and 0908 recompressed at 110 dpi)"),
    ("E8", "v1_2_testo_spezzato", "v1.2", "text, chunked", "long protocols cut into chunks of ~25k characters, lists merged (0902, 0911 only)"),
]
CONFRONTI = [("E1", "E3"), ("E3", "E5"), ("E5", "E6"), ("E3", "E4"), ("E6", "E7"), ("E6", "E8")]
CONT = {"enti_identificati": "nome", "menzioni_generiche": "espressione"}


def leggi(cartella):
    per = defaultdict(list)
    for f in sorted((BASE / cartella).glob("[0-9]*_run*.json")):
        per[f.name.split("_run")[0]].append(formato_v2(json.loads(f.read_text(encoding="utf-8"))))
    return per


def stab(runs, cont, tollerante):
    nomi = [{x[CONT[cont]] for x in d[cont]} for d in runs]
    n = (norm if tollerante else norm_stretta)
    ins = [{n(x) for x in s} for s in nomi]
    eq = uguali if tollerante else (lambda a, b: a == b)
    v = [jaccard(a, b, eq) for a, b in itertools.combinations(ins, 2)]
    return round(sum(v) / len(v), 3) if v else ""


def main():
    righe, riep = [], []
    for eid, cart, pr, inp, nota in ESPERIMENTI:
        per = leggi(cart)
        if not per:
            continue
        for c, runs in sorted(per.items()):
            ide = [d["enti_identificati"] for d in runs]
            cit = [e for l in ide for e in l]
            righe.append(dict(exp=eid, tag=cart, prompt=pr, input=inp, codice=c, n_run=len(runs),
                              enti_nucleo=statistics.median(len(l) for l in ide),
                              firmatari=statistics.median(sum(e["ruolo_nel_documento"] == "firmatario" for e in l) for l in ide),
                              menzioni_generiche=statistics.median(len(d["menzioni_generiche"]) for d in runs),
                              jaccard_nucleo_stretto=stab(runs, "enti_identificati", False), jaccard_nucleo_tollerante=stab(runs, "enti_identificati", True),
                              jaccard_periferia_stretto=stab(runs, "menzioni_generiche", False), jaccard_periferia_tollerante=stab(runs, "menzioni_generiche", True),
                              citazioni_nucleo_non_trovate=round(sum(not e.get("citazione_trovata_nel_testo", True) for e in cit) / len(cit), 3) if cit else "",
                              token_input=sum(d["meta"].get("token_input") or 0 for d in runs), token_output=sum(d["meta"].get("token_output") or 0 for d in runs)))
        r = [x for x in righe if x["exp"] == eid]
        m = lambda k: round(statistics.mean(x[k] for x in r if x[k] != ""), 3)
        riep.append((eid, pr, inp, len(r), sum(x["n_run"] for x in r), sum(x["enti_nucleo"] for x in r),
                     m("jaccard_nucleo_stretto"), m("jaccard_nucleo_tollerante"), m("jaccard_periferia_tollerante"),
                     sum(x["token_input"] for x in r), sum(x["token_output"] for x in r)))
    out = REPO / "docs" / "experiments_misure.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0]), delimiter=";"); w.writeheader(); w.writerows(righe)
    print("exp prompt input n_prot n_run enti_nucleo J_nucleo_str J_nucleo_toll J_perif_toll tok_in tok_out")
    for r in riep: print(*r)
    tag = {e[0]: e[1] for e in ESPERIMENTI}
    conf = []
    for a, b in CONFRONTI:
        A, B = carica(tag[a], "enti_identificati", 2), carica(tag[b], "enti_identificati", 2)
        com = sorted(set(A) & set(B)); na = nb = ca = 0
        for c in com:
            na += len(A[c]); nb += len(B[c]); ca += sum(any(uguali(k, k2) for k2 in B[c]) for k in A[c])
        conf.append(dict(a=a, b=b, protocolli_comuni=len(com), enti_a=na, enti_b=nb, in_comune=ca, solo_a=na - ca, solo_b=nb - ca))
    with open(REPO / "docs" / "experiments_confronti.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(conf[0]), delimiter=";"); w.writeheader(); w.writerows(conf)
    print(); [print(*c.values()) for c in conf]


if __name__ == "__main__":
    main()
