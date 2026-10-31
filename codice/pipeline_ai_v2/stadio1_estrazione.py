"""Stadio 1 (v2, prompt v1): estrazione degli enti nominati in un protocollo, in due elenchi separati.
  enti_identificati   : organizzazioni con nome proprio (nome, forma giuridica dichiarata, ruolo nel documento, citazione)
  menzioni_generiche  : tipologie, strutture senza nome, istituzioni senza riferimento (espressione, tipo, ente di appartenenza, ruolo, citazione)
Nessuna classificazione nelle 30 categorie (è lo stadio 2).

Esempi:
  python codice/pipeline_ai_v2/stadio1_estrazione.py --regione Toscana --runs 3 --input pdf
  python codice/pipeline_ai_v2/stadio1_estrazione.py --regione Toscana --runs 3 --input testo
  python codice/pipeline_ai_v2/stadio1_estrazione.py --codici 0912 --runs 1          (prova rapida)
  python codice/pipeline_ai_v2/stadio1_estrazione.py --regione Toscana --dry-run     (non chiama il modello)

Input:  testo -> microdati/protocolli/protocollo_<codice>.txt
        pdf   -> microdati/protocolli_pdf/protocollo_<codice>.pdf  (i file sopra --max-mb, default 3 MB, vengono saltati
                 e elencati in saltati_per_dimensione.txt)
Output: microdati/ai_v2/stadio1/<tag>/<codice>_run<k>.json   (tag di default: <prompt>_<input>, per es. v1_1_pdf; fuori da git)
        microdati/ai_v2/stadio1/<tag>/riepilogo.csv           (stabilità tra le run, per contenitore)
Ogni file registra modello, prompt (hash), parametri, durata e token. Gli errori non sono silenziosi:
vengono scritti in errori.log e lo script termina con codice 1."""
import argparse, base64, csv, hashlib, json, os, re, sys, time, unicodedata
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MICRODATI, REPO  # noqa: E402

PROMPT = REPO / "prompts" / "v2" / "stadio1_estrazione_enti_v1_1.txt"   # sovrascritto da --prompt
ESCLUSI = {"0909", "0326", "044101", "0507", "1612", "1613"}
S = {"type": "string"}
SN = {"type": ["string", "null"]}
IN = {"type": ["integer", "null"]}


def obj(**props):
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


SCHEMA = obj(
    enti_identificati={"type": "array", "items": obj(
        nome=S, forma_giuridica_dichiarata=SN,
        ruolo_nel_documento={"type": "string", "enum": ["firmatario", "componente_rete", "solo_citato"]},
        citazione=S, pagina=IN)},
    menzioni_generiche={"type": "array", "items": obj(
        espressione=S,
        tipo_menzione={"type": "string", "enum": ["tipologia", "struttura_senza_nome", "istituzione_senza_riferimento"]},
        ente_di_appartenenza=SN,
        ruolo_nel_documento={"type": "string", "enum": ["componente_rete", "solo_citato"]},
        citazione=S, pagina=IN)},
    note=SN)
CONTENITORI = {"enti_identificati": "nome", "menzioni_generiche": "espressione"}


def norm(s):
    """minuscolo, senza accenti (il testo OCR spesso li perde), solo parole"""
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\W+", " ", s).strip()


def copertura(citazione, ref_norm):
    """quota di sequenze di 3 parole della citazione presenti nel testo (tollera errori OCR sparsi)"""
    w = norm(citazione).split()
    if len(w) < 3:
        return 1.0 if norm(citazione) and norm(citazione) in ref_norm else 0.0
    tri = [" ".join(w[i:i + 3]) for i in range(len(w) - 2)]
    return sum(t in ref_norm for t in tri) / len(tri)


def carica_prompt():
    t = PROMPT.read_text(encoding="utf-8")
    sys_p = t.split("### SYSTEM", 1)[1].split("### USER", 1)[0].strip()
    usr_p = t.split("### USER", 1)[1].strip()
    return sys_p, usr_p, hashlib.sha256(t.encode()).hexdigest()[:12]


def carica_env():
    env = REPO / ".env"
    if env.exists():
        for r in env.read_text(encoding="utf-8").splitlines():
            if "=" in r and not r.strip().startswith("#"):
                k, v = r.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def codici_da_processare(args):
    if args.codici:
        return [c.strip() for c in args.codici.split(",")]
    import pandas as pd
    a = pd.read_excel(MICRODATI / "rif_anagrafica_v1.xlsx", dtype=str)
    a = a[(a.regione == args.regione) & ~a.codice.isin(ESCLUSI)]
    return sorted(a.codice)


