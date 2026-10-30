# Ipotesi di lavoro per la ripartenza dell'estrazione AI (v2)

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

- Pre-compilato da noi con l'output AI esistente (gpt-4.1): `annotazione/gold_enti_v1_template.xlsx`. Due file, `_A1` e `_A2`, per due annotatori indipendenti (Paolo ed Elena), ciascuno con i propri protocolli. Gli annotatori non vedono il questionario.
- Si misura l'accordo tra i due annotatori prima di usare il gold standard come verità.
- La verità è il protocollo.
