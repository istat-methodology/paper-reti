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
- **Campione per la pubblicazione (2026-10-31).** Il primo campione (36 protocolli: Toscana per intero più altri 25, scelti senza un disegno probabilistico) non è adatto a fare stime nel paper. Il nuovo campione è stratificato per regione e, in ogni regione, sulla lunghezza del protocollo. Numerosità: **n = 60**, seed 20261031 (`campione/campione_pubblicazione_v1.csv`). Si usa per definire prompt, run e metriche e per la validazione. La quota di enti unanimi da rivedere si decide dopo l'estrazione su 251.
- **Gold standard (2026-11-01).** Il questionario non entra in questa fase. Il gold è un sottoinsieme estratto a caso dai 60: 20 protocolli, esclusi i 3 pilota (usati per mettere a punto il prompt) e i protocolli oltre 100.000 caratteri (onere di annotazione; limite da dichiarare). Campionamento sistematico per regione e lunghezza, seed 20261101 (`campione/campione_gold_v1.csv`, `codice/campione_gold.py`). Annotazione manuale **da zero**, senza vedere output di modelli, di enti e di menzioni generiche (la periferia serve: ospedali, polizia municipale, prefettura). Annotatore principale Paolo su tutti i 20; 8 protocolli (`doppia=si`) li annota anche un secondo annotatore (Elena, se disponibile, altrimenti Mauro). Template: `annotazione/gold_v2/gold_enti_v3_template.xlsx`.
- **Due fasi di validazione (2026-11-01).** Fase 1: gold da zero sui 20 protocolli; misura recall e precision dello stadio 1, accordo tra annotatori, verità per lo stadio 2 (30 categorie). Fase 2: revisione delle incoerenze interne del modello (non unanimi, ruoli instabili, doppioni, quota di unanimi) sui restanti 40 protocolli del campione, non sui 20 del gold (310 righe di revisione sui 40 protocolli, 7,8 per protocollo; il campione del 10% degli unanimi è estratto di nuovo).
- **Vecchio gold (set di sviluppo).** I fogli del primo campione, pre-compilati con l'output della pipeline v1 (gpt-4.1), sono in `annotazione/gold_v1_legacy/`. Non sono indipendenti (l'annotatore parte da una lista del modello) e non sono un campione probabilistico: servono come materiale di sviluppo e per un controllo secondario, dichiarati come tali. Cinque protocolli (044103, 1265, 1104, 1605, 1001) sono anche nel nuovo gold e si riannotano da zero.
- **Repo riordinata (2026-10-31).** Pipeline v1 e script del campione v1 in `archivio/`; fogli e campione v1 in `annotazione/gold_v1_legacy/`.
