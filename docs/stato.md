# Stato

Aggiornato: 2026-10-28

## Cambio di impianto
Mauro ritiene le analisi dei colleghi poco difendibili e riproducibili. Nuovo impianto:
- **Lato AI**: congelato. La pipeline di Paolo (molte chiamate API) non si rifà. Si usano i suoi risultati.
- **Lato questionario**: ricostruito dai PDF dei questionari compilati, con uno script. I PDF hanno layout identico.
- **Campione**: Mauro pensa di recuperare tutti i 251–253 questionari (prima ipotesi ≈100). Consegna domani insieme ai protocolli (TXT/PDF) e ai risultati AI. Se resta un campione, si dichiara benchmark su campione di convenienza e non inferenza di statistica ufficiale.
- Il CSV GINO dei colleghi diventa controllo incrociato del parser.

## Fatto
- Repo online (primo commit 24b6e41): README, CLAUDE.md, docs, codice, riferimenti, microdati ignorati.
- `codice/parse_questionari.py`: legge le spunte (immagini: radio/checkbox vuoto/pieno), commenti, numerosità e testi liberi di tutte le domande (0, 1.1–1.2, 2.1–2.2, 3.1–3.9, 4.1–4.2). Si ferma con errore se una voce non si ancora o una spunta manca.
- Verifica su 3 questionari, che sono (1009,1), (1009,12), (1012,95) nel CSV: data stipula, durata, scadenza, nome file caricato, ambito, monitoraggio coincidono.
- Il campo 3.9 contiene il nome del file del protocollo: candidato a chiave per abbinare questionario, protocollo e output AI (coincide con `UPLOAD_FILE` del CSV).
- Analisi sul CSV (accordo per categoria, numerosità): vedi `risultati_preliminari.md`. Resta valida come indicazione, ma verrà rifatta sul nuovo impianto.

## 28/10: 251 questionari
- Mauro ha caricato 251 PDF in `microdati/gino/`. Rinominati `questionario_<codice>.pdf`. Il codice è regione (2 cifre) + progressivo (2 cifre), per Bolzano/Trento regione + codice territoriale (41/42) + progressivo (6 cifre). I protocolli useranno `protocollo_<codice>`.
- `risultati_questionari_gino.csv` (colleghi, 251 righe): codice regione, provincia, nome dell'allegato, pagina di 3.9. Non l'ho ancora usato.
- Parser lanciato su tutti: 251 questionari, 43.172 righe, nessun errore (172 righe per questionario). Servono ~95 secondi.
- Correzione: gli ID oggetto delle immagini delle spunte cambiano da PDF a PDF (es. 0201 ne ha 13 pagine). Ora le spunte si classificano per dimensione e luminosità media.
- Confronto con il CSV dei colleghi, chiave = nome file 3.9 + data stipula: 240 abbinati, durata e scadenza coincidono in tutti i 240. 11 questionari non si abbinano per differenze di testo (da risolvere con l'anagrafica).
- Il formato lungo (`gino_pdf_risposte_lungo.csv`) è approvato da Mauro. Manca la colonna ID (ora `file`) e l'anagrafica, che Mauro fornirà.

## Limiti noti del parser
- Apostrofi già `?` nel PDF (es. "D?INTESA"): perdita a monte.
- Testi lunghi (titolo) possono essere tagliati dal layout del PDF.
- Le spunte sono riconosciute per dimensione e luminosità (16 px radio, 26 px checkbox). Se compare un'immagine con luminosità diversa, lo script si ferma.
- Il confronto parser vs CSV è fatto su durata e scadenza (240 casi). Da estendere a 2.1, 2.2, 3.3, 3.4, 3.5, 3.7 e al resto.

## Domani (Mauro + Paolo)
1. Come sono nominati i file dei protocolli dati alla pipeline (per verificare la chiave dal campo 3.9).
2. Lista esatta delle variabili estratte dai nuovi script AI.
3. Output AI disponibile per tutti i 251–253 protocolli, nello stesso formato?
4. Mauro carica questionari, protocolli (TXT/PDF) e risultati AI.

## Da fare dopo la consegna
1. Mettere i PDF in `microdati/gino/` e lanciare il parser su tutti; controllare errori.
2. Confronto parser vs CSV colleghi su tutte le variabili (quantifica gli errori di trascrizione).
3. Ricostruire `common.py` sul nuovo impianto: questionario da PDF, AI da output di Paolo, chiave dal campo 3.9.
4. Aggiornare `docs/variabili_questionario_v1.xlsx`: oggi parte dal tracciato CSV e non si legge. Rifarlo per domanda (numerazione del questionario): testo, tipo, modalità, cosa cerca l'AI, se si confronta.
5. Rifare l'accordo per categoria e la numerosità sul nuovo impianto.
6. Definizioni unificate: proponente; gestione vs governance.
7. Validare la mappatura dei 604 soggetti AI senza categoria (provvisoria, `ALT`).
8. Audit sui PDF dei protocolli: campione stratificato di 40–100 (nessun gold standard).
9. Verifica letteratura per il claim "primo confronto micro".
10. Scegliere la rivista (JOS troppo lenta ~18 mesi; SJIAOS livello basso; speciale SIS o Metron entro il 31/12/2026).

## Domande aperte a Mauro
- Che guida/definizione vedono i rispondenti per "proponente"?
- Cosa conta la 2.2?
- Significato di DURATA 0/999 (nel Q3 la durata è 0 con scadenza 08/10/2024).
- Regione: con o senza rispondente 1012?
- Chi legge i PDF per l'audit?
