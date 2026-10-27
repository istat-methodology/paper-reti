import pandas as pd, numpy as np, os, warnings; warnings.filterwarnings('ignore')
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from config import MICRODATI, DOCS, RIFERIMENTI
MD=str(MICRODATI)+"/"
rd=lambda f:pd.read_csv(MD+"gino/"+f,sep=';',encoding='cp1252',dtype=str)
c=rd('gino_protocolli.csv'); c=c[c.UPLOAD_FILE.notna()].copy(); N=len(c)
keys=set(c.ID_RISPONDENTE_RILEV+'|'+c.PROGRESSIVO_QUEST)
s=pd.read_excel(MD+'gino/gino_soggetti.xlsx',sheet_name=0,dtype=str)
s['k']=s.ID_RISPONDENTE_RILEV+'|'+s.PROGRESSIVO_QUEST; s=s[s.k.isin(keys)].copy(); s['cod']=s.SOGGETTO_PROP_VALORI.astype(int)
ob=rd('gino_obiettivi_strategici.csv'); ob['k']=ob.ID_RISPONDENTE_RILEV+'|'+ob.PROGRESSIVO_QUEST; ob=ob[ob.k.isin(keys)]
oo=rd('gino_obiettivi_operativi.csv'); oo['k']=oo.ID_RISPONDENTE_RILEV+'|'+oo.PROGRESSIVO_QUEST; oo=oo[oo.k.isin(keys)]
cats=pd.read_csv(RIFERIMENTI/'categorie_gino_30.csv',sep=';',encoding='utf-8-sig')[['codice','etichetta']]
cats.columns=['cod','label']
def multi(df,col,k='k'):
    g=df[df[col].notna()].groupby(k).size().reindex(sorted(keys),fill_value=0); return int((g>0).sum()), round(float(g.mean()),1), int(g.max())
P=multi(s,'SOGGETTO_PROP_CHECK'); A=multi(s,'ATTORI_COINVOLTI_CHECK'); I=multi(s,'SOGGETTI_INCARICATI_CK'); T=multi(s,'TIPO_E_NUM_CHECK')
O=multi(ob,'OBIETTIVI_CHECK'); OO=multi(oo,'OBIETTIVI_OPERATIVI_CK')
def junk(col,chk):
    t=s[s[chk].notna()][col]; blank=t.isna().sum(); tt=t.dropna().str.strip().str.lower()
    j=((tt.str.len()<=3)|tt.isin(['come sopra','idem','vedi sopra','ok','si','sì','come da protocollo'])).sum(); return len(t),int(blank),int(j)
