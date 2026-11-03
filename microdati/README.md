# microdati

Questa cartella è ignorata da git (vedi `.gitignore`). Si committa solo questo README.

Per usare i dati da un'altra posizione: `export RETI_MICRODATI=/percorso/microdati`.

## Cartelle
- `gino/`: questionari compilati (`questionario_<codice>.pdf`), CSV prodotti dal parser, Excel delle associazioni regionali
- `protocolli/`: protocolli d'intesa in TXT (`protocollo_<codice>.txt`)
- `protocolli_pdf/`: protocolli in PDF. `protocollo_<codice>.pdf` (251 file, uno per questionario), `_originali/` (zip regionali come sono arrivati), `_estratti/<regione>/` (PDF estratti dagli zip, con il nome originale)
- `rif_anagrafica_v2.xlsx`: anagrafica con nome nuovo e originale di questionari, protocolli TXT e protocolli PDF, regione, metodo di abbinamento
- `ai/`: output della pipeline LLM: `ai_<codice>.json` (uno per questionario) e i due JSON unici di partenza

## Codice dei file
Il codice collega questionario, protocollo e output AI. Regione (2 cifre) + progressivo (2 cifre), per esempio `0101`. Per Bolzano e Trento: regione + codice territoriale (41 o 42) + progressivo, 6 cifre, per esempio `044101`.

## Anagrafica
`rif_anagrafica_v2.xlsx` estende la v1 (eliminata il 2026-11-03) con le colonne `protocollo_pdf_nuovo`, `protocollo_pdf_originale`, `protocollo_pdf_stato` e con i fogli `Pdf_senza_txt` e `Riepilogo` esteso. Fogli: Anagrafica (una riga per questionario), Protocolli_non_usati, Pdf_senza_txt, Riepilogo. Due questionari possono condividere lo stesso protocollo: in quel caso `protocollo_<codice>.txt` e `.pdf` sono una copia (0909 e 0910).
`codice/anagrafica_protocolli.py` genera la v1 (solo TXT) e richiede `protocolli/_originali/<regione>/`, cartella che non c'è più. La v2 è stata prodotta con uno script una tantum e non ha ancora un generatore nel repo.

## Protocolli PDF (2026-11-03)
I 17 zip regionali in `_originali/` contengono 338 PDF.
- 250 PDF sono i protocolli dei 251 questionari (0909 e 0910 condividono quello di Prato). Sono copiati come `protocollo_<codice>.pdf`.
- 85 PDF sono fuori campione: altri documenti caricati dalle regioni (convenzioni, leggi, linee guida, protocolli non collegati a un questionario), soprattutto Toscana e Puglia. Sono nel foglio `Protocolli_non_usati`, colonna `pdf_originale`. Non sono stati rinominati né eliminati: restano in `_estratti/` con il nome originale.
- 3 PDF non hanno un TXT corrispondente: 2 file di prova a Trento/Bolzano (`Test_rta`) e `01_Piemonte/protocollo.PDF`, senza timestamp. Sono nel foglio `Pdf_senza_txt`.

Per 0903 e 0908 il PDF è la versione originale non compressa (la compressione rovinava il file).
I nomi dentro gli zip sono in UTF-8: `unzip` da shell rovina gli accenti, si estrae con Python (`zipfile`).

## Output AI
`ai/ai_<codice>.json` si genera con `codice/ai_split.py` dal JSON unico versione 2.5. L'abbinamento è in `rif_ai_abbinamento_v1.csv`. Dove due questionari condividono un protocollo, i due file sono identici.

## File del parser
- `gino/gino_pdf_risposte_lungo.csv`: una riga per questionario, domanda e voce
- `gino/gino_pdf_risposte_largo.csv`: una riga per questionario

Si rigenerano con `codice/parse_questionari.py`.

## Convenzione nomi
`<tipo>_<contenuto>[_<dettaglio>][_<versione>]`, con tipo = gino / protocollo / ai / confronto.
