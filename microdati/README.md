# microdati

Questa cartella è ignorata da git (vedi `.gitignore`). Si committa solo questo README e `_fonti.csv`.

I file veri stanno in OneDrive: `Istat/Papers/2026 - Reti Territoriali extended/analisi/microdati/`.
Per lavorare da qui: copiali nelle sottocartelle, oppure `export RETI_MICRODATI=/percorso/microdati`.

- `gino/`: questionario compilato dagli uffici regionali (protocolli, obiettivi, soggetti)
- `ai/`: output della pipeline LLM (JSON arricchiti, tabelle p2_6)
- `rif/`: tabelle di riferimento (30 categorie → 10 gruppi)
- `_fonti.csv`: nome originale, byte e sha256 di ogni file, per la provenienza

Convenzione nomi: `<tipo>_<contenuto>[_<dettaglio>][_<versione>]`, con tipo = gino / ai / rif / confronto. `pN_M` indica la fase della pipeline.