jp=junk('SOGGETTO_PROP_TEXT','SOGGETTO_PROP_CHECK'); ja=junk('ATTORI_COINVOLTI_TEXT','ATTORI_COINVOLTI_CHECK'); ji=junk('SOGGETTO_INCARICATO_TEXT','SOGGETTI_INCARICATI_CK')
nn=lambda col:int(c[col].notna().sum())
vc=lambda col:c[col].value_counts().to_dict()
d=pd.to_datetime(c.DATA_STIPULA,format='%d/%m/%Y'); e=pd.to_datetime(c.DATA_FINE_ACCORDO,format='%d/%m/%Y'); dur=pd.to_numeric(c.DURATA_ACCORDO)
ok=d.notna()&e.notna()&dur.between(1,30); exp=d[ok]+pd.to_timedelta(dur[ok]*365.25,unit='D'); gap=((e[ok]-exp).dt.days.abs()/365.25)
nprop=s[s.SOGGETTO_PROP_CHECK.notna()].groupby('k').size().reindex(sorted(keys),fill_value=0)
reg=c.VAR_91.value_counts()
# ---------------- Variabili
V=[ # id, sez, dom, testo, variabile, file, tipo, nmod, nresp, formato, note
("V01","Intestazione","-","Chiavi del record","ID_RISPONDENTE_RILEV; PROGRESSIVO_QUEST","Tutti","Identificativo",None,N,"Rispondente (ufficio regionale) + progressivo protocollo","Chiave di raccordo con l'output AI. 254 record nel tracciato, 251 con file allegato. Il rispondente 4 contiene dati di prova."),
("V02","Intestazione","-","Nome del rispondente (Regione/Provincia autonoma)","VAR_91","CAV",'Testo (ente)',None,nn('VAR_91'),"Es. 'Regione Piemonte'","Serve per l'analisi per regione. Il rispondente 1012 pesa molto (vedi foglio Qualità interna)."),
("V03","Intestazione","-","CAV di riferimento","ELENCO_CAV; TESTO_LIBERO_NOME_CAV","CAV","Codice da lista + testo libero",None,nn('ELENCO_CAV'),"Codice CAV (es. UTE0100023) oppure nome libero","Non riguarda il contenuto del protocollo. Fuori dal confronto."),
("V04","1. Identificazione","1.1","Titolo del documento","TITOLO_DOCUMENTO","CAV","Testo libero",None,nn('TITOLO_DOCUMENTO'),"Testo","Trascrizione del titolo. Serve come controllo del raccordo questionario-PDF."),
("V05","1. Identificazione","1.2","Ambito della rete","AMBITO_RETE; ALTRO_SPECIFICARE_1_2","CAV","Categoriale singola",8,nn('AMBITO_RETE'),"8 modalità (vedi foglio Modalità)","Modalità non esclusive nella pratica (comunale / intercomunale / ambito sociale / provinciale). 'Altro' scelto da 23 rispondenti."),
("V06","2. Caratteristiche della rete","2.1","Soggetto proponente (scegliere tutti)","SOGGETTO_PROP_CHECK; SOGGETTO_PROP_TEXT","Soggetti","Categoriale multipla (30 categorie) + commento",30,P[0],f"30 categorie; media {P[1]} categorie per protocollo, max {P[2]}","La domanda non definisce 'proponente'. Commento libero: su %d selezioni, %d vuoti e %d molto brevi o generici."%(jp[0],jp[1],jp[2])),
("V07","2. Caratteristiche della rete","2.2","Tipologia e numerosità dei soggetti","TIPO_E_NUM_CHECK; TIPO_E_NUM_TENDINA; TIPO_E_NUM_TEXT","Soggetti","Categoriale multipla + conteggio",30,T[0],f"30 categorie con conteggio (menu a tendina 0-10+); {T[1]} categorie per protocollo in media","Non è chiaro cosa si conti (firmatari, destinatari, tutti i soggetti citati). Comuni aggregati in un solo conteggio."),
("V08","3. Natura e obiettivi","3.1","Data della stipula","DATA_STIPULA","CAV","Data (gg/mm/aaaa)",None,nn('DATA_STIPULA'),"Date da %s a %s"%(d.min().date(),d.max().date()),"Protocolli con più date (firma, integrazioni, rinnovi) possono essere ambigui."),
("V09","3. Natura e obiettivi","3.2","Natura dell'accordo","NATURA_ACCORDO; ALTRO_SPECIFICARE_3_2","CAV","Categoriale singola",4,nn('NATURA_ACCORDO'),"Protocollo / Accordo / Convenzione / Altro","Il nome usato nel titolo non sempre coincide con la natura giuridica."),
("V10","3. Natura e obiettivi","3.3","Attori coinvolti","ATTORI_COINVOLTI_CHECK; ATTORI_COINVOLTI_TEXT","Soggetti","Categoriale multipla (30 categorie) + commento",30,A[0],f"30 categorie; media {A[1]} per protocollo, max {A[2]}","Il confine con 'proponente' e con 'firmatario' non è definito. Commento: su %d selezioni, %d vuoti, %d brevi o generici."%(ja[0],ja[1],ja[2])),
("V11","3. Natura e obiettivi","3.4","Obiettivi strategici","OBIETTIVI_CHECK; OBIETTIVI_ACCORDO; ALTRO_SPECIFICARE_3_4","Obiettivi","Categoriale multipla",12,O[0],f"12 modalità; media {O[1]} scelte per protocollo, max {O[2]}","Molte scelte per protocollo: le modalità non sono mutuamente esclusive e si sovrappongono. Tracciato separato."),
("V12","3. Natura e obiettivi","3.5","Obiettivi operativi","OBIETTIVI_OPERATIVI_CK; OBIETTIVI_OPERATIVI_ACC; ALTRO_SPECIFICARE_3_5","Ob. operativi","Categoriale multipla",9,OO[0],f"9 modalità; media {OO[1]} scelte per protocollo, max {OO[2]}","Come 3.4. Tracciato separato."),
("V13","3. Natura e obiettivi","3.6","Durata dell'accordo (anni)","DURATA_ACCORDO","CAV","Numerica (anni)",None,nn('DURATA_ACCORDO'),"Numero intero","Usa codici non documentati: 0 e 999 (vedi Qualità interna)."),
("V14","3. Natura e obiettivi","3.6","Data di scadenza dell'accordo","DATA_FINE_ACCORDO","CAV","Data",None,nn('DATA_FINE_ACCORDO'),"Date da %s a %s"%(e.min().date(),e.max().date()),"Compilata in 188 casi su 251. Non gestisce il tacito rinnovo."),
("V15","3. Natura e obiettivi","3.7","Soggetto incaricato di gestire / monitorare / coordinare","SOGGETTI_INCARICATI_CK; SOGGETTO_INCARICATO_TEXT","Soggetti","Categoriale multipla (30 categorie) + commento",30,I[0],f"30 categorie; media {I[1]} per protocollo, max {I[2]}","Tre funzioni in una sola domanda. Commento: su %d selezioni, %d vuoti, %d brevi o generici."%(ji[0],ji[1],ji[2])),
("V16","3. Natura e obiettivi","3.8","Presenza di un monitoraggio / valutazione dell'accordo","PRESENZA_MONITORAGGIO","CAV","Categoriale singola",3,nn('PRESENZA_MONITORAGGIO'),"1 Sì, 2 No, 3 Non so","Si chiede se esiste un monitoraggio, non chi lo fa. 'Non so' è una risposta ammessa."),
("V17","3. Natura e obiettivi","3.9","File allegato (PDF del protocollo)","UPLOAD_FILE","CAV","File",None,nn('UPLOAD_FILE'),"Nome file","Fonte per l'analisi del testo. 3 file compaiono in più di un record."),
("V18","4. Nella sua regione","4.1","Prassi per l'inserimento in casa rifugio","PRASSI_INSERIMENTO; PRASSI_SPECIFICARE","CAV","Categoriale singola",5,nn('PRASSI_INSERIMENTO'),"5 modalità","Riguarda la prassi regionale, non il protocollo."),
("V19","4. Nella sua regione","4.2","La donna può rivolgersi direttamente alla casa rifugio?","RIVOLGE_DIRETTAMENTE","CAV","Binaria",2,nn('RIVOLGE_DIRETTAMENTE'),"Sì / No","Riguarda la prassi regionale, non il protocollo."),
]
# ---------------- Modalita
def rows_from(var,labels,counts,src):
    out=[]
    for k,l in labels:
        n=int(counts.get(str(k),0)); out.append((var,k,l,n,src))
    return out
