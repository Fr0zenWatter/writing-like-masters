# Scholar Style Distillation Lite Skill
## Minimum Non-Temporal TeX-to-Style Protocol

> **Purpose**
> Read a prepared local collection of native TeX papers and produce a concise,
> practical description of the scholar's writing style. Focus on notation,
> vocabulary, syntax, paragraph organization, rhetorical flow, and LaTeX habits.
> Do not analyze career stages or stylistic evolution over time.

Use this protocol when the user wants a fast, usable style summary rather than
an exhaustive, auditable reconstruction of the author's evolving style.

---

# 1. Scope and Boundaries

Start only from an existing prepared corpus:

```text
<repository_root>/corpora/<author-slug>/
|-- corpus_manifest.csv
`-- tex/
    `-- <paper_id>/
        |-- metadata.json
        `-- source/
            `-- <canonical_main>.tex
```

This stage must not:

- search the web or download papers;
- convert or inspect PDFs;
- replace excluded papers;
- modify, rename, or reorganize source TeX;
- build a career timeline or classify early, transitional, mature, weakening,
  or abandoned traits;
- perform an exhaustive census of every math span or symbol occurrence.

Use only accepted native-TeX rows from `corpus_manifest.csv`. Resolve
`\input` and `\include` only inside the corresponding paper directory. Treat
one paper as one sample even when it contains several TeX components.

Skip a paper if its canonical main file is missing, a required component is
missing, or the readable content is dominated by template code. Record the
reason in the evidence file; do not acquire a replacement.

---

# 2. Sample Selection

The goal is representative reading, not corpus-wide enumeration.

- With 3-10 usable papers, read all of them.
- With more than 10 usable papers, select 6-10 representative papers.
- Prefer sole-authored papers, complete sources, several paper types or topics,
  and more than one coauthor configuration when available.
- Do not select or weight papers by date, and do not infer temporal change.
- With fewer than 3 usable papers, produce a clearly labeled provisional style.

For each sampled paper, inspect the resolved source as a whole. At minimum read:

- preamble and author-defined macros;
- abstract and introduction;
- notation or definition blocks;
- at least one central theorem/result and its surrounding proof or explanation;
- conclusion or final discussion when present;
- section headings, labels, references, and transitions.

Ignore bibliography contents, publisher boilerplate, comments, TODO material,
and formatting code that does not reflect authorial writing decisions.

---

# 3. Outputs

Create only:

```text
<corpus_directory>/STYLE_EVIDENCE_LITE.md
<repository_root>/styles/<author-slug>.txt
```

Do not create a `.style_analysis/` tree, a full symbol-census JSON file, or
separate paper fingerprints.

`STYLE_EVIDENCE_LITE.md` must contain five compact sections:

```text
1. Corpus scope, selected papers, and exclusions
2. One short observation card per selected paper
3. Cross-paper findings by style dimension
4. Exact native-TeX specimens with source locations
5. Final-rule evidence, confidence, and limitations
```

An observation card should normally be one table row or one short paragraph.
It must cover only the strongest observations needed for synthesis.

---

# 4. Required Style Dimensions

Analyze the following seven dimensions. Prefer qualitative, source-backed
patterns over large statistical inventories.

## 4.1 Mathematical Notation

Identify recurring choices for:

- object classes and letter/font families;
- indices, modifiers, operators, relations, and delimiters;
- notation introduction and local scope;
- equation construction and numbering;
- custom semantic macros.

Do not enumerate every occurrence. Sample notation from definitions, theorem
statements, representative proofs, and recurring macros. Never infer a fixed
meaning from frequency alone. If a symbol changes meaning between papers,
state that meanings are local and preserve only the transferable construction.

## 4.2 Prose-Math Interface

Observe how prose introduces a symbol or display, explains it afterward,
states assumptions, supplies intuition, and refers back to equations or named
results. Record recurring sequences such as:

```text
motivation -> definition -> formal statement -> consequence
```

## 4.3 Vocabulary and Claim Strength

Record functional preferences for:

- prove/show/claim/conjecture/assume;
- hedging and qualification;
- inference and contrast;
- definitions and reminders;
- limitations and contributions.

Describe decisions, not just word counts. Distinguish proved statements from
proposals, heuristics, assumptions, citations, and open questions.

## 4.4 Sentence Architecture

Identify typical clause order, information placement, active or impersonal
voice, first-person usage, parentheticals, enumeration, and sentence rhythm.
Approximate metrics may guide reading, but they are optional and must not be
presented as exact prescriptions.

## 4.5 Paragraph Organization

