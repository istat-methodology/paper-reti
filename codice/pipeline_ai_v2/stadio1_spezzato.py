"""Stadio 1 con protocolli lunghi spezzati in pezzi, poi fusione degli elenchi.

Sotto --soglia caratteri il testo va intero (come stadio1_estrazione.py). Sopra, viene tagliato sui capoversi in pezzi di
circa --pezzo caratteri, con --sovrapposizione tra pezzi consecutivi e gli ultimi --coda caratteri (di solito le firme)
aggiunti a ogni pezzo. Ogni pezzo è una chiamata; i risultati dei pezzi sono salvati in <tag>/_pezzi/ (se una chiamata
fallisce, si rifanno solo quelle mancanti). Fusione: nome tollerante, nome più completo, ruolo più forte.
Output: microdati/ai_v2/stadio1/<tag>/<codice>_run<k>.json, stesso formato di stadio1_estrazione.py (pagina = null).

Esempi: python stadio1_spezzato.py --codici 0902,0911 --runs 3 --prompt v1_2 --tag v1_2_testo_spezzato
        python stadio1_spezzato.py --campione campione/campione_pubblicazione_v1.csv --runs 5 --tag pubblicazione_v1_2
        python stadio1_spezzato.py --tutti --runs 5 --tag pubblicazione_v1_2      (salta le run già fatte)
"""
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stadio1_estrazione as S1  # noqa: E402
from stabilita_tollerante import norm as norm_t, uguali  # noqa: E402

MICRODATI, REPO = S1.MICRODATI, S1.REPO
FORZA_RUOLO = {"firmatario": 3, "componente_rete": 2, "solo_citato": 1}
AVVISO = ("ATTENZIONE: il testo che segue è un estratto di un documento più lungo (parte {i} di {n}). "
          "Estrai solo gli enti e le menzioni presenti in questo estratto e non dedurre nulla da ciò che manca. "
          "Le prime righe possono ripetere la fine dell'estratto precedente. In fondo è riportato il blocco finale del documento.\n\n")


def spezza(testo, pezzo, sovr, coda):
    """lista di testi: pezzi tagliati sui capoversi, con sovrapposizione e coda del documento"""
    par = [p for p in testo.split("\n\n")]
    pezzi, cur, lung = [], [], 0
    for p in par:
        cur.append(p); lung += len(p) + 2
        if lung >= pezzo:
            pezzi.append(cur)
            tail, l2 = [], 0
            for q in reversed(cur):
                if l2 >= sovr: break
                tail.insert(0, q); l2 += len(q) + 2
            cur, lung = list(tail), l2
    if cur and (not pezzi or len("\n\n".join(cur)) > sovr + 200):
        pezzi.append(cur)
    testi = ["\n\n".join(c) for c in pezzi] or [testo]
    fine = testo[-coda:] if coda else ""
    out = []
    for i, t in enumerate(testi):
        if fine and fine not in t and i < len(testi) - 1:
            t = t + "\n\n[...]\n\n" + fine
        out.append(t)
    return out


def chiama(client, cfg, sys_p, usr_p, testo, i, n):
    usr = (AVVISO.format(i=i, n=n) if n > 1 else "") + usr_p
    inp = [{"role": "user", "content": [{"type": "input_text", "text": usr + "\n\n## TESTO DEL PROTOCOLLO\n<<<\n" + testo + "\n>>>"}]}]
    kw = dict(model=cfg["deployment"], instructions=sys_p, input=inp,
              text={"format": {"type": "json_schema", "name": "stadio1_enti", "schema": S1.SCHEMA, "strict": True}})
    if cfg["effort"]:
        kw["reasoning"] = {"effort": cfg["effort"]}
    r = client.responses.create(**kw)
    u = getattr(r, "usage", None)
    return json.loads(r.output_text), (getattr(u, "input_tokens", 0) or 0), (getattr(u, "output_tokens", 0) or 0)


def stesso_ente(k1, k2):
    """nomi normalizzati: uguali/simili (come nel confronto tra run), oppure le parole del nome più corto
    (almeno 2) sono tutte nel più lungo e i due nomi iniziano con la stessa parola
    ("procura siena" in "procura repubblica tribunale siena")"""
    if uguali(k1, k2):
        return True
    a, b = k1.split(), k2.split()
    if len(a) > len(b):
        a, b = b, a
    return len(a) >= 2 and a[0] == b[0] and set(a) <= set(b)


