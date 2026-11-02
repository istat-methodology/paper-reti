# Gold standard: istruzioni per l'annotazione

Grazie. Ti chiediamo di estrarre a mano gli enti da 20 protocolli. Servono come riferimento per valutare l'estrazione automatica.

## Cosa trovi
- `gold_enti_v4_template.xlsx`: il file da compilare (fogli `istruzioni`, `protocolli`, `enti`, `menzioni_generiche`, `categorie` con le 30 categorie del questionario).
- `protocolli/`: i 20 protocolli in testo (`protocollo_<codice>.txt`).
- `associazione_protocolli.csv` (e foglio `protocolli` del template): per ogni codice, il nome del PDF caricato nel questionario e il titolo del documento. Serve per trovare il PDF originale giusto.

## Come lavorare
1. Annota da zero, sul PDF originale (il testo serve solo come aiuto per la ricerca). Non usare altri file o elenchi di enti già fatti.
2. Foglio `enti`: una riga per ogni organizzazione che il testo nomina con un nome proprio. Indica il ruolo (firmatario, componente_rete, solo_citato), la categoria principale (codice 1-30) e, se serve, quelle secondarie. Indica anche, quando il testo lo dice in modo esplicito, le funzioni `promotore`, `coordinatore_capofila` e `monitoraggio` (`si` o vuoto; regole nel foglio `istruzioni`).
3. Foglio `menzioni_generiche`: i soggetti citati solo per tipo o funzione, senza nome proprio (ospedali, polizia municipale, prefettura, le forze dell'ordine, Pronto soccorso...). Una riga per espressione distinta.
4. Quando hai finito un protocollo, scrivi `si` in `completato` nel foglio `protocolli`.
5. Alcuni protocolli (`doppia = si`) li annota anche una seconda persona, in modo indipendente. Non serve confrontarsi prima.

## Note
- Il testo viene da una conversione dal PDF: ci possono essere errori di a capo o caratteri. Se un passaggio non si capisce, scrivilo in `note`.
- Non sono enti: leggi e decreti, documenti e linee guida, persone fisiche, organismi internazionali citati come fonte (ONU, UE, OMS), tavoli e reti istituiti dal protocollo (elenca invece gli enti che ne fanno parte).
- Versione v4 del template (2026-11-02): rispetto alla v3 ha le tre colonne delle funzioni nel foglio `enti`. Se hai già iniziato nella v3, copia le tue righe nella v4 (colonne `codice`…`cat_secondarie` restano uguali; `pagina` e `note` si spostano a destra).
- Dubbi sulle definizioni: annotali in `note` e decidiamo insieme alla fine.

Quando hai finito, rimanda il file con il tuo nome nel nome del file (es. `gold_enti_v4_paolo.xlsx`).
