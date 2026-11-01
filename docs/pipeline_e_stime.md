# Pipeline e stime

Aggiornato: 2026-11-01. Spiega come la run sui 251 protocolli, il campione di 60 e il gold standard si combinano nelle stime. Il questionario non entra fino allo stadio 4.

## Idea
La run sui 251 protocolli è un censimento con errore di misura. Il campione serve a misurare quell'errore. Le stime sono le liste della run, corrette con i tassi di errore del campione.

## Schema

```
POPOLAZIONE: 249 protocolli
   │
   ├─► RUN (stadio 1 + stadio 2) su tutti i protocolli, 5 run ........ liste grezze
   │      nucleo (enti con nome) + periferia (menzioni generiche), ruolo, categoria, frequenza tra run
   │
   └─► CAMPIONE n = 60 (stratificato per regione e lunghezza)
          │
          ├─► GOLD, 20 protocolli (estratti dai 60; esclusi pilota e > 100.000 caratteri)
          │      annotazione manuale da zero ............................ VERITÀ
          │      → recall, precision, accordo tra annotatori, categorie (verità stadio 2)
          │
          └─► FASE 2, 40 protocolli (gli altri del campione)
                 revisione delle incoerenze del modello ................. PRECISION
                 (enti non unanimi, ruoli instabili, doppioni, quota di unanimi)

TASSI DI ERRORE (con pesi di campionamento, intervalli per protocollo)
   precision: gold + fase 2 (60 protocolli)
   recall:    solo gold (20 protocolli)
   per classe: nucleo/periferia, ruolo, categoria, fascia di lunghezza
          │
          ▼
STIMA sui 249 protocolli = liste della run corrette con i tassi
          │
          ▼
STADIO 4: confronto con il questionario (item 2.2; controllo con 2.1, 3.3, 3.7)
```

## Ruolo dei tre insiemi
| Insieme | Protocolli | Cosa fornisce | Cosa non fornisce |
|---|---|---|---|
| Run completa | 249 | liste grezze per tutta la popolazione | misura dell'errore |
| Gold | 20 | verità: recall, precision, accordo, categorie | stime su protocolli molto lunghi |
| Fase 2 | 40 | precision di nucleo e ruoli | recall (il revisore parte dalla lista del modello) |

## Stima
1. Per ogni classe (nucleo, periferia, ruolo, categoria, fascia di lunghezza) si calcolano precision e recall sul campione, con pesi pari all'inverso della probabilità di estrazione.
2. Stimatore di base: rapporto tra enti veri (gold) ed enti del modello, applicato al totale dei 249. Se il gold mostra che la recall dipende dalla lunghezza, il rapporto si stratifica.
3. Intervalli: bootstrap sui protocolli (l'unità di campionamento è il protocollo, non l'ente).
4. Il metodo di correzione si fissa quando arriva il gold. Il default sopra è un punto di partenza.

## Stadio 4: questionario
La verità è il protocollo. Sui 20 del gold si confronta il valore dell'item 2.2 con il conteggio vero. Sui 249 lo si confronta con la stima del modello corretta. La differenza questionario–protocollo è un risultato solo se supera l'errore del modello.

## Limiti da dichiarare
- Il gold ha 20 protocolli: intervalli larghi, stime per singola categoria (30) instabili e da aggregare.
- I protocolli sopra 100.000 caratteri non sono nel gold; per loro c'è la precision della fase 2 ma non la recall.
- La periferia non converge tra le run: la stima dipende dalla regola di conteggio (da decidere con i colleghi della produzione).
- I protocolli pilota (3) sono fuori dal gold e in fase 2.
- Un solo annotatore principale; accordo misurato su 8 protocolli.

## Documenti collegati
`docs/decisioni.md` (decisioni), `docs/experiments.md` (esperimenti e annotazione), `campione/README.md` (campione e gold), `annotazione/README.md`.
