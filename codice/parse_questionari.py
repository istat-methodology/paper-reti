"""Parsing dei PDF dei questionari GINO -> tabella lunga e larga.

Il layout dei PDF e' identico: le spunte sono immagini (4 tipi: radio vuoto/pieno, checkbox vuoto/pieno).
Ogni voce e' ancorata a una riga di testo; la spunta si legge dall'immagine nel blocco di quella voce.
Uso: python3 parse_questionari.py [cartella_pdf]   (default: <MICRODATI>/gino, file questionario*.pdf)
Output (in <MICRODATI>/gino): gino_pdf_risposte_lungo.csv, gino_pdf_risposte_largo.csv
"""
import sys, re, glob, os; sys.dont_write_bytecode = True
import pdfplumber, pandas as pd
from pathlib import Path
from config import MICRODATI

# immagini delle spunte (stessi oggetti in tutti i PDF visti): vuoto/pieno
IMG = {28: ("radio", 0), 29: ("radio", 1), 30: ("check", 0), 31: ("check", 1)}
XCOMM = 330      # a destra di questa x: colonna commento (e numerosita' oltre XNUM)
XNUM = 560
# 30 categorie nell'ordine del questionario: (codice, prefisso della prima riga nel PDF)
LABELS = ["CAV", "Case Rifugio", "Comuni", "Polizia Municipale", "Settore educativo comunale", "Servizi sociali comunali",
          "Servizio abusi e maltrattamenti", "Province/Citt", "Ambiti della programmazione", "Regioni/province Autonome",
          "Ospedale", "ASL (consultori", "Prefettura", "Questura", "Carabinieri/Polizia", "Scuole/Ufficio", "Procura Minorile",
          "Procura Ordinaria", "Ordine avvocati", "Ordine psicologi", "Ordine medici", "Altri ordini professionali", "Organismi di parit",
          "Ente terzo settore - ETS (iscritto al RUNTS)[", "Ente terzo settore - ETS (iscritto al RUNTS) costituito", "Servizi per l'impiego",
          "Sindacati", "Universit", "Associazioni che si occupano", "Altro"]
TABLE_Q = ["2.1", "2.2", "3.3", "3.7"]
HDR = re.compile(r"^(\d)\.(\d+)\s")
SEC = re.compile(r"^\d\.\s")

COLHDR = {"SOGGETTO", "ATTORE", "COMMENTO", "NUMEROSITA'"}   # intestazioni di colonna ripetute a ogni pagina

def lines_of(pg):
    rows = []
    for w in sorted(pg.extract_words(), key=lambda w: (w["top"], w["x0"])):
        if w["text"] in COLHDR: continue
        if rows and abs(rows[-1]["top"] - w["top"]) < 3: rows[-1]["w"].append(w)
        else: rows.append({"top": w["top"], "w": [w]})
    for r in rows: r["w"].sort(key=lambda w: w["x0"]); r["text"] = " ".join(w["text"] for w in r["w"]); r["x0"] = r["w"][0]["x0"]
    return rows

def txt(ws): return " ".join(w["text"] for w in sorted(ws, key=lambda w: (round(w["top"] / 3), w["x0"])))

