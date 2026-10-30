# Definizioni dei soggetti (v1, bozza)

**Stato: bozza di lavoro, 2026-10-30.** Serve a due cose: guidare i prompt dell'estrazione AI e guidare chi annota a mano il gold standard. Le parti marcate **[ipotesi]** sono scelte nostre, da confermare con i colleghi che hanno costruito il questionario. Le parti marcate **[da verificare]** sono riferimenti normativi scritti senza aver letto il testo ufficiale.

Fonti usate: nota metodologica Istat (`riferimenti/rif_istat_reti_territoriali_2025_v1.pdf`, pp. 16-18 e nota 11 a p. 15); Intesa Stato-Regioni del 27/11/2014 (artt. 1 e 8, letti sul testo); D.Lgs. 117/2017 (Codice del Terzo settore, da verificare su Normattiva).

## 1. Cosa conta come "ente"

**[ipotesi]** Un ente è un soggetto distinto (persona giuridica, ufficio o struttura) che nel protocollo è firmatario o ha un compito o un impegno nella rete.

- Si contano: firmatari; soggetti che il testo indica come componenti della rete, del tavolo o della cabina di regia; soggetti a cui sono assegnati compiti operativi.
- Non si contano: norme, convenzioni internazionali, ministeri citati solo come riferimento normativo, enti citati come esempio o come fonte, enti di altre reti.
- Citazioni generiche ("i Comuni dell'ambito", "le associazioni del territorio"): un solo record, marcato `generico`, senza numero. I Comuni nominati uno per uno sono un record ciascuno.
- Struttura e gestore: se il protocollo nomina sia il CAV sia l'associazione che lo gestisce, sono due enti. Se nomina solo l'associazione "che gestisce il CAV", è un ente solo.
- Stesso ente nominato in modi diversi (sigla, nome esteso): un record solo.

## 2. Glossario

**ETS (Ente del Terzo settore).** Stato giuridico, non funzione. Ente privato senza scopo di lucro che persegue finalità civiche, solidaristiche o di utilità sociale e che è iscritto al RUNTS (D.Lgs. 117/2017, art. 4) **[da verificare]**. Rientrano: organizzazioni di volontariato, associazioni di promozione sociale, enti filantropici, imprese sociali (comprese le cooperative sociali), reti associative, società di mutuo soccorso, altre associazioni e fondazioni iscritte. Sono escluse le amministrazioni pubbliche, i partiti, i sindacati e le associazioni professionali e di categoria **[da verificare]**.

**RUNTS.** Registro unico nazionale del Terzo settore. L'iscrizione è ciò che rende un ente "ETS". Nei protocolli l'iscrizione quasi mai è dichiarata. Controllo esterno (elenco RUNTS) è un passo separato dall'estrazione.

**ODV (Organizzazione di volontariato).** Tipo di ETS: associazione che si avvale in modo prevalente dell'attività di volontari (art. 32) **[da verificare]**.

**APS (Associazione di promozione sociale).** Tipo di ETS: associazione che svolge attività di utilità sociale a favore di associati, familiari o terzi (art. 35) **[da verificare]**.

**Impresa sociale.** Ente che esercita attività d'impresa di interesse generale senza scopo di lucro (D.Lgs. 112/2017). Le cooperative sociali (L. 381/1991) lo sono di diritto **[da verificare]**.

**Ente filantropico.** Tipo di ETS che eroga denaro o beni. Le fondazioni di origine bancaria non sono ETS.

**CAV (Centro antiviolenza).** Funzione, non stato giuridico. Struttura che accoglie donne di ogni età e i loro figli minorenni, a titolo gratuito (Intesa 2014, art. 1). Promossa da enti locali, da associazioni, o da entrambi. Le associazioni devono essere iscritte agli albi regionali e avere come finalità statutaria il contrasto alla violenza o almeno cinque anni di esperienza nel settore (Intesa 2014, art. 1, come letto sul testo).

**Casa rifugio.** Struttura ad indirizzo segreto che dà alloggio sicuro alle donne e ai figli (Intesa 2014, art. 8). Secondo Istat (nota 11 a p. 15) può essere di pronta emergenza, di primo livello (protezione) o di secondo livello (accompagnamento verso la semi-autonomia).

**Associazione di donne (ETS "per le donne").** Etichetta Istat della categoria 25. **[ipotesi]** Associazione o centro costituito da donne, con finalità statutaria di sostegno e tutela delle donne.

**Ambito sociale / Zona-distretto / Società della Salute.** Livello di programmazione sociale e socio-sanitaria. Nel caso Toscana, la Società della Salute è un consorzio pubblico tra Comuni e Azienda USL per la zona-distretto.

