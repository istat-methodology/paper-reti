# Campione per la pubblicazione

**Stato: n = 60, estratto il 2026-10-31 (seed 20261031). File: `campione_pubblicazione_v1.csv`. La quota di enti unanimi da rivedere si decide dopo l'estrazione su 251.**

## A cosa serve
Lo stesso campione serve a due cose: (1) definire prompt congelato, numero di run, soglie di spezzatura e metriche; (2) validare a mano gli enti estratti (revisione e annotazione). Lo stadio 1 gira su tutti i 251 protocolli; il campione è la parte rivista a mano e da cui si stima l'errore.

## Popolazione (frame)
- 251 protocolli, 18 regioni; il testo c'è per tutti. Restano fuori dal frame i 2 protocolli senza testo (044101, 1612): 249 protocolli.
- Nessuna esclusione per lunghezza: i protocolli lunghi si leggono spezzati.
- I 11 protocolli della Toscana usati come pilota (0901–0908, 0910–0912) restano nel frame. Se uno è estratto, è segnato `pilota` e i risultati si riportano anche senza.

## Disegno
- **Strati: regione** (18). Almeno 1 protocollo per regione; il resto in proporzione al numero di protocolli (resti più grandi).
- **Dentro la regione: campionamento sistematico sulla lunghezza** del testo (protocolli ordinati per caratteri, passo fisso, partenza casuale con seed registrato). La lunghezza varia molto: mediana 7.800 caratteri nel Lazio, 39.900 in Lombardia, 20.200 in Piemonte.
- Seed e script: `codice/campione_pubblicazione.py --n 60 --seed 20261031`. L'estrazione si fa una volta e si congela.

## Numerosità: n = 60, allocazione per regione (alternative: 40, 80)
| Regione | Protocolli | n = 40 | n = 60 | n = 80 |
|---|---|---|---|---|
| Lazio | 95 | 10 | 18 | 26 |
| Lombardia | 27 | 4 | 6 | 8 |
| Piemonte | 22 | 3 | 5 | 7 |
| Emilia-Romagna | 15 | 2 | 4 | 5 |
| Puglia | 15 | 2 | 4 | 5 |
| Abruzzo | 13 | 2 | 3 | 4 |
| Calabria | 13 | 2 | 3 | 4 |
| Toscana | 12 | 2 | 3 | 4 |
| Veneto | 9 | 2 | 2 | 3 |
| Trento | 7 | 2 | 2 | 3 |
| Friuli-Venezia Giulia | 5 | 2 | 2 | 2 |
| Marche | 5 | 1 | 2 | 2 |
| Liguria | 3 | 1 | 1 | 1 |
| Bolzano | 3 | 1 | 1 | 2 |
| Basilicata | 2 | 1 | 1 | 1 |
| Sardegna | 1 | 1 | 1 | 1 |
| Umbria | 1 | 1 | 1 | 1 |
| Valle d'Aosta | 1 | 1 | 1 | 1 |
| **Totale** | **249** | **40** | **60** | **80** |

Le 18 unità minime (una per regione) pesano il 45% di n = 40 e il 23% di n = 80.

## Lavoro di revisione (stima dalla Toscana, 5 run)
- Circa 5 enti da rivedere per protocollo: 28 non presenti in tutte le run, 17 dal campione del 10% degli unanimi, 6 possibili doppioni, 5 ruoli instabili (su 11 protocolli).
- La quota di enti unanimi da rivedere (10%) si può decidere dopo l'estrazione su 251, quando si conosce il numero di enti. Con 10% si stima il tasso di errore degli unanimi con ±4 punti, con 25% con ±2.5 (ipotesi: errore intorno al 3%, circa 1.200 enti unanimi in 60 protocolli; da rifare con i dati veri).
- L'annotazione indipendente (elenco degli enti senza vedere quello dell'AI, per misurare i mancanti) è più pesante: si può fare su un sottoinsieme del campione.

## Campione estratto (n = 60)
- Quartili di lunghezza: frame 7.860 / 19.605 / 35.149 caratteri, campione 10.352 / 21.466 / 37.622. 14 protocolli su 60 superano i 40.000 caratteri (frame: 45 su 249): verranno spezzati.
- Contiene il protocollo più lungo (1613, Puglia, 306.622 caratteri), incluso perché non si esclude per lunghezza.
- Protocolli pilota estratti: 0905, 0907, 0911 (tutti e 3 i protocolli della Toscana). Sono marcati `si` nella colonna `pilota`.
