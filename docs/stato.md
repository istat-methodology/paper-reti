# Stato

Aggiornato: 2026-11-02

## Fatto
- 251 questionari GINO in PDF, rinominati `questionario_<codice>.pdf`.
- `parse_questionari.py` li converte in CSV: 251 questionari, 43.172 righe nel formato lungo (172 per questionario), nessun errore. Il formato lungo è approvato come riferimento.
- Controllo incrociato con l'export del database GINO, chiave = nome del file caricato (3.9) + data di stipula: 240 questionari abbinati, durata e scadenza coincidono in tutti.
- Repo impostato; microdati fuori da git.

- Protocolli (337 TXT, 335 senza i file di prova) abbinati ai 251 questionari: 239 per timestamp, 12 per nome dell'allegato. Nei 239 il nome del file coincide con l'allegato di 3.9 in 236 casi; gli altri 3 differiscono solo per la codifica dei caratteri. Due questionari (0909, 0910) condividono lo stesso protocollo. 85 file non sono usati da nessun questionario (altri documenti caricati, soprattutto Toscana e Puglia).
- Anagrafica `microdati/rif_anagrafica_v1.xlsx` con nome nuovo/originale e regione.

- Output AI: due JSON unici (253 protocolli) spezzati in 251 file `ai_<codice>.json`, uno per questionario. Abbinamento per timestamp (227) o nome (24). Esclusi due file di prova e `09_PISTOIA PROV .txt`, che non corrisponde a nessun questionario. Il protocollo di Prato è condiviso da 0909 e 0910.
- Contenuto dell'output AI: elenchi di soggetti (con categoria e ruolo: firmatario, proponente, attore) e nomi di proponenti, attori, coordinatori, soggetti di monitoraggio, cabina di regia, più arricchimento geografico e RUNTS. Non ci sono date, natura dell'accordo, durata né obiettivi: la copertura riguarda 2.1, 2.2, 3.3, 3.7 e in parte 3.8.
- La cartella `output/` contiene analisi aggregate dei colleghi: ignorata da git, non si usa per ora.

## In arrivo
- L'elenco delle variabili che i nuovi script AI estraggono oltre ai soggetti.

## Prompt
`prompts/prompt_protocolli.txt`: quattro passi (firmatari e soggetti; proponenti; attori; governance). Sintesi e corrispondenza con le domande in `docs/metodologia.md`. Il vocabolario dei tipi coincide in gran parte con le 30 categorie del questionario. I passi 2–4 scelgono solo tra i soggetti del passo 1 e restituiscono vuoto nel dubbio.

## Run su 240 documenti (descrizione, 2026-11-02)
Tabelle in `risultati/descrizione_run_stadio1_v2.xlsx` (240 documenti; la v1 è sui 249 file), generate da `codice/pipeline_ai_v2/descrizione_run.py`. Sono conteggi e stabilità tra run, non stime: la correzione con i tassi del gold viene dopo. Nucleo: mediana 12 enti per protocollo (Q1 4.75, Q3 25.25); 89% dei cluster in tutte le 5 run; Jaccard tollerante mediano 0.98; ruolo prevalente sugli enti in almeno 3 run: 58% `firmatario`, 27% `solo_citato`, 15% `componente_rete`. Periferia: mediana 17 voci; 67% in tutte le 5 run; Jaccard 0.83. Da guardare: 1223 (Jaccard 0.60), 1613 (306.000 caratteri, Jaccard 0.66).

