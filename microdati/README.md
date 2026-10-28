# microdati

Questa cartella è ignorata da git (vedi `.gitignore`). Si committa solo questo README.

Per usare i dati da un'altra posizione: `export RETI_MICRODATI=/percorso/microdati`.

## Cartelle
- `gino/`: questionari compilati (`questionario_<codice>.pdf`), CSV prodotti dal parser, Excel delle associazioni regionali
- `protocolli/`: protocolli d'intesa in TXT (`protocollo_<codice>.txt`); gli originali, divisi per regione, stanno in `protocolli/_originali/`
- `rif_anagrafica_v1.xlsx`: anagrafica con nome nuovo e originale di questionari e protocolli, regione, metodo di abbinamento
- `ai/`: output della pipeline LLM sui protocolli

## Codice dei file
Il codice collega questionario, protocollo e output AI. Regione (2 cifre) + progressivo (2 cifre), per esempio `0101`. Per Bolzano e Trento: regione + codice territoriale (41 o 42) + progressivo, 6 cifre, per esempio `044101`.

## Anagrafica
`rif_anagrafica_v1.xlsx` (si rigenera con `codice/anagrafica_protocolli.py`). Fogli: Anagrafica (una riga per questionario), Protocolli_non_usati, Riepilogo. Due questionari possono condividere lo stesso protocollo: in quel caso `protocollo_<codice>.txt` è una copia.

## File del parser
- `gino/gino_pdf_risposte_lungo.csv`: una riga per questionario, domanda e voce
- `gino/gino_pdf_risposte_largo.csv`: una riga per questionario

Si rigenerano con `codice/parse_questionari.py`.

## Convenzione nomi
`<tipo>_<contenuto>[_<dettaglio>][_<versione>]`, con tipo = gino / protocollo / ai / confronto.
