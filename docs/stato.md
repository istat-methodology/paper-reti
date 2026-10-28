# Stato

Aggiornato: 2026-10-28

## Fatto
- 251 questionari GINO in PDF, rinominati `questionario_<codice>.pdf`.
- `parse_questionari.py` li converte in CSV: 251 questionari, 43.172 righe nel formato lungo (172 per questionario), nessun errore. Il formato lungo è approvato come riferimento.
- Controllo incrociato con l'export del database GINO, chiave = nome del file caricato (3.9) + data di stipula: 240 questionari abbinati, durata e scadenza coincidono in tutti.
- Repo impostato; microdati fuori da git.

## In arrivo
- I protocolli (`protocollo_<codice>`).
- Gli output AI sui protocolli.
- L'anagrafica con ID, regione e collegamento questionario–protocollo.

## Prossimi passi
1. Mettere protocolli e output AI in `microdati/` e fissare il codice di collegamento.
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
