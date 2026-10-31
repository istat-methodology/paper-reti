# Experiments log

Working log of the experiments on the entity-extraction pipeline. Each experiment has an id, a prompt, an input and the measures
that came out of it. Numbers in the tables are regenerated from the run files by `codice/pipeline_ai_v2/registro_misure.py`
(`docs/experiments_misure.csv`, `docs/experiments_confronti.csv`). Add an experiment by adding a row to `ESPERIMENTI` in that script and a
section here.

Last update: 31 Oct 2026.

## 1. Purpose and rules

The paper compares what an LLM extracts from the territorial anti-violence protocols with what the GINO questionnaire reports.
The protocol is the ground truth. We start the AI extraction from scratch and validate it in stages.

1. **Stage 1.** Extract every organisation named in a protocol, with its role in the document.
2. **Stage 2.** Classify each entity into the 30 GINO categories (not started).
3. **Stage 3.** Validate stages 1–2 against manual annotation (planned, section 6).
4. **Stage 4.** Compare with the questionnaire. Target: item 2.2, type and number of entities. Check: union of items 2.1, 3.3 and 3.7. No split into proponent / actor / commissioner.

Rules that apply to everything below.
- **Pilot.** The experiments below use 11 Toscana protocols as a pilot. All prompt changes were made after looking at these results, so the stability figures here are optimistic. The publication sample is drawn separately (`campione/README.md`); pilot protocols that fall in it are marked.
- **No seed.** The model is called without a seed. Runs differ, and the difference is what we measure.
- **Verification.** A quoted passage is checked against the OCR text: accents ignored, word 3-grams, coverage ≥ 0.8.

## 2. Setup

| | |
|---|---|
| Model | `gpt-6.1-terra`, Azure, Responses API, strict JSON schema output |
| Runs | 3 per protocol and per experiment |
| Sample (dev) | Toscana, protocols 0901–0912 except 0909: 11 protocols |
| Input | `testo`: OCR text of the protocol. `pdf`: the PDF sent as `input_file` |
| Scripts | `codice/pipeline_ai_v2/stadio1_estrazione.py`, `stadio1_spezzato.py` (chunked text) |
| Prompts | `prompts/v2/stadio1_estrazione_enti_<version>.txt`, in Italian |
| Definitions | `docs/definizioni_soggetti_v1.md` |

Output of stage 1 (from v1 on): two lists.
- **Core** (`enti_identificati`): organisations with a proper name. Fields: name, declared legal form, role (`firmatario`, `componente_rete`, `solo_citato`), quote, page.
- **Periphery** (`menzioni_generiche`): mentions by type, function or as an internal unit (Carabinieri without a command, "Pronto soccorso", "le associazioni sportive"). Fields: expression, mention type, parent entity, role, quote, page.

## 3. Measures

- **Stability between runs.** Jaccard index between the sets of entity names of two runs, averaged over the 3 pairs, then over protocols.
  - *Strict:* names compared after lower-casing and removing accents.
  - *Tolerant:* names compared without "Comune di", "Azienda", articles and similar words. Equal, included in each other or difflib ratio ≥ 0.85 counts as a match. One-to-one, deterministic matching.
  The tolerant version is the reference. Most strict-only differences are name variants ("Chiusi" vs "Comune di Chiusi").
- **Presence.** An entity is present in an experiment if it appears in at least 2 of its 3 runs.
- **Difference between experiments.** Entities present in one experiment and not in the other, with the tolerant name match.
- **Entities per run.** Median over runs, summed over protocols.
- **Citations not found.** Share of quotes that do not match the OCR text.

*Measurement fix (31 Oct).* The first version of the tolerant Jaccard matched names in set order, which changes at each Python run. Figures moved by up to 0.07 on a single protocol. It is now deterministic. Figures reported in chat before the fix differ from the table by at most 0.01 on the means.

## 4. Experiments