def parse(path):
    recs = []; head = {}; blocks = {}   # qid -> lista di (pagina, linea)
    sel = []                            # (pagina, top, tipo, stato)
    cur = "0"; allines = []
    with pdfplumber.open(path) as pdf:
        for pn, pg in enumerate(pdf.pages):
            for im in pg.images:
                t = IMG.get(im["stream"].objid)
                if t: sel.append(dict(p=pn, top=(im["top"] + im["bottom"]) / 2, tipo=t[0], stato=t[1], x0=im["x0"], cur=None))
            for ln in lines_of(pg):
                if ln["top"] < 45 or ln["text"].startswith("Reti territoriali"): continue
                m = HDR.match(ln["text"]) if ln["x0"] < 50 else None
                if m: cur = f"{m.group(1)}.{m.group(2)}"
                elif ln["x0"] < 50 and SEC.match(ln["text"]): cur = "S"
                ln.update(p=pn, q=cur, hdr=bool(m)); allines.append(ln)
    for s in sel:  # domanda di appartenenza: ultima intestazione prima della spunta
        prev = [l for l in allines if l["hdr"] and (l["p"], l["top"]) <= (s["p"], s["top"])]
        s["q"] = prev[-1]["q"] if prev else "0"
    # intestazione
    for l in allines:
        if l["q"] == "0":
            if l["text"].startswith("Nome del rispondente"): head["rispondente"] = l["text"].split(":", 1)[1].strip()
    z = [l["text"] for l in allines if l["q"] == "0"]
    if "Se il CAV non è prensente in lista indicare di seguito la denominazione:" in z:
        i = z.index("Se il CAV non è prensente in lista indicare di seguito la denominazione:"); head["cav_altro"] = " ".join(z[i + 1:]).strip()
    out = []
    def add(q, cod, lab, selected=None, comm="", num="", extra=""):
        out.append(dict(domanda=q, voce=cod, etichetta=lab, selezionato=selected, commento=comm, numerosita=num, testo=extra))
    for k, v in head.items(): add("0", k, k, extra=v)
    Q = lambda q: [l for l in allines if l["q"] == q]
    # testi liberi
    add("1.1", "titolo", "Titolo", extra=" ".join(l["text"] for l in Q("1.1") if not l["hdr"]))
    add("3.1", "data", "Data stipula", extra=" ".join(l["text"] for l in Q("3.1") if not l["hdr"]))
    t36 = " ".join(l["text"] for l in Q("3.6"))
    a = re.search(r"in anni:\s*(.*?)(?:Data di scadenza|$)", t36); b = re.search(r"Data di scadenza dell'accordo:\s*(.*)", t36)
    add("3.6", "anni", "Durata in anni", extra=a.group(1).strip() if a else ""); add("3.6", "scadenza", "Data di scadenza", extra=b.group(1).strip() if b else "")
    f = [l for l in Q("3.9") if not l["hdr"] and not l["text"].startswith("Selezionare")]
    nome = []
    for l in f:
        if l["text"].startswith("File Size"): add("3.9", "file_size", "File size", extra=l["text"][9:].strip())
        elif l["text"].startswith("Data Upload"): add("3.9", "data_upload", "Data upload", extra=l["text"][11:].strip())
        else: nome.append(l["text"])
    add("3.9", "file_nome", "Nome file", extra=" ".join(nome))
    # domande a tabella (30 categorie)
    for q in TABLE_Q:
        L = [l for l in Q(q) if not l["hdr"] and l["x0"] < 100]
        anch = []; i = 0
        for l in L:
            if i < 30 and l["text"].startswith(LABELS[i]) and (LABELS[i] != "Altro" or l["text"] == "Altro" or l["text"].startswith("Altro")):
                anch.append(l); i += 1
        if len(anch) != 30: raise ValueError(f"{path} {q}: trovate {len(anch)} voci su 30")
        allq = [l for l in Q(q) if not l["hdr"]]
        for j, an in enumerate(anch):
            nxt = anch[j + 1] if j + 1 < 30 else None
            lo = (an["p"], an["top"] - 4); hi = (nxt["p"], nxt["top"] - 4) if nxt else (99, 0)
            blk = [l for l in allq if lo <= (l["p"], l["top"]) < hi]
            ws = [w for l in blk for w in l["w"]]
            comm = txt([w for w in ws if XCOMM <= w["x0"] < XNUM]) if q == "2.2" else txt([w for w in ws if w["x0"] >= XCOMM])
            num = txt([w for w in ws if w["x0"] >= XNUM]) if q == "2.2" else ""
            lab = txt([w for w in ws if w["x0"] < XCOMM])
            if q == "2.2": selected = None
            else:
                ss = [s for s in sel if s["q"] == q and lo <= (s["p"], s["top"]) < hi]
                selected = ss[0]["stato"] if len(ss) == 1 else None
                if len(ss) != 1: raise ValueError(f"{path} {q} voce {j+1}: {len(ss)} spunte")
            add(q, f"{j+1:02d}", lab, selected, comm, num)
    # domande a opzioni (radio/checkbox con etichette libere)
    for q in ["1.2", "3.2", "3.4", "3.5", "3.8", "4.1", "4.2"]:
        ss = sorted([s for s in sel if s["q"] == q], key=lambda s: (s["p"], s["top"]))
        allq = [l for l in Q(q) if not l["hdr"]]
        for j, s in enumerate(ss):
            nx = ss[j + 1] if j + 1 < len(ss) else None
            lo = (s["p"], s["top"] - 8); hi = (nx["p"], nx["top"] - 8) if nx else (99, 0)
            blk = " ".join(l["text"] for l in allq if lo <= (l["p"], l["top"]) < hi)
            lab, _, spec = blk.partition("Specificare:")
            lab = re.sub(r"^Altro Altro$", "Altro", lab.strip())
            add(q, f"{j+1:02d}", lab, s["stato"], extra=spec.strip())
    # specificare dopo ultima voce quando separato (es. 3.4/3.5 "Altro Specificare:")
    return out

def main():
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else MICRODATI / "gino"
    files = sorted(glob.glob(str(d / "questionario*.pdf")))
    rows = []
    for f in files:
        for r in parse(f): r["file"] = os.path.basename(f); rows.append(r)
    lungo = pd.DataFrame(rows)[["file", "domanda", "voce", "etichetta", "selezionato", "commento", "numerosita", "testo"]]
    lungo.to_csv(MICRODATI / "gino/gino_pdf_risposte_lungo.csv", sep=";", index=False, encoding="utf-8-sig")
    w = lungo.copy(); w["col"] = "q" + w.domanda.str.replace(".", "_", regex=False) + "_" + w.voce
    parts = []
    for c, fld in [("sel", "selezionato"), ("comm", "commento"), ("num", "numerosita"), ("testo", "testo")]:
        x = w[w[fld].notna() & (w[fld].astype(str) != "")].pivot(index="file", columns="col", values=fld); x.columns = [f"{k}__{c}" for k in x.columns]; parts.append(x)
    pd.concat(parts, axis=1).to_csv(MICRODATI / "gino/gino_pdf_risposte_largo.csv", sep=";", encoding="utf-8-sig")
    print(len(files), "questionari,", len(lungo), "righe")

if __name__ == "__main__": main()