def fondi(risultati):
    """unisce gli elenchi dei pezzi: nome tollerante, nome più lungo, ruolo più forte, prima citazione"""
    ident, gen = [], []
    for d in risultati:
        for e in d["enti_identificati"]:
            k = norm_t(e["nome"])
            t = next((x for x in ident if stesso_ente(k, x["_k"])), None)
            if t is None:
                ident.append(dict(e, _k=k)); continue
            if len(e["nome"]) > len(t["nome"]):
                t["nome"], t["_k"] = e["nome"], k
            if FORZA_RUOLO[e["ruolo_nel_documento"]] > FORZA_RUOLO[t["ruolo_nel_documento"]]:
                t["ruolo_nel_documento"], t["citazione"] = e["ruolo_nel_documento"], e["citazione"]
            t["forma_giuridica_dichiarata"] = t["forma_giuridica_dichiarata"] or e["forma_giuridica_dichiarata"]
        for e in d["menzioni_generiche"]:
            k = norm_t(e["espressione"]); ka = norm_t(e["ente_di_appartenenza"] or "")
            t = next((x for x in gen if x["_ka"] == ka and uguali(k, x["_k"])), None)
            if t is None:
                gen.append(dict(e, _k=k, _ka=ka)); continue
            if FORZA_RUOLO[e["ruolo_nel_documento"]] > FORZA_RUOLO[t["ruolo_nel_documento"]]:
                t["ruolo_nel_documento"] = e["ruolo_nel_documento"]
    for x in ident + gen:
        x.pop("_k", None); x.pop("_ka", None); x["pagina"] = None
    note = " | ".join(f"p{i + 1}: {d['note']}" for i, d in enumerate(risultati) if d.get("note")) or None
    return dict(enti_identificati=ident, menzioni_generiche=gen, note=note)


def scrivi_atomico(path, testo):
    """scrive su un file temporaneo e lo rinomina: se il processo muore a metà, il file vecchio resta intatto"""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(testo, encoding="utf-8"); os.replace(tmp, path)


def leggi_cache(f):
    """contenuto del pezzo già fatto, o None se manca o è rovinato (in quel caso il pezzo si rifà)"""
    try:
        c = json.loads(f.read_text(encoding="utf-8")); return c["dati"], c["tin"], c["tout"]
    except Exception:
        return None


