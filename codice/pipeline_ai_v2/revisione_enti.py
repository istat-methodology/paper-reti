"""Revisione manuale degli enti del nucleo (stadio 1).

  prepara:  python revisione_enti.py prepara --tag v1_2_testo [--codici 0901,0902] [--n-run 5] [--campione 0.1]
            -> revisione/revisione_<tag>.xlsx (enti da rivedere, con colonne di decisione)
               revisione/enti_automatici_<tag>.csv (tutti gli enti, prima della revisione)
  applica:  python revisione_enti.py applica --tag v1_2_testo --decisioni revisione/revisione_<tag>_compilato.xlsx
            -> revisione/enti_finali_<tag>.csv (decisioni applicate)

Un ente è da rivedere se: non è presente in tutte le run, cambia ruolo tra run, ha un nome simile a un altro ente dello
stesso protocollo (possibile doppione), ha la citazione non trovata nel testo, oppure è nel campione casuale degli enti
unanimi (per stimare la precisione del consenso). Le decisioni sono righe (protocollo, nome) -> azione: restano
valide se si rilanciano le run, perché si agganciano a qualsiasi variante del nome."""
import argparse, csv, difflib, json, random, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MICRODATI, REPO  # noqa: E402
from stabilita_tollerante import BASE, formato_v2, norm, uguali  # noqa: E402

OUT = REPO / "revisione"
FORZA = {"firmatario": 3, "componente_rete": 2, "solo_citato": 1}
AZIONI = ["corretto", "sbagliato", "elimina", "unisci"]


def carica(tag, codici=None, n_run=None):
    """{codice: (n_run, [gruppo])}; gruppo = nomi (Counter), varianti (norm), run, ruoli (Counter), citazioni"""
    runs = {}
    for f in sorted((BASE / tag).glob("[0-9]*_run*.json")):
        d = formato_v2(json.loads(f.read_text(encoding="utf-8"))); c = d["meta"]["codice"]
        if codici and c not in codici:
            continue
        runs.setdefault(c, {})[d["meta"]["run"]] = d["enti_identificati"]
    out = {}
    for c, r in sorted(runs.items()):
        ids = sorted(r)[:n_run] if n_run else sorted(r)
        gr = []
        for i in ids:
            for e in r[i]:
                k = norm(e["nome"])
                if not k:
                    continue
                g = next((g for g in gr if any(uguali(k, v) for v in g["varianti"])), None)
                if g is None:
                    g = dict(nomi=Counter(), varianti=set(), run=set(), ruoli=Counter(), cit=[], cit_ok=Counter())
                    gr.append(g)
                g["varianti"].add(k)
                if i not in g["run"]:
                    g["ruoli"][e["ruolo_nel_documento"]] += 1
                g["run"].add(i); g["nomi"][e["nome"]] += 1
                g["cit"].append((FORZA[e["ruolo_nel_documento"]], e["citazione"]))
                g["cit_ok"][bool(e.get("citazione_trovata_nel_testo", True))] += 1
        out[c] = (len(ids), gr)
    return out


def nome(g):
    return max(g["nomi"], key=lambda n: (g["nomi"][n], len(n)))


def contesto(codice, citazione, margine=250, _cache={}):
    """tratto di testo del protocollo attorno alla citazione, con la citazione tra « »; se non si trova, la sola citazione"""
    import re
    if codice not in _cache:
        t = (MICRODATI / "protocolli" / f"protocollo_{codice}.txt").read_text(encoding="utf-8", errors="ignore")
        _cache[codice] = re.sub(r"\s+", " ", t)
    t = _cache[codice]; q = re.sub(r"\s+", " ", citazione).strip()
    for cand in (q, q[:80], q[:40]):
        k = t.lower().find(cand.lower()) if cand else -1
        if k >= 0:
            fine = k + len(q) if cand == q else k + len(cand)
            return ("…" if k > margine else "") + t[max(0, k - margine):k] + "«" + t[k:fine] + "»" + t[fine:fine + margine] + "…"
    return "«" + q + "» (citazione non ritrovata nel testo)"