def costruisci_input(usr_p, codice, modo):
    if modo == "testo":
        testo = (MICRODATI / "protocolli" / f"protocollo_{codice}.txt").read_text(encoding="utf-8", errors="ignore")
        return [{"role": "user", "content": [{"type": "input_text", "text": usr_p + "\n\n## TESTO DEL PROTOCOLLO\n<<<\n" + testo + "\n>>>"}]}]
    pdf = MICRODATI / "protocolli_pdf" / f"protocollo_{codice}.pdf"
    b64 = base64.b64encode(pdf.read_bytes()).decode()
    return [{"role": "user", "content": [
        {"type": "input_file", "filename": pdf.name, "file_data": f"data:application/pdf;base64,{b64}"},
        {"type": "input_text", "text": usr_p + "\n\nIl protocollo è nel PDF allegato."}]}]


def una_run(client, cfg, codice, k, sys_p, usr_p, p_hash, outdir):
    out = outdir / f"{codice}_run{k}.json"
    t0 = time.time()
    kw = dict(model=cfg["deployment"], instructions=sys_p, input=costruisci_input(usr_p, codice, cfg["input"]),
              text={"format": {"type": "json_schema", "name": "stadio1_enti", "schema": SCHEMA, "strict": True}})
    if cfg["effort"]:
        kw["reasoning"] = {"effort": cfg["effort"]}
    r = client.responses.create(**kw)
    dati = json.loads(r.output_text)
    ref = norm((MICRODATI / "protocolli" / f"protocollo_{codice}.txt").read_text(encoding="utf-8", errors="ignore"))
    for cont in CONTENITORI:
        for e in dati[cont]:
            e["citazione_copertura"] = round(copertura(e["citazione"], ref), 2)
            e["citazione_trovata_nel_testo"] = e["citazione_copertura"] >= 0.8
    u = getattr(r, "usage", None)
    meta = dict(codice=codice, run=k, input=cfg["input"], deployment=cfg["deployment"], modello_restituito=getattr(r, "model", None),
                prompt_file=str(PROMPT.relative_to(REPO)), prompt_sha=p_hash, reasoning_effort=cfg["effort"],
                response_id=getattr(r, "id", None), data_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                secondi=round(time.time() - t0, 1),
                token_input=getattr(u, "input_tokens", None), token_output=getattr(u, "output_tokens", None))
    out.write_text(json.dumps({"meta": meta, **dati}, ensure_ascii=False, indent=1), encoding="utf-8")
    return codice, k, len(dati["enti_identificati"]), len(dati["menzioni_generiche"])