def una_run(client, cfg, codice, k, sys_p, usr_p, p_hash, outdir, a):
    t0 = time.time()
    testo = (MICRODATI / "protocolli" / f"protocollo_{codice}.txt").read_text(encoding="utf-8", errors="ignore")
    pezzi = spezza(testo, a.pezzo, a.sovrapposizione, a.coda) if len(testo) > a.soglia else [testo]
    cache = outdir / "_pezzi"; cache.mkdir(exist_ok=True)
    ris, tin, tout = [], 0, 0
    for i, p in enumerate(pezzi, 1):
        f = cache / f"{codice}_run{k}_p{i}di{len(pezzi)}.json"
        c = None if a.rifai_pezzi else leggi_cache(f)
        if c is None:
            c = chiama(client, cfg, sys_p, usr_p, p, i, len(pezzi))
            scrivi_atomico(f, json.dumps(dict(dati=c[0], tin=c[1], tout=c[2]), ensure_ascii=False))
        d, ti, to = c
        ris.append(d); tin += ti; tout += to
    dati = fondi(ris) if len(ris) > 1 else ris[0]
    ref = S1.norm(testo)
    for cont in S1.CONTENITORI:
        for e in dati[cont]:
            e["citazione_copertura"] = round(S1.copertura(e["citazione"], ref), 2)
            e["citazione_trovata_nel_testo"] = e["citazione_copertura"] >= 0.8
    meta = dict(codice=codice, run=k, input="testo_spezzato" if len(pezzi) > 1 else "testo", n_pezzi=len(pezzi),
                lunghezza_pezzi=[len(p) for p in pezzi], parametri=dict(soglia=a.soglia, pezzo=a.pezzo, sovrapposizione=a.sovrapposizione, coda=a.coda),
                deployment=cfg["deployment"], prompt_file=str(S1.PROMPT.relative_to(REPO)), prompt_sha=p_hash, reasoning_effort=cfg["effort"],
                data_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"), secondi=round(time.time() - t0, 1),
                token_input=tin, token_output=tout)
    scrivi_atomico(outdir / f"{codice}_run{k}.json", json.dumps({"meta": meta, **dati}, ensure_ascii=False, indent=1))
    return codice, k, len(pezzi), len(dati["enti_identificati"]), len(dati["menzioni_generiche"])


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--regione"); g.add_argument("--codici")
    g.add_argument("--campione", help="CSV del campione (colonna 'codice'), per es. campione/campione_pubblicazione_v1.csv")
    g.add_argument("--tutti", action="store_true", help="tutti i protocolli con almeno 500 caratteri di testo (249)")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--effort", default=None)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--forza", action="store_true", help="rifà le run finali (riusando i pezzi già estratti: serve per rifare solo la fusione)")
    ap.add_argument("--rifai-pezzi", action="store_true", help="con --forza: rifà anche le chiamate al modello")
    ap.add_argument("--timeout", type=int, default=300, help="secondi massimi per una chiamata")
    ap.add_argument("--tentativi", type=int, default=5, help="nuovi tentativi automatici per chiamata (con attesa crescente)")
    ap.add_argument("--giri", type=int, default=6, help="dopo i fallimenti, quante volte rifare le run mancanti")
    ap.add_argument("--attesa", type=int, default=60, help="secondi di attesa tra un giro e l'altro")
    ap.add_argument("--prompt", default="v1_2")
    ap.add_argument("--tag", default=None, help="default: <prompt>_testo_spezzato")
    ap.add_argument("--soglia", type=int, default=40000)
    ap.add_argument("--pezzo", type=int, default=25000)
    ap.add_argument("--sovrapposizione", type=int, default=2000)
    ap.add_argument("--coda", type=int, default=5000)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    S1.PROMPT = REPO / "prompts" / "v2" / f"stadio1_estrazione_enti_{a.prompt}.txt"
    S1.carica_env()
    sys_p, usr_p, p_hash = S1.carica_prompt()
    if a.campione or a.tutti:
        import pandas as pd
        if a.campione:
            codici = sorted(pd.read_csv(a.campione, sep=";", encoding="utf-8-sig", dtype=str).codice)
        else:
            an = pd.read_excel(MICRODATI / "rif_anagrafica_v2.xlsx", dtype=str).codice
            codici = sorted(c for c in an if len((MICRODATI / "protocolli" / f"protocollo_{c}.txt").read_text(encoding="utf-8", errors="ignore")) >= 500)
    else:
        codici = S1.codici_da_processare(a)
    outdir = MICRODATI / "ai_v2" / "stadio1" / (a.tag or f"{a.prompt}_testo_spezzato")
    if a.dry_run:
        for c in codici:
            t = (MICRODATI / "protocolli" / f"protocollo_{c}.txt").read_text(encoding="utf-8", errors="ignore")
            p = spezza(t, a.pezzo, a.sovrapposizione, a.coda) if len(t) > a.soglia else [t]
            print(f"  {c}: {len(t):,} caratteri -> {len(p)} pezzi {[len(x) for x in p]}")
        return
    outdir.mkdir(parents=True, exist_ok=True)
    cfg = dict(deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", ""), effort=a.effort)
    def mancanti(forza):
        return [(c, k) for c in codici for k in range(1, a.runs + 1) if forza or not (outdir / f"{c}_run{k}.json").exists()]

    compiti = mancanti(a.forza)
    totale = len(compiti)
    print(f"{len(codici)} protocolli, {a.runs} run, prompt {p_hash}, {totale} run da fare -> {outdir}")
    errori = []
    if compiti:
        from openai import OpenAI
        client = OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_OPENAI_API_KEY"], timeout=a.timeout, max_retries=a.tentativi)
        fatte, t0 = 0, time.time()
        for giro in range(1, a.giri + 1):
            errori = []
            with ThreadPoolExecutor(max_workers=a.workers) as ex:
                fut = {ex.submit(una_run, client, cfg, c, k, sys_p, usr_p, p_hash, outdir, a): (c, k) for c, k in compiti}
                for f in as_completed(fut):
                    c, k = fut[f]
                    try:
                        _, _, n, n1, n2 = f.result(); fatte += 1
                        el = time.time() - t0; eta = el / fatte * (totale - fatte)
                        print(f"  ok  {c} run{k}: {n} pezzi, {n1} identificati, {n2} generiche   [{fatte}/{totale}, {el / 60:.0f} min, ancora circa {eta / 60:.0f} min]", flush=True)
                    except Exception as e:
                        msg = f"{c} run{k}: {type(e).__name__}: {str(e)[:300]}".replace(os.environ.get("AZURE_OPENAI_API_KEY", "#"), "***")
                        errori.append(msg); print("  ERR", msg, flush=True)
            if errori:
                with open(outdir / "errori.log", "a", encoding="utf-8") as f:
                    f.write(f"--- {datetime.now().isoformat(timespec='seconds')} giro {giro}\n" + "\n".join(errori) + "\n")
            compiti = mancanti(False)
            if not compiti:
                errori = []; break
            if giro < a.giri:
                print(f"\n{len(compiti)} run mancanti. Giro {giro}/{a.giri} finito, nuovo tentativo tra {a.attesa} s (i pezzi già fatti non si rifanno).", flush=True)
                time.sleep(a.attesa)
    S1.riepilogo(outdir, codici)
    if errori:
        print(f"\n{len(mancanti(False))} run ancora mancanti: rilancia lo stesso comando (i pezzi già fatti non si rifanno)."); sys.exit(1)


if __name__ == "__main__":
    main()