def scrivi_excel(a, righe, dati):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation
    import pandas as pd
    random.seed(20261031)
    an = pd.read_excel(MICRODATI / "rif_anagrafica_v1.xlsx", dtype=str).set_index("codice")
    # righe mescolate dentro ogni protocollo, con id progressivo: chi rivede non vede il motivo
    per = {}
    for r in righe: per.setdefault(r["codice"], []).append(r)
    ordine = []
    for c in sorted(per):
        random.shuffle(per[c]); ordine += per[c]
    for n, r in enumerate(ordine, 1): r["id"] = f"R{n:04d}"
    wb = Workbook(); grassetto = Font(bold=True); fill = PatternFill("solid", fgColor="DDEBF7"); fill_dec = PatternFill("solid", fgColor="FFF2CC")
    wrap = Alignment(wrap_text=True, vertical="top")

    ist = wb.active; ist.title = "istruzioni"
    testo = [
        "REVISIONE DEGLI ENTI ESTRATTI DAI PROTOCOLLI",
        "",
        "Foglio 'revisione': una riga per ente proposto dal modello. 'codice_protocollo' è il protocollo; 'id_riga' è solo un numero di riga.",
        "Leggi il contesto (la citazione del protocollo è tra « »). Se serve, apri il protocollo: il foglio 'protocolli' dice quale file.",
        "Per ogni riga scegli un valore in 'azione'. Una riga senza azione risulta non rivista.",
        "",
        "corretto  = è un'organizzazione con un nome proprio e il ruolo proposto è giusto.",
        "sbagliato = è un'organizzazione, ma il nome o il ruolo sono sbagliati: scrivi il valore giusto in 'nome_corretto' e/o 'ruolo_corretto'.",
        "elimina   = non è un'organizzazione (persona, legge, documento, progetto, programma).",
        "unisci    = è lo stesso ente di un'altra riga dello stesso protocollo (stesso ente scritto in due modi, o l'ente e la sua sigla): scrivi in 'unisci_con' il nome dell'altra riga",
        "            (il foglio 'tutti_gli_enti' elenca tutti gli enti del protocollo). Due enti diversi con nome simile (due Comuni, due Procure di città diverse) NON si uniscono.",
        "",
        "Ruoli: firmatario = sottoscrive il documento; componente_rete = fa parte della rete o ha impegni; solo_citato = nominato senza far parte della rete e senza impegni.",
        "Un'organizzazione che non fa parte della rete NON si elimina: resta, con ruolo solo_citato (esempio: l'ente che certifica la firma digitale).",
        "'note': dubbi e casi particolari.",
        "Foglio 'mancanti': se leggendo il protocollo vedi un ente con nome proprio che non è in 'tutti_gli_enti', scrivilo lì.",
        "Finisci un protocollo prima di passare al successivo.",
    ]
    for t in testo: ist.append([t])
    ist["A1"].font = Font(bold=True, size=13); ist.column_dimensions["A"].width = 170

    ws = wb.create_sheet("revisione")
    cols = ["id_riga", "codice_protocollo", "nome", "ruolo_proposto", "contesto", "azione", "unisci_con", "nome_corretto", "ruolo_corretto", "note"]
    ws.append(cols)
    for r in ordine:
        ws.append([r["id"], r["codice"], r["nome"], r["ruolo_prevalente"], contesto(r["codice"], r["citazione"]), None, None, None, None, None])
    for c in ws[1]:
        c.font = grassetto; c.fill = fill_dec if c.value in ("azione", "unisci_con", "nome_corretto", "ruolo_corretto", "note") else fill
    for col, w_ in zip("ABCDEFGHIJ", [8, 8, 42, 16, 90, 12, 34, 34, 16, 34]): ws.column_dimensions[col].width = w_
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = wrap
    n = len(ordine) + 1
    dv = DataValidation(type="list", formula1='"' + ",".join(AZIONI) + '"', allow_blank=True); ws.add_data_validation(dv); dv.add(f"F2:F{n}")
    dv2 = DataValidation(type="list", formula1='"firmatario,componente_rete,solo_citato"', allow_blank=True); ws.add_data_validation(dv2); dv2.add(f"I2:I{n}")
    ws.freeze_panes = "D2"; ws.auto_filter.ref = f"A1:J{n}"

    wt = wb.create_sheet("tutti_gli_enti"); wt.append(["codice_protocollo", "nome", "ruolo_proposto"])
    for c in sorted(dati):
        for g in sorted(dati[c][1], key=lambda g: nome(g).lower()): wt.append([c, nome(g), g["ruoli"].most_common(1)[0][0]])
    for c in wt[1]: c.font = grassetto; c.fill = fill
    for col, w_ in zip("ABC", [8, 70, 18]): wt.column_dimensions[col].width = w_
    wt.freeze_panes = "A2"; wt.auto_filter.ref = f"A1:C{wt.max_row}"

    wp = wb.create_sheet("protocolli"); wp.append(["codice_protocollo", "regione", "titolo_documento", "file_allegato", "caratteri", "righe_da_rivedere"])
    conta = Counter(r["codice"] for r in righe)
    for c in sorted(dati):
        t = (MICRODATI / "protocolli" / f"protocollo_{c}.txt").read_text(encoding="utf-8", errors="ignore")
        x = an.loc[c] if c in an.index else {}
        wp.append([c, x.get("regione"), x.get("titolo_documento"), x.get("allegato_gino_3_9"), len(t), conta.get(c, 0)])
    for c in wp[1]: c.font = grassetto; c.fill = fill
    for col, w_ in zip("ABCDEF", [8, 16, 80, 50, 10, 16]): wp.column_dimensions[col].width = w_
    wp.freeze_panes = "A2"

    wm = wb.create_sheet("mancanti"); wm.append(["codice_protocollo", "nome_ente_mancante", "ruolo", "dove_nel_testo", "note"])
    for c in wm[1]: c.font = grassetto; c.fill = fill_dec
    for col, w_ in zip("ABCDE", [8, 60, 18, 60, 40]): wm.column_dimensions[col].width = w_
    dv3 = DataValidation(type="list", formula1='"firmatario,componente_rete,solo_citato"', allow_blank=True); wm.add_data_validation(dv3); dv3.add("C2:C500")

    wi = wb.create_sheet("info_tecnica"); wi.append(["id_riga", "codice_protocollo", "nome", "n_run_presente", "n_run", "ruolo_prevalente", "ruoli", "varianti_nome", "motivo"])
    for r in ordine:
        wi.append([r["id"], r["codice"], r["nome"], r["n_run_presente"], r["n_run"], r["ruolo_prevalente"], r["ruoli"], r["varianti_nome"], r["motivo"]])
    wi.sheet_state = "hidden"
    wb.save(OUT / f"revisione_{a.tag}.xlsx")


