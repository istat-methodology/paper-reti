"""Accordo questionario-AI per regione e per dimensione del protocollo (caratteri del TXT).
Legge risultati/confronto_micro_soggetti_v1.xlsx; scrive risultati/confronto_regioni_dimensione_v1.xlsx"""
import numpy as np, pandas as pd
from config import RISULTATI, MICRODATI
T=pd.read_excel(RISULTATI/"confronto_micro_soggetti_v1.xlsx",sheet_name="micro_presenza_categorie_tutte",dtype={"codice":str})
T=T[T.domanda.isin(["2.1","3.3","3.7a"])]
L=pd.Series({c:len(open(MICRODATI/"protocolli"/f"protocollo_{c}.txt",encoding="utf-8",errors="ignore").read()) for c in T.codice.unique()},name="caratteri")
cod=T[["codice","regione"]].drop_duplicates().merge(L,left_on="codice",right_index=True)
cod["dimensione"]=pd.qcut(cod.caratteri,4,labels=["Q1 (più corti)","Q2","Q3","Q4 (più lunghi)"])
bins=cod.groupby("dimensione",observed=True).caratteri.agg(["min","max"]).reset_index()
T=T.merge(cod[["codice","caratteri","dimensione"]],on="codice")
def mis(g):
    a=((g.q==1)&(g.ai==1)).sum(); b=((g.q==1)&(g.ai==0)).sum(); c=((g.q==0)&(g.ai==1)).sum(); d=((g.q==0)&(g.ai==0)).sum()
    n=a+b+c+d; po=(a+d)/n; pe=((a+b)*(a+c)+(c+d)*(b+d))/n**2
    return pd.Series(dict(n_questionari=g.codice.nunique(),entrambi=a,solo_questionario=b,solo_AI=c,nessuno=d,
        jaccard=a/(a+b+c) if a+b+c else np.nan,kappa=(po-pe)/(1-pe) if pe<1 else np.nan,pabak=2*po-1))
def tab(col):
    x=T.groupby([col,"domanda"],observed=True).apply(mis,include_groups=False).reset_index()
    return x.sort_values(["domanda",col])
R=tab("regione"); D=tab("dimensione")
with pd.ExcelWriter(RISULTATI/"confronto_regioni_dimensione_v1.xlsx") as w:
    R.round(3).to_excel(w,sheet_name="per_regione",index=False); D.round(3).to_excel(w,sheet_name="per_dimensione",index=False)
    bins.to_excel(w,sheet_name="classi_dimensione",index=False)
pd.set_option("display.width",200)
for d in ["2.1","3.3","3.7a"]:
    print(d); print(R[R.domanda==d][["regione","n_questionari","entrambi","solo_questionario","solo_AI","jaccard","kappa"]].round(2).to_string(index=False))
print(bins.to_string(index=False)); print(D[["dimensione","domanda","entrambi","solo_questionario","solo_AI","jaccard","kappa"]].round(2).to_string(index=False))
