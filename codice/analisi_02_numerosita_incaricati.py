"""Numerosità (domanda 2.2) e soggetti incaricati (3.7) contro l'output AI. Eseguire da qualsiasi cartella."""
import os, sys, pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
sys.dont_write_bytecode=True; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import common
mm,a,h,prot,cats_df=common.load(); keys=set(mm.k); cats=cats_df.set_index('codice').etichetta
# ---- 2.2 numerosità: conteggio umano per protocollo e categoria vs nomi AI distinti
h['n']=pd.to_numeric(h.TIPO_E_NUM_TENDINA,errors='coerce')
hn=h[h.TIPO_E_NUM_CHECK.notna()].groupby(['k','cod']).n.sum().reset_index()
an=a.drop_duplicates(['k','nome','cod_alt']).groupby(['k','cod_alt']).size().reset_index(name='n_ai').rename(columns={'cod_alt':'cod'})
c=hn.merge(an,on=['k','cod'],how='outer').fillna(0)
both=c[(c.n>0)&(c.n_ai>0)]
print('== NUMEROSITA'); print('totale umano',int(c.n.sum()),'| totale AI',int(c.n_ai.sum()),'| celle con entrambi >0:',len(both),'| esatto',int((both.n==both.n_ai).sum()))
pp=c.groupby('k')[['n','n_ai']].sum(); print('protocolli: umano<AI',int((pp.n<pp.n_ai).sum()),'umano>AI',int((pp.n>pp.n_ai).sum()),'uguali',int((pp.n==pp.n_ai).sum()))
bc=c.groupby('cod')[['n','n_ai']].sum(); bc['rapporto_AI_umano']=(bc.n_ai/bc.n).round(2); bc.insert(0,'categoria',cats.reindex(bc.index).str[:30]); print(bc.to_string())
# ---- 3.7 incaricati vs flag AI
gov=h[h.SOGGETTI_INCARICATI_CK.notna()].groupby(['k','cod']).size().reset_index(); gov['hu']=1
grid=mm[mm.rm=='Proponente'][['k','cod']]
isT=lambda col:a[col].astype(str).str.lower().isin(['true','1','1.0'])
def cmp(mask,name):
    s=a[mask&a.cod_alt.notna()].groupby(['k','cod_alt']).size().reset_index().rename(columns={'cod_alt':'cod'}); s['ai']=1
    g=grid.merge(gov[['k','cod','hu']],on=['k','cod'],how='left').merge(s[['k','cod','ai']],on=['k','cod'],how='left').fillna(0)
    b=int(((g.hu==1)&(g.ai==1)).sum()); ho=int(((g.hu==1)&(g.ai==0)).sum()); ao=int(((g.hu==0)&(g.ai==1)).sum())
    print(f'{name:22s} entrambi {b:4d} solo_umano {ho:4d} solo_AI {ao:4d} jaccard {b/(b+ho+ao):.3f}')
print('\n== 3.7 INCARICATI (selezioni umane: %d)'%len(gov))
for col in ['is_governance','is_coordinamento','is_monitoraggio','is_gestione','is_capofila']: cmp(isT(col),col)
cmp(isT('is_coordinamento')|isT('is_monitoraggio')|isT('is_gestione'),'coord|monit|gestione')
