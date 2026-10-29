# paper-reti

Paper sulle reti territoriali antiviolenza: come gli strumenti LLM si affiancano alla raccolta tradizionale per indagini nella statistica ufficiale.

Istat, Direzione metodologica.

## Idea

Gli uffici regionali compilano il questionario GINO leggendo i protocolli d'intesa delle reti territoriali. Una pipeline LLM legge gli stessi protocolli ed estrae le stesse informazioni. Confrontiamo i due risultati a livello micro: la fonte è la stessa, cambia chi la legge.

- **RQ1 – qualità del questionario.** Quanta sovra/sotto-copertura c'è rispetto al protocollo? Dove le definizioni sono ambigue (proponente, attore, incaricato)? Parte del disaccordo dipende da come le domande sono formulate, non dagli errori di chi risponde.
- **RQ2 – integrazione.** Il protocollo può arricchire l'indagine? Prima validazione, poi arricchimento, poi eventuale precompilazione o sostituzione del questionario.

Il paper contiene sia il controllo di qualità sia l'integrazione.

## Le tre fonti

Tutte collegate dallo stesso codice (regione + progressivo, per esempio `0101`; 6 cifre per Bolzano e Trento).

| Fonte | File | Come si ottiene |
|---|---|---|
| Questionario GINO | `questionario_<codice>.pdf` → CSV | `codice/parse_questionari.py` legge i 251 PDF compilati |
| Protocollo | `protocollo_<codice>.txt` | testo del documento da cui si compila il questionario |
| Output AI | `ai_<codice>.json` | pipeline LLM sul protocollo (prompt in `prompts/`), spezzata con `codice/ai_split.py` |

```
protocollo ──► questionario compilato (PDF) ──► parser ──► CSV
    │
    └────────► pipeline LLM (prompts/) ───────► JSON ───► ai_<codice>.json
                                                           │
                                  confronto micro  ◄───────┘
```

Il confronto copre le domande sui soggetti (2.1, 2.2, 3.3, 3.7): l'output AI attuale non contiene date, natura dell'accordo, durata né obiettivi. L'anagrafica `microdati/rif_anagrafica_v1.xlsx` elenca nomi nuovi e originali.

I microdati non sono nel repo: vedi `microdati/README.md`.

## Struttura

```
README.md, CLAUDE.md
docs/          stato, decisioni, metodologia
prompts/       prompt della pipeline LLM (versionati)
codice/        config.py, parse_questionari.py, anagrafica_protocolli.py, ai_split.py, pipeline_ai/
riferimenti/   categorie_gino_30.csv (30 categorie di soggetti → 10 gruppi)
microdati/     non versionata, tranne il README
output/        analisi aggregate preesistenti, non versionata, non usata per ora
```

## Eseguire

```
export RETI_MICRODATI="/percorso/microdati"    # opzionale, default: <repo>/microdati
cd codice
python3 parse_questionari.py       # PDF questionari -> CSV (lungo e largo), ~95 s
python3 anagrafica_protocolli.py   # anagrafica e copie dei protocolli (richiede gli originali)
python3 ai_split.py                # JSON AI unico -> ai_<codice>.json
```

Servono python3, pandas, openpyxl, numpy, Pillow, pdfplumber.

## Documenti

- `docs/stato.md`: stato, prossimi passi, domande aperte
- `docs/decisioni.md`: scelte fatte e motivi
- `docs/metodologia.md`: fonti, prompt, corrispondenza domande–AI, disegno del confronto