M=[]
M+=rows_from("AMBITO_RETE",[(1,"Comunale"),(2,"Area metropolitana/provinciale"),(3,"Ambito sociale"),(4,"Ambito sanitario coincidente con articolazioni locali delle Aziende Sanitarie Locali e/o Case della Salute e/o ATS (dipende dall'assetto regionale)"),(5,"Ambito distrettuale - legale"),(6,"Ambito intercomunale (Unione comuni etc.)"),(7,"Ambito regionale/Prov. Autonome"),(8,"Altro (specificare)")],vc('AMBITO_RETE'),"Testo: questionario PDF (integrale). Codice: dedotto dall'ordine; 'Altro'=8 verificato (23 con testo)")
M+=rows_from("NATURA_ACCORDO",[(1,"Protocollo"),(2,"Accordo"),(3,"Convenzione"),(4,"Altro")],vc('NATURA_ACCORDO'),"Testo: questionario PDF. Codice verificato sui titoli (es. 'Accordo operativo'=2, 'Convenzione'=3)")
M+=rows_from("PRESENZA_MONITORAGGIO",[(1,"SI"),(2,"NO"),(3,"NON SO")],vc('PRESENZA_MONITORAGGIO'),"Testo: questionario PDF. Codice confermato da Mauro il 9/10/2026")
M+=rows_from("PRASSI_INSERIMENTO",[(1,"L'accesso alla Casa rifugio deve essere preceduto dall'accesso al CAV di riferimento"),(2,"L'accesso alla Casa rifugio deve essere preceduto dall'accesso ad un qualsiasi CAV"),(3,"L'accesso alla Casa rifugio avviene esclusivamente tramite il 1522"),(4,"L'accesso alla Casa rifugio avviene da qualsiasi nodo della rete antiviolenza (polizia, carabinieri, pronto soccorso, ecc.)"),(5,"Altro")],vc('PRASSI_INSERIMENTO'),"Testo: questionario PDF (integrale). Codice: dedotto dall'ordine; da confermare")
M+=rows_from("RIVOLGE_DIRETTAMENTE",[(1,"SI"),(2,"NO")],vc('RIVOLGE_DIRETTAMENTE'),"Testo: questionario PDF. Codice 1=SI, 2=NO dedotto; da confermare")
so=[(1,"Promuovere la conoscenza dei servizi e interventi già esistenti nell'ambito della rete territoriale"),(2,"Condividere procedure codificate di accoglienza e presa in carico delle vittime, di invio delle donne ad altri soggetti a seconda delle competenze"),(3,"Sviluppare strategie operative di intervento che permettano azioni efficaci ed integrate a tutela della sicurezza e della protezione delle donne e dei loro figli/e (anche con riferimento al coinvolgimento del sistema giuridico e sanitario)"),(4,"Promuovere e/o rafforzare gli interventi rivolti agli autori di violenza"),(5,"Promuovere la realizzazione di interventi di formazione"),(6,"Promuovere e/o rafforzare le azioni di prevenzione della violenza contro le donne"),(7,"Rafforzare la comunicazione e le sinergie tra gli attori che sono firmatari dell'accordo"),(8,"Creare e/o rafforzare sinergie con altri soggetti del territorio che non sono firmatari dell'accordo, la cui presenza migliorerebbe la qualità dei servizi"),(9,"Promuovere campagne informative e di sensibilizzazione anche con riferimento all'abbattimento degli stereotipi di genere"),(10,"Promuovere e/o rafforzare percorsi educativi con la scuola"),(11,"Promuovere attività di ricerca, raccolta dati e di studio per conoscere meglio il fenomeno della violenza sulle donne a livello territoriale"),(12,"Altro")]
oc=ob[ob.OBIETTIVI_CHECK.notna()].OBIETTIVI_ACCORDO.value_counts().to_dict()
M+=rows_from("OBIETTIVI_ACCORDO (3.4)",so,oc,"Testo: questionario PDF (integrale). Codice: dedotto dall'ordine; 'Altro'=12 verificato (27 con testo)")
sop=[(1,"Aggiornamento elenchi dei componenti della rete (referente, contatto, funzione)"),(2,"Procedura/protocollo di intervento reperibilità in caso di emergenza"),(3,"Procedure / protocollo di intervento di invio di casi dai servizi territoriali e/o specialistici ai Centri Antiviolenza e Case Rifugio (ad esempio schede di comunicazione ecc.)"),(4,"Procedure / protocollo di intervento invio di casi dai Centri Antiviolenza e Case Rifugio ai servizi territoriali e/o specialistici (esempio schede di comunicazione ecc.)"),(5,"Procedure / protocollo di intervento per l'accoglienza e il sostegno della donna ed eventuali figli/e minori vittime di violenza subita e/o assistita"),(6,"Modalità operative per la presa in carico della vittima di violenza (schede di monitoraggio del percorso, percorsi di inserimento lavorativo, ecc.)"),(7,"Elaborazione linee guida per il miglioramento dell'erogazione dei servizi (di tipo sociale, sanitario, educativo ecc.)"),(8,"Procedure / protocolli per l'avvio e la realizzazione di percorsi di formazione"),(9,"Altro")]
oc2=oo[oo.OBIETTIVI_OPERATIVI_CK.notna()].OBIETTIVI_OPERATIVI_ACC.value_counts().to_dict()
M+=rows_from("OBIETTIVI_OPERATIVI_ACC (3.5)",sop,oc2,"Testo: questionario PDF (integrale). Codice: dedotto dall'ordine; 'Altro'=9 verificato (36 con testo)")
# 30 categorie
cat_rows=[]
for _,r in cats.iterrows():
    k=int(r.cod); sub=s[s.cod==k]
    cat_rows.append((k,r.label,int(sub.SOGGETTO_PROP_CHECK.notna().sum()),int(sub.TIPO_E_NUM_CHECK.notna().sum()),int(pd.to_numeric(sub.TIPO_E_NUM_TENDINA,errors='coerce').fillna(0).sum()),int(sub.ATTORI_COINVOLTI_CHECK.notna().sum()),int(sub.SOGGETTI_INCARICATI_CK.notna().sum())))
