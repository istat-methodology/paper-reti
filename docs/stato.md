# Stato

Aggiornato: 2026-10-28

## Fatto
- 251 questionari GINO in PDF, rinominati `questionario_<codice>.pdf`.
- `parse_questionari.py` li converte in CSV: 251 questionari, 43.172 righe nel formato lungo (172 per questionario), nessun errore. Il formato lungo è approvato come riferimento.
- Controllo incrociato con l'export del database GINO, chiave = nome del file caricato (3.9) + data di stipula: 240 questionari abbinati, durata e scadenza coincidono in tutti.
- Repo impostato; microdati fuori da git.

- Protocolli (337 TXT, 335 senza i file di prova) abbinati ai 251 questionari: 239 per timestamp, 12 per nome dell'allegato. Nei 239 il nome del file coincide con l'allegato di 3.9 in 236 casi; gli altri 3 differiscono solo per la codifica dei caratteri. Due questionari (0909, 0910) condividono lo stesso protocollo. 85 file non sono usati da nessun questionario (altri documenti caricati, soprattutto Toscana e Puglia).
- Anagrafica `microdati/rif_anagrafica_v1.xlsx` con nome nuovo/originale e regione.

## In arrivo
- Gli output AI sui protocolli.

## Prossimi passi
1. Mettere gli output AI in `microdati/ai/` e collegarli con il codice.
2. Definire le variabili da confrontare, per domanda e con la numerazione del questionario: tipo, modalità, cosa corrisponde nell'output AI.
3. Estendere il controllo del parser a tutte le variabili.
4. Costruire il confronto questionario–AI (RQ1) e valutare l'integrazione (RQ2).
5. Definizioni da unificare: proponente; gestione vs governance.
6. Audit su un campione stratificato di protocolli.
7. Verifica della letteratura sul claim "primo confronto micro".
8. Scegliere la rivista (JOS troppo lenta, ~18 mesi; SJIAOS livello basso; numero speciale SIS o Metron, scadenza 31/12/2026).

## Domande aperte
- Che guida o definizione vedono i rispondenti per "proponente" (2.1)?
- Cosa conta la numerosità in 2.2?
- Significato di durata 0 in 3.6 (un questionario ha durata 0 e scadenza valorizzata).
- Chi legge i protocolli per l'audit?