def riepilogo(outdir, codici):
    righe, stab = [], []
    for c in codici:
        runs = sorted(outdir.glob(f"{c}_run*.json"))
        if not runs:
            continue
        dati = [json.loads(f.read_text(encoding="utf-8")) for f in runs]
        riga_stab = [c, len(runs)]
        for cont, campo in CONTENITORI.items():
            reg = defaultdict(lambda: dict(nome="", ruoli=set(), extra=set(), n=0, cit_ok=0))
            per_run = []
            for d in dati:
                chiavi = set()
                for e in d[cont]:
                    key = norm(e[campo]); chiavi.add(key)
                    x = reg[key]; x["nome"] = x["nome"] or e[campo]; x["ruoli"].add(e["ruolo_nel_documento"]); x["n"] += 1
                    x["cit_ok"] += int(e.get("citazione_trovata_nel_testo", False))
                    extra = e.get("forma_giuridica_dichiarata") if cont == "enti_identificati" else e.get("tipo_menzione")
                    if extra:
                        x["extra"].add(extra)
                per_run.append(chiavi)
            tutte, comuni = set.union(*per_run), set.intersection(*per_run)
            jac = [len(a & b) / len(a | b) for i, a in enumerate(per_run) for b in per_run[i + 1:] if a | b]
            riga_stab += [[len(p) for p in per_run], len(comuni), len(tutte), round(sum(jac) / len(jac), 3) if jac else ""]
            for key, x in sorted(reg.items(), key=lambda kv: -kv[1]["n"]):
                righe.append(dict(codice=c, contenitore=cont, nome=x["nome"], n_run_presente=x["n"], n_run=len(runs),
                                  ruoli="|".join(sorted(x["ruoli"])), forma_o_tipo="|".join(sorted(x["extra"])), citazioni_trovate=x["cit_ok"]))
        stab.append(riga_stab)
    with open(outdir / "riepilogo.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["codice", "contenitore", "nome", "n_run_presente", "n_run", "ruoli", "forma_o_tipo", "citazioni_trovate"], delimiter=";")
        w.writeheader(); w.writerows(righe)
    for i, (cont, titolo) in enumerate([("enti_identificati", "NUCLEO: enti identificati"), ("menzioni_generiche", "PERIFERIA: menzioni generiche")]):
        print(f"\n{titolo}\ncodice  run  enti_per_run      in_tutte_le_run  in_almeno_una  jaccard_medio")
        for s in stab:
            q = s[2 + 4 * i: 6 + 4 * i]
            print(f"{s[0]:<7} {s[1]:<4} {str(q[0]):<17} {q[1]:<16} {q[2]:<14} {q[3]}")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--regione"); g.add_argument("--codici")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--input", choices=["testo", "pdf"], default="testo")
    ap.add_argument("--effort", default=None, help="reasoning effort (low/medium/high), se il modello lo supporta")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--forza", action="store_true", help="rifà anche le run già presenti")
    ap.add_argument("--prompt", default="v1_1", help="versione del prompt in prompts/v2/ (stadio1_estrazione_enti_<versione>.txt)")
    ap.add_argument("--tag", default=None, help="nome della cartella di output (default: <versione prompt>_<input>)")
    ap.add_argument("--max-mb", type=float, default=3.0, help="con --input pdf salta i PDF più grandi di questa soglia in MB (0 = nessun limite)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    global PROMPT
    PROMPT = REPO / "prompts" / "v2" / f"stadio1_estrazione_enti_{a.prompt}.txt"
    carica_env()
    sys_p, usr_p, p_hash = carica_prompt()
    codici = codici_da_processare(a)
    outdir = MICRODATI / "ai_v2" / "stadio1" / (a.tag or f"{a.prompt}_{a.input}")
    if not a.dry_run:
        outdir.mkdir(parents=True, exist_ok=True)
    if a.input == "pdf" and a.max_mb > 0:
        grandi = {c: (MICRODATI / "protocolli_pdf" / f"protocollo_{c}.pdf").stat().st_size / 1e6 for c in codici}
        grandi = {c: mb for c, mb in grandi.items() if mb > a.max_mb}
        if grandi:
            print("Saltati per dimensione (> %s MB): %s" % (a.max_mb, ", ".join(f"{c} ({mb:.1f} MB)" for c, mb in grandi.items())))
            if not a.dry_run:
                (outdir / "saltati_per_dimensione.txt").write_text(f"soglia {a.max_mb} MB\n" + "\n".join(f"{c}\t{mb:.1f} MB" for c, mb in grandi.items()) + "\n", encoding="utf-8")
            codici = [c for c in codici if c not in grandi]
    cfg = dict(input=a.input, deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", ""), effort=a.effort)
    compiti = [(c, k) for c in codici for k in range(1, a.runs + 1) if a.forza or not (outdir / f"{c}_run{k}.json").exists()]
    print(f"{len(codici)} protocolli, {a.runs} run, input={a.input}, prompt {p_hash}, {len(compiti)} chiamate da fare -> {outdir}")

    if a.dry_run:
        for c in codici:
            req = costruisci_input(usr_p, c, a.input)
            n = sum(len(x.get("text", "")) + len(x.get("file_data", "")) for x in req[0]["content"])
            print(f"  {c}: richiesta di {n:,} caratteri")
        return
    if not compiti:
        riepilogo(outdir, codici); return

    from openai import OpenAI
    client = OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_OPENAI_API_KEY"], timeout=900, max_retries=2)
    errori = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        fut = {ex.submit(una_run, client, cfg, c, k, sys_p, usr_p, p_hash, outdir): (c, k) for c, k in compiti}
        for f in as_completed(fut):
            c, k = fut[f]
            try:
                _, _, n1, n2 = f.result()
                print(f"  ok  {c} run{k}: {n1} identificati, {n2} generiche")
            except Exception as e:
                msg = f"{c} run{k}: {type(e).__name__}: {str(e)[:300]}".replace(os.environ.get("AZURE_OPENAI_API_KEY", "#"), "***")
                errori.append(msg); print("  ERR", msg)
    if errori:
        with open(outdir / "errori.log", "a", encoding="utf-8") as f:
            f.write(f"--- {datetime.now().isoformat(timespec='seconds')}\n" + "\n".join(errori) + "\n")
    riepilogo(outdir, codici)
    if errori:
        print(f"\n{len(errori)} chiamate fallite: vedi {outdir / 'errori.log'}. Rilancia lo stesso comando per rifare solo quelle."); sys.exit(1)


if __name__ == "__main__":
    main()
