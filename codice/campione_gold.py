"""Estrae il sottoinsieme 'gold' (annotazione manuale da zero) dai 60 protocolli del campione.
Disegno: esclusi i protocolli pilota (usati per mettere a punto il prompt) e quelli oltre 100.000 caratteri (onere di annotazione); ordinati per regione e lunghezza;
campionamento sistematico con partenza casuale (seed fisso). Un sotto-campione 'doppia' per il secondo annotatore.
"""
import csv, random, sys
from pathlib import Path
RAD = Path(__file__).resolve().parent.parent
SEED, N_GOLD, N_DOPPIA, MAX_CAR = 20261101, 20, 8, 100000

def sistematico(lista, n, rng):
    k = len(lista) / n
    start = rng.random() * k
    return [lista[int(start + i * k)] for i in range(n)]

def main():
    rows = list(csv.DictReader(open(RAD/"campione/campione_pubblicazione_v1.csv", encoding="utf-8-sig"), delimiter=";"))
    pool = [r for r in rows if r["pilota"] != "si" and int(r["caratteri"]) <= MAX_CAR]
    pool.sort(key=lambda r: (r["regione"], int(r["caratteri"])))
    rng = random.Random(SEED)
    gold = sistematico(pool, N_GOLD, rng)
    gold.sort(key=lambda r: (r["regione"], int(r["caratteri"])))
    dop = {r["codice"] for r in sistematico(gold, N_DOPPIA, rng)}
    out = RAD/"campione/campione_gold_v1.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["codice","regione","caratteri","doppia"])
        for r in gold: w.writerow([r["codice"], r["regione"], r["caratteri"], "si" if r["codice"] in dop else "no"])
    print("pool", len(pool), "gold", len(gold), "doppia", len(dop))
    for r in gold: print(r["codice"], r["regione"], r["caratteri"], "doppia" if r["codice"] in dop else "")
main()