| Id | Prompt | Input | Protocols | Runs | Core entities | Jaccard core (strict) | Jaccard core (tolerant) | Jaccard periphery (tolerant) | Tokens in / out (k) |
|---|---|---|---|---|---|---|---|---|---|
| E1 | v0 | text | 11 | 33 | 436 | 0.883 | 0.924 | 0.626 | 435 / 178 |
| E2 | v0 | PDF | 8 | 24 | 227 | 0.905 | 0.934 | 0.812 | 1263 / 103 |
| E3 | v1 | text | 11 | 33 | 324 | 0.905 | 0.956 | 0.799 | 466 / 181 |
| E4 | v1 | PDF | 8 | 24 | 186 | 0.957 | 0.969 | 0.824 | 1286 / 104 |
| E5 | v1.1 | text | 11 | 33 | 271 | 0.886 | 0.948 | 0.756 | 474 / 179 |
| E6 | v1.2 | text | 11 | 33 | 293 | 0.940 | 0.960 | 0.808 | 483 / 175 |
| E7 | v1.2 | PDF | 11 | 33 | 295 | 0.889 | 0.954 | 0.825 | 2146 / 157 |
| E8 | v1.2 | text, chunked | 2 | 6 | 45 | 0.967 | 0.983 | 0.847 | 345 / 132 |

PDF experiments E2 and E4 cover 8 protocols: three PDFs (0902, 0903, 0908) were above the 3 MB size filter. E7 covers all 11 (limit raised to 4.1 MB, see 4.8). For v0, "core" is the entities with `generico = false` and "periphery" those with `generico = true`; v0 has no mention types.
Core entity counts are not comparable across rows with a different number of protocols.

Differences in content between pairs of experiments (core, present in ≥ 2 runs, protocols in common):

| A → B | Protocols | Entities A | Entities B | In common | Only A | Only B |
|---|---|---|---|---|---|---|
| E1 → E3 (v0 → v1) | 11 | 359 | 294 | 289 | 70 | 5 |
| E3 → E5 (v1 → v1.1) | 11 | 294 | 243 | 241 | 53 | 2 |
| E5 → E6 (v1.1 → v1.2) | 11 | 243 | 262 | 240 | 3 | 22 |
| E3 → E4 (v1 text → PDF) | 8 | 154 | 160 | 152 | 2 | 8 |
| E6 → E7 (v1.2 text → PDF) | 11 | 262 | 262 | 254 | 8 | 8 |
| E6 → E8 (v1.2 whole → chunked) | 2 | 37 | 45 | 36 | 1 | 9 |

### 4.1 E1, E2: first prompt (v0)
Single list of entities with a `generico` flag, one prompt for everything. Text and PDF (prompt sha `5ee461bb6392`).
- Core stability is already high (0.92–0.93 tolerant). Periphery on text is low (0.63): the generic mentions are the unstable part.
- The flat list mixes entities with a proper name and generic mentions. This is the reason for the two-container design.

### 4.2 E3, E4: two containers (v1)
Prompt `164df7315df7`. Separate list for entities with a proper name and for generic mentions. Fusion rule: if an entity is named in full elsewhere, no generic mention is created.
- Stability up on text: core 0.956, periphery 0.799 (from 0.924 and 0.626 in v0).
- 70 entities of the v0 core are no longer in the v1 core (5 are new). I did not inspect all 70 one by one; the design moves units, types and bodies without a proper name to the periphery.
- **Text vs PDF.** On the 8 protocols in common, 152 core entities are in both, 2 only with text, 8 only with PDF. The PDF recovers signatories that the OCR text loses, for example the Comune di Roccastrada in 0905 (signature pages). Five of the 11 Toscana PDFs are scans without a text layer (0901, 0903, 0905, 0907, 0912), so the OCR is the only text there, and the OCR loses accents and some signature blocks.
- **Quotes.** On PDF runs, 8% of core quotes are not found in the OCR text, because the model reads text the OCR lost. On text runs all quotes are found, by construction.
- Roles on the PDF core (v1): 294 `firmatario`, 86 `componente_rete`, 174 `solo_citato`. 0904 has no signatory: it is a guidelines document.

### 4.3 E5: prompt v1.1
Prompt `eb88bdaf0acc`. Changes: international bodies (UN, Council of Europe, EU, WHO, International Criminal Court), programmes, paths, tables and networks (Codice Rosa) are not entities; one record for entities with the same proper name; one name per entity in its fullest form; new `pagina` field.
- Stability does not improve (core 0.948 vs 0.956). The purpose was to remove entities that do not belong.
- It removes 53 core entities. About 25 are the intended ones (international bodies, networks such as Rete TOSCA and Codice Rosa).
- It also removes things that matter. The model read "commissions and tables are not entities" as covering the signing **conferences of mayors**: 5 in 0903 and 3 in 0907, all `firmatario`. The Centro Pari Opportunità Valdelsa (0902, `firmatario`) became a generic mention. Italian national bodies with a proper name (Conferenza Unificata, Consiglio dei Ministri, Commissione parlamentare sul femminicidio, D.i.Re., CISMAI coordination) also disappeared, against the rule that keeps them in the core as `solo_citato`.
- Remaining differences are name variants that the matching does not join.
- Instability left in 0912 (0.455 strict, 1.0 tolerant): "Chiusi" in one run, "Comune di Chiusi" in the others. In 0911 the third run splits Corte d'Appello, Procura and Tribunale of Genoa and Massa into separate records.

