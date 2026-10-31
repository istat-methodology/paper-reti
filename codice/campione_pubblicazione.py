"""Campione per la pubblicazione: stratificato per regione, sistematico sulla lunghezza dentro la regione.

Frame: protocolli con almeno MIN_CARATTERI caratteri di testo (esclude i protocolli senza testo).
Allocazione: 1 protocollo per regione, il resto in proporzione al numero di protocolli (resti più grandi).
Dentro la regione: protocolli ordinati per lunghezza (a parità, per codice); k punti equidistanti con partenza casuale (seed).
Uso: python codice/campione_pubblicazione.py [--n 60] [--seed 20261031]
Scrive campione/campione_pubblicazione_v1.csv (solo codici e lunghezze: si può committare)."""
import argparse
import numpy as np
import pandas as pd
from config import MICRODATI, REPO

MIN_CARATTERI = 500
PILOTA = {"0901", "0902", "0903", "0904", "0905", "0906", "0907", "0908", "0910", "0911", "0912"}   # Toscana, esperimenti di stadio 1


def alloca(cnt, n):
    base = pd.Series(1, index=cnt.index)
    q = (cnt - 1) / (cnt - 1).sum() * (n - len(cnt))
    add = np.floor(q).astype(int); base += add
    r = (q - add).sort_values(ascending=False); k = 0
    while base.sum() < n:
        i = r.index[k % len(r)]
        if base[i] < cnt[i]:
            base[i] += 1
        k += 1
    return base


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=60); ap.add_argument("--seed", type=int, default=20261031)
    a = ap.parse_args()
    an = pd.read_excel(MICRODATI / "rif_anagrafica_v1.xlsx", dtype=str)[["codice", "regione"]]
    an["caratteri"] = [len((MICRODATI / "protocolli" / f"protocollo_{c}.txt").read_text(encoding="utf-8", errors="ignore")) for c in an.codice]
    frame = an[an.caratteri >= MIN_CARATTERI].copy()
    cnt = frame.groupby("regione").size().sort_values(ascending=False)
    k = alloca(cnt, a.n)
    rng = np.random.default_rng(a.seed)
    sel = []
    for reg in sorted(cnt.index):
        s = frame[frame.regione == reg].sort_values(["caratteri", "codice"]).reset_index(drop=True)
        N, kk = len(s), int(k[reg]); u = rng.random()
        pos = sorted({min(int((u + j) * N / kk), N - 1) for j in range(kk)})
        assert len(pos) == kk, (reg, N, kk, pos)
        sel.append(s.iloc[pos].assign(rango_lunghezza=[f"{p + 1}/{N}" for p in pos]))
    out = pd.concat(sel)
    out["pilota"] = out.codice.isin(PILOTA).map({True: "si", False: "no"})
    out = out.sort_values(["regione", "caratteri"])
    f = REPO / "campione" / "campione_pubblicazione_v1.csv"
    out[["codice", "regione", "caratteri", "rango_lunghezza", "pilota"]].to_csv(f, sep=";", index=False, encoding="utf-8-sig")
    print(f"frame {len(frame)} protocolli, 18 regioni -> campione {len(out)} (seed {a.seed}) -> {f}")
    print(out.groupby("regione").size().reindex(cnt.index).to_string())
    for nome, d in (("frame", frame), ("campione", out)):
        q = d.caratteri.quantile([.25, .5, .75, .9]).round(0).astype(int).tolist()
        print(f"{nome:9s} caratteri: quartili {q[:3]}, p90 {q[3]}, max {d.caratteri.max()}")
    print("pilota estratti:", out[out.pilota == "si"].codice.tolist())
    print("oltre 40.000 caratteri:", int((out.caratteri > 40000).sum()), "su", len(out), "; frame:", int((frame.caratteri > 40000).sum()), "su", len(frame))


if __name__ == "__main__":
    main()
