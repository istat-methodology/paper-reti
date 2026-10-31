"""Quante run servono: sottocampiona le run di un tag (es. 10) a n = 3, 5, 7, ... e misura
- unione: entità viste in almeno una delle n run
- in tutte: entità presenti in tutte le n run
- da rivedere: unione - in tutte
- copertura: unione / unione a tutte le run
- falsi stabili: entità presenti in tutte le n run ma non in tutte le run disponibili
Nomi confrontati con il criterio tollerante (stabilita_tollerante.uguali). Entità = gruppi di nomi equivalenti tra run.
Uso: python n_run_campionamento.py --tag v1_2_testo [--contenitore ...] [--rep 200]"""
import argparse, itertools, json, random, sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stabilita_tollerante import BASE, NOME, formato_v2, norm, uguali  # noqa: E402


def presenze(tag, cont):
    """per codice: (n_run, lista di insiemi di indici-run per ciascuna entità)"""
    runs = defaultdict(dict)
    for f in sorted((BASE / tag).glob("[0-9]*_run*.json")):
        d = formato_v2(json.loads(f.read_text(encoding="utf-8")))
        runs[d["meta"]["codice"]][d["meta"]["run"]] = {norm(x[NOME[cont]]) for x in d[cont]} - {""}
    out = {}
    for c, r in runs.items():
        ids = sorted(r); gruppi = []   # [chiave, set(run)]
        for i in ids:
            for k in sorted(r[i]):
                g = next((g for g in gruppi if uguali(k, g[0])), None)
                if g is None: gruppi.append([k, {i}])
                else: g[1].add(i)
        out[c] = (ids, [g[1] for g in gruppi])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True); ap.add_argument("--contenitore", default="enti_identificati", choices=NOME)
    ap.add_argument("--rep", type=int, default=200); ap.add_argument("--ns", default="3,5,7,10")
    a = ap.parse_args(); random.seed(1)
    P = presenze(a.tag, a.contenitore)
    ns = [int(x) for x in a.ns.split(",")]
    print(f"{a.tag} / {a.contenitore}: {len(P)} protocolli, run per protocollo {sorted({len(v[0]) for v in P.values()})}")
    hist = Counter()
    for c, (ids, gr) in P.items():
        for g in gr: hist[len(g)] += 1
    print("entità per n. di run in cui compaiono:", dict(sorted(hist.items(), reverse=True)))
    print("\n n  unione  in_tutte  da_rivedere  copertura  falsi_stabili")
    for n in ns:
        tot = Counter(); 
        for c, (ids, gr) in P.items():
            nn = min(n, len(ids)); U_all = len(gr)
            sets = list(itertools.combinations(ids, nn))
            if len(sets) > a.rep: sets = random.sample(sets, a.rep)
            acc = Counter()
            for s in sets:
                s = set(s); pres = [g & s for g in gr]
                u = sum(1 for p in pres if p); t = sum(1 for p in pres if len(p) == nn)
                fs = sum(1 for g, p in zip(gr, pres) if len(p) == nn and len(g) < len(ids))
                acc.update(unione=u, tutte=t, falsi=fs)
            for k, v in acc.items(): tot[k] += v / len(sets)
            tot["U"] += U_all
        print(f"{n:2d}  {tot['unione']:6.1f}  {tot['tutte']:7.1f}  {tot['unione']-tot['tutte']:10.1f}  {tot['unione']/tot['U']:8.3f}  {tot['falsi']:12.1f}")
    print(f"\n(totale su tutte le run: {sum(len(g) for _, g in P.values())} entità)")


if __name__ == "__main__":
    main()
