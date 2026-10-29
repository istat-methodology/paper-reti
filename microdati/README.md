# microdati

Questa cartella è ignorata da git (vedi `.gitignore`). Si committa solo questo README.

Per usare i dati da un'altra posizione: `export RETI_MICRODATI=/percorso/microdati`.

## Cartelle
- `gino/`: questionari compilati (`questionario_<codice>.pdf`), CSV prodotti dal parser, Excel delle associazioni regionali
- `protocolli/`: protocolli d'intesa in TXT (`protocollo_<codice>.txt`)
- `rif_anagrafica_v1.xlsx`: anagrafica con nome nuovo e originale di questionari e protocolli, regione, metodo di abbinamento
- `ai/`: output della pipeline LLM: `ai_<codice>.json` (uno per questionario) e i due JSON unici di partenza

## Codice dei file
Il codice collega questionario, protocollo e output AI. Regione (2 cifre) + progressivo (2 cifre), per esempio `0101`. Per Bolzano e Trento: regione + codice territoriale (41 o 42) + progressivo, 6 cifre, per esempio `044101`.

## Anagrafica
`rif_anagrafica_v1.xlsx` (si rigenera con `codice/anagrafica_protocolli.py`, che richiede i file originali dei protocolli in `protocolli/_originali/<regione>/`). Fogli: Anagrafica (una riga per questionario), Protocolli_non_usati, Riepilogo. Due questionari possono condividere lo stesso protocollo: in quel caso `protocollo_<codice>.txt` è una copia.

## Output AI
`ai/ai_<codice>.json` si genera con `codice/ai_split.py` dal JSON unico versione 2.5. L'abbinamento è in `rif_ai_abbinamento_v1.csv`. Dove due questionari condividono un protocollo, i due file sono identici.

## File del parser
- `gino/gino_pdf_risposte_lungo.csv`: una riga per questionario, domanda e voce
- `gino/gino_pdf_risposte_largo.csv`: una riga per questionario

Si rigenerano con `codice/parse_questionari.py`.

## Convenzione nomi
`<tipo>_<contenuto>[_<dettaglio>][_<versione>]`, con tipo = gino / protocollo / ai / confronto.
