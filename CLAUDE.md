# Contesto per Claude

Paper su reti territoriali antiviolenza: confronto micro tra i questionari GINO (parsati dai PDF) e l'estrazione LLM dai protocolli. Leggi `README.md`, `docs/stato.md` e `docs/decisioni.md` prima di tutto.

## Regole
- Lingua del paper: inglese. Con Mauro si conversa in italiano.
- Stile: frasi dichiarative semplici, paragrafi corti, niente frasi generiche.
- Prima di scrivere testo del paper, fai domande se il contesto non è chiaro.
- I microdati non vanno mai committati (nomi di enti, testo libero, PDF). Controlla `.gitignore` prima di ogni `git add`.
- Niente commit né push se non richiesti.
- Tre fonti collegate dal codice del file: questionario (PDF parsati con `codice/parse_questionari.py`), protocollo (TXT), output AI (`ai_<codice>.json`). Gli output AI si usano come arrivano, non si rifà la pipeline.
- I prompt della pipeline sono in `prompts/`: leggili prima di interpretare differenze tra questionario e AI. Il disaccordo può venire da definizioni diverse (proponente, attore, incaricato), non solo da errori.
- Per il blocco `questionario` dei JSON 2.6: non è output AI, non va usato.
- Niente script complessi né ipotesi non richieste: chiedi.
- File nuovi con la convenzione `<tipo>_<contenuto>[_<dettaglio>][_<versione>]`.
