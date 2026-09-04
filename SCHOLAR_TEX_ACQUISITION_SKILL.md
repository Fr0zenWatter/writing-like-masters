# Scholar TeX Acquisition Skill
## A Minimum Viable Protocol for Building a Prepared TeX Corpus

> **Purpose**
> Use this file to identify a scholar, locate public TeX source packages, download and validate a small representative corpus, and place it in one canonical local layout.
> This skill ends when the prepared corpus is ready. It does not analyze authorial style and does not generate <code>STYLE_EVIDENCE.md</code> or the published style file.

---

# 0. Output Goal

Produce one local corpus that can be passed unchanged to:

~~~text
SCHOLAR_STYLE_DISTILLATION_SKILL.md
~~~

The acquisition stage is responsible for:

~~~text
scholar identity
-> paper discovery
-> same-name disambiguation
-> TeX source download
-> optional PDF fallback conversion when explicitly enabled
-> safe extraction
-> paper and version deduplication
-> canonical main-file selection
-> dependency check
-> manifest and exclusion record
-> prepared corpus
~~~

It is not responsible for:

~~~text
style fingerprints
temporal style periods
writing rules
published final style
~~~

## Repository Storage Invariant

In a repository checkout, keep downloaded and generated acquisition material in one disposable workspace:

~~~text
<repository_root>/
|-- .acquisition_work/<author-slug>/    # discovery cache and candidate records
|-- corpora/<author-slug>/              # prepared corpus
`-- styles/<author-slug>.txt            # tracked final style, written by the next stage
~~~

Use a stable lowercase kebab-case <code>author-slug</code>. Unless the user explicitly selects another destination, set <code>output_directory</code> to <code>&lt;repository_root&gt;/corpora/&lt;author-slug&gt;</code>. Never create an author corpus directly at the repository root. An explicitly requested non-canonical destination may be used with the acquisition helper's <code>--allow-output-outside-corpora</code> flag.


# 1. Minimum Input

Accept these inputs:

~~~text
target_scholar: canonical name
identity_anchor: at least one strong anchor when available
field_or_topic: optional but useful for same-name disambiguation
repository_root: directory containing this workflow and scripts/
author_slug: stable lowercase kebab-case identifier
output_directory: normally <repository_root>/corpora/<author_slug>
paper_limit: default 30, with a normal target range of 20-30
~~~

A strong identity anchor may be an ORCID, MathSciNet author ID, official publication page, institutional profile, arXiv author page, or two confirmed paper titles.

If no formal identifier exists, combine at least two weaker signals:

- research field or recurring topic;
- institution or past affiliation;
- recurring coauthors;
- a confirmed paper title;
- a publication list linked from an official page.

Do not accept a paper on an author-name match alone when the name is ambiguous. Record uncertain papers as exclusions and continue with the confirmed corpus.


# 2. Corpus Size and Stop Rule

Build a representative corpus rather than an exhaustive archive.

- When at least 30 usable native-TeX papers exist, collect 30 papers.
- When 20-29 usable native-TeX papers exist, collect all of them.
- Cover early, middle, and recent work, normally allocating roughly one third of the corpus to each chronological part.
- Prefer sole-authored papers when available.
- Include more than one coauthor group, topic, or venue so later analysis can distinguish authorial style from local effects.
- Prefer a coherent current version of each paper.
- Count one paper once even if its source contains several required TeX files.
- Stop once the target range, timeline coverage, and attribution diversity are satisfied.

After arXiv, HAL, and Zenodo have all been searched, if fewer than 20 usable native-TeX papers exist, report the exact native-TeX count and ask whether PDF fallback should be enabled. Do not download PDFs before the user answers. If the user declines, collect the available native sources and mark the corpus limited. The style stage will decide whether only a provisional style can be inferred.

Do not prolong the run to rescue a small number of problematic papers. A missing source, broken dependency, inseparable mixed archive, or unresolved identity may be excluded.


# 3. Discovery and Disambiguation

Use a fast two-turn identity gate when the user initially supplies only a name:

1. Locate the single strongest public identity page, normally an official university profile, official personal homepage, ORCID record, or authoritative publication page.
2. Return its clickable URL with one short affiliation or field description and ask whether this is the intended scholar.
3. Do not start repository discovery or downloads until the user confirms.
4. After confirmation, treat that page as the identity anchor and search arXiv, HAL, and Zenodo in the same acquisition run.

If the proposed page is rejected, locate the next strongest candidate rather than presenting a long unfiltered person list.

Use discovery sources in this order when available:

1. an official or institutional publication list;
2. ORCID or MathSciNet author records;
3. exact-author searches in arXiv, HAL, and Zenodo after identity confirmation;
4. confirmed arXiv identifiers or repository records;
5. title searches used to locate source packages for already attributed papers;
6. a general author-name search, only with explicit disambiguation.

For every candidate, collect before downloading:

~~~text
title
authors
first public year
stable identifier, preferably arXiv ID or DOI
source or abstract URL
identity evidence
~~~

Accept the paper when one strong identity anchor or two independent weaker signals match. Check especially the field, coauthor network, affiliation, and overlap with the confirmed publication list.

Deduplicate records by stable identifier first and normalized title second. Treat a preprint and its published version as one paper unless the user explicitly wants revision comparison. In a default run, prefer the latest coherent TeX version whose authorship and title match the confirmed record.


# 3A. Automation Boundary

Use the language model for candidate discovery, identity disambiguation, representative selection, and decisions about mixed or contaminated manuscripts. Once the candidate list is confirmed, stop performing repetitive file operations manually.

For the normal three-repository workflow, run the reusable discovery helper located beside this skill before acquisition:

~~~text
python scripts/scholar_multisource_discover.py --author "<canonical name>" --official-url "<confirmed identity page>" --cache-dir .acquisition_work/<author-slug>/cache --output .acquisition_work/<author-slug>/candidates.json --limit 30
~~~

The helper queries arXiv, HAL, and Zenodo, filters exact author names, records PDF-only results without downloading them, deduplicates native-source candidates, and samples early, middle, and recent work. Review the resulting discovery report before downloading. Identity confirmation and ambiguous-author decisions remain model responsibilities.

Write a JSON array in which every candidate contains:

~~~text
paper_id, year, title, authors, source_url, source_kind
~~~

An item that is already known to be unusable may also contain <code>exclusion_reason</code>. Then run the reusable helper located beside this skill:

~~~text
python scripts/scholar_tex_acquire.py --candidates .acquisition_work/<author-slug>/candidates.json --output corpora/<author-slug> --target-scholar "<canonical name>" --identity-anchor "<identity evidence>" --discovery-sources "<sources consulted>"
~~~

The script performs bounded download retries, content sniffing, safe extraction, hashing, main-file scoring, local dependency traversal, metadata writing, manifest generation, exclusion reporting, timing, and resumable validation. Review its selected main files and manifest after it finishes. Do not delegate identity or authorial-attribution judgments to filename scoring.

When the user explicitly enables PDF fallback, run it only after the TeX acquisition pass:

~~~text
python scripts/scholar_pdf_to_latex.py --corpus corpora/<author-slug> --plan .acquisition_work/<author-slug>/pdf-conversion-plan.json
~~~

This keeps source acquisition and style inference separate. The PDF helper may extend the prepared corpus and manifest, but it must not generate <code>STYLE_EVIDENCE.md</code> or the published style file.


# 4. Source Acquisition

Use this source priority:

~~~text
1. User-provided or already local TeX source
2. Public arXiv source package for a confirmed paper
3. Public native-TeX attachment in HAL or Zenodo
4. Public TeX repository linked by the author or publisher
5. Public PDF converted to provenance-marked LaTeX, only when PDF fallback is explicitly enabled
6. Exclude when no usable source can be acquired
~~~

The default TeX-first mode does not reconstruct TeX from PDF. When the user explicitly enables PDF fallback, apply the rules in Section 4A and keep every converted paper at a lower evidence weight than native TeX.

For every remote source:

1. Record the source URL before download.
2. Download the original source response into the paper directory.
3. Compute SHA-256 for the downloaded package or standalone TeX file.
4. Detect whether the response is a tar archive, gzip stream, zip archive, or plain TeX; do not rely only on the filename extension.
5. Extract into a new, empty <code>source/</code> directory.
6. Reject archive entries whose resolved paths leave that paper directory.
7. Preserve filenames and source contents exactly.

If a request fails, retry only when the failure is plausibly transient. After two failed attempts for the same URL, record <code>download_failed</code> and continue. Do not substitute an unverified same-title or same-name paper.


# 4A. Optional PDF Fallback

Use PDF fallback only for a paper whose identity is already confirmed and for which no public TeX source has been found.

1. Preserve the downloaded PDF unchanged and record its SHA-256 digest and resolved URL.
2. Verify PDF content by file signature; do not trust an extension or HTTP content type alone.
3. When the source is a book or proceedings volume, locate the article by title and author, extract only its pages for conversion, and preserve the original container PDF.
4. Prefer an existing text layer. Use OCR only when the text layer is insufficient.
5. Generate <code>source/converted_from_pdf.tex</code> as a transcription with provenance comments. Mark formula-like or unreadable blocks as uncertain and direct the reader to the source PDF.
6. Never infer, repair, or silently normalize a mathematical formula that cannot be recovered reliably.
7. Require enough recoverable prose for style analysis. Otherwise retain the PDF, set <code>include_in_style=false</code>, and record <code>pdf_conversion_failed</code>.

Use these default source-fidelity weights:

~~~text
native TeX                         1.00
PDF with a usable text layer       0.45
PDF requiring OCR                  0.25
failed or insufficient conversion  0.00
~~~

These are upper bounds. A lower weight may be used when extraction quality is partial. PDF-derived LaTeX may support prose and rhetorical evidence. It is not authoritative evidence for mathematical notation, equations, macros, environments, page layout, or typography.


# 5. Canonical Main File and Dependencies

Identify one canonical main TeX file per accepted paper.

A main-file candidate normally contains:

~~~text
\documentclass and \begin{document}
or an older \documentstyle driver
or a clearly identifiable plain-TeX driver ending in \bye
paper title or matching author metadata
section structure or body inputs
~~~

When several candidates exist:

1. prefer the latest coherent manuscript version;
2. reject obvious response letters, rebuttals, cover letters, slides, posters, notes, examples, and journal templates;
3. compare title and author metadata with the confirmed record;
4. follow the local input graph and select the driver that reaches the research body;
5. exclude the paper when multiple drafts remain inseparable without substantive editorial judgment.

Resolve <code>\input</code> and <code>\include</code> recursively inside the paper directory. Record every TeX component required by the canonical main file. Ignore commented-out inputs. Never resolve a path outside the paper directory.

An accepted paper must have:

- one readable canonical main file;
- every required local TeX dependency used for the research body;
- enough title or author evidence to connect it to the confirmed paper;
- a source tree that can be analyzed without choosing among mixed research drafts.

Keep class files, style files, bibliography files, figures, and data present in the downloaded package. They are preserved for traceability even though the style stage may exclude them from prose statistics.


# 6. Exclusion Rules

Use <code>include_in_style=false</code> and a concrete reason when any of these applies:

- same-name author cannot be ruled out;
- only a PDF is available and PDF fallback was not enabled or did not recover enough prose;
- source download fails twice;
- the response is not a valid TeX source package;
- the canonical main file cannot be identified;
- a required TeX dependency is missing;
- old drafts, current drafts, rebuttals, notes, and templates are inseparably mixed;
- external group template or collaborator commentary dominates the recoverable manuscript;
- the record duplicates an already accepted paper.

Do not exclude merely because metadata such as venue, DOI, or publication year is missing. Store minor unknowns as <code>null</code>.

Do not repair native source prose, remove comments, normalize macros, or rewrite filenames during acquisition. PDF-derived files must remain clearly distinguishable from native source and must never replace it silently.


# 7. Canonical Acquisition Output

Write exactly this top-level layout under the canonical corpus directory:

~~~text
<repository_root>/corpora/<author-slug>/
|-- corpus_manifest.csv
|-- exclusions.md
|-- ACQUISITION_REPORT.md
|-- pdf_conversion_plan.json       # only when PDF fallback is enabled
`-- tex/
    `-- <paper_id>/
        |-- metadata.json
        |-- <original_source_package_or_pdf>
        `-- source/
            |-- <original extracted source tree, when native TeX>
            |-- <article.pdf, only when cropped from a PDF container>
            `-- <converted_from_pdf.tex, only for PDF fallback>
~~~

Do not create style-analysis files in this stage. Do not create empty administrative directories. Do not duplicate the source into separate raw and curated trees.

Use a stable paper ID:

~~~text
<author-slug>-<first-public-year>-<arxiv-or-local-id>
~~~

Examples of the identifier shape:

~~~text
ada-lovelace-2024-2401.12345
ada-lovelace-2021-doi-suffix
ada-lovelace-2019-local-01
~~~

The examples define form only. Never invent an identifier when a stable source identifier exists.


# 8. Manifest Contract

Create one row for every candidate paper, accepted or excluded. Use UTF-8 CSV with a header and proper quoting.

Required columns:

~~~text
paper_id
year
title
authors
source_url
source_kind
source_package
canonical_main
required_components
sha256
include_in_style
exclusion_reason
source_pdf
source_container_pdf
conversion_method
conversion_quality
evidence_weight
conversion_warnings
~~~

Rules:

- Paths are relative to <code>output_directory</code> and use forward slashes in the manifest.
- <code>authors</code> is a semicolon-separated display list inside one CSV field.
- <code>required_components</code> is a semicolon-separated relative-path list.
- <code>sha256</code> refers to the original downloaded package or standalone source file.
- <code>include_in_style</code> is exactly <code>true</code> or <code>false</code>.
- An accepted row has an empty <code>exclusion_reason</code>.
- An excluded row has a short machine-readable reason followed by a concise explanation.
- Native TeX rows use <code>conversion_method=native-tex</code> and <code>evidence_weight=1.00</code>.
- PDF-derived rows identify the converted article PDF in <code>source_pdf</code>, record the conversion method and quality, and use an evidence weight no greater than <code>0.45</code> for text-layer extraction or <code>0.25</code> for OCR.

Each accepted paper also receives <code>metadata.json</code> with the manifest fields and, when identifiable:

~~~text
solo_or_coauthored
coauthors
venue
topic
version
identity_evidence
notes
~~~

Unknown optional fields are <code>null</code>. Do not block completion on minor metadata.


# 9. Acquisition Report

Write <code>ACQUISITION_REPORT.md</code> as a short handoff document. Include:

~~~text
target scholar and identity anchor
discovery sources consulted
per-repository exact-author, native-TeX, and PDF-only discovery counts
download date
candidate count
accepted paper count
excluded paper count
year range
sole-authored and coauthored counts when known
topic or venue coverage when known
canonical-main and dependency validation result
known limitations
native-TeX and PDF-derived counts, methods, quality labels, and weights when fallback is enabled
absolute prepared-corpus path
~~~

Do not include style observations, vocabulary counts, temporal style periods, or prose recommendations.

Write <code>exclusions.md</code> as a compact table:

~~~text
paper_id | title | source | reason
~~~


# 10. Completion Validation

The acquisition stage is complete only when:

~~~text
[ ] The scholar identity and disambiguation anchor are recorded.
[ ] arXiv, HAL, and Zenodo discovery counts are recorded.
[ ] Every candidate has exactly one manifest row.
[ ] Every accepted row points to one existing canonical main TeX file.
[ ] Every recorded required component exists inside the same paper directory.
[ ] Every preserved source package has a verified SHA-256 value.
[ ] Every PDF-derived row preserves its source PDF and records conversion method, quality, warnings, and evidence weight.
[ ] Every PDF-derived mathematical block that is not reliably recovered is explicitly marked uncertain.
[ ] Duplicate papers count once.
[ ] Excluded papers have explicit reasons.
[ ] No excluded paper is marked include_in_style=true.
[ ] No source file was rewritten during acquisition.
[ ] No download or extraction temporary files remain.
[ ] STYLE_EVIDENCE.md and the published style file were not generated by this stage.
~~~

If fewer than 20 native-TeX papers are found, PDF fallback was explicitly offered before any PDF download. If the user declines, complete the acquisition report and label the corpus limited. Do not invent or substitute papers merely to pass a count threshold.


# 11. Handoff to Style Distillation

End the acquisition task with this concise report:

~~~text
Prepared corpus: <absolute output_directory>
Accepted papers: <count>
Excluded papers: <count>
Manifest: <absolute path>/corpus_manifest.csv
Acquisition report: <absolute path>/ACQUISITION_REPORT.md
Next stage: run SCHOLAR_STYLE_DISTILLATION_SKILL.md on this prepared corpus.
~~~

The style stage must treat the acquisition source tree as read-only input. It may add <code>STYLE_EVIDENCE.md</code> at the corpus root, but it writes the publishable final file to <code>&lt;repository_root&gt;/styles/&lt;author-slug&gt;.txt</code>. It must not download new papers or alter the source tree. It must also apply <code>evidence_weight</code> and the source-fidelity restrictions recorded for every PDF-derived row.


# 12. Invocation Template

~~~text
Use SCHOLAR_TEX_ACQUISITION_SKILL.md in three-repository TeX-first mode.
Target scholar: <canonical name>.
Identity anchor: <ORCID, MathSciNet ID, official page, or confirmed titles>.
Field or topic: <optional disambiguation context>.
Repository root: <repository_root>.
Author slug: <author-slug>.
Search arXiv, HAL, and Zenodo and build a 20-30 paper public TeX corpus in <repository_root>/corpora/<author-slug>.
Keep discovery caches and candidate records in <repository_root>/.acquisition_work/<author-slug>/.
If fewer than 20 native-TeX papers are found, ask before downloading any PDFs.
Skip a small number of unusable or ambiguous papers.
Stop after corpus_manifest.csv, exclusions.md, ACQUISITION_REPORT.md,
and the canonical tex/ tree are complete. Do not extract style.
~~~