## Controlli sulla popolazione (2026-11-02)
- Fuori ambito: 1701, 1702, 0201, 044103. Copie (resta un file): 1258, 1261, 0326, 1306, 0909. Popolazione: 240 documenti.
- Campione v2: n = 58 (rimpiazzo 044103 → 044102; Basilicata e Valle d'Aosta senza unità). Gold v2: 044103 → 1210 (niente tedesco nel gold).
- Fatto (2026-11-02): pacchetto gold v2 (`annotazione/gold_v2/pacchetto_gold_v2.zip`, senza 044103 e con 1210; il v1 resta come riferimento); foglio di revisione di fase 2 rifatto sui 38 protocolli del campione fuori dal gold (305 righe, 8.0 per protocollo; il vecchio, a 40 protocolli, è in `revisione/archivio_campione_v1/`); descrizione della run sui 240 documenti.
- **Da fare:** avvisare Paolo del cambio (togliere 044103, aggiungere 1210) e mandargli il pacchetto v2; assegnare la fase 2; aggiornare i pesi di campionamento con la nuova popolazione.
- Funzioni (promotore, coordinatore/capofila, monitoraggio responsabile): colonne nel template v4 del gold, annotate da Paolo insieme al resto. Il pacchetto v2 contiene la v4.
- Da valutare: documenti contenuti in altri (1308, 1307 in 1305; 1295 in 1276); quasi-copie del Lazio (0113/0122, 1285/1286, 1242 con 1261/1264, ecc.); 1245 e 0116 come possibili non protocolli; 044102 (nel campione, fase 2, deciso di tenerlo) è in tedesco e 044104 è bilingue.

## Protocolli in PDF (2026-11-03)
- 338 PDF dai 17 zip regionali (`microdati/protocolli_pdf/_originali/`). 251 `protocollo_<codice>.pdf`, abbinati agli stessi 251 questionari dei TXT (0909 e 0910 condividono il file).
- Fuori campione, tenuti con il nome originale in `_estratti/`: 85 PDF di convenzioni, leggi e altri documenti che le regioni hanno caricato oltre ai protocolli, più 3 senza TXT (2 prove, 1 file Piemonte senza timestamp). Elenco in `microdati/rif_anagrafica_v2.xlsx`, fogli `Protocolli_non_usati` e `Pdf_senza_txt`.
- Mapping nuovo/originale in `rif_anagrafica_v2.xlsx` (colonne `protocollo_pdf_*`); gli script leggono ora la v2. 0903 e 0908 tengono la versione non compressa.

## Struttura (2026-11-02)
Due parti: A, si possono usare strumenti AI nella raccolta dati? (RQ0, analisi dei protocolli); B, confronto con il questionario già condotto (RQ1 confrontabilità e cause, RQ2 integrazione; B1 insiemi di enti, B2 ruoli). Recall del gold su tutti gli enti, poi per ruolo. Vedi `README.md` e `docs/decisioni.md`.

## Prossimi passi
1. Controllare il parser su tutte le variabili contro il CSV dei colleghi e costruire la tabella micro questionario × AI per le domande sui soggetti.
2. Definire le variabili da confrontare, per domanda e con la numerazione del questionario: tipo, modalità, cosa corrisponde nell'output AI.
3. Estendere il controllo del parser a tutte le variabili.
4. Costruire il confronto questionario–AI (RQ1) e valutare l'integrazione (RQ2).
5. Definizioni da unificare: proponente; gestione vs governance.
6. Audit su un campione stratificato di protocolli.
7. Verifica della letteratura sul claim "primo confronto micro".
8. Scegliere la rivista (JOS troppo lenta, ~18 mesi; SJIAOS livello basso; numero speciale SIS o Metron, scadenza 31/12/2026).

## Domande aperte
- Ipotesi da verificare sul gold: il questionario non conta le istituzioni senza nome (Prefettura, Pronto soccorso). Decide il perimetro del confronto B1.
- Verifica in letteratura del claim "prima volta in statistica ufficiale" per l'esperimento della parte A.
- Pipeline: quale modello e quali parametri (temperatura), come sono trattati i protocolli lunghi (spezzati o interi), come entrano i `runts_matches` nel passo 1?
- Il prompt per 2.2 (numerosità) non esiste: si conta `soggetti`, che comprende tutti gli enti citati. Si usa `firmatari` oppure `attori_coinvolti` come riferimento?
- Che guida o definizione vedono i rispondenti per "proponente" (2.1)?
- Cosa conta la numerosità in 2.2?
- Significato di durata 0 in 3.6 (un questionario ha durata 0 e scadenza valorizzata).
- Chi legge i protocolli per l'audit?

## Pipeline AI v2 (aggiornamento 2026-10-31)
- Stadio 1 (enti e ruolo) sperimentato sulla Toscana: 9 esperimenti (prompt v0–v1.2, testo e PDF, protocolli lunghi spezzati, numero di run). Risultati in `docs/experiments.md`; stabilità del nucleo tra run 0.96 (confronto tollerante dei nomi).
- Pronto: script di revisione manuale degli enti (`codice/pipeline_ai_v2/revisione_enti.py`).
- Fatto (2026-10-31/11-01): campione n = 60; stadio 1 con 5 run sul campione; gold da zero su 20 protocolli estratti dai 60 (`campione/campione_gold_v1.csv`), template in `annotazione/gold_v2/`.
- In sospeso: annotazione del gold (Paolo; secondo annotatore su 8 protocolli); revisione di fase 2 sui 38 protocolli fuori dal gold; congelamento di prompt e parametri (`parametri/`); decisione sul conteggio della periferia; risposta dei colleghi sulle definizioni; stadi 2–4.

## Dove siamo (2026-11-01, sera)
- Commit e tag `freeze-stadio1` fatti. Run di stadio 1 su tutti i protocolli in corso: `python codice/pipeline_ai_v2/stadio1_spezzato.py --tutti --runs 5 --tag pubblicazione_v1_2 --workers 2` (si riprende rilanciando lo stesso comando).
- Gold: pacchetto in `annotazione/gold_v2/pacchetto_gold.zip`; Paolo inizia il 2026-11-02 (sui PDF). Secondo annotatore sugli 8 protocolli `doppia=si`: Elena o Mauro, da confermare.
- Revisione di fase 2: `revisione/revisione_pubblicazione_v1_2.xlsx` (38 protocolli, 305 righe, rifatto il 2026-11-02), non ancora assegnata.
- Schema complessivo: `docs/pipeline_e_stime.md`.

## Prossimi passi
1. ~~Contare i protocolli processati dalla run.~~ Fatto (2026-11-02): 249 protocolli × 5 run = 1.245 file, tutti completi. Run su 249 file con testo (251 meno 044101 e 1612). Popolazione di riferimento dopo i controlli: 240 documenti (4 fuori ambito, 5 copie); vedi `docs/decisioni.md` e `campione/frame_esclusioni_v1.csv`. Un solo errore di connessione (0701, run 1), ripreso dallo script. Prima di usare le liste della run: misure sui 249 (nucleo, periferia, stabilità).
2. Stadio 2 (classificazione nelle 30 categorie) sulle liste della run: prompt da scrivere.
3. Quando arriva il gold: accordo tra annotatori, recall e precision di stadio 1, pooling degli enti trovati solo dal modello.
4. Assegnare la fase 2 a un revisore; decidere la quota di unanimi da rivedere.
5. Regola di conteggio della periferia (con i colleghi della produzione); metodo di correzione per le stime.
6. Verificare i ruoli e i casi aperti (Banca d'Italia in 0906, RELIVE, WWP EN, OMS); doppioni nella fusione dei pezzi (SDS, Donne Insieme); protocollo 1613.
7. Unione dei Comuni (categoria 3 o 8); definizioni da confermare con Paolo ed Elena.
