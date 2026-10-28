# paper-reti

Paper sulle reti territoriali antiviolenza: come gli strumenti LLM si affiancano alla raccolta tradizionale per indagini nella statistica ufficiale.

Istat, Direzione metodologica.

## Idea

Gli uffici regionali compilano il questionario GINO leggendo i protocolli d'intesa delle reti territoriali. Una pipeline LLM legge gli stessi protocolli ed estrae le stesse informazioni. Confrontiamo i due risultati a livello micro.

- **RQ1 – qualità del questionario.** Quanta sovra/sotto-copertura c'è rispetto al protocollo? Dove le definizioni sono ambigue (cos'è un proponente, un attore, un incaricato)?
- **RQ2 – integrazione.** Il protocollo può arricchire l'indagine? Prima validazione, poi arricchimento, poi eventuale precompilazione o sostituzione del questionario.

Il paper contiene sia il controllo di qualità sia l'integrazione. Pipeline di estrazione (geocoding, RUNTS) fuori scopo.

## Dati

Tre fonti, tutte fuori da git (vedi `microdati/README.md`):

1. **Questionari GINO**: 251 PDF compilati, layout identico. `codice/parse_questionari.py` li converte in CSV.
2. **Protocolli**: i documenti (TXT o PDF) da cui si compila il questionario.
3. **Output AI**: le variabili che la pipeline LLM estrae dai protocolli.

Il codice nel nome del file (`questionario_0101.pdf`, `protocollo_0101.*`) collega le tre fonti.

## Struttura

```
README.md, CLAUDE.md
docs/          stato, decisioni, metodologia
codice/        config.py, parse_questionari.py, pipeline_ai/ (script di estrazione LLM, riferimento)
riferimenti/   categorie_gino_30.csv (30 categorie di soggetti → 10 gruppi)
microdati/     non versionata, tranne il README
```

## Eseguire

```
export RETI_MICRODATI="/percorso/microdati"    # opzionale, default: <repo>/microdati
cd codice && python3 parse_questionari.py
```

Legge `microdati/gino/questionario*.pdf` e scrive `gino_pdf_risposte_lungo.csv` e `gino_pdf_risposte_largo.csv` nella stessa cartella (circa 95 secondi per 251 questionari). Servono python3, pandas, pdfplumber, numpy, Pillow.

## Stato

`docs/stato.md` ha lo stato e i prossimi passi. `docs/decisioni.md` ha le scelte fatte. `docs/metodologia.md` descrive i dati e il disegno del confronto.