### 4.4 E6, E7: prompt v1.2
Prompt `155f9b79ef07`. Five edits to v1.1, no new structure.
1. Tribunale and Procura of the same city are different entities. A judicial office with its seat is one entity.
2. Examples added to the core: a conference of mayors, Conferenza Unificata, Consiglio dei Ministri, parliamentary commission, D.i.Re.
3. Tables, networks, working groups and commissions are excluded only when set up by the protocol or another local act. Conferences of mayors and other bodies that sign with their own name are entities, role `firmatario`.
4. Two denominations of the same entity give one record with the name used in the preamble or signature block (Ufficio Scolastico Provinciale / Territoriale; Consigliera di Parità / Ufficio della Consigliera di Parità).
5. "Chiusi" next to "Comune di Chiusi" gives "Comune di Chiusi".

Results.
- Text: core 0.960, periphery 0.808. Three protocols at 1.0 (0901, 0903, 0911). 0903 goes from 0.864 to 1.0, 0911 from 0.82 to 1.0.
- 22 entities come back, 3 leave: the 8 conferences of mayors, the Centro Pari Opportunità Valdelsa, the national bodies. "Ufficio Scolastico Territoriale di Arezzo" disappears by design.
- Not solved: in 0910 RELIVE and Work With Perpetrators European Network (European project and network, role `solo_citato`) came back in 2 of 3 runs, and WHO ("O.M.S.") in 0912. Banca d'Italia is no longer in 0906 with text. To check in the text.
- **Text vs PDF (E7).** Core 262 vs 262, 254 in common, 8 on each side. At least 4 of the 16 differences are name variants of the same entity. The PDF adds Comune di Roccastrada (`firmatario`), Società della Salute zona Valdichiana (`firmatario`, 0912) and Studio Notarile Catania. The text adds Ministero della Giustizia (0902), Ospedale di Campostaggia, RELIVE and WWP EN.

### 4.5 Decision on text and PDF
Text and PDF give the same core (262 entities each, 254 in common). The PDF costs about 4.5 times the input tokens (2146k vs 483k) and has size and network problems. We work on text. The PDF stays for protocols whose text is empty or unusable: at least one protocol of the 251 has a single character of OCR text. The count of such protocols is not done yet.

### 4.6 Periphery
Less stable than the core in every experiment (0.76–0.83 tolerant), and it moves with the prompt. It is kept in a separate container and analysed separately. How to count it in the comparison with the questionnaire is not decided: this is to be agreed with the colleagues who run the survey.

### 4.7 Protocol length
Text length of the 251 protocols (characters): median 19,300; third quartile 34,800; 90th percentile 50,200; maximum 306,600. 26 protocols are above 50,000, 5 above 100,000, 1 above 200,000. Table in `microdati/ai_v2/stadio1/dimensioni.csv` (script `misura_dimensioni.py`).
In Toscana length and number of entities are unrelated: 0908 (41k characters) has 75 core entities and is stable (0.97), 0911 (93k) has 8, 0902 (144k, 66 pages) has 33 and a core Jaccard of 0.92.
The text has no page breaks and no reliable article headings, so chunking has to cut on paragraphs.

### 4.8 PDF compression for the size filter
Three PDFs were above 3 MB: 0902 (4.0 MB, 274 images at 300 dpi), 0903 (7.8 MB), 0908 (3.8 MB). At 110 dpi, quality 60: 0903 → 2.3 MB and 0908 → 1.1 MB; the signature page of 0903 is legible. 0902 does not go below 3 MB without becoming illegible (72 dpi, 2.7 MB: not legible); it was sent as is with the limit at 4.1 MB. Originals are in `microdati/protocolli_pdf/_originali/`.

### 4.9 E8: chunked text for long protocols
Script `stadio1_spezzato.py`. Above 40,000 characters the text is cut on paragraphs into chunks of about 25,000 characters with 2,000 overlap, and the last 5,000 characters (usually signatures) are added to each chunk. Lists from chunks are merged: tolerant name match, fullest name, strongest role (`firmatario` > `componente_rete` > `solo_citato`). Prompt v1.2 plus a line telling the model the text is an extract. Test on 0902 (7 chunks) and 0911 (4 chunks), 3 runs, whole text (E6) against chunked (E8).

