# Campione per la pubblicazione

**Stato: n = 60 estratto il 2026-10-31 (seed 20261031, `campione_pubblicazione_v1.csv`); dal 2026-11-02 vale la v2, n = 58 (`campione_pubblicazione_v2.csv`): fuori ambito, copie e rimpiazzi, vedi sezione in fondo. La quota di enti unanimi da rivedere si decide dopo l'estrazione su 249.**

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
- La quota di enti unanimi da rivedere (10%) si può decidere dopo l'estrazione su 249, quando si conosce il numero di enti. Con 10% si stima il tasso di errore degli unanimi con ±4 punti, con 25% con ±2.5 (ipotesi: errore intorno al 3%, circa 1.200 enti unanimi in 60 protocolli; da rifare con i dati veri).
- L'annotazione indipendente (elenco degli enti senza vedere quello dell'AI, per misurare i mancanti) è più pesante: si può fare su un sottoinsieme del campione.

## Campione estratto (n = 60)
- Quartili di lunghezza: frame 7.860 / 19.605 / 35.149 caratteri, campione 10.352 / 21.466 / 37.622. 14 protocolli su 60 superano i 40.000 caratteri (frame: 45 su 249): verranno spezzati.
- Contiene il protocollo più lungo (1613, Puglia, 306.622 caratteri), incluso perché non si esclude per lunghezza.
- Protocolli pilota estratti: 0905, 0907, 0911 (tutti e 3 i protocolli della Toscana). Sono marcati `si` nella colonna `pilota`.

## Sottoinsieme gold (n = 20)
- **Disegno.** Dai 60 si escludono i 3 pilota (il prompt è stato messo a punto su quelli) e i protocolli oltre 100.000 caratteri (onere di annotazione): restano 54. Ordinati per regione e lunghezza, 20 protocolli con campionamento sistematico e partenza casuale, seed 20261101. File: `campione_gold_v1.csv`; script: `codice/campione_gold.py`.
- **Doppia annotazione.** 8 dei 20 (colonna `doppia`, campionamento sistematico) sono annotati da due persone.
- **Limite.** I protocolli molto lunghi (oltre 100.000 caratteri) non sono nel gold. Il più lungo del gold ha circa 56.000 caratteri; 6 superano i 40.000 e sono spezzati dalla pipeline.
- **Fase 2.** I restanti 38 protocolli del campione v2 (58 meno i 20 del gold) (inclusi i 3 pilota e quelli molto lunghi) sono il campione della revisione delle incoerenze interne del modello.

## Revisione del frame e campione v2 (2026-11-02)
- **Frame v2: 240 documenti.** Dai 249 file con testo si tolgono 4 file fuori ambito (1701, 1702, 0201, 044103) e 5 copie (1258, 1261, 0326, 1306, 0909). Motivi in `frame_esclusioni_v1.csv`. L'unità è il documento.
- **Campione v2: n = 58.** Le unità tolte (1702, 0201, 044103) si rimpiazzano nello stesso strato con il documento non estratto di lunghezza più vicina. Rimpiazzo solo per 044103 (→ 044102, Bolzano). Basilicata e Valle d'Aosta non hanno altri documenti: n = 58 e 16 regioni. `rango_lunghezza` è ricalcolato sul frame v2. Script: `codice/campione_sostituzioni.py`.
- **Pesi.** Le dimensioni degli strati cambiano: Lazio 93 (era 95), Lombardia 26, Abruzzo 12, Toscana 11, Bolzano 2, Basilicata e Valle d'Aosta 0. Il peso di uno strato è N/n con il nuovo N.
- **Gold v2.** 044103 era nel gold. Niente tedesco nel gold: lo sostituisce 1210 (Lazio), l'unità di campione idonea più vicina per lunghezza (`campione_gold_v2.csv`). Nuovo criterio di idoneità, oltre a non pilota e fino a 100.000 caratteri: testo non in tedesco. Il pacchetto di annotazione va rigenerato. 044102 resta nel campione (fase 2, deciso il 2026-11-02); è in tedesco, 044104 è bilingue.
- **Pilota.** Resta 0910 (non 0909) come copia del documento di Prato.
- Il campione v1 e il gold v1 restano in repo come riferimento e non vanno usati per le stime.
