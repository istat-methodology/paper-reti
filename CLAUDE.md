# Contesto per Claude

Paper su reti territoriali antiviolenza: confronto micro tra i questionari GINO (parsati dai PDF) e l'estrazione LLM dai protocolli. Leggi `README.md`, `docs/stato.md` e `docs/decisioni.md` prima di tutto.

## Regole
- Lingua del paper: inglese. Con Mauro si conversa in italiano.
- Stile: frasi dichiarative semplici, paragrafi corti, niente frasi generiche.
- Prima di scrivere testo del paper, fai domande se il contesto non è chiaro.
- I microdati non vanno mai committati (nomi di enti, testo libero, PDF). Controlla `.gitignore` prima di ogni `git add`.
- Niente commit né push se non richiesti.
- Lato questionario: si parte dai PDF compilati (`codice/parse_questionari.py`). Lato AI: si usano gli output della pipeline come arrivano, non si rifà.
- Niente script complessi né ipotesi non richieste: chiedi.
- File nuovi con la convenzione `<tipo>_<contenuto>[_<dettaglio>][_<versione>]`.
