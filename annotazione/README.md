# Annotazione

## gold_v2 (gold per il paper)
Sottoinsieme di 20 protocolli estratto a caso dal campione di 60 (`campione/campione_gold_v1.csv`, `codice/campione_gold.py`, seed 20261101). Esclusi i 3 pilota e i protocolli oltre 100.000 caratteri.

Annotazione manuale da zero, senza vedere output di modelli: enti con nome proprio (con ruolo e categoria) e menzioni generiche (periferia). Annotatore principale Paolo su tutti i protocolli; 8 protocolli con `doppia=si` li annota anche un secondo annotatore (Elena, se disponibile, altrimenti Mauro), per misurare l'accordo.

- `gold_v2/gold_enti_v4_template.xlsx`: template, v4 dal 2026-11-02 (la v3 non ha le colonne `promotore`, `coordinatore_capofila`, `monitoraggio` nel foglio `enti`; fogli `istruzioni`, `protocolli`, `enti`, `menzioni_generiche`, `categorie`).

Usi: recall e precision dello stadio 1, accordo tra annotatori, verità per lo stadio 2 (30 categorie).

## gold_v1_legacy (set di sviluppo)
Primo campione di 36 protocolli (Toscana per intero più altri) e fogli di annotazione `gold_enti_v2_A1/A2`, pre-compilati con l'output della pipeline v1 (gpt-4.1). Paolo ed Elena li stanno compilando. Non sono indipendenti dal modello né un campione probabilistico: servono come materiale di sviluppo e come controllo secondario. Cinque protocolli sono anche nel nuovo gold (044103, 1265, 1104, 1605, 1001).