def prepara(a):
    random.seed(20261031)
    dati = carica(a.tag, a.codici.split(",") if a.codici else None, a.n_run)
    OUT.mkdir(exist_ok=True)
    righe, tutti, coppia_id = [], [], 0
    for c, (n, gr) in dati.items():
        coppie = {}
        for i in range(len(gr)):
            for j in range(i + 1, len(gr)):
                x, y = nome(gr[i]), nome(gr[j]); nx, ny = norm(x), norm(y)
                sx, sy = set(nx.split()), set(ny.split())
                sub = min(len(sx), len(sy)) >= 2 and (sx <= sy or sy <= sx)   # un nome è contenuto nell'altro
                if sub or difflib.SequenceMatcher(None, nx, ny).ratio() >= 0.9:
                    coppia_id += 1; coppie.setdefault(i, []).append(coppia_id); coppie.setdefault(j, []).append(coppia_id)
        for idx, g in enumerate(gr):
            motivi = []
            if len(g["run"]) < n: motivi.append(f"non in tutte le run ({len(g['run'])}/{n})")
            if len(g["ruoli"]) > 1: motivi.append("ruolo instabile")
            if idx in coppie: motivi.append("possibile doppione (coppia " + ",".join(map(str, coppie[idx])) + ")")
            if g["cit_ok"][False] > g["cit_ok"][True]: motivi.append("citazione non trovata nel testo")
            if not motivi and random.random() < a.campione: motivi.append("campione dei presenti in tutte le run")
            ruolo = g["ruoli"].most_common(1)[0][0]
            cit = max(g["cit"])[1]
            riga = dict(codice=c, nome=nome(g), n_run_presente=len(g["run"]), n_run=n, ruolo_prevalente=ruolo,
                        ruoli="; ".join(f"{k} {v}" for k, v in g["ruoli"].most_common()),
                        varianti_nome=" | ".join(sorted(g["nomi"])), motivo=" + ".join(motivi), citazione=cit.replace("\n", " ")[:300])
            tutti.append({k: riga[k] for k in ("codice", "nome", "n_run_presente", "n_run", "ruolo_prevalente", "ruoli", "varianti_nome")})
            if motivi:
                righe.append(riga)
    righe.sort(key=lambda r: (r["codice"], -FORZA[r["ruolo_prevalente"]], r["nome"]))
    with open(OUT / f"enti_automatici_{a.tag}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(tutti[0]), delimiter=";"); w.writeheader(); w.writerows(tutti)
    scrivi_excel(a, righe, dati)
    c = Counter(m.split(" (")[0].split(" +")[0] for r in righe for m in r["motivo"].split(" + "))
    print(f"{len(dati)} protocolli, {len(tutti)} enti, {len(righe)} da rivedere ({len(righe) / len(dati):.1f} per protocollo)")
    for k, v in c.most_common(): print(f"  {k}: {v}")
    print("->", OUT / f"revisione_{a.tag}.xlsx")


def applica(a):
    import openpyxl
    dati = carica(a.tag, None, a.n_run)
    wb = openpyxl.load_workbook(a.decisioni)
    if "da_rivedere" in wb.sheetnames:        # formato precedente
        ws = wb["da_rivedere"]; h = [c.value for c in ws[1]]; righe = [dict(zip(h, r)) for r in ws.iter_rows(min_row=2, values_only=True)]
    else:                                     # formato attuale: decisioni in 'revisione', varianti in 'info_tecnica' (stesso id)
        ws = wb["revisione"]; h = [c.value for c in ws[1]]; righe = [dict(zip(h, r)) for r in ws.iter_rows(min_row=2, values_only=True)]
        wi = wb["info_tecnica"]; hi = [c.value for c in wi[1]]
        info = {r[0]: dict(zip(hi, r)) for r in wi.iter_rows(min_row=2, values_only=True)}
        for d in righe: d["varianti_nome"] = info.get(d.get("id_riga", d.get("id")), {}).get("varianti_nome")
    dec, esiti, avvisi = {}, [], []
    for d in righe:
        d["id"] = d.get("id_riga", d.get("id")); d["codice"] = d.get("codice_protocollo", d.get("codice"))
        d["nome_finale"] = d.get("nome_corretto", d.get("nome_finale")); d["ruolo_finale"] = d.get("ruolo_corretto", d.get("ruolo_finale"))
        az = (d.get("azione") or "").strip().lower()
        az = {"ok": "corretto"}.get(az, az)
        if not az and (d.get("nome_finale") or d.get("ruolo_finale")): az = "sbagliato"      # correzione senza azione
        if not az and d.get("unisci_con"): az = "unisci"
        d["azione"] = az or None
        esiti.append(dict(id_riga=d["id"], codice=d["codice"], nome=d["nome"], ruolo_proposto=d.get("ruolo_proposto") or d.get("ruolo_prevalente"),
                          esito=az or "non_rivisto", nome_corretto=d.get("nome_finale"), ruolo_corretto=d.get("ruolo_finale"), unisci_con=d.get("unisci_con")))
        if az == "sbagliato" and not (d.get("nome_finale") or d.get("ruolo_finale")):
            avvisi.append(f"{d['id']} {d['codice']} {d['nome'][:40]}: 'sbagliato' senza nome_corretto né ruolo_corretto")
        if az == "unisci" and not d.get("unisci_con"):
            avvisi.append(f"{d['id']} {d['codice']} {d['nome'][:40]}: 'unisci' senza 'unisci_con'"); d["azione"] = None
        if az and az not in AZIONI:
            avvisi.append(f"{d['id']} azione non riconosciuta: {az!r}"); d["azione"] = None
        if d["azione"]:
            for v in str(d.get("varianti_nome") or d["nome"]).split(" | "):
                dec[(str(d["codice"]), norm(v))] = d
    with open(OUT / f"esiti_{a.tag}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(esiti[0]), delimiter=";"); w.writeheader(); w.writerows(esiti)
    ce = Counter(e["esito"] for e in esiti)
    print("esiti:", ", ".join(f"{k} {v}" for k, v in ce.most_common()))
    for v in avvisi[:20]: print("  AVVISO", v)
    finali = []
    for c, (n, gr) in dati.items():
        eliminati, uniti = set(), {}
        info = {}
        for idx, g in enumerate(gr):
            d = next((dec[(c, v)] for v in g["varianti"] if (c, v) in dec), None); info[idx] = d
            if d and d["azione"] == "elimina": eliminati.add(idx)
            if d and d["azione"] == "unisci" and d.get("unisci_con"):
                t = norm(d["unisci_con"])
                tgt = next((j for j, h2 in enumerate(gr) if j != idx and any(uguali(t, v) for v in h2["varianti"])), None)
                if tgt is not None: uniti[idx] = tgt
        for idx, g in enumerate(gr):
            if idx in eliminati or idx in uniti: continue
            run = set(g["run"]); ruoli = Counter(g["ruoli"])
            for src, tgt in uniti.items():
                if tgt == idx: run |= gr[src]["run"]; ruoli += gr[src]["ruoli"]
            d = info[idx]
            nm = (d.get("nome_finale") if d else None) or nome(g)
            ruolo = (d.get("ruolo_finale") if d else None) or ruoli.most_common(1)[0][0]
            finali.append(dict(codice=c, nome=nm, ruolo=ruolo, n_run_presente=len(run), n_run=n,
                               stato="rivisto" if d or any(t == idx for t in uniti.values()) else "automatico"))
    with open(OUT / f"enti_finali_{a.tag}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(finali[0]), delimiter=";"); w.writeheader(); w.writerows(finali)
    print(f"{len(finali)} enti finali ({sum(x['stato'] == 'rivisto' for x in finali)} rivisti) -> {OUT / ('enti_finali_' + a.tag + '.csv')}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("prepara"); p.add_argument("--tag", required=True); p.add_argument("--codici"); p.add_argument("--n-run", type=int); p.add_argument("--campione", type=float, default=0.1)
    q = sp.add_parser("applica"); q.add_argument("--tag", required=True); q.add_argument("--decisioni", required=True); q.add_argument("--n-run", type=int)
    a = ap.parse_args(); prepara(a) if a.cmd == "prepara" else applica(a)
