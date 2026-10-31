# Decisioni

**Ultimo aggiornamento: 2026-10-31**

- **Questionario da PDF.** Il lato questionario si ricostruisce parsando i PDF compilati con `parse_questionari.py`. Motivo: il passaggio dal PDF ai dati è riproducibile e verificabile.
- **Output AI come arrivano (superata il 2026-10-30).** Si usavano gli output della pipeline v1. Ora la pipeline si rifà da zero, vedi sotto.
- **Benchmark, non statistica ufficiale.** Il confronto è un benchmark sui questionari disponibili. Nessuna inferenza sull'universo. Se il campione non è il totale, si descrive e si confronta con l'universo.
- **Formato lungo.** `gino_pdf_risposte_lungo.csv` è il formato di riferimento. Il largo si deriva da lì.
- **Codice nel nome file.** `questionario_<codice>` e `protocollo_<codice>` condividono il codice regione + progressivo. Serve a collegare le fonti.
- **Abbinamento questionario–protocollo.** Il timestamp nel nome del file protocollo coincide con la data di ultima modifica del questionario (stessa regione). Dove manca (Toscana, parte della Puglia) si abbina per nome dell'allegato indicato in 3.9. I protocolli si copiano come `protocollo_<codice>.txt`, in una cartella piatta; gli originali restano in `protocolli/_originali/`.
- **Prompt versionati.** `prompts/` è nel repo: non contiene microdati ed è parte del metodo.
- **Un file AI per questionario.** Il JSON unico (versione 2.5) è spezzato in `ai_<codice>.json`. Si usa la 2.5 perché la 2.6 aggiunge un blocco `questionario` copiato dal questionario, che non è output AI. Abbinamento per timestamp nel nome (227 casi) o per nome del file (24).
- **Spunte per luminosità.** Le immagini delle spunte si riconoscono per dimensione (16 px radio, 26 px checkbox) e luminosità media, perché gli ID oggetto cambiano da PDF a PDF.
- **Microdati fuori da git.** Percorso configurabile con `RETI_MICRODATI`.

## Pipeline AI v2 (2026-10-30 / 31)
- **Si riparte da zero.** Prompt, definizioni e validazione per stadi: 1 enti e ruolo, 2 classificazione nelle 30 categorie, 3 validazione manuale, 4 confronto con il questionario (item 2.2; controllo: unione di 2.1, 3.3 e 3.7). Registro: `docs/experiments.md`.
- **Modello e chiamate.** `gpt-6.1-terra` su Azure, Responses API, output JSON con schema; senza seed. Gli script che chiamano il modello li lancia Mauro.
- **Due contenitori.** Nucleo (enti con nome proprio) e periferia (menzioni generiche) si analizzano separatamente. Come contare la periferia è da decidere con i colleghi della produzione.
- **Testo, non PDF.** Il testo dà lo stesso nucleo del PDF a un quarto dei token. Il PDF resta per le scansioni senza testo (solo 2 protocolli su 251 hanno meno di 100 caratteri).
- **Prompt candidato: v1.2.** Il più stabile; le eccezioni non si aggiungono al prompt ma alla revisione manuale.
- **Protocolli lunghi.** Sopra 40.000 caratteri il testo si spezza in pezzi da circa 25.000 (2.000 di sovrapposizione, ultimi 5.000 caratteri in ogni pezzo) e gli elenchi si fondono. Provato su 0902 e 0911.
- **5 run per protocollo.** Sul nucleo, 5 run coprono il 99.5% degli enti visti in 10. La periferia non converge: si registra la frequenza.
- **Revisione manuale.** Si rivedono gli enti non presenti in tutte le run, i ruoli instabili, i possibili doppioni e un campione dei presenti in tutte le run. Le decisioni sono una tabella (`revisione/`), applicata da `revisione_enti.py applica`.
- **Stadio 1 su tutti i 251 testi; revisione e annotazione su un campione.**
- **Campione v1 superato (2026-10-31).** Aveva assunto la Toscana come set di sviluppo e inserita per intero: arbitrario per un paper. Il nuovo campione è stratificato per regione e, in ogni regione, sulla lunghezza del protocollo; è lo stesso campione per definire prompt, run e metriche e per la validazione manuale. Numerosità decisa il 2026-10-31: **n = 60**, estratto con seed 20261031 (`campione/campione_pubblicazione_v1.csv`). La quota di enti unanimi da rivedere si decide dopo l'estrazione su 251.
- **Repo riordinata (2026-10-31).** Pipeline v1, campione v1 e relativi fogli in `archivio/`.