| Protocol | Version | Core entities | Signatories | Generic mentions | Jaccard core (tol.) | Jaccard periphery (tol.) | Tokens in (k) |
|---|---|---|---|---|---|---|---|
| 0902 | whole | 33 | 16–17 | 30–37 | 0.924 | 0.722 | 129 |
| 0902 | chunked | 38 | 18 | 90–97 | 0.966 | 0.824 | 218 |
| 0911 | whole | 8 | 5 | 28–35 | 1.000 | 0.793 | 84 |
| 0911 | chunked | 7 | 5 | 31–35 | 1.000 | 0.869 | 127 |

- **0911 (93k characters):** no change in the core. The difference is one name (Garante, two wordings). Periphery slightly more stable.
- **0902 (144k characters):** the chunked version finds entities the whole version misses. Checked in the text, in the signature and annex blocks: the Procura della Repubblica di Siena (signatory of an annex), the Società della Salute Alta Val d'Elsa (signatory, with its director), Azienda USL 7, Provincia di Siena (a job title in a list of contacts). Core stability goes from 0.924 to 0.966.
- **Generic mentions** triple on 0902 (about 95 against 33): the whole run does not list everything in a long document.
- **Not clean:** the merge leaves duplicates because the same entity gets different names in different chunks. "Procura di Siena", "Procura della Repubblica di Siena" and "Procura della Repubblica presso il Tribunale di Siena" stay as three records (roles `solo_citato`, `firmatario`, `firmatario`); "Donne Insieme Val d'Elsa" has three wordings; "SDS Valdelsa", "SDS Zona Alta Val d'Elsa" and "Società della salute Zona Alta Val d'Elsa" stay separate. "SUN" (a university department named in a bibliographic note) is not an organisation of the network. The core count of 38 is therefore not a count of distinct entities.
- **Merge rule A (tested, tag `v1_2_testo_spezzato_A`, same chunk results re-merged):** two names are joined if the words of the shorter one (at least 2) are all in the longer one and both start with the same word. It joins the three Procura di Siena records into one. Core entities per run on 0902 go from 37–39 to 36–38; Jaccard 0.931. It does not join names that differ in the first word or in spelling: SDS Valdelsa, SDS Zona Alta Val d'Elsa and Società della salute Zona Alta Val d'Elsa (acronym), and the two wordings of Donne Insieme Val d'Elsa / Valdelsa. About 3–4 duplicates remain in 38.
- **Cost:** 1.5 times the input tokens on 0911 and 1.7 times on 0902.
- **Decision (provisional):** chunking helps on long protocols and is kept for protocols above 40,000 characters, if the merge is improved. Open: a better rule to join names of the same entity across chunks, or a final consolidation pass. Tested on 2 protocols only; to be confirmed on a larger set.

### 4.10 E9: how many runs (10 runs on text, prompt v1.2)
The `v1_2_testo` folder now holds 10 runs per protocol (Toscana, 11 protocols). Script `n_run_campionamento.py` draws subsets of n runs (up to 200 per protocol and n) and measures, with the tolerant name match: entities seen in at least one run (union), in all n runs, the difference (the set to review), the coverage of the union at 10 runs, and the "false stable" entities (in all n runs but not in all 10).

Core (entities with a proper name), 264 distinct entities in total, 243 present in all 10 runs:

| n runs | Union | In all n | To review | Coverage | False stable |
|---|---|---|---|---|---|
| 3 | 260.8 | 247.6 | 13.2 | 0.988 | 4.6 |
| 5 | 262.6 | 245.3 | 17.3 | 0.995 | 2.3 |
| 7 | 263.3 | 244.1 | 19.2 | 0.997 | 1.1 |
| 10 | 264.0 | 243.0 | 21.0 | 1.000 | 0.0 |

Periphery (generic mentions), 296 distinct, 160 present in all 10 runs, 32 present in one run only:

| n runs | Union | In all n | To review | Coverage | False stable |
|---|---|---|---|---|---|
| 3 | 260.1 | 185.4 | 74.7 | 0.879 | 25.4 |
| 5 | 275.4 | 173.2 | 102.2 | 0.931 | 13.2 |
| 7 | 285.3 | 166.2 | 119.0 | 0.964 | 6.2 |
| 10 | 296.0 | 160.0 | 136.0 | 1.000 | 0.0 |

