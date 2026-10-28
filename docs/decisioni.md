# Decisioni

**Ultimo aggiornamento: 2026-10-28**

- **Questionario da PDF.** Il lato questionario si ricostruisce parsando i PDF compilati con `parse_questionari.py`. Motivo: il passaggio dal PDF ai dati è riproducibile e verificabile.
- **Output AI come arrivano.** La pipeline LLM sui protocolli non si rifà (molte chiamate API). Si usano i suoi output.
- **Benchmark, non statistica ufficiale.** Il confronto è un benchmark sui questionari disponibili. Nessuna inferenza sull'universo. Se il campione non è il totale, si descrive e si confronta con l'universo.
- **Formato lungo.** `gino_pdf_risposte_lungo.csv` è il formato di riferimento. Il largo si deriva da lì.
- **Codice nel nome file.** `questionario_<codice>` e `protocollo_<codice>` condividono il codice regione + progressivo. Serve a collegare le fonti.
- **Spunte per luminosità.** Le immagini delle spunte si riconoscono per dimensione (16 px radio, 26 px checkbox) e luminosità media, perché gli ID oggetto cambiano da PDF a PDF.
- **Microdati fuori da git.** Percorso configurabile con `RETI_MICRODATI`.
