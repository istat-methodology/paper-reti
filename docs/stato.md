# Stato

Aggiornato: 2026-10-28

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
- Pipeline: quale modello e quali parametri (temperatura), come sono trattati i protocolli lunghi (spezzati o interi), come entrano i `runts_matches` nel passo 1?
- Il prompt per 2.2 (numerosità) non esiste: si conta `soggetti`, che comprende tutti gli enti citati. Si usa `firmatari` oppure `attori_coinvolti` come riferimento?
- Che guida o definizione vedono i rispondenti per "proponente" (2.1)?
- Cosa conta la numerosità in 2.2?
- Significato di durata 0 in 3.6 (un questionario ha durata 0 e scadenza valorizzata).
- Chi legge i protocolli per l'audit?