- **Core:** 3 runs already cover 98.8% of the entities seen in 10 runs; 5 runs cover 99.5%. Going from 5 to 10 runs finds about 1.4 more entities over 11 protocols and adds 4 to the review set.
- **Core, what varies:** 25 name groups are not in all 10 runs (some are variants of the same entity, for example "Provincia di Massa Carrara" and "Amministrazione provinciale di Massa Carrara"). 17 of the 25 are `solo_citato`: provinces of Trento and Bolzano, Consiglio and Giunta Regionale della Toscana, Banca d'Italia, a European society, RELIVE, WWP EN, O.M.S. The signatories that vary are the Provincia di Massa Carrara (6 of 10), the Procura della Repubblica di Siena (5 of 10) and the Consigliera di Parità di Lucca (8 of 10).
- **Periphery:** does not converge. The union keeps growing with n (260 → 296), and with 3 runs a quarter of the mentions that look unanimous are not unanimous in 10. The presence of a generic mention in all runs is not a reliable criterion; a frequency threshold is more meaningful, once the counting rule for the periphery is decided.

## 5. Findings so far

- The two-container design (named entities vs generic mentions) is what stabilises the core. Core Jaccard is 0.92–0.96 across prompts and inputs.
- The prompt changes between v1 and v1.2 move which entities are in the core, not how stable they are. Each of v1.1 and v1.2 was checked by listing the entities that appear or disappear, not only by stability.
- Text and PDF give the same core on Toscana. The PDF recovers signatories on scanned protocols and costs 4.5 times the tokens.
- Name variants account for a large part of what looks like instability. The matching rule matters for the figures and must be fixed before the final runs.

## 6. Annotation (planned)

Manual validation by two annotators (Paolo, Elena), blind to the questionnaire, on the publication sample.
- **Sample.** The first sample (36 protocols, Toscana in full) is withdrawn: treating Toscana as the development set and including it entirely was arbitrary. The new sample is stratified by region and, within region, by protocol length. It is used both to fix prompt, number of runs and metrics, and for manual validation. Size and draw: `campione/README.md`. The old files are in `archivio/annotazione_campione_v1/`.
- **Review of stage 1.** For each protocol in the sample: entities not present in all runs, entities with unstable role, possible duplicates and a random share of the unanimous ones (`revisione_enti.py`). Decisions: ok / remove / merge, optional final name and role.
- **Independent annotation.** Entities named in the protocol, listed by the annotators without seeing the AI list, on a subset. It measures recall and agreement between annotators.
- **Planned measures.** Precision of the unanimous and of the non-unanimous entities; missing entities; agreement between annotators; agreement on the 30 categories (stage 2).
- **Status.** Not started. The definitions in `docs/definizioni_soggetti_v1.md` are being checked by the annotators.

## 7. Next steps

1. Improve the merge of chunk lists (duplicates of the same entity), then repeat E8 on more long protocols of the sample.
2. Check in the text the open points of v1.2: Banca d'Italia in 0906, RELIVE, WWP EN and WHO.
3. Freeze the prompt and parameters (`parametri/`, a commit and a tag), draw the sample, run stage 1 on all 251 texts with 5 runs (chunked above 40,000 characters). Report stability and core vs periphery on all protocols; manual review on the sample.
4. Annotation results, then stage 2 and stage 4.
5. Open decisions: counting rule for the periphery; whether the number in item 2.2 counts only core entities; Unione dei Comuni as category 3 or 8; whether respondents tick more than one category.

## 8. Reproduce

```
python codice/pipeline_ai_v2/stadio1_estrazione.py --regione Toscana --runs 3 --input testo --prompt v1_2
python codice/pipeline_ai_v2/stadio1_estrazione.py --regione Toscana --runs 3 --input pdf --prompt v1_2 --max-mb 4.1
python codice/pipeline_ai_v2/stadio1_spezzato.py --codici 0902,0911 --runs 3 --prompt v1_2
python codice/pipeline_ai_v2/stabilita_tollerante.py --tag v1_2_testo [--contenitore menzioni_generiche]
python codice/pipeline_ai_v2/confronta_prompt.py --a v1_1_testo --b v1_2_testo
python codice/pipeline_ai_v2/n_run_campionamento.py --tag v1_2_testo [--contenitore menzioni_generiche]
python codice/pipeline_ai_v2/registro_misure.py
```
Run files are in `microdati/ai_v2/stadio1/<tag>/` (not in git). The v0 runs are in the folders `testo` and `pdf`.
