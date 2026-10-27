# Decisioni

- Unità di confronto: protocollo × categoria (30) × ruolo (Proponente, Attore).
- Ruoli AI: proponente = `soggetto_proponente`, attore = `attore`.
- Mappatura base: i 604 soggetti AI senza categoria sono esclusi. Mappatura alt (provvisoria, da validare): ODV/APS/imprese sociali/altri ETS/enti filantropici → 24; Unione dei Comuni → 3; Centri/Sportelli di ascolto → 1; Consorzi → 30. Si riportano sempre entrambe.
- Metriche: Jaccard, κ, PABAK. κ da solo non basta.
- Niente gold standard: serve un audit sui PDF.
- Microdati fuori da git; percorso configurabile con `RETI_MICRODATI`.

## 2026-10-27 – nuovo impianto
- Il lato questionario si ricostruisce dai PDF compilati con `parse_questionari.py`. Motivo: le trasformazioni dei colleghi non sono riproducibili né difendibili.
- Il lato AI non si rifà (costo di molte chiamate API): si usano i risultati di Paolo.
- Il CSV dei colleghi serve solo da controllo incrociato.
- Il campione, se non è il totale, è un benchmark di convenienza: si descrive e si confronta con l'universo. Nessuna inferenza di statistica ufficiale.
- Chiave candidata per l'abbinamento: nome del file caricato (campo 3.9).
- L'Excel delle variabili va rifatto per domanda, partendo dal PDF del questionario.