Identify what one paragraph normally accomplishes, how it opens and closes,
where qualifications appear, and how mathematical proof steps are separated.
Recover 3-6 reusable paragraph patterns rather than cataloguing every paragraph.

## 4.6 Rhetorical and Section Flow

Summarize the author's common moves in introductions, definitions, theorem
presentation, proofs, conclusions, and transitions. State how the text moves
from problem to result and from one proof obligation to the next. Cover only
section types actually represented in the sample.

## 4.7 LaTeX Habits

Record useful semantic practices involving macros, theorem environments,
equation environments, labels, references, citations, lists, and document
structure. Exclude obsolete font machinery, manual spacing, publisher code,
and other template artifacts from the transferable style.

---

# 5. Evidence Rules

First summarize each sampled paper, then compare papers. A long paper must not
receive more author-level votes merely because it contains more text or math.

- A firm author-level rule normally needs support from at least 3 papers.
- A pattern supported by 2 papers may be written as conditional.
- A one-paper pattern should be omitted or labeled paper-specific.
- Do not promote a pattern confined to one obvious topic, coauthor group, or
  document template as a universal authorial rule.
- Prefer rules that remain useful for producing new writing.

Do not copy source prose. Abstract it into move sequences, paragraph engines,
or executable guidance such as:

```text
WHEN: a new technical object is needed
DO: state its type and ambient assumptions before the defining display
AVOID: introducing several unexplained symbols inside the theorem statement
WHY: the sampled papers keep the local namespace recoverable
```

## Exact TeX Specimens

Retain normally 12-24 compact native-TeX specimens across the sample; use
fewer when the corpus does not support that many without padding. Suitable
specimens include symbols, short families, macro invocations, compact
definitions, and short equation skeletons.

For every retained specimen:

1. preserve the exact source spelling;
2. record paper ID, source path, and line number in `STYLE_EVIDENCE_LITE.md`;
3. verify the literal text in the original source;
4. read the surrounding definition or use before describing its role;
5. label it `DIRECT` when reusable for the same role or `ADAPT` when only the
   construction is transferable.

Do not include long equations, derivations, source sentences, or a
paper-specific symbol as an unexplained default.

---

# 6. Final Style File

Generate `<repository_root>/styles/<author-slug>.txt` after the compact evidence
file is complete. The TXT must be standalone and normally contain about
1,500-3,000 words unless the user requests another size.

Use this structure:

```text
AUTHOR STYLE LITE
=================

1. STYLE IDENTITY
2. GLOBAL WRITING PRINCIPLES
3. MATHEMATICAL NOTATION
4. PROSE-MATH INTERFACE
5. VOCABULARY AND CLAIM STRENGTH
6. SENTENCE ARCHITECTURE
7. PARAGRAPH ORGANIZATION
8. RHETORICAL MOVES AND SECTION FLOW
9. LATEX HABITS
10. DO / DO NOT AND REVISION CHECKLIST
```

Write primarily as executable guidance. Use `WHEN / DO / AVOID / WHY` where it
adds clarity, but do not force every observation into that template. Include
only verified compact TeX specimens. Do not include a maturity model, career
periods, temporal labels, or claims that one period represents the author
better than another.

---

# 7. Completion Check

```text
[ ] Only accepted native-TeX papers were used.
[ ] The selected sample follows the size and representativeness rules.
[ ] Every selected canonical main file and required component is readable.
[ ] No network search, PDF processing, replacement acquisition, or source edit occurred.
[ ] STYLE_EVIDENCE_LITE.md contains all five required sections.
[ ] All seven style dimensions are covered when the corpus supports them.
[ ] Firm rules have support from at least three papers; weaker rules are qualified.
[ ] Every exact TeX specimen was located and checked in its original source.
[ ] The final TXT contains all ten sections and is standalone.
[ ] No temporal-evolution or maturity analysis was introduced.
[ ] The output language, length, encoding, and any required prefix are correct.
```

---

# 8. Invocation Template

```text
Use SCHOLAR_STYLE_DISTILLATION_LITE_SKILL.md.
Repository root: <repository_root>.
Author slug: <author-slug>.
Prepared corpus: <repository_root>/corpora/<author-slug>.
Do not search for or download papers. Use native TeX only.
Generate compact evidence at:
<repository_root>/corpora/<author-slug>/STYLE_EVIDENCE_LITE.md.
Generate the final style at:
<repository_root>/styles/<author-slug>.txt.
Do not perform temporal analysis.
Output language: <language>.
Required prefix: <optional verbatim text>.
```
