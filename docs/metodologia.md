# Metodologia

## Fonti
- **Questionario GINO.** Compilato dagli uffici regionali a partire dal protocollo. Sezioni: 1 identificativi (1.1 titolo, 1.2 ambito), 2 caratteristiche (2.1 soggetto proponente, 2.2 tipologia e numerosità), 3 natura e obiettivi (3.1 data, 3.2 natura, 3.3 attori, 3.4 obiettivi strategici, 3.5 obiettivi operativi, 3.6 durata, 3.7 incaricato di gestire/monitorare/coordinare, 3.8 monitoraggio, 3.9 allegato), 4 prassi regionale (4.1, 4.2).
- **Protocollo.** Il documento (TXT o PDF) da cui si compila il questionario.
- **Output AI.** Variabili estratte dai protocolli da una pipeline LLM.

## Parsing dei questionari
`codice/parse_questionari.py`. Il layout dei PDF è identico. Le spunte sono immagini (vuota o piena). Ogni voce è ancorata a una riga di testo; la spunta si legge dall'immagine nel blocco della voce. Le domande 2.1, 2.2, 3.3 e 3.7 hanno 30 categorie di soggetti (`riferimenti/categorie_gino_30.csv`). Lo script si ferma con un errore se una voce non si ancora o manca una spunta.

Formato lungo, una riga per questionario, domanda e voce:
- `file`: nome del PDF
- `domanda`: numero (`0` = intestazione)
- `voce`: opzione o categoria (`01`…`30`), o nome del campo di testo
- `etichetta`: testo della voce
- `selezionato`: 1/0, vuoto per i campi di testo e per 2.2
- `commento`, `numerosita`, `testo`: contenuti liberi

## Disegno del confronto (da confermare)
- Unità: questionario × categoria × ruolo (proponente, attore), più le altre variabili (date, natura, obiettivi).
- Metriche: accordo (entrambi, solo questionario, solo AI), Jaccard, κ di Cohen, PABAK. Con prevalenze basse il κ da solo non basta.
- Il disaccordo mescola errori e differenze di definizione. Nessuno dei due lati è la verità: serve un audit su un campione stratificato di protocolli letti a mano.

## Limiti noti del parser
- Alcuni apostrofi sono già `?` nel PDF.
- Testi lunghi (titolo) possono essere tagliati dal layout.
- Un'immagine di spunta con luminosità diversa da quelle note ferma lo script.