# ---------------- Qualita interna
Q=[
("Rispondenti","Protocolli per ufficio rispondente (primi tre)", "; ".join(f"{a}: {b}" for a,b in reg.head(3).items()), f"{reg.iloc[0]/N:.0%} dei protocolli viene da un solo rispondente: le medie nazionali dipendono molto da lui."),
("Rispondenti","Protocolli con 10 o più categorie proponenti", int((nprop>=10).sum()), "Alcuni rispondenti indicano come proponenti quasi tutti i firmatari; altri una o due categorie."),
("3.6 Durata","Durata = 0 con data di scadenza compilata", int(((dur==0)&e.notna()).sum()), "Il codice 0 sembra voler dire 'non indicata, vedi scadenza'. Non è documentato."),
("3.6 Durata","Durata con codici 99, 100, 999", int(dur.isin([99,100,999]).sum()), "999 (4 casi) probabilmente 'indeterminata'. Non è documentato."),
("3.6 Durata","Durata vuota", int(dur.isna().sum()), ""),
("3.6 Scadenza","Data di scadenza vuota", int(e.isna().sum()), ""),
("3.6 Scadenza","Data di scadenza dal 2040 in poi", int((e.dt.year>=2040).sum()), "Anni usati come 'senza scadenza' o errori di digitazione."),
("3.6 Durata/scadenza",f"Durata (1-30 anni) e scadenza non coerenti (scarto > 1 anno) su {int(ok.sum())} casi confrontabili", int((gap>1).sum()), "Controllo interno al solo questionario."),
("3.1/3.6 Date","Scadenza anteriore alla stipula", int((e<d).sum()), ""),
("1.2 Ambito","'Altro' scelto", int((c.AMBITO_RETE=='8').sum()), "Con specificazione compilata in %d casi."%nn('ALTRO_SPECIFICARE_1_2')),
("3.2 Natura","'Altro' scelto", int((c.NATURA_ACCORDO=='4').sum()), "Con specificazione compilata in %d casi."%nn('ALTRO_SPECIFICARE_3_2')),
("3.8 Monitoraggio","Risposta 'Non so'", int((c.PRESENZA_MONITORAGGIO=='3').sum()), "Il confronto binario con l'AI le esclude."),
("4.1 Prassi","Modalità 3 (solo 1522) mai scelta", int((c.PRASSI_INSERIMENTO=='3').sum()), ""),
("3.9 File","File allegati che compaiono in più record", int(c.UPLOAD_FILE.duplicated().sum()), "Stesso PDF associato a più compilazioni."),
("Intestazione","CAV di riferimento: lista vuota", int(c.ELENCO_CAV.isna().sum()), "Nome libero in %d casi."%nn('TESTO_LIBERO_NOME_CAV')),
("2.1/3.3/3.7 Commenti","Commenti vuoti o brevi/generici sulle selezioni (proponenti / attori / incaricati)", f"{jp[1]+jp[2]} su {jp[0]} / {ja[1]+ja[2]} su {ja[0]} / {ji[1]+ji[2]} su {ji[0]}", "Limita il confronto per nome degli enti."),
]
# ---------------- Confronto con PDF (proposta)
C=[
("V04","1.1 Titolo","Sì","Frontespizio / intestazione","Basso","Trascrizione diretta","No (campo copiato dal questionario)","Non fatta","Estrarre il titolo dal PDF e confrontare per similarità testuale","Alta corrispondenza. Serve a validare il raccordo questionario-PDF","Alta"),
("V05","1.2 Ambito della rete","Parziale","Territorio dei firmatari, premesse","Alto","Otto modalità che si sovrappongono (comunale, intercomunale, ambito sociale, provinciale). 'Altro' scelto 23 volte","No (campo copiato dal questionario)","Non fatta","Nuova estrazione LLM con regole esplicite + lettura di un campione","Accordo medio, errori tra modalità adiacenti","Media"),
("V06","2.1 Soggetto proponente","Parziale","Formule di promozione, premesse, firmatari","Alto","'Proponente' non è definito: i rispondenti includono firmatari o chi ha impegni","Sì (ruolo soggetto_proponente)","Fatta in forma aggregata (Jaccard 0,22)","Confronto con tre definizioni: promotore esplicito, convocante, firmatario. Lettura di un campione sui PDF","L'accordo cresce con la definizione più larga. Gli umani sono vicini a 'firmatario'","Alta"),
("V07","2.2 Tipologia e numerosità","Sì","Elenco firmatari e destinatari","Alto","Non è chiaro cosa si conti; i comuni vengono aggregati","Sì (nomi distinti per categoria)","Parziale (conteggi AI maggiori in 200 protocolli su 251)","Confronto dei conteggi per categoria, definendo cosa si conta (firmatari / citati). Lettura di un campione","AI >= umano; differenze maggiori per Comuni, Altro, Polizia municipale","Alta"),
("V08","3.1 Data della stipula","Sì","Data in calce o in epigrafe","Medio","Più date possibili (firma, integrazioni, rinnovi)","No (campo copiato dal questionario)","Non fatta: il 98% di coincidenza non misura l'AI","Estrazione LLM della data e confronto con il questionario","Alta concordanza, differenze nei protocolli con più date","Alta"),
("V09","3.2 Natura dell'accordo","Sì","Titolo e preambolo","Medio","Il nome usato nel titolo non coincide sempre con la natura","No (campo copiato dal questionario)","Non fatta","Estrazione LLM di titolo e natura","Alta concordanza","Media"),
("V10","3.3 Attori coinvolti","Sì","Elenco firmatari, articoli sugli impegni","Alto","Confine con 'proponente' e 'firmatario'","Sì (ruolo attore)","Fatta in forma aggregata (Jaccard 0,57)","Analisi per categoria e per dimensione del protocollo; audit dei casi solo AI e solo umano","Accordo buono sui protocolli grandi, peggiore su ETS e Altro","Alta"),
("V11","3.4 Obiettivi strategici","Sì","Articolo 'Obiettivi' / premesse","Medio","Molte scelte per protocollo; modalità sovrapposte","No","Non fatta","Classificazione LLM con definizione di ogni modalità. Accordo e kappa per modalità","Accordo moderato; la sovra-selezione umana è probabile","Media"),
("V12","3.5 Obiettivi operativi","Sì","Articoli sugli impegni operativi","Medio","Come 3.4","No","Non fatta","Come 3.4","Accordo moderato","Media"),
("V13","3.6 Durata (anni)","Sì","Clausola di durata","Alto","Codici 0 e 999 non documentati; tacito rinnovo","No","Non fatta","Estrazione LLM di durata, scadenza, rinnovo. Confronto dopo aver chiarito i codici","Molti protocolli non indicano una durata","Media"),
("V14","3.6 Data di scadenza","Parziale","Clausola di durata (spesso assente)","Alto","Scadenza calcolata o dedotta dal rispondente","No","Non fatta","Come V13","Concordanza bassa se il testo non indica la scadenza","Media"),
("V15","3.7 Incaricati di gestire/monitorare/coordinare","Parziale","Articoli su coordinamento e monitoraggio, tavoli","Alto","Tre funzioni nella stessa domanda","Sì (flag governance, coordinamento, monitoraggio, gestione)","Fatta in forma aggregata (Jaccard 0,21 sul flag governance)","Decidere un criterio unico (gestione sì o no). Confronto con un campione letto","Concordanza bassa; l'AI segna più soggetti degli umani","Alta"),
("V16","3.8 Presenza di monitoraggio","Parziale","Clausole di monitoraggio o valutazione","Alto","Si chiede se c'è un monitoraggio, non chi lo fa. 'Non so' ammesso","Sì, ma indiretto (flag aggregato sui soggetti)","Fatta (138/218; kappa circa 0,23)","Nuova estrazione dedicata con tre esiti: sì, no, non determinabile","Concordanza limitata dalla definizione","Alta"),
("V17","3.9 File allegato","No","-","Basso","È il documento stesso","-","-","Controlli di qualità del PDF: leggibilità, OCR, file duplicati, protocolli con 0 soggetti estratti (5)","Mostra l'incidenza dell'OCR sugli errori","Media"),
("V18","4.1 Prassi casa rifugio","No","-","-","Riguarda la prassi regionale, non il protocollo","-","-","Fuori dal confronto","-","Bassa"),
("V19","4.2 Accesso diretto casa rifugio","No","-","-","Riguarda la prassi regionale, non il protocollo","-","-","Fuori dal confronto","-","Bassa"),
("V01-V03","Chiavi, rispondente, CAV","No","-","-","Metadati del questionario","-","-","Solo per il raccordo e l'analisi per regione","-","-"),
]
OPEN=[
("Codici","Confermare i codici di PRASSI_INSERIMENTO e RIVOLGE_DIRETTAMENTE (1=SI?). Sono assegnati in base all'ordine nel PDF."),
("Codici","Cosa significano DURATA_ACCORDO = 0 e 999? E DATA_FINE_ACCORDO = 2040-2050?"),
("2.1","Qual era l'istruzione ai rispondenti per 'proponente'? C'è una guida alla compilazione?"),
("2.2","Cosa deve contare la numerosità: firmatari, destinatari, tutti i soggetti citati?"),
("3.7","Va considerata gestione = governance? La domanda del questionario le unisce, il manuale dell'AI le separa."),
("3.1-3.2, 1.2","Questi campi nell'output AI sono copiati dal questionario. Confermare, e decidere se estrarli dai PDF."),
("Dati","Rispondente 4 = prova? Escluderlo. Confermare che i 3 record senza file (1014/1, 1015/1, 1019/1) vanno fuori."),
("Dati","Il rispondente 1012 ha 95 protocolli su 251. Analisi per regione con o senza?"),
("Audit","Chi legge i PDF, con quale scheda, e con quali definizioni di proponente / attore / incaricato? Servono anche le regole per i protocolli con atti integrativi."),
("Fonte","Alcune informazioni del questionario non sono nel PDF (es. ordini aggiunti con atti successivi). Come le trattiamo?"),
]
# ---------------- write workbook
wb=Workbook(); AR="Arial"
hf=Font(name=AR,bold=True,color="FFFFFF",size=10); hfill=PatternFill("solid",fgColor="1F3864"); bf=Font(name=AR,size=10)
thin=Side(style="thin",color="BFBFBF"); brd=Border(left=thin,right=thin,top=thin,bottom=thin)
inp=PatternFill("solid",fgColor="FFF2CC")
def sheet(name,header,rows,widths,first=False,fills=None):
    ws=wb.active if first else wb.create_sheet(); ws.title=name
    ws.append(header)
    for r in rows: ws.append(list(r))
    for cell in ws[1]: cell.font=hf; cell.fill=hfill; cell.alignment=Alignment(wrap_text=True,vertical="center"); cell.border=brd
    for row in ws.iter_rows(min_row=2):
        for cell in row: cell.font=bf; cell.alignment=Alignment(wrap_text=True,vertical="top"); cell.border=brd
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w
    ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions; ws.row_dimensions[1].height=32
    return ws
