# Contesto per Claude

Paper su reti territoriali antiviolenza: confronto micro tra i questionari GINO (parsati dai PDF) e l'estrazione LLM dai protocolli. Leggi `README.md`, `docs/stato.md` e `docs/decisioni.md` prima di tutto.

## Regole
- Lingua del paper: inglese. Con Mauro si conversa in italiano.
- Stile: frasi dichiarative semplici, paragrafi corti, niente frasi generiche.
- Prima di scrivere testo del paper, fai domande se il contesto non è chiaro.
- I microdati di partenza (PDF dei questionari, protocolli, JSON AI, CSV del parser, testo libero) non vanno mai committati: controlla `.gitignore` prima di ogni `git add`. Gli output delle analisi in `risultati/` possono contenere nomi di enti e si possono committare (decisione di Mauro, 2026-10-29), perché finiscono nel paper.
- Niente commit né push se non richiesti.
- Tre fonti collegate dal codice del file: questionario (PDF parsati con `codice/parse_questionari.py`), protocollo (TXT), output AI. Dal 2026-10-30 la pipeline AI si rifà da zero (v2, `codice/pipeline_ai_v2/`, registro in `docs/experiments.md`); gli output della v1 (`ai_<codice>.json`) sono il punto di partenza storico, non il risultato.
- I prompt della pipeline sono in `prompts/` (v1 archiviata, v2 attuale): leggili prima di interpretare differenze tra questionario e AI. Il disaccordo può venire da definizioni diverse (proponente, attore, incaricato), non solo da errori.
- Per il blocco `questionario` dei JSON 2.6: non è output AI, non va usato.
- Niente script complessi né ipotesi non richieste: chiedi.
- File nuovi con la convenzione `<tipo>_<contenuto>[_<dettaglio>][_<versione>]`.
