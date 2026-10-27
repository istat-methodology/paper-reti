# Contesto per Claude

Paper su reti territoriali antiviolenza: confronto micro tra questionario GINO e parsing LLM dei PDF dei protocolli. Leggi `README.md` e `docs/stato.md` prima di tutto.

## Regole
- Lingua: italiano. Tono casuale e diretto, frasi dichiarative semplici, paragrafi corti. Niente frasi generiche.
- Prima di scrivere testo del paper, fai domande se il contesto non è chiaro.
- Non usare la parola "inventario": il file si chiama "variabili questionario V1".
- I microdati non vanno MAI committati (nomi di enti, testo libero). Controlla `.gitignore` prima di ogni `git add`.
- Niente commit né push se non richiesti.
- Non fidarsi delle analisi aggregate dei colleghi: ricalcolare dai microdati.
- Il confronto sta in `codice/common.py`: nessuna dipendenza dal file Match dei colleghi.
- Output nuovi con la convenzione `<tipo>_<contenuto>[_<dettaglio>][_<versione>]`.
- In attesa: lista esatta delle variabili estratte dai nuovi script AI (Paolo/Elena).
