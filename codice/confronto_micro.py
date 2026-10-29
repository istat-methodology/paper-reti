"""Tabella micro questionario x AI per le domande sui soggetti (2.1, 2.2, 3.3, 3.7).
Uso: python3 confronto_micro.py [--ai CARTELLA_AI] [--out FILE.xlsx]
Il blocco 'questionario' dei JSON 2.6 non si usa: qui si leggono solo i campi AI."""
import argparse, json, re, glob, os
import pandas as pd
from pathlib import Path
from config import MICRODATI, RIFERIMENTI, RISULTATI

ESCLUSI = {  # questionario -> motivo
    "0909": "duplicato di 0910 (stesso questionario Prato; manca Pistoia)",
    "0326": "AI mancante (output vuoto)", "044101": "AI mancante (output vuoto)",
    "0507": "AI mancante (output vuoto)", "1612": "AI mancante (output vuoto)",
    "1613": "AI mancante (output vuoto)",
}
# tipo AI -> codice categoria GINO. 'prov' = mapping provvisorio, da approvare
mp=pd.read_csv(RIFERIMENTI/"rif_mapping_tipi_ai_gino_v1.csv",sep=";",encoding="utf-8-sig")  # mapping tipo AI -> categoria GINO (modificabile)
MAPTIPO=dict(zip(mp.tipo_AI,mp.codice))
def norm(s): return re.sub(r"\s+"," ",str(s)).strip().casefold()

ap=argparse.ArgumentParser()
ap.add_argument("--ai",default=str(MICRODATI/"ai")); ap.add_argument("--out",default=str(RISULTATI/"confronto_micro_soggetti_v1.xlsx"))
a=ap.parse_args()

cat=pd.read_csv(RIFERIMENTI/"categorie_gino_30.csv",sep=";",encoding="utf-8-sig"); lab=dict(zip(cat.codice,cat.etichetta))
l=pd.read_csv(MICRODATI/"gino/gino_pdf_risposte_lungo.csv",sep=";",encoding="utf-8-sig",dtype=str)
anag=pd.read_excel(MICRODATI/"rif_anagrafica_v1.xlsx",sheet_name="Anagrafica",dtype=str).set_index("codice")
l["cod"]=l.file.str.extract(r"questionario_(\d+)\.pdf")[0]; l["cat"]=pd.to_numeric(l.voce,errors="coerce")
codici=[c for c in sorted(l.cod.unique()) if c not in ESCLUSI]

ROLES={"2.1":["soggetti_proponenti"],"3.3":["attori_coinvolti"],
       "3.7a":["coordinatori","soggetti_monitoraggio"],"3.7b":["coordinatori","soggetti_monitoraggio","cabina_regia"]}
rows=[];num=[];nonabb=[];amb=0
for c in codici:
    d=json.load(open(os.path.join(a.ai,f"ai_{c}.json"),encoding="utf-8"))
    tipo_of={}
    for s in d["soggetti"]:
        k=norm(s.get("nome","")); t=s.get("tipo","")
        code=MAPTIPO.get(t)
        if code is None: raise SystemExit(f"tipo non mappato: {t}")
        if k in tipo_of and tipo_of[k]!=code: amb+=1
        tipo_of.setdefault(k,code)
    # conteggio soggetti per categoria (2.2)
    cnt={}
    for s in d["soggetti"]: cnt[(MAPTIPO.get(s["tipo"]))]=cnt.get(MAPTIPO.get(s["tipo"]),0)+1
    q22=l[(l.cod==c)&(l.domanda=="2.2")].set_index("cat")
    for k in range(1,31):
        raw=q22.loc[k,"numerosita"] if k in q22.index else None
        m=re.match(r"\D*(\d+)",raw) if isinstance(raw,str) else None
        num.append(dict(codice=c,regione=anag.loc[c,"regione"],cat=k,etichetta=lab[k],q_numerosita=int(m.group(1)) if m else None,
                        q_numerosita_raw=raw,ai_n_soggetti=cnt.get(k,0)))
    for dom,fields in ROLES.items():
        base=dom[:3]; qq=l[(l.cod==c)&(l.domanda==base)].set_index("cat").selezionato
        names={}
        for f in fields:
            for n in d.get(f,[]):
                t=tipo_of.get(norm(n))
                if t is None: nonabb.append(dict(codice=c,domanda=dom,campo=f,nome=n)); continue
                names.setdefault(t,set()).add(norm(n))
        for k in range(1,31):
            rows.append(dict(codice=c,regione=anag.loc[c,"regione"],domanda=dom,cat=k,etichetta=lab[k],
                             q=int(float(qq.get(k,0) or 0)),ai=int(k in names),ai_n=len(names.get(k,()))))
T=pd.DataFrame(rows); N=pd.DataFrame(num)
T["esito"]=T.q.astype(str)+T.ai.astype(str)
T["esito"]=T.esito.map({"11":"entrambi","10":"solo_questionario","01":"solo_AI","00":"nessuno"})
R=T.pivot_table(index="domanda",columns="esito",values="cat",aggfunc="count",fill_value=0).reset_index()
R=R[["domanda","entrambi","solo_questionario","solo_AI","nessuno"]]
tot=R[["entrambi","solo_questionario","solo_AI"]].sum(axis=1)
for k in ["entrambi","solo_questionario","solo_AI"]: R["%_"+k]=(100*R[k]/tot).round(1)  # sul totale delle celle con almeno una fonte
R["n_questionari"]=len(codici)
RISULTATI.mkdir(exist_ok=True)
with pd.ExcelWriter(a.out) as w:
    R.to_excel(w,sheet_name="riepilogo",index=False); T[T.esito!="nessuno"].sort_values(["domanda","cat","codice"]).to_excel(w,sheet_name="micro_presenza_categorie",index=False); T.to_excel(w,sheet_name="micro_presenza_categorie_tutte",index=False); N.to_excel(w,sheet_name="micro_2_2_numerosita",index=False)
    pd.DataFrame([dict(codice=k,motivo=v) for k,v in ESCLUSI.items()]).to_excel(w,sheet_name="esclusi",index=False)
    pd.DataFrame(nonabb).to_excel(w,sheet_name="nomi_AI_non_abbinati",index=False)
print("questionari:",len(codici),"| nomi ambigui:",amb,"| nomi AI non abbinati ai soggetti:",len(nonabb)); print(R.to_string())
