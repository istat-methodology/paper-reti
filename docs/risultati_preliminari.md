# Risultati preliminari

Ricalcolati dai microdati con `codice/analisi_01` e `analisi_02`. 251 protocolli × 30 categorie.

## Accordo per categoria (celle protocollo × categoria)

| Ruolo | Mappatura | Entrambi | Solo umano | Solo AI | Nessuno | Jaccard | κ | PABAK |
|---|---|---|---|---|---|---|---|---|
| Proponente | base | 247 | 677 | 192 | 6414 | 0.221 | 0.308 | 0.769 |
| Proponente | alt | 252 | 672 | 201 | 6405 | 0.224 | 0.310 | 0.768 |
| Attore | base | 1333 | 458 | 560 | 5179 | 0.567 | 0.634 | 0.730 |
| Attore | alt | 1359 | 432 | 589 | 5150 | 0.571 | 0.637 | 0.729 |

Lettura: sui proponenti l'umano segna molto più dell'AI (924 vs 439–453). PABAK alto e κ basso: prevalenza bassa, il PABAK qui è gonfiato dai "nessuno". La mappatura dei 604 soggetti cambia poco i risultati.

## Numerosità (domanda 2.2)

Totale umano 4791, AI 5854. Umano < AI in 200 protocolli, > in 44, uguale in 7. Celle con entrambi >0: 1388, conteggio esatto in 825. L'AI conta meno su polizia municipale (0.19), settore educativo (0.22), servizi sociali comunali (0.46).

## Da tenere a mente
- Il disaccordo sui proponenti è in gran parte di definizione, non di errore.
- Nessun gold standard: serve l'audit sui PDF.
