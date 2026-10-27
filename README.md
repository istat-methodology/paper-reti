# paper-reti

Paper sulle reti territoriali antiviolenza: come gli strumenti LLM si affiancano alla raccolta tradizionale per indagini nella statistica ufficiale.

Gruppo: Istat, Direzione metodologia (Mauro Bruno, Paolo, Elena). Revisione di *Reti Territoriali extended*, a partire dall'analisi di Paolo.

## Idea

Gli uffici regionali compilano il questionario GINO leggendo i PDF dei protocolli d'intesa. Una pipeline LLM legge gli stessi PDF e estrae le stesse informazioni. Confrontiamo i due risultati a livello micro: unità = protocollo × categoria di soggetto × ruolo.

- **RQ1 – qualità del questionario.** Quanta sovra/sotto-copertura c'è? Dove le definizioni sono ambigue (cos'è un proponente, un attore, un incaricato)?
- **RQ2 – integrazione.** Il PDF può arricchire l'indagine? Prima validazione, poi arricchimento, poi eventuale precompilazione o sostituzione del questionario.

Entrambe le analisi (controllo qualità e integrazione) vanno nel paper. Dettagli della pipeline (geocoding, RUNTS) fuori scopo.

## Dati

251 protocolli abbinati (254 questionari, 253 output AI). Chiave: `ID_RISPONDENTE_RILEV` + `PROGRESSIVO_QUEST`. I microdati non sono nel repo: vedi `microdati/README.md`.

## Cosa c'è stato fatto finora

- Ricalcolo indipendente del Match AI/umano dei colleghi: i numeri tornano.
- Accordo per categoria (30 e 10 gruppi): Jaccard, κ di Cohen, PABAK (il κ inganna con prevalenze alte), sensibilità alla mappatura dei 604 soggetti AI senza categoria.
- **Proponente**: il disaccordo è soprattutto di definizione. La domanda 2.1 non ha definizione; gli umani tendono a segnare chi compare nel testo/firma, l'AI il promotore esplicito.
- **Attori**: accordo buono, migliore nei protocolli grandi.
- **Numerosità (2.2)**: i conteggi AI sono maggiori in 200 protocolli su 251.
- **3.7**: l'AI fonde gestire/monitorare/coordinare; il questionario separa gestione e governance.
- I campi `questionario_*` nell'output AI sono copiati dal questionario, non estratti: l'accordo sui metadati non è evidenza sull'LLM.
- Qualità interna del questionario: codici durata (0/999), scadenze incoerenti, commenti liberi.
- Elenco delle variabili del questionario con modalità: `docs/variabili_questionario_v1.xlsx`.

Numeri e dettagli: `docs/risultati_preliminari.md`. Stato e prossimi passi: `docs/stato.md`.

## Struttura

```
README.md, CLAUDE.md
docs/          stato, decisioni, metodologia, risultati preliminari, variabili
codice/        config.py, common.py, analisi_*.py, pipeline_ai/
riferimenti/   categorie_gino_30.csv (30 categorie → 10 gruppi)
risultati/     output delle analisi (precedenti/ ignorata)
microdati/     NON versionata, tranne README e _fonti.csv
```

## Eseguire

```
export RETI_MICRODATI="/percorso/analisi/microdati"   # opzionale
cd codice && python3 analisi_01_accordo_categorie.py
```

Servono python3, pandas, openpyxl.
