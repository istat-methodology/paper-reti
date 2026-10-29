# Metodologia

## Le tre fonti
1. **Questionario GINO**, compilato dagli uffici regionali leggendo il protocollo. Sezioni: 1 identificativi (1.1 titolo, 1.2 ambito), 2 caratteristiche (2.1 soggetto proponente, 2.2 tipologia e numerosità dei soggetti), 3 natura e obiettivi (3.1 data, 3.2 natura, 3.3 attori coinvolti, 3.4 obiettivi strategici, 3.5 obiettivi operativi, 3.6 durata, 3.7 incaricato di gestire/monitorare/coordinare, 3.8 monitoraggio, 3.9 allegato), 4 prassi regionale (4.1, 4.2).
2. **Protocollo** (TXT): il documento da cui si compila il questionario e su cui lavora la pipeline.
3. **Output AI**: estrazione LLM dal protocollo, un JSON per protocollo.

Il codice nel nome del file (regione + progressivo) collega le tre fonti.

## Parsing dei questionari
`codice/parse_questionari.py`. Il layout dei PDF è identico. Le spunte sono immagini (vuota o piena), riconosciute per dimensione e luminosità. Ogni voce è ancorata a una riga di testo; la spunta si legge dall'immagine nel blocco della voce. Le domande 2.1, 2.2, 3.3 e 3.7 hanno 30 categorie di soggetti (`riferimenti/categorie_gino_30.csv`). Lo script si ferma con un errore se una voce non si ancora o manca una spunta.

Formato lungo, una riga per questionario, domanda e voce:
- `file`: nome del PDF
- `domanda`: numero (`0` = intestazione)
- `voce`: opzione o categoria (`01`…`30`), o nome del campo di testo
- `etichetta`: testo della voce
- `selezionato`: 1/0, vuoto per i campi di testo e per 2.2
- `commento`, `numerosita`, `testo`: contenuti liberi

## Pipeline AI e prompt
I prompt sono in `prompts/prompt_protocolli.txt`. La pipeline procede in quattro passi su ogni protocollo. I passi 2–4 ricevono il testo e la lista dei soggetti del passo 1, e possono scegliere solo tra quelli.

| Passo | Campo nel JSON | Definizione nel prompt |
|---|---|---|
| 1 | `firmatari` | enti che sottoscrivono formalmente il protocollo |
| 1 | `soggetti` | tutti gli enti citati nel testo, qualunque sia il ruolo; ognuno con nome, tipo (vocabolario chiuso), comune, indirizzo, capofila, note |
| 2 | `soggetti_proponenti` | enti che promuovono, avviano o danno impulso al protocollo. Firmatari, capofila, coordinatori e partecipanti non sono proponenti per default. Se non è esplicito: vuoto |
| 3 | `attori_coinvolti` | enti che partecipano operativamente alla rete (servizi, supporto, interventi, presa in carico). Possono includere i proponenti. Esclusi enti citati solo in contesto normativo o una sola volta senza ruolo. Se non è chiaro: escluso |
| 4 | `coordinatori`, `soggetti_monitoraggio`, `cabina_regia`, `tavolo_di_coordinamento` | enti che coordinano, monitorano o verificano, o sono indicati come parte della cabina di regia o del tavolo. Se non è esplicito: vuoto |

Il vocabolario del tipo coincide con le 30 categorie del questionario, con tre differenze: c'è "Centri/Sportelli di ascolto", "Altri ordini professionali" non ha l'elenco tra parentesi e il prompt non prevede "Unione dei Comuni" né le categorie di terzo settore del RUNTS (ODV, APS, imprese sociali).

Dopo il passo 1 il JSON contiene un arricchimento deterministico, non LLM: abbinamento alla lista dei CAV, abbinamento al RUNTS (che può cambiare il tipo: nei 251 file lo ha cambiato per 309 soggetti su 5.860, di cui 259 dal RUNTS e 50 dalla lista CAV), codici geografici. Il campo `ruolo` di ogni soggetto riassume i passi.

## Corrispondenza domande–AI

| Domanda | Questionario | AI | Nota |
|---|---|---|---|
| 2.1 | soggetto proponente, 30 categorie, spunta + commento | `soggetti_proponenti` | il questionario non definisce "proponente"; il prompt sì (promotore esplicito) e per sicurezza restituisce vuoto nel dubbio |
| 2.2 | tipologia e numerosità, per categoria | conteggio di `soggetti` per tipo (e di `firmatari`) | `soggetti` contiene tutti gli enti citati, non solo i membri della rete: confronto da definire |
| 3.3 | attori coinvolti, 30 categorie | `attori_coinvolti` | il questionario non definisce "attore"; il prompt esclude gli enti senza ruolo operativo |
| 3.7 | soggetto incaricato di gestire/monitorare/coordinare | `coordinatori`, `soggetti_monitoraggio` (e `cabina_regia`, `tavolo_di_coordinamento`) | il questionario unisce tre funzioni; il prompt le separa |
| 3.8 | presenza di monitoraggio (SI/NO/NON SO) | indiretto: `soggetti_monitoraggio` non vuoto | da verificare |
| 1.1, 1.2, 3.1, 3.2, 3.4–3.6, 3.9, 4.x | vari | non presenti nell'output attuale | in attesa dei nuovi script |

I firmatari non hanno una domanda nel questionario, ma servono: è probabile che chi compila 2.1 segni anche chi firma.

## Disegno del confronto (da confermare)
- Unità: questionario × categoria × ruolo (proponente, attore, incaricato), a livello di presenza della categoria. Poi, dove possibile, a livello di nome del soggetto e di numerosità.
- Metriche: accordo (entrambi, solo questionario, solo AI), Jaccard, κ di Cohen, PABAK. Con prevalenze basse il κ da solo non basta.
- Il disaccordo mescola tre cose: errori di compilazione, errori dell'AI, differenze di definizione tra domanda e prompt. Nessuno dei due lati è la verità: serve un audit su un campione stratificato di protocolli letti a mano.
- Lettura dei prompt: le istruzioni di prudenza ("meglio vuoto che sbagliato", "se non è chiaro: escludi") rendono l'AI più restrittiva su proponenti e attori. Il confronto va letto tenendone conto.

## Limiti noti
- Parser: alcuni apostrofi sono già `?` nel PDF; i testi lunghi (titolo) possono essere tagliati dal layout; un'immagine di spunta con luminosità diversa da quelle note ferma lo script.
- Abbinamento: per 1701 e 1702 (stesso nome file) l'abbinamento si basa sul timestamp; i due documenti sono quasi certamente identici.
- Pipeline: errori del passo 1 si propagano ai passi 2–4, che scelgono solo tra i soggetti estratti.
