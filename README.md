# paper-reti

Paper sulle reti territoriali antiviolenza: come gli strumenti LLM si affiancano alla raccolta tradizionale per indagini nella statistica ufficiale.

Istat, Direzione metodologica.

## Idea

In un'indagine tradizionale come il monitoraggio delle reti, il questionario GINO riporta in forma strutturata il contenuto di un protocollo d'intesa. Il protocollo è un PDF senza struttura standard, difficile da analizzare. Gli uffici regionali lo leggono e compilano il questionario. Una pipeline LLM legge gli stessi protocolli. La fonte è la stessa, cambia chi la legge.

Il messaggio del paper: nella statistica ufficiale gli strumenti AI integrano gli strumenti tradizionali di raccolta dati. Il lavoro ha due parti.

**Parte A – si possono usare strumenti AI in un processo di produzione statistica, in particolare nella fase di raccolta dati?**
- **RQ0.** Un'estrazione AI dai protocolli è abbastanza affidabile da essere usata nella raccolta dati? La risposta è l'esperimento: definizione dei prompt, più run per protocollo, estrazione di un campione, gold standard annotato a mano, confronto, stime con errore noto. Per quanto ne sappiamo, in statistica ufficiale è la prima volta che un esperimento di questo tipo viene fatto per intero (claim da verificare in letteratura).
- La pipeline estrae gli enti di ogni protocollo, con ruolo nel documento (`firmatario`, `componente_rete`, `solo_citato`) e categoria (30 modalità). Le stime riguardano `firmatario` e `componente_rete`; i `solo_citato` si riportano a parte; le menzioni generiche non entrano nelle stime e servono a valutare l'estrazione. La parte A non usa il questionario né i suoi ruoli.

**Parte B – l'indagine è già stata condotta ed è online. Come si colloca l'output AI rispetto al questionario?**
- **RQ1 – confrontabilità e cause delle differenze.** L'output AI è confrontabile con il questionario? In alcuni casi sì, in altri no. Le differenze si spiegano in modo quantitativo con due cause: i fattori legati ai compilatori (competenza, lettura del protocollo) e l'aspetto definitorio (proponente, attore, incaricato; definizioni ambigue). Il secondo è il più importante e va trattato con cautela: le differenze di definizione sono una proprietà delle domande, non errori dei rispondenti. Include la sovra/sotto-copertura rispetto al protocollo e il confronto per categoria (30 modalità).
- **RQ2 – integrazione.** Il protocollo può arricchire l'indagine? Prima validazione, poi arricchimento, poi eventuale precompilazione o sostituzione del questionario.

La parte B si articola in due livelli. B1 confronta gli insiemi di enti (item 2.2, con controllo sull'unione di 2.1, 3.3 e 3.7) e non richiede di definire i ruoli del questionario. B2 confronta per proponente, attore e incaricato ed è condizionato alle definizioni dei colleghi che hanno costruito il questionario.

## Le tre fonti

Tutte collegate dallo stesso codice (regione + progressivo, per esempio `0101`; 6 cifre per Bolzano e Trento).

| Fonte | File | Come si ottiene |
|---|---|---|
| Questionario GINO | `questionario_<codice>.pdf` → CSV | `codice/parse_questionari.py` legge i 251 PDF compilati |
| Protocollo | `protocollo_<codice>.txt` | testo del documento da cui si compila il questionario |
| Output AI | `ai_<codice>.json` (pipeline v1, archiviata) · `microdati/ai_v2/` (pipeline v2) | pipeline LLM sul protocollo; la v2 è rifatta da zero, vedi `docs/experiments.md` |

```
protocollo ──► questionario compilato (PDF) ──► parser ──► CSV
    │
    └────────► pipeline LLM (prompts/) ───────► JSON ───► ai_<codice>.json
                                                           │
                                  confronto micro  ◄───────┘
```

Il confronto copre le domande sui soggetti (2.1, 2.2, 3.3, 3.7): l'output AI attuale non contiene date, natura dell'accordo, durata né obiettivi. L'anagrafica `microdati/rif_anagrafica_v1.xlsx` elenca nomi nuovi e originali.

I microdati non sono nel repo: vedi `microdati/README.md`.

## Ambiente

```
python3 -m venv .venv
source .venv/bin/activate        # su Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # poi inserire chiave, endpoint e deployment
python codice/test_api.py        # prova la connessione al modello
```

`.venv/` e `.env` sono ignorati da git: la chiave non va mai committata.

## Struttura

```
README.md, CLAUDE.md
docs/             stato, decisioni, metodologia, definizioni, ipotesi di lavoro, registro esperimenti (experiments.md), pipeline e stime (pipeline_e_stime.md)
prompts/          prompt versionati: v1/ (pipeline archiviata), v2/ (pipeline attuale, v1_2 = candidato al congelamento)
parametri/        parametri_pubblicazione.json: modello, prompt, n. run, soglie di spezzatura, campione
campione/         campione per la pubblicazione (v2: 58 documenti), gold v2, frame_esclusioni_v1.csv (fuori ambito e copie)
codice/           config.py, parse_questionari.py, anagrafica_protocolli.py, confronto_*.py, test_api.py
codice/pipeline_ai_v2/   stadio 1 (estrazione, spezzatura), stabilità, revisione, misure, registro esperimenti
revisione/        fogli di revisione degli enti e decisioni (con nomi di enti: si possono committare)
annotazione/      gold standard: sottoinsieme di 20 protocolli annotati da zero (gold_v2); fogli del primo campione (gold_v1_legacy)
risultati/        tabelle e figure per il paper, generate da script
riferimenti/      categorie_gino_30.csv (30 categorie di soggetti → 10 gruppi), documento Istat
archivio/         pipeline v1 e script del primo campione: non si usano
microdati/        non versionata, tranne il README
output/           analisi aggregate preesistenti, non versionata, non usata per ora
```

## Eseguire

```
export RETI_MICRODATI="/percorso/microdati"    # opzionale, default: <repo>/microdati
cd codice
python3 parse_questionari.py       # PDF questionari -> CSV (lungo e largo), ~95 s
python3 anagrafica_protocolli.py   # anagrafica e copie dei protocolli (richiede gli originali)
python3 ai_split.py                # (archivio/pipeline_v1) JSON AI unico -> ai_<codice>.json
```

Servono python3, pandas, openpyxl, numpy, Pillow, pdfplumber.

## Documenti

- `docs/stato.md`: stato, prossimi passi, domande aperte
- `docs/decisioni.md`: scelte fatte e motivi
- `docs/metodologia.md`: fonti, prompt, corrispondenza domande–AI, disegno del confronto
- `docs/pipeline_e_stime.md`: come run completa, campione e gold diventano stime