# Leggimi
ws=wb.active; ws.title="Leggimi"
L=[("Variabili del questionario 'Reti territoriali antiviolenza' (bozza V1, 27/10/2026)",),("",),
("Scopo","Elencare le variabili del questionario, il loro tipo e le modalità, e preparare la scelta delle variabili da confrontare con i PDF dei protocolli."),
("Fonti","Microdati in analisi/microdati (cartelle gino, ai, rif; elenco nel foglio 'Fonti'); 3 questionari d'esempio in PDF (cartella data)."),
("Perimetro",f"{N} record con file allegato (254 nel tracciato, esclusi i 3 senza file e il rispondente di prova 4). Le percentuali usano questo denominatore."),
("Fogli","Fonti: file di origine con nome originale. Variabili: elenco con tipo e copertura. Modalità: codici, etichette e frequenze (incluse le 30 categorie di soggetti). Qualità interna: controlli sul solo questionario. Confronto con PDF: proposta, con colonne da compilare. Domande aperte. Il campo AI è quello dell'output analizzato finora; le variabili estratte dai nuovi script di Paolo vanno aggiunte."),
("Colonne gialle","Le colonne 'Decisione' e 'Note' nel foglio 'Confronto con PDF' sono da compilare con i colleghi. Le altre colonne di quel foglio sono una proposta di lavoro."),
("Stato dei dati","I valori sono calcolati dai tracciati e scritti come numeri fissi (nessuna formula). Gli script sono in analisi/codice (variabili_questionario_build.py)."),
("Cautela","Il testo delle modalità è preso dal questionario PDF. I codici numerici sono assegnati in base all'ordine delle modalità; la sola conferma esplicita riguarda PRESENZA_MONITORAGGIO. Vedi la colonna 'Fonte della codifica'.")]
for r in L: ws.append(list(r))
ws["A1"].font=Font(name=AR,bold=True,size=13)
for row in ws.iter_rows(min_row=3):
    row[0].font=Font(name=AR,bold=True,size=10)
    for cell in row[1:]: cell.font=bf; cell.alignment=Alignment(wrap_text=True,vertical="top")
