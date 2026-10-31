# Ipotesi di lavoro per la ripartenza dell'estrazione AI (v2)

> **Nota (2026-10-31).** Il campione di 36 protocolli (`archivio/annotazione_campione_v1/`) e la scelta della Toscana come set di sviluppo sono superati: vedi `docs/decisioni.md` e `campione/README.md`. I fogli di annotazione v2 sono archiviati e vanno rifatti sul nuovo campione.


**Aggiornato: 2026-10-30.** Da confermare con i colleghi che hanno costruito il questionario. Quando arrivano le istruzioni di compilazione, si rivede questo file.

## Impostazione

Si riparte dall'inizio, anche dai prompt, e si valida a stadi. Ogni stadio si chiude prima di passare al successivo.

1. **Definizioni.** `docs/definizioni_soggetti_v1.md`.
2. **Estrazione di tutti gli enti** di ogni protocollo, validata a mano.
3. **Classificazione**: ruolo/natura (ETS, APS, CAV, ...) e una delle 30 categorie, validata a mano.
4. **Confronto con il questionario**, solo dopo i primi tre stadi.

Campione per l'annotazione: 36 protocolli (`annotazione/campione_v1.csv`, `codice/campione_annotazione.py`, seed fisso).

- **Toscana: tutti gli 11 protocolli** (0909 escluso perché condivide il testo con 0910). Pilota: i questionari sono stati compilati dalla responsabile del progetto.
- **Altre regioni: 25 protocolli.** Uno per regione, il resto in proporzione ai protocolli della regione. Dentro la regione la scelta è sistematica sulla lunghezza, per coprire protocolli corti e lunghi.
- **Sardegna esclusa.** Ha un solo protocollo (170.000 caratteri, 110 enti AI), troppo oneroso. Va dichiarato come limite.
- Lazio ha 95 protocolli su 245 ma corti (mediana 7.800 caratteri): con la proporzionalità pura il campione sarebbe concentrato lì e povero di casi complessi.

Assegnazione: 12 protocolli (uno ogni tre, spaziati per regione e lunghezza) sono annotati da entrambi, per misurare l'accordo. Gli altri 24 sono divisi tra A1 e A2 bilanciando il numero di enti. Ogni annotatore controlla circa 700 enti su 23-25 protocolli.

Si lavora ancora con gpt-4.1 finché non è pronta la nuova run.

## Ipotesi sul confronto con il questionario

- **Obiettivo del confronto: 2.2 (tipologia e numerosità).** Nessuna distinzione tra proponente, attore e incaricato.
- **Controllo: unione delle spunte di 2.1, 3.3 e 3.7.** Una categoria è presente nel protocollo se è spuntata in almeno una delle tre.
- **2.2 conta i soggetti, uno per uno** (ipotesi). Un Comune nominato = 1. Da verificare confrontando 2.2 con i conteggi del gold standard.
- Le spunte multiple: si assume che i compilatori non le usino. Da verificare.

## Ipotesi sulle definizioni

- Unione dei Comuni: nel codice di Paolo va nella categoria 8 (Province/Città metropolitane); qui è proposta 3 (Comuni). Da discutere con Paolo.
- Stato giuridico (ETS) e funzione (CAV) sono livelli diversi. Vedi `definizioni_soggetti_v1.md`, sezione 3.
- Iscrizione RUNTS presunta dal testo, verificata a parte.

## Tavole Istat pubblicate

**Non si usano come benchmark macro** finché non sono controllate: Mauro ritiene che contengano molti errori. Il PDF resta nel repo come riferimento per le definizioni (nota metodologica, pp. 16-18). Quando si individuano errori specifici, si elencano qui.

## Gold standard

- Pre-compilato da noi con l'output AI esistente (gpt-4.1): `annotazione/gold_enti_v2_template.xlsx`. Due file, `_A1` e `_A2`, per due annotatori indipendenti (Paolo ed Elena), ciascuno con i propri protocolli. Gli annotatori non vedono il questionario.
- Si misura l'accordo tra i due annotatori prima di usare il gold standard come verità.
- La verità è il protocollo.

## Stadio 1: estrazione degli enti

Prompt v1: `prompts/v2/stadio1_estrazione_enti_v1.txt` (la v0 resta nel repo per confronto). Script: `codice/pipeline_ai_v2/stadio1_estrazione.py`. Output in `microdati/ai_v2/stadio1/` (fuori da git).

**Due contenitori separati**, perché nella v0 il confine tra enti precisi ed espressioni generiche era la principale fonte di instabilità (generici stabili al 47% nelle 3 run, enti con nome al 85%).
- `enti_identificati` (nucleo): il testo contiene un nome proprio che individua una specifica organizzazione. Campi: nome, forma giuridica dichiarata, ruolo nel documento (firmatario / componente_rete / solo_citato), citazione letterale.
- `menzioni_generiche` (periferia): tipologie ("i Comuni", "associazioni sportive"), strutture senza nome (Pronto soccorso, reparto di Ginecologia, con l'ente di appartenenza), istituzioni senza riferimento locale (Carabinieri, Polizia di Stato, "la Prefettura", "la Regione"). Come contarle si decide con i colleghi di produzione.
- Fusione: se l'ente è nominato per intero altrove nel documento, la menzione generica confluisce nell'ente identificato.
- Casi di confine tenuti nel nucleo: enti nazionali o internazionali con nome proprio (Ministero dell'Interno, Garante privacy, ONU), di solito `solo_citato`.
- Tavoli, reti, cabine di regia e gruppi di lavoro creati dal protocollo non sono enti.

**Prompt v1.1** (`prompts/v2/stadio1_estrazione_enti_v1_1.txt`), dopo le prime run in PDF sulla Toscana:
- percorsi, programmi, reti e tavoli ("Codice Rosa", "Rete regionale Codice Rosa") non sono enti, anche se non creati dal protocollo;
- gli organismi internazionali citati come fonte di norme (ONU, Consiglio d'Europa, Comitato dei Ministri, UE, OMS) non sono enti. Restano nel nucleo gli enti nazionali italiani con nome proprio;
- un'associazione e il centro che gestisce con lo stesso nome proprio ("Olympia de Gouges") sono un solo record se il testo non li distingue;
- ogni ente con un solo nome, nella forma più completa del testo (le varianti di nome tra le run gonfiavano l'instabilità);
- nuovo campo `pagina`: dove compare la citazione. Per le scansioni il controllo della citazione contro il testo OCR non è affidabile (nel testo OCR mancano anche firmatari presenti nel PDF, per esempio i Comuni nel blocco firme dello 0905).

**Analisi.** Nucleo e periferia si analizzano separatamente: stabilità tra le run, confronto testo/PDF, accordo con il gold standard. Sul nucleo provvisorio della v0 (enti non marcati generici) testo e PDF coincidono quasi del tutto (226 enti in comune, 11 solo testo, 7 solo PDF; Jaccard tra run 0,90 per entrambi).

**Run.** 3 run per protocollo, per misurare la stabilità. Due varianti di input, testo estratto e PDF originale (5 dei 11 protocolli toscani sono scansioni, e 0902 è misto). Con il PDF si saltano i file sopra 3 MB (0902, 0903, 0908). Il prompt si mette a punto sui protocolli toscani (sviluppo) e si valuta sugli altri 25 del campione (test).
