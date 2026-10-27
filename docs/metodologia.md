# Metodologia

**Fonti.** GINO: questionario compilato dagli uffici regionali dai PDF. AI: pipeline s1.1 con 4 query (firmatari/soggetti, proponenti, attori, governance), 30 categorie aggregabili in 10 gruppi (`riferimenti/categorie_gino_30.csv`).

**Abbinamento.** Chiave `ID_RISPONDENTE_RILEV|PROGRESSIVO_QUEST`. 251 protocolli abbinati.

**Griglia.** Per ogni protocollo, 30 categorie × 2 ruoli. `hu` = categoria selezionata nel questionario (campi `SOGGETTO_PROP_CHECK`, `ATTORI_COINVOLTI_CHECK`); `ai` = almeno un soggetto AI della categoria con quel ruolo.

**Metriche.** Accordo (entrambi, solo umano, solo AI), Jaccard, κ di Cohen, PABAK; test dei segni; eta² per regione.

**Limite.** Nessuno dei due è la verità. Il disaccordo mescola errori e differenze di definizione. L'audit sul PDF li separa.