ws.column_dimensions["A"].width=18; ws.column_dimensions["B"].width=110
rowsV=[(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],(r[8]/N if r[8] and r[8]<=N else None),r[9],r[10]) for r in V]
w1=sheet("Variabili",["Id","Sezione","Domanda","Testo (sintesi)","Variabile nel tracciato","Tracciato","Tipo","N modalità","N con risposta","% con risposta","Formato / modalità","Note su definizione e qualità"],rowsV,[6,18,9,34,38,12,26,10,11,11,36,60])
for r in w1.iter_rows(min_row=2): r[9].number_format="0%"
w2=sheet("Modalità",["Variabile","Codice","Etichetta (testo del questionario)","N selezioni",f"% su {N}","Fonte della codifica"],[(a,b,l,n,(n/N),f) for a,b,l,n,f in M],[34,9,60,12,10,60])
for r in w2.iter_rows(min_row=2): r[4].number_format="0%"
# 30 categorie
w3=sheet("30 categorie soggetti",["Codice","Categoria","Proponenti (2.1)","Con numerosità (2.2)","Somma numerosità (2.2)","Attori (3.3)","Incaricati (3.7)"],cat_rows,[8,70,14,16,16,12,14])
w4=sheet("Qualità interna",["Domanda / area","Controllo","Risultato","Nota"],Q,[22,62,22,70])
w5=sheet("Confronto con PDF",["Id","Variabile","Confrontabile con i PDF","Dove nel PDF","Rischio di interpretazione","Perché","Campo AI nell'output analizzato (da aggiornare con gli script di Paolo)","Stato dell'analisi","Analisi proposta","Risultato atteso (ipotesi)","Priorità (proposta)","Decisione","Note colleghi"],[tuple(r)+("","") for r in C],[9,28,14,30,12,46,28,30,48,38,11,16,36])
for row in w5.iter_rows(min_row=2):
    row[11].fill=inp; row[12].fill=inp
dv=DataValidation(type="list",formula1='"Includere,Escludere,Da discutere"',allow_blank=True); w5.add_data_validation(dv); dv.add(f"L2:L{len(C)+1}")
w6=sheet("Domande aperte",["N.","Area","Domanda","Risposta"],[(i+1,a,b,"") for i,(a,b) in enumerate(OPEN)],[6,16,110,40])
for row in w6.iter_rows(min_row=2): row[3].fill=inp
fonti=pd.read_csv(MD+"_fonti.csv",sep=";",encoding="utf-8-sig",dtype=str)
fonti=fonti[fonti.file.str.startswith("microdati/")]
sheet("Fonti",["File (in analisi/)","Nome originale","Contenuto","Note"],[(r.file,r.nome_originale,r.contenuto,r.note if isinstance(r.note,str) else "") for r in fonti.itertuples()],[52,58,70,50])
out=str(DOCS/"variabili_questionario_v1.xlsx"); wb.move_sheet("Fonti",offset=-(len(wb.sheetnames)-2)); wb.save(out); print("saved",out)
for r in Q: print(r[:3])
print(P,A,I,T,O,OO,N)
