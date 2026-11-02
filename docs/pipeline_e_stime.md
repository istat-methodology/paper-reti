# Pipeline e stime

Aggiornato: 2026-11-02. Spiega come la run sui 249 file (240 documenti dopo i controlli), il campione di 58 (v2) e il gold standard si combinano nelle stime. Il questionario non entra nella parte A; entra solo nella parte B (stadio 4).

## Idea
La run sui 249 file (240 documenti dopo i controlli) è un censimento con errore di misura. Il campione serve a misurare quell'errore. Le stime sono le liste della run, corrette con i tassi di errore del campione.

## Schema

```
POPOLAZIONE: 240 documenti
   │
   ├─► RUN (stadio 1 + stadio 2) su tutti i protocolli, 5 run ........ liste grezze
   │      nucleo (enti con nome) + periferia (menzioni generiche), ruolo, categoria, frequenza tra run
   │
   └─► CAMPIONE n = 58 (v2; stratificato per regione e lunghezza)
          │
          ├─► GOLD, 20 protocolli (estratti dai 60; esclusi pilota e > 100.000 caratteri)
          │      annotazione manuale da zero ............................ VERITÀ
          │      → recall, precision, accordo tra annotatori, categorie (verità stadio 2)
          │
          └─► FASE 2, 38 protocolli (gli altri del campione)
                 revisione delle incoerenze del modello ................. PRECISION
                 (enti non unanimi, ruoli instabili, doppioni, quota di unanimi)

TASSI DI ERRORE (con pesi di campionamento, intervalli per protocollo)
   precision: gold + fase 2 (60 protocolli)
   recall:    solo gold (20 protocolli)
   per classe: nucleo/periferia, ruolo, categoria, fascia di lunghezza
          │
          ▼
STIMA sui 240 documenti = liste della run corrette con i tassi
          │
          ▼
STADIO 4: confronto con il questionario (item 2.2; controllo con 2.1, 3.3, 3.7)
```

## Ruolo dei tre insiemi
| Insieme | Protocolli | Cosa fornisce | Cosa non fornisce |
|---|---|---|---|
| Run completa | 249 file, 240 documenti | liste grezze per tutta la popolazione | misura dell'errore |
| Gold | 20 | verità: recall, precision, accordo, categorie | stime su protocolli molto lunghi |
| Fase 2 | 38 | precision di nucleo e ruoli | recall (il revisore parte dalla lista del modello) |

## Stima (parte A)
Le stime riguardano `firmatario` e `componente_rete`. I `solo_citato` si riportano a parte. Le menzioni generiche non entrano nelle stime: servono a valutare la qualità dell'estrazione (recall e precision della periferia, confine tra nucleo e periferia, stabilità, accordo tra annotatori). Il ruolo nel documento si valuta sul gold come output dello stadio 1.

1. Per ogni classe (nucleo, periferia, ruolo, categoria, fascia di lunghezza) si calcolano precision e recall sul campione, con pesi pari all'inverso della probabilità di estrazione.
2. Stimatore di base: rapporto tra enti veri (gold) ed enti del modello, applicato al totale dei 240 documenti. Se il gold mostra che la recall dipende dalla lunghezza, il rapporto si stratifica.
3. Intervalli: bootstrap sui protocolli (l'unità di campionamento è il protocollo, non l'ente).
4. Il metodo di correzione si fissa quando arriva il gold. Il default sopra è un punto di partenza.

## Parte B (stadio 4): confronto con il questionario
È il confronto con la raccolta dati tradizionale. Due livelli: **B1**, insiemi di enti (item 2.2, controllo con l'unione di 2.1, 3.3 e 3.7), senza ruoli del questionario; **B2**, per proponente, attore e incaricato, condizionato alle definizioni (analisi esplorativa finché non arrivano). Il perimetro è quello degli enti con nome proprio: si assume che il questionario non conti le menzioni generiche (Prefettura, Pronto soccorso). Ipotesi da verificare sul gold.

La verità è il protocollo. Sui 20 del gold si confronta il valore dell'item 2.2 con il conteggio vero. Sui 240 documenti lo si confronta con la stima del modello corretta. La differenza questionario–protocollo è un risultato solo se supera l'errore del modello.

## Limiti da dichiarare
- Basilicata e Valle d'Aosta non hanno documenti in ambito e non sono rappresentate.
- Il gold ha 20 protocolli: intervalli larghi, stime per singola categoria (30) instabili e da aggregare.
- I protocolli sopra 100.000 caratteri non sono nel gold; per loro c'è la precision della fase 2 ma non la recall.
- La periferia non converge tra le run: non entra nelle stime, si usa per valutare l'estrazione. Resta da chiarire come conta il questionario le istituzioni senza nome (confronto B1).
- I protocolli pilota (3) sono fuori dal gold e in fase 2.
- Un solo annotatore principale; accordo misurato su 8 protocolli.

## Documenti collegati
`docs/decisioni.md` (decisioni), `docs/experiments.md` (esperimenti e annotazione), `campione/README.md` (campione e gold), `annotazione/README.md`.
