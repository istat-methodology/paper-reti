"""Accordo questionario-AI da risultati/confronto_micro_soggetti_v1.xlsx (foglio micro_presenza_categorie).
Misure: accordo osservato, Jaccard, kappa di Cohen, PABAK. Livelli: per domanda e per domanda x categoria."""
import numpy as np, pandas as pd
from config import RISULTATI
src=RISULTATI/"confronto_micro_soggetti_v1.xlsx"
T=pd.read_excel(src,sheet_name="micro_presenza_categorie_tutte",dtype={"codice":str})
def misure(g):
    a=((g.q==1)&(g.ai==1)).sum(); b=((g.q==1)&(g.ai==0)).sum(); c=((g.q==0)&(g.ai==1)).sum(); d=((g.q==0)&(g.ai==0)).sum()
    n=a+b+c+d; po=(a+d)/n; pe=((a+b)*(a+c)+(c+d)*(b+d))/n**2
    return pd.Series(dict(entrambi=a,solo_questionario=b,solo_AI=c,nessuno=d,n=n,
        prev_questionario=(a+b)/n,prev_AI=(a+c)/n,accordo=po,
        jaccard=a/(a+b+c) if a+b+c else np.nan,
        kappa=(po-pe)/(1-pe) if pe<1 else np.nan,pabak=2*po-1))
D=T.groupby("domanda").apply(misure,include_groups=False).reset_index()
C=T.groupby(["domanda","cat","etichetta"]).apply(misure,include_groups=False).reset_index()
with pd.ExcelWriter(RISULTATI/"confronto_accordo_v1.xlsx") as w:
    D.round(3).to_excel(w,sheet_name="per_domanda",index=False)
    C.round(3).to_excel(w,sheet_name="per_domanda_categoria",index=False)
pd.set_option("display.width",200)
print(D.round(3).to_string(index=False))