**Codice Rosa.** Percorso di accoglienza nel pronto soccorso per vittime di violenza (nota 7 a p. 7 del documento Istat). Il Codice Rosa è un percorso, non un ente: l'ente è il pronto soccorso (categoria 11) o l'Azienda (12).

## 3. Regole generali di classificazione

1. **[ipotesi] Funzione prima dello stato giuridico.** Un ente che gestisce un CAV ha come categoria principale 1 (CAV). La natura giuridica (24 o 25) va come categoria secondaria.
2. **[ipotesi] Più categorie ammesse, una sola principale.** Il questionario ha caselle multiple, quindi un ente può avere categorie secondarie. In fase di prova si registrano tutte; per i conteggi si usa la principale.
3. **[ipotesi] 24 e 25 sono alternative.** Se l'ente è un'associazione di donne è 25, altrimenti 24.
4. **[ipotesi] Iscrizione RUNTS presunta.** Un'associazione, fondazione o cooperativa sociale senza scopo di lucro che opera nel contrasto alla violenza è classificata 24 o 25, salvo evidenza contraria nel testo. La verifica sul RUNTS è un passo a parte.
5. **Nel dubbio: 30 (Altro)**, con nota. Non si forza una categoria.
6. **Non si usa il nome dell'ente come unico indizio** quando il testo dice altro (es. "Casa della donna" può essere un CAV o un'associazione).

## 4. Le 30 categorie

Etichette dal questionario (`riferimenti/categorie_gino_30.csv`). Inclusioni ed esclusioni sono **[ipotesi]** nostre.

| Cod. | Categoria | Include | Non include / note |
|---|---|---|---|
| 1 | CAV | Centri antiviolenza | Il gestore (associazione) va in 24/25 se nominato a parte |
| 2 | Case Rifugio | Strutture di pronta emergenza, primo e secondo livello | Idem per il gestore |
| 3 | Comuni | Comune come ente; Unione dei Comuni (diverso da Paolo, vedi `ipotesi_lavoro_v2.md`) | Servizi interni al Comune: 4-7 |
| 4 | Polizia Municipale | Polizia locale | Polizia provinciale: 15 |
| 5 | Settore educativo comunale | Servizi educativi comunali, nidi | Scuole statali: 16 |
| 6 | Servizi sociali comunali | Assessorato/servizio sociale del Comune | Ambito sociale: 9 |
| 7 | Servizio abusi e maltrattamenti comunale | Servizio comunale dedicato | Se non è dedicato: 6 |
| 8 | Province/Città metropolitane | Provincia, Città metropolitana | |
| 9 | Ambiti della programmazione sociale e socio-sanitaria | Ambito, Piano di zona, Distretto, Società della Salute, zona-distretto, consorzio pubblico di servizi sociali | |
| 10 | Regioni/Province autonome | Giunta, assessorati, agenzie regionali emanazione della Regione | |
| 11 | Ospedale | Ospedale, Pronto soccorso, Azienda ospedaliera/universitaria | Consultori: 12 |
| 12 | ASL | Azienda USL, consultori, servizi territoriali, salute mentale, dipendenze | |
| 13 | Prefettura | Prefettura/UTG | |
| 14 | Questura | Questura | |
| 15 | Carabinieri/Polizia/altre forze dell'ordine | Carabinieri, Polizia di Stato, Guardia di Finanza, Polizia provinciale | Polizia Municipale: 4 |
| 16 | Scuole/Ufficio scolastico | Istituti, Ufficio scolastico regionale/provinciale | |
| 17 | Procura minorile/Tribunale minorile | Tribunale per i minorenni e relativa Procura | |
| 18 | Procura ordinaria/Tribunale/Corte d'appello | Tribunale ordinario, Procura della Repubblica, Corte d'appello | |
| 19 | Ordine avvocati | | |
| 20 | Ordine psicologi e assistenti sociali | | |
| 21 | Ordine medici/odontoiatri e farmacisti | | |
| 22 | Altri ordini professionali | Infermieri, ostetriche, giornalisti, ecc. | |
| 23 | Organismi di parità | Consigliera di parità, Commissione pari opportunità, CUG | |
| 24 | ETS (RUNTS) | ODV, APS, cooperative sociali, imprese sociali, altre associazioni e fondazioni senza scopo di lucro | Presunto (regola 4) |
| 25 | ETS costituito da donne per le donne | Associazioni e centri di donne | Alternativa a 24 |
| 26 | Servizi per l'impiego | Centri per l'impiego, agenzie regionali del lavoro | |
| 27 | Sindacati/Associazioni di categoria | Sindacati, associazioni datoriali, di categoria | |
| 28 | Università | Atenei, dipartimenti | |
| 29 | Associazioni per uomini maltrattanti | Programmi di trattamento per autori | |
| 30 | Altro | Ministeri, INPS, INAIL, Camera di commercio, fondazioni bancarie, consorzi non classificabili | Sempre con nota |
