"""Abbina i protocolli ai questionari e crea l'anagrafica (Excel) con i nuovi nomi.

Input : microdati/gino/questionari_gino_associati_da_regionali.xlsx (foglio Associazioni)
        microdati/protocolli/_originali/<regione>/*.txt   (file come sono arrivati)
Output: microdati/rif_anagrafica_v1.xlsx
        microdati/protocolli/protocollo_<codice>.txt      (copie con il nuovo nome)

Abbinamento, in ordine:
 1. timestamp nel nome del file (AAMMGGhhmmss) = data di ultima modifica del questionario, stessa regione;
 2. dove manca il timestamp: nome del file allegato (campo 3.9), prima identico poi normalizzato.
"""
import sys; sys.dont_write_bytecode = True
import re, shutil, unicodedata
import pandas as pd
from config import MICRODATI

P = MICRODATI / "protocolli"; ORIG = P / "_originali"
a = pd.read_excel(MICRODATI / "gino" / "questionari_gino_associati_da_regionali.xlsx", sheet_name="Associazioni", dtype=str)
a["codice"] = a.nome_pdf_questionario.str.replace(".pdf", "", regex=False)
a["ts"] = pd.to_datetime(a.data_ultima_modifica, format="%d-%m-%Y %H:%M:%S").dt.strftime("%y%m%d%H%M%S")

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    for _ in range(3): s = re.sub(r"\.(pdf|txt|docx?|p7m|odt)$", "", s.strip())
    return re.sub(r"[^a-z0-9]", "", s)

files = []
for f in sorted(ORIG.glob("*/*.txt")):
    b = f.stem; reg = f.parent.name
    m = re.match(r"^\d+_\d+_rta_\d+_(\d{12})_\d+---(.*)$", b)
    ts, nome = (m.group(1), m.group(2)) if m else (None, re.sub(r"^\d{2}_", "", b))
    files.append(dict(rel=f"{reg}/{f.name}", reg=reg, ts=ts, nome=nome, n=norm(nome)))
t = pd.DataFrame(files)
t = t[~t.rel.str.contains("Test_rta")]          # file di prova

rows = []
for r in a.itertuples():
    c = t[(t.reg == r.codice_regione)]
    k = c[c.ts == r.ts]; metodo = "timestamp"
    if len(k) == 0:
        stem = re.sub(r"\.[A-Za-z0-9]{2,4}$", "", r.nome_pdf_allegato)
        k = c[c.ts.isna() & (c.nome == stem)]; metodo = "nome identico"
        if len(k) == 0: k = c[c.ts.isna() & (c.n == norm(r.nome_pdf_allegato))]; metodo = "nome normalizzato"
        if len(k) == 0:   # allegato rinominato nel caricamento (es. suffisso "_caricato su GINO")
            k = c[c.ts.isna() & (c.n == norm(re.sub(r"_caricato su GINO", "", stem)))]; metodo = "nome senza suffisso"
    note = ""
    if len(k) > 1: note = f"{len(k)} candidati, scelto il primo"
    rows.append(dict(codice=r.codice, questionario_nuovo=f"questionario_{r.codice}.pdf", questionario_originale=r.nome_pdf_questionario,
                     codice_regione=r.codice_regione, regione=r.regione_nome, codice_territoriale=r.codice_territoriale,
                     protocollo_nuovo=f"protocollo_{r.codice}.txt" if len(k) else "", protocollo_originale=k.rel.iloc[0] if len(k) else "",
                     metodo=metodo if len(k) else "NON ABBINATO", allegato_gino_3_9=r.nome_pdf_allegato, titolo_documento=r.titolo_documento, note=note))
an = pd.DataFrame(rows)
cond = an[an.protocollo_originale != ""].groupby("protocollo_originale").codice.transform("size")
an.loc[cond.index, "note"] = (an.loc[cond.index, "note"] + (cond > 1).map({True: " protocollo condiviso con altro questionario", False: ""})).str.strip()
usati = set(an.protocollo_originale)
non = t[~t.rel.isin(usati)][["reg", "rel", "nome"]].rename(columns={"reg": "codice_regione", "rel": "protocollo_originale", "nome": "nome_senza_prefisso"})
rie = pd.DataFrame({"Indicatore": ["Questionari", "Protocolli abbinati", "Questionari senza protocollo", "Protocolli condivisi tra più questionari",
                                   "File protocollo originali (esclusi i test)", "File non usati da nessun questionario"],
                    "Valore": [len(an), int((an.protocollo_originale != "").sum()), int((an.protocollo_originale == "").sum()),
                               int(an.note.str.contains("condiviso").sum()), len(t), len(non)]})
with pd.ExcelWriter(MICRODATI / "rif_anagrafica_v1.xlsx") as w:
    an.to_excel(w, sheet_name="Anagrafica", index=False); non.to_excel(w, sheet_name="Protocolli_non_usati", index=False); rie.to_excel(w, sheet_name="Riepilogo", index=False)
for r in an[an.protocollo_originale != ""].itertuples():
    shutil.copy2(ORIG / r.protocollo_originale, P / r.protocollo_nuovo)
print(rie.to_string(index=False)); print(an.metodo.value_counts().to_string()); print(an[an.note != ""][["codice", "metodo", "note"]].to_string(index=False))
