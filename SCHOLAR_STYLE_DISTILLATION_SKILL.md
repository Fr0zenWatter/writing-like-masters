# Scholar Style Distillation Skill
## An Authorial Writing Style Distillation Protocol Based on “Temporal Evolution × Spatial Layers”

> **Purpose**
> Use this file only with a prepared local collection of <code>.tex</code> files by the target scholar. Run <code>SCHOLAR_TEX_ACQUISITION_SKILL.md</code> separately when sources must be found or downloaded.
> Codex should not merely imitate sentences. It should recover the author's **writing decision system** from the usable corpus and ultimately generate:
>
> <code>&lt;repository_root&gt;/styles/&lt;author-slug&gt;.txt</code>
>
> This TXT file should function as an “author writing skill”: short enough to remain loaded over time, specific enough to guide real writing, and abstract enough not to depend on the substantive content of any single paper.

---

# QUICK MODE: Minimum Viable Style Distillation

Use this mode when the user asks for a minimum working style extraction. This mode starts from a prepared local TeX corpus. It performs no online search, author discovery, source download, archive extraction, or replacement-paper collection.

If TeX must first be acquired, finish <code>SCHOLAR_TEX_ACQUISITION_SKILL.md</code> and then pass its output directory to this skill. The prepared corpus is the read-only source interface; the final style is published separately from disposable corpus data.

Quick Mode replaces the full protocol's separate fingerprint and synthesis files with one consolidated evidence file. It does not relax mathematical fidelity, temporal reasoning, authorship attribution, the eight spatial layers, or the required 18-section structure of the final style file.

## S1. Prepared-Corpus Input

Preferred input layout:

~~~text
<corpus_directory>/
|-- corpus_manifest.csv
|-- exclusions.md
`-- tex/
    `-- <paper_id>/
        |-- metadata.json
        `-- source/
            |-- <canonical_main>.tex
            `-- <required_components and other original source files>
~~~

In a repository checkout, use these canonical paths:

~~~text
<repository_root>/corpora/<author-slug>/
<repository_root>/styles/<author-slug>.txt
~~~

Use the same stable lowercase kebab-case <code>author-slug</code> chosen during acquisition. Keep evidence and other reproducible intermediates with the ignored corpus; keep only the standalone final style in <code>styles/</code> for Git publication. Use a different final output directory only when the user explicitly requests one.

The manifest should contain one row per candidate paper and identify at least:

~~~text
paper_id, year, title, authors, canonical_main,
required_components, include_in_style, exclusion_reason,
conversion_method, conversion_quality, evidence_weight
~~~

It may also contain source URL, source kind, hashes, venue, topic, coauthors, version information, <code>source_pdf</code>, <code>source_container_pdf</code>, and <code>conversion_warnings</code>. Read <code>metadata.json</code> for fields not present in the manifest.

If the user supplies only a local folder of TeX files, build an internal paper-level index from filenames and TeX metadata. Do not go online to fill missing fields. Unknown minor metadata may remain unknown.

## S2. Input Validation and Scope

1. Read only rows with <code>include_in_style=true</code>.
2. Verify that each accepted paper has one canonical main TeX file.
3. Resolve <code>\input</code> and <code>\include</code> only inside that paper directory.
4. Treat one paper as one sample even when it has multiple required TeX components.
5. Skip a paper when its main file is absent, a required dependency is missing, the archive contains inseparable drafts or rebuttals, or the text is dominated by external template material.
6. Record newly discovered exclusions in <code>STYLE_EVIDENCE.md</code>. Do not download a replacement in this stage.
7. Never modify source TeX files during analysis.
8. Treat <code>conversion_method=native-tex</code> as source-fidelity weight <code>1.00</code>. For PDF-derived LaTeX, apply the recorded <code>evidence_weight</code>, capped at <code>0.45</code> for text-layer conversion and <code>0.25</code> for OCR.
9. Use PDF-derived LaTeX only for recoverable prose, paragraph movement, claim calibration, and rhetorical structure. Do not use it as evidence for notation, equations, LaTeX commands, environments, page layout, typography, or fine punctuation.
10. Exclude <code>pdfuncertain</code> blocks, <code>[unreadable]</code> spans, repeated headers and footers, page numbers, and conversion boilerplate from style statistics.

If at least nine usable papers remain, select or use 9-12 papers spanning early, middle, and recent work, normally 3-4 from each part of the timeline. Prefer sole-authored samples and repeated traits across different coauthors, topics, or venues. If 5-8 papers remain, use all and mark temporal conclusions as limited. With fewer than five papers, generate only a provisional recent style and state that maturity cannot be established.

## S3. Quick-Mode Outputs

Write only these new files, split between the disposable evidence workspace and the publishable style directory:

~~~text
<corpus_directory>/STYLE_EVIDENCE.md
<repository_root>/styles/<author-slug>.txt
~~~

Do not reorganize, rename, or duplicate the prepared corpus. Do not create the full <code>.style_analysis/</code> tree in Quick Mode. Do not place the final style file inside <code>corpora/</code> in the canonical repository workflow.

<code>STYLE_EVIDENCE.md</code> must contain:

~~~text
1. Corpus scope and exclusions
2. One compact fingerprint block per accepted paper
3. Early / transition / mature evidence, or a provisional timeline
4. Per-paper typed symbol censuses and the corpus-level symbol registry
5. Symbol grammar, collision map, and exact native-TeX specimen bank
6. The eight-layer temporal matrix
7. Stable traits
8. Mature or recent supported traits
9. Weakening or abandoned traits
10. Coauthor, venue, and topic effects
11. Evidence map for rules selected for the final style file
12. Confidence and limitations
~~~

Each compact fingerprint must cover metadata and section map; a typed mathematical-symbol census with exact native-TeX specimens; prose-math interface; vocabulary and claim calibration; sentence and paragraph structure; rhetorical and discourse moves; flow and transitions; LaTeX choices; and possible temporal or attribution effects. In a notation-rich corpus, the symbol census is mandatory and must not be compressed into a few anecdotal examples.

## S4. Evidence Thresholds

Compute paper-level summaries before cross-paper comparisons so a long paper cannot dominate.

- Promote a trait to a firm author-level rule only when it appears in at least three accepted papers and survives either a time change or a change of coauthor, topic, or venue.
- Express a trait as conditional when it appears in at least two papers but is tied to a section, period, topic, coauthor, or venue.
- Omit a single-paper trait from the final style file unless it is needed as an overfitting warning.
- Do not infer a fixed meaning for a mathematical symbol from frequency alone.
- Do not call the latest period mature unless several spatial layers show convergence.
- A PDF-derived paper counts as a separate paper only for the prose traits it recovers. Scale its support by <code>evidence_weight</code>; a rule supported only by PDF conversions remains provisional.
- Promote notation, equation, macro, environment, or layout traits only from native TeX evidence.
- Preserve every recoverable native-TeX symbol occurrence in the evidence-stage inventory before selecting author-level rules. Frequency may rank candidates, but semantic definitions, local scope, object type, and cross-paper recurrence determine the rule.
- A compact TeX specimen may be copied exactly into the final style file when it demonstrates a supported notation rule. This exception applies to symbols, symbol clusters, macro invocations, short definitions, and short equation skeletons—not to source prose or long derivations.

## S5. Final Generation

Generate <code>&lt;repository_root&gt;/styles/&lt;author-slug&gt;.txt</code> only after <code>STYLE_EVIDENCE.md</code> is complete. Follow all 18 required sections in this skill. Express the result primarily as executable rules:

~~~text
WHEN: research situation or discourse need
DO: authorial decision
AVOID: competing choice rejected by evidence
WHY: mathematical or rhetorical function
~~~

The final file must:

- begin with any user-supplied required prefix verbatim;
- remain standalone without the corpus or evidence file;
- contain approximately 4,000-10,000 words unless the user specifies another size;
- distinguish proved, proposed, heuristic, assumed, cited, and numerical statements;
- cover all eight spatial layers and all required section models;
- make <code>4. MATHEMATICAL NOTATION</code> the largest or joint-largest operational section when the corpus is notation-rich;
- include a substantial, typed set of exact native-TeX symbol specimens, normally 30-80 distinct compact specimens when the corpus supports that many, without padding or manufacturing examples;
- prefer stable identity plus mature or recent supported practice;
- exclude copied source sentences, unmarked paper-specific notation, venue boilerplate, and unsupported claims about style. A paper-specific symbol may appear only as a labeled <code>ADAPT</code> or <code>LOCAL_ONLY</code> specimen that illustrates a transferable rule; it must not be presented as the author's default symbol for a new topic.

## S6. Completion Check

~~~text
[ ] No network acquisition was performed by this stage.
[ ] Every included paper has a readable canonical main TeX file.
[ ] Excluded papers do not enter statistics.
[ ] Native and PDF-derived samples use their recorded source-fidelity weights.
[ ] PDF-derived uncertainty blocks and conversion artifacts do not enter style evidence.
[ ] STYLE_EVIDENCE.md covers every accepted paper and all eight layers.
[ ] Every native-TeX paper has a typed symbol census, including custom macro forms and definition context where recoverable.
[ ] The corpus-level symbol registry distinguishes stable rules from topic-local mappings and symbol collisions.
[ ] Firm rules have multi-paper evidence.
[ ] The final style file contains all 18 required sections.
[ ] In a notation-rich corpus, MATHEMATICAL NOTATION is the largest or joint-largest operational section and contains exact TeX specimens.
[ ] A supplied prefix matches exactly.
[ ] The final language, word count, and encoding are valid.
[ ] No source TeX file was changed.
~~~

## S7. Invocation Template

~~~text
Use SCHOLAR_STYLE_DISTILLATION_SKILL.md in Quick Mode.
Repository root: <repository_root>.
Author slug: <author-slug>.
Prepared corpus: <corpus_directory>.
Do not search for or download papers.
Generate <corpus_directory>/STYLE_EVIDENCE.md.
Generate the final style at <repository_root>/styles/<author-slug>.txt.
Output language: <language>.
Required prefix: <optional verbatim text>.
~~~

---

# 0. Core Objective

Do not reduce authorial style to frequent words, elegant sentences, or average sentence length.

The real task is to recover:

> In a given research situation, and for a given function, what language, syntax, rhetorical move, paragraph structure, discourse organization, mathematical notation, equation narrative, and LaTeX expression does the author choose?

The author must also be treated as a **system that evolves over time**.

The objective is not:

~~~text
Style = the average style across all papers
~~~

Instead:

~~~text
Mature authorial style
=
stable identity traits across periods
+
advanced traits formed and retained in the mature period
+
task- and section-specific habits
-
early habits later abandoned by the author
-
noise clearly attributable to coauthors, venues, or individual papers
~~~

---

# 1. Overall Analytical Coordinate System

Analyze the corpus simultaneously along two dimensions.

## 1.1 Temporal Axis

First place each paper on the author's career trajectory.

Do not assume that newer is necessarily better.

Infer the following periods from the corpus:

- Formation Period;
- Transition Period;
- Mature Period;
- if needed, further divide the mature period into Mature I and Mature II.

For every stylistic feature, determine which of the following categories applies:

~~~text
STABLE
Persists across periods and forms part of the author's identity.

EMERGING
Weak or absent early, then gradually develops.

INTENSIFYING
Present throughout, but clearly strengthened in the mature period.

WEAKENING
Prominent early, then gradually declines.

ABANDONED
Present early, but largely discarded by the mature period.

MATURE_ONLY
Appears in the mature period and is then retained consistently.

PAPER_SPECIFIC
Appears in only a small number of papers and should not be generalized.

COAUTHOR_SENSITIVE
Changes noticeably with coauthors.

VENUE_SENSITIVE
May be shaped by journal, conference, or length requirements.

TOPIC_SENSITIVE
Appears only for a particular class of research problems or methods.
~~~

---

## 1.2 Spatial Axis

Divide authorial style into eight layers:

1. Mathematical Notation Style;
2. Vocabulary Style;
3. Sentence Style;
4. Rhetorical Moves;
5. Paragraph Style;
6. Discourse Style;
7. Flow & Transitions;
8. LaTeX Style.

These eight layers are not independent.

Ultimately recover the following chain:

~~~text
Research situation
→ rhetorical goal
→ discourse position
→ paragraph function
→ sentence architecture
→ vocabulary choice
→ mathematical expression
→ LaTeX implementation
~~~

---

# 2. Input Corpus and File Management

Assume that multiple <code>.tex</code> files exist inside the supplied <code>corpus_directory</code>.

Use filenames, directory names, bibliography information, and body text to recover, in order of priority:

- paper year;
- paper title;
- author list;
- whether the paper is sole-authored;
- coauthors;
- section type;
- paper topic;
- theoretical, empirical, or methodological category;
- working-paper or published version;
- journal, conference, or book chapter, when identifiable.

If <code>metadata.csv</code>, <code>metadata.tsv</code>, or a similar file exists, read it first.

Build an internal table such as:

~~~text
paper_id
year
title
authors
solo_or_coauthored
coauthors
venue
paper_type
topic
version
tex_files
~~~

When one paper has multiple <code>.tex</code> files, recognize them as components of the same paper rather than treating them as independent samples.

When both working-paper and published versions exist, treat the pair as a particularly valuable local sample of temporal evolution.

---

# 3. Analytical Principles

## 3.1 Do Not Use Naive Frequency Counts

Do not classify an expression as authorial style merely because it appears often.

Whenever possible, evaluate every conclusion against:

- the number of papers in which it appears;
- the number of years it spans;
- whether it is concentrated under one coauthor;
- whether it is concentrated in one section;
- whether it is concentrated in one topic;
- whether the author later abandons it;
- whether it remains present in the mature period.

---

## 3.2 Do Not Copy Directly

The final style file must not become a repository of source sentences.

Abstract patterns such as:

~~~text
Concession → core claim → mechanism
~~~

Do not preserve large numbers of sentences such as:

~~~text
Although X, we argue that Y because Z.
~~~

A small number of phrase preferences may be recorded, but only to explain selection rules, not to make Codex repeat them mechanically.

---

## 3.3 Recover Decision Rules First

Express observations whenever possible in this form:

~~~text
WHEN:
Existing evidence supports one explanation but does not rule out a competing mechanism

DO:
Use suggest / is consistent with

AVOID:
demonstrate / establish

WHY:
At this level of evidence, the author tends to preserve uncertainty about the mechanism
~~~

Avoid observations such as:

~~~text
The author often uses suggest
~~~

---

# 4. Phase One: Build a Style Fingerprint for Each Paper

The separate files in Phases One through Three are required in full mode. In Quick Mode, consolidate the same analysis into <code>STYLE_EVIDENCE.md</code> as specified above.

Create an internal style fingerprint for every paper.

Recommended output location:

~~~text
<corpus_directory>/.style_analysis/fingerprints/
~~~

For example:

~~~text
<corpus_directory>/.style_analysis/fingerprints/2008_paper_name.md
~~~

Each fingerprint must contain at least:

~~~text
Metadata
Section map
Typed symbol census and exact native-TeX specimens
Symbol definitions, scope, reuse, and collisions
Modifier, index, operator, and delimiter grammar
Vocabulary
Sentence
Rhetorical moves
Paragraph
Discourse
Flow
LaTeX
Possible coauthor effects
Distinctive traits
Possible temporal significance
Confidence
~~~

Analyze only at this stage. Do not imitate yet.

---

# 5. Eight Spatial Layers × Temporal Evolution

---

# 5.1 Mathematical Notation and Symbol System

This is the first and highest-priority spatial layer. Treat notation as a typed, compositional decision system rather than as a miscellaneous list of frequent symbols.

The operational object is:

~~~text
SYMBOL SYSTEM
= typed symbol inventory
+ concept/role-to-symbol mappings
+ base-symbol and font conventions
+ modifier grammar
+ index grammar
+ operator, relation, and delimiter conventions
+ symbol introduction, scope, reuse, and collision policy
+ equation composition rules
+ prose–math integration
~~~

## Priority, Space Allocation, and Completion Gate

For a notation-rich corpus—normally one in which mathematical displays, inline notation, or author-defined math macros occur throughout most accepted papers—apply all of the following:

- devote approximately 30-40% of evidence-stage analysis to mathematical notation, symbol use, and the prose–math interface;
- devote approximately 25-35% of the final style file to <code>4. MATHEMATICAL NOTATION</code>, allowing up to 40% when notation is unusually central;
- make that section the largest or joint-largest operational section;
- normally include 30-80 distinct compact native-TeX specimens when the corpus supports them;
- do not reduce the symbol system to five or ten favorite symbols;
- do not pad the output, repeat equivalent specimens, or invent symbols merely to satisfy a target.

Do not generate the final style file until the typed inventory, cross-paper registry, grammar, collision analysis, and temporal analysis below are complete. If the corpus is genuinely light on notation, state that limitation and reduce these allocations rather than manufacturing evidence.

## Native-TeX Extraction and Specimen Policy

Notation evidence must come from native TeX. Scan inline math, display math, equation environments, theorem-like environments, and author-defined math macros. Resolve <code>\input</code> and <code>\include</code> within the accepted paper before building the inventory.

Use two passes:

~~~text
PASS A — MECHANICAL EXTRACTION
Enumerate math spans, symbol tokens, command spellings, modifiers, indices,
custom math macros, equation locations, and paper-level occurrence counts.

PASS B — SEMANTIC RESOLUTION
Read definitions and mathematical context to assign object class, semantic role,
domain meaning, scope, index ranges, collisions, and transfer status.
~~~

Do not substitute a handful of manually noticed formulas for Pass A. Prefer a TeX-aware parser or a reproducible tokenization pass when available. If malformed source, macro indirection, or parser limitations leave gaps, record them instead of silently treating the inventory as exhaustive.

For each specimen, preserve both forms when they differ:

~~~text
RAW_TEX       exact source spelling, such as a custom macro invocation
NORMALIZED_TEX canonical or expanded mathematical form used for comparison
~~~

Whitespace may be normalized for comparison, but <code>RAW_TEX</code> must remain recoverable. When a custom macro carries mathematical meaning, record both its invocation and its definition. Do not treat formatting commands, equation labels, counters, or template boilerplate as mathematical symbols.

It is explicitly permitted to copy compact notation specimens from native TeX into the final style file. Permitted specimens include:

- individual symbols and indexed or modified forms;
- short symbol families;
- operator and relation spellings;
- custom math macro invocations with a compact definition;
- short definitions and equation skeletons needed to demonstrate composition.

This permission does not extend to copied prose, complete long equations when a shorter skeleton suffices, long derivations, or topic-specific formula collections with no stylistic function.

Assign every final-file specimen one transfer label:

~~~text
DIRECT
A stable or mature mapping that may be reused when the same semantic role recurs.

ADAPT
A transferable construction pattern whose domain-specific base symbols or meanings must be replaced.

LOCAL_ONLY
A paper-specific specimen retained only to explain evidence, variation, or a collision. Never reuse it by default.
~~~

An exact specimen is evidence, not automatically a rule. Frequency alone never establishes meaning or transferability.

## Per-Paper Typed Symbol Census

Index every recoverable mathematical-symbol occurrence. The evidence file may aggregate repeated occurrences into one row, but it must retain occurrence counts and locations so that definitions, reuse, and collisions remain auditable.

Use one entry per distinct <code>symbol form × semantic role × scope</code>. Record at least:

~~~text
ENTRY_ID
PAPER_ID / YEAR / SECTION / LOCATION
RAW_TEX
NORMALIZED_TEX
BASE_SYMBOL
OBJECT_CLASS
SEMANTIC_ROLE
DOMAIN_MEANING
MODIFIER_STACK
INDEX_LIST
INDEX_ROLES_AND_RANGES
DEFINITION_OR_FIRST_USE
LOCAL_OR_GLOBAL_SCOPE
OCCURRENCE_COUNT_AND_LOCATIONS
CUSTOM_MACRO_DEFINITION
POSSIBLE_COLLISIONS
TRANSFER_LABEL
CONFIDENCE
~~~

Keep <code>SEMANTIC_ROLE</code> distinct from <code>DOMAIN_MEANING</code>. For example, “estimator” is a reusable semantic role; “estimated elasticity of labor supply” is a paper-local domain meaning.

## Object-Type Grammar

Classify symbols before comparing their visible forms. Recover the author's preferences for at least the applicable classes:

~~~text
scalar / constant
parameter / estimand / hypothesis
estimate / estimator
random variable / realization
vector / matrix / tensor
set / index set / event
space / class / sigma-algebra
function / map / functional
sequence / process
distribution / measure / probability law
operator / relation
error / residual / disturbance / noise
loss / objective / criterion
derivative / gradient / Hessian
bound / rate / asymptotic order
~~~

For each class, analyze Latin versus Greek letters, upper versus lower case, roman versus italic, bold versus arrow notation, calligraphic versus blackboard bold, and any stable pairing between related object classes.

Do not infer object type from typography alone. Verify it from definitions, surrounding prose, dimensions, operations, and later reuse.

## Cross-Paper Symbol Dictionary

Build the dictionary by semantic role, not only by visible character. Each candidate mapping must contain:

~~~text
CONCEPT_OR_ROLE
OBJECT_CLASS
PREFERRED_TEX
ATTESTED_ALTERNATIVES
DOMAIN_CONDITIONS
EXACT_TEX_SPECIMENS
DEFINITION_PATTERN
SUPPORTING_PAPERS_AND_PERIODS
COUNTEREXAMPLES_OR_COLLISIONS
TEMPORAL_STATUS
COAUTHOR / VENUE / TOPIC EFFECTS
TRANSFER_LABEL
CONFIDENCE
~~~

Keep three levels separate:

1. the complete per-paper inventory;
2. the cross-paper registry of observed mappings and conflicts;
3. the small set of stable, mature, or explicitly conditional rules suitable for new writing.

The final dictionary may be extensive, but it must not flatten these levels. If the same symbol has several meanings, create separate conditioned entries. If the same meaning receives several symbols, identify the context that selects among them.

## Modifier Grammar

Analyze modifiers compositionally as <code>base object + modifier + resulting semantic role</code>. Cover the forms actually present in the corpus, including when applicable:

~~~text
hat / widehat
tilde / widetilde
bar / overline
star / dagger
prime
superscript -1, T, top, or other operation markers
subscript 0 or other status markers
bold / boldsymbol / vector arrow
mathrm / mathsf / mathtt
calligraphic / blackboard bold / fraktur
parenthesized, bracketed, or nested modifier stacks
~~~

For every supported rule, state:

~~~text
BASE OBJECT TYPE → MODIFIER → RESULTING ROLE
ORDER WHEN MODIFIERS STACK
WHETHER THE RULE IS GLOBAL OR CONTEXT-DEPENDENT
EXACT NATIVE-TEX EXAMPLES
COLLISIONS AND EXCEPTIONS
~~~

Do not write universal claims such as “a hat means estimator” when the corpus uses hats for several roles. Express the rule conditionally and preserve counterexamples.

## Index Grammar

Infer index roles from definitions and quantification rather than guessing from particular letters. Classify applicable roles such as:

~~~text
unit / individual / observation
time / period / lag
group / cluster / market / location
treatment / arm / state
coordinate / dimension / component
equation / constraint / moment condition
sample / fold / replication / bootstrap draw
iteration / algorithmic step
model / specification / layer
generic summation or enumeration index
~~~

Record:

- preferred letters for each role and their alternatives;
- declared ranges and index sets;
- free versus bound indices;
- the order of multiple subscripts and superscripts;
- comma use and grouping inside subscripts;
- whether fixed attributes precede or follow varying indices;
- how lags, leads, derivatives, versions, and iteration counts are distinguished;
- reuse or collision of an index letter across scopes.

Represent a multi-index rule explicitly, for example:

~~~text
WHEN: an object varies by <role A>, <role B>, and <role C>
DO: order indices as <A, B, C>, evidenced by <exact TeX specimens>
AVOID: competing order <...>
CONDITION: section, topic, or period if applicable
~~~

## Operator, Relation, and Delimiter Conventions

Do not combine all mathematical marks into one undifferentiated “operator style” list. Analyze separately:

~~~text
probability and expectation: P / Pr / \mathbb{P}, E / \mathbb{E}
indicators and characteristic functions
optimization: argmin / argmax / inf / sup
linear algebra: transpose / inverse / trace / determinant / rank
calculus: derivative / partial derivative / gradient / Hessian
norms, seminorms, absolute values, inner products, and brackets
independence, equality, approximation, equivalence, and ordering relations
convergence modes and asymptotic-order notation
distribution and law notation
set, measure, topology, and function-space operators
conditioning bars, evaluation bars, and “such that” separators
delimiter sizing and nesting
~~~

For each category, record semantic role, exact TeX spelling, argument order, delimiter behavior, subscript/superscript placement, definition policy, and contextual alternatives.

## Namespace, Scope, Reuse, and Collision Policy

Recover how the author manages a finite symbol namespace:

- where symbols are first defined;
- whether notation is global to the paper, local to a section, local to a proof, or local to one display;
- whether definitions are repeated after long gaps;
- whether the same base letter is reused after a scope closes;
- how nearby symbols are made visually distinct;
- how the author handles standard disciplinary notation that conflicts with a local object;
- whether symbol families are reserved for related concepts;
- whether one-use symbols are introduced or an expression is repeated directly;
- how symbols are renamed between general and special cases;
- whether appendices preserve or reinitialize the main-text namespace.

Create a collision map for both directions:

~~~text
ONE SYMBOL → MULTIPLE MEANINGS
ONE MEANING → MULTIPLE SYMBOLS
VISUALLY CONFUSABLE SYMBOLS USED NEARBY
CUSTOM MACRO → CHANGING EXPANSION OR MEANING
~~~

## Equation Architecture

Analyze:

- one-step presentation versus staged definition;
- general → special and abstract → instantiated movement;
- use of auxiliary objects and named intermediate quantities;
- compact versus modular form;
- number and type of new symbols introduced per equation;
- reuse of previously defined symbol families;
- organization and alignment of multiline equations;
- equation labeling, cross-reference, punctuation, and local explanation;
- how much derivation is retained in the main text;
- movement of algebra, regularity conditions, and proofs to appendices.

Preserve short exact equation skeletons when their architecture cannot be represented adequately by isolated symbols. Replace irrelevant long operands with typed placeholders only in <code>NORMALIZED_TEX</code>; retain the exact source in the evidence record.

## Notation Introduction and Lifecycle

Analyze patterns such as:

~~~text
Let X denote ...
We denote by X ...
Define X := ...
For each i in I, let ...
~~~

Also analyze:

- prose → symbol versus symbol → prose;
- definition operators such as <code>=</code>, <code>:=</code>, and <code>\equiv</code>;
- whether object type, dimension, domain, range, units, and index range are stated;
- whether an explanation or intuition follows immediately;
- whether related notation is introduced in one consolidated block or just in time;
- how notation is recalled, specialized, redefined, or retired;
- how symbols introduced in assumptions, theorems, proofs, figures, and tables enter the main namespace.

## Prose–Math Interface

Analyze:

~~~text
how equations are prepared in the preceding prose
how displayed symbols are read or interpreted afterward
whether every new object is defined
whether the object type and role are explicit
whether intuition is provided
whether the equation is tied back to the research problem
how prose avoids merely repeating the display
~~~

## Mathematical Narrative and Compression

Recover recurring mathematical move sequences such as:

~~~text
Motivation → Definition → Assumption → Lemma → Proposition
→ Corollary → Interpretation or empirical implication
~~~

Evaluate:

- information density per equation;
- new-symbol load and the rate of one-use symbols;
- auxiliary definitions;
- matrix, vector, function, or operator compression;
- when a family of symbols replaces repeated prose;
- when the author deliberately expands a compact expression for readability;
- movement of notation and technical detail to appendices.

## Convert Evidence into Executable Symbol Rules

Every promoted notation rule must use this contract:

~~~text
RULE_ID:
RULE_TYPE: object type / mapping / modifier / index / operator / scope / equation
WHEN: mathematical situation and semantic role
DO: authorial notation decision
AVOID: evidenced competing form
WHY: readability, type distinction, convention, or narrative function
EXACT_TEX_SPECIMENS: one or more compact native-TeX examples
SUPPORT: paper IDs, periods, and sections
COUNTEREVIDENCE: exceptions or collisions
TEMPORAL_STATUS: stable / emerging / intensifying / weakening / abandoned /
                 mature-only / paper-specific
ATTRIBUTION: author / coauthor-sensitive / venue-sensitive / topic-sensitive
TRANSFER: DIRECT / ADAPT / LOCAL_ONLY
CONFIDENCE: high / medium / low
~~~

Prefer a conditional rule with explicit scope over a falsely universal symbol definition.

### Required Temporal and Attribution Analysis

Determine:

- whether the typed symbol palette becomes more systematic over time;
- whether notation becomes simpler or merely more compressed;
- whether one-use symbols decline;
- whether object classes become more visually distinguishable;
- whether modifier and index grammars stabilize;
- whether collisions and redefinitions decline;
- whether intuition receives greater emphasis;
- whether technical detail increasingly moves to appendices;
- whether explanations before and after theorems change;
- which mappings or symbol families belong to particular topics or coauthors;
- whether a personal macro system or notation template emerges;
- whether a clear standard of mathematical narration emerges in the mature period.

### Required Evidence-Stage Outputs

In full mode, place these artifacts in the relevant fingerprint and synthesis files. In Quick Mode, give each a clearly labeled subsection in <code>STYLE_EVIDENCE.md</code>:

~~~text
PER_PAPER_TYPED_SYMBOL_CENSUS
CORPUS_SYMBOL_REGISTRY
TYPED_SYMBOL_PALETTE
SYMBOL_DICTIONARY
MODIFIER_GRAMMAR
INDEX_GRAMMAR
OPERATOR_RELATION_DELIMITER_POLICY
NAMESPACE_AND_COLLISION_MAP
EXACT_TEX_SPECIMEN_BANK
EQUATION_ARCHITECTURE
NOTATION_INTRODUCTION_AND_LIFECYCLE_POLICY
PROSE_MATH_INTERFACE
MATHEMATICAL_NARRATIVE
MATHEMATICAL_COMPRESSION_POLICY
MATHEMATICAL_STYLE_TRAJECTORY
~~~

<code>SYMBOL_DICTIONARY</code> contains conditioned concept/role mappings. The modifier, index, operator, and namespace outputs together constitute <code>SYMBOL_GRAMMAR</code>; do not use that label without supplying those components.

### Required Final-File Structure for Mathematical Notation

Section <code>4. MATHEMATICAL NOTATION</code> of the final style file must contain:

~~~text
4.1 Notation design principles
4.2 Typed symbol palette
4.3 Stable and conditional concept/role mappings
4.4 Modifier grammar
4.5 Index grammar
4.6 Operator, relation, and delimiter conventions
4.7 Namespace, scope, reuse, and collision rules
4.8 Notation introduction and lifecycle
4.9 Equation-composition rules
4.10 Exact native-TeX specimen bank
4.11 Temporal, topic, and coauthor qualifications
4.12 Notation DO / DO NOT checklist
~~~

The specimen bank should contain many compact examples when the evidence permits, grouped by rule and object type rather than dumped in source order. Each specimen must show its transfer label and a one-line semantic or grammatical gloss. The final section must remain usable without opening the corpus.

Use this compact final-file format:

~~~text
[RULE_ID] <rule title>
WHEN: <mathematical situation>
DO: <notation decision>
EXAMPLES:
- DIRECT | <exact RAW_TEX> | <object class → semantic role> | support: <papers/periods>
- ADAPT  | <exact RAW_TEX> | <transferable construction and what must change>
EXCEPTION:
- LOCAL_ONLY | <exact RAW_TEX> | <why it must not be generalized>
~~~

The placeholders above define the format only. All populated TeX specimens must come from the accepted native-TeX corpus.

---

# 5.2 Vocabulary Style

Analyze how the author selects words for different functions.

Cover at least:

- advancing a claim;
- reporting a finding;
- expressing causality;
- expressing association;
- hedging;
- boosting;
- contrast;
- progression;
- summary;
- introducing literature;
- identifying a gap;
- stating a contribution;
- explaining a mechanism;
- reporting robustness;
- stating a limitation;
- generalizing.

Focus on:

~~~text
Function → evidence strength → vocabulary choice
~~~

Compare near-synonyms such as:

~~~text
show / suggest / indicate / demonstrate
argue / propose / hypothesize / posit
extend / complement / challenge
because / thereby / consistent with
however / nevertheless / yet
~~~

### Required Temporal Analysis

Determine:

- which vocabulary preferences persist from the early to the mature period;
- which hedges increase or decrease with career maturity;
- whether claim strength changes;
- whether verbose academic boilerplate declines;
- whether the author increasingly prefers shorter, stronger, and more precise wording;
- whether efficient expressions specific to the mature period appear;
- whether coauthors materially change vocabulary choice.

Output:

~~~text
Stable vocabulary rules
Emerging vocabulary rules
Abandoned early vocabulary
Mature vocabulary preferences
Section-specific vocabulary
Claim-strength vocabulary
Coauthor-sensitive vocabulary
~~~

---

# 5.3 Sentence Style

Analyze:

- mean sentence length and its distribution;
- number of clauses;
- proportions of simple, compound, and complex sentences;
- active and passive voice;
- first-person and impersonal constructions;
- nominalization;
- attributive, adverbial, and appositive structures;
- parentheticals, parentheses, dashes, and semicolons;
- the number of rhetorical moves carried by one sentence;
- whether information focus appears at the beginning, in the main clause, in a subordinate clause, or at the end.

Abstract recurring sentence architectures such as:

~~~text
Concession → Claim → Mechanism

Method → Finding → Implication

Prior view → Missing condition → New question

Condition → Prediction → Reason

Result → Magnitude → Qualification
~~~

### Required Temporal Analysis

Determine:

- whether sentences become shorter or longer as the author matures;
- whether multilayer subordination declines;
- whether core claims become more direct;
- whether a rhythm of “long setup sentence + short landing sentence” emerges;
- whether sentences surrounding mathematical displays become more concise;
- which complex early syntactic patterns are later abandoned.

Output:

~~~text
Stable sentence architectures
Mature sentence architectures
Early abandoned architectures
Sentence rhythm rules
Information-placement rules
Claim sentence rules
~~~

---

# 5.4 Rhetorical Moves

Label what sentences and paragraphs are doing.

Include, but do not limit the analysis to:

- phenomenon;
- importance;
- consensus;
- literature classification;
- limitation;
- gap;
- puzzle;
- research question;
- concept definition;
- boundary;
- core claim;
- mechanism;
- hypothesis;
- competing explanation;
- setting;
- method;
- identification defense;
- result;
- interpretation;
- effect size;
- robustness;
- alternative explanation;
- qualification;
- generalizability;
- contribution;
- transition.

Analyze move sequences such as:

~~~text
Phenomenon
→ Importance
→ Existing explanation
→ Limitation
→ Puzzle
→ Core idea
→ Evidence
→ Contribution
~~~

### Required Temporal Analysis

Determine:

- whether the mature author reaches the puzzle more quickly;
- whether conventional, extended literature setup declines;
- whether the core mechanism appears earlier;
- whether the author increasingly anticipates reviewer objections;
- whether contribution lists become shorter but more precise;
- whether the author shifts from explaining an existing gap to redefining the problem;
- whether a stable mature-period rhetorical algorithm emerges.

Output:

~~~text
Stable rhetorical moves
Mature rhetorical algorithm
Early rhetorical habits later abandoned
Section-specific move sequences
Reviewer-defense patterns
~~~

---

# 5.5 Paragraph Style

Analyze:

- number of sentences per paragraph;
- position of the topic sentence;
- function of the first and final sentence;
- number of core claims assigned to one paragraph;
- distribution of citations;
- proportion devoted to explanation;
- position of qualifications;
- position of transitions.

Recover paragraph prototypes such as:

~~~text
Claim
→ Explanation
→ Evidence
→ Interpretation
→ Qualification
→ Transition
~~~

or:

~~~text
Existing view
→ Supporting basis
→ Missing issue
→ Consequence
→ Our entry point
~~~

### Required Temporal Analysis

Determine:

- whether paragraphs become shorter with maturity;
- whether paragraphs increasingly perform one task each;
- whether topic sentences become stronger;
- whether core claims move earlier;
- whether citations shift from scattered placement to clusters;
- whether explanatory tails decline;
- whether a stable mature-period “paragraph engine” emerges.

Output:

~~~text
10–20 paragraph prototypes
Stable prototypes
Mature prototypes
Abandoned early paragraph habits
Paragraph opening rules
Paragraph closing rules
~~~

---

# 5.6 Discourse Style

Analyze the following separately:

~~~text
Introduction
Literature Review
Theory
Methods
Results
Discussion / Conclusion
Appendix / Proof sections
~~~

## Introduction

Observe:

- whether the opening begins with a phenomenon, theory, event, or puzzle;
- how quickly it establishes importance;
- whether literature appears before or after the puzzle;
- when the core argument appears;
- whether the mechanism is developed in the introduction;
- how much of the method is introduced;
- how much of the results is reported;
- how many contributions are listed;
- whether a roadmap is included.

## Literature Review

Observe:

- whether literature is organized by theory, method, result, or chronology;
- citation clusters;
- how prior work is evaluated;
- how intellectual distance is constructed;
- whether the review forms a standalone section.

## Theory

Observe:

- the order of intuition, definitions, assumptions, and model;
- how many steps are used to develop the mechanism;
- setup length before a hypothesis;
- explanation before and after a theorem or proposition;
- use of special cases and examples.

## Methods

Observe:

- the order of data, sample, variables, and identification;
- the balance between method description and defense;
- allocation of technical detail between the main text and appendices.

## Results

Observe:

- the order of direction, significance, and magnitude;
- baseline, mechanism, heterogeneity, and robustness;
- how prose is organized before and after tables;
- how unexpected results are handled.

## Discussion / Conclusion

Observe:

- whether findings are restated;
- how the text returns to theory;
- contribution;
- limitation;
- generalizability;
- future research;
- final closure.

### Required Temporal Analysis

Analyze stylistic evolution separately for every section.

Do not assume:

~~~text
The mature period for the Introduction = the mature period for Theory
~~~

The author may mature first in:

~~~text
Theory exposition
~~~

and only later in:

~~~text
Introduction rhetoric
~~~

Output:

~~~text
INTRODUCTION_STYLE_TRAJECTORY
LITERATURE_STYLE_TRAJECTORY
THEORY_STYLE_TRAJECTORY
METHOD_STYLE_TRAJECTORY
RESULT_STYLE_TRAJECTORY
DISCUSSION_STYLE_TRAJECTORY
~~~

Identify the mature model separately for each.

---

# 5.7 Flow & Transitions

Analyze how sentences, paragraphs, and sections connect.

Include:

~~~text
Backward link
Forward link
Keyword carry-over
Old → new information
Bridge sentence
Transition strength
Question-driven transition
Contrast-driven transition
Mechanism-driven transition
~~~

Pay particular attention to:

~~~text
end of the previous sentence → beginning of the next sentence
end of the previous paragraph → beginning of the next paragraph
conclusion of the previous section → task of the next section
~~~

### Required Temporal Analysis

Determine:

- whether the mature period relies less on explicit connectives;
- whether conceptual continuity carries more of the flow;
- whether mechanical use of therefore, however, and similar terms declines;
- whether a distinctive bridge pattern emerges;
- whether section transitions become shorter and denser.

Output:

~~~text
Stable transition mechanisms
Mature transition mechanisms
Paragraph-pair patterns
Section-transition patterns
Overused early transitions to avoid
~~~

---

# 5.8 LaTeX Style

Analyze the following.

## Commands & Macros

- <code>newcommand</code>;
- <code>renewcommand</code>;
- <code>DeclareMathOperator</code>;
- semantic macros;
- formatting macros;
- macro naming;
- macro reuse;
- parameters.

## Math Typesetting

- <code>equation</code> / <code>align</code> / <code>gather</code> / <code>multline</code>;
- <code>\left</code> / <code>\right</code>;
- <code>bigl</code> / <code>bigr</code>;
- spacing;
- <code>aligned</code>;
- <code>cases</code>;
- punctuation;
- numbered versus unnumbered displays.

## Labels & References

- label naming;
- <code>eqref</code> / <code>ref</code> / <code>autoref</code>;
- prefixes;
- Equation versus Eq.;
- forward and backward references.

## Citation Coding

- <code>cite</code> / <code>citep</code> / <code>citet</code>;
- narrative citation;
- parenthetical citation;
- citation clusters;
- citation placement.

## Figures & Tables

- captions;
- labels;
- placement;
- first mention;
- prose before and after a table;
- tabular architecture.

## Document Architecture

- section depth;
- <code>input</code> / <code>include</code>;
- theorem environments;
- appendices;
- bibliography;
- TODO and revision commands.

### Required Temporal Analysis

Determine:

- whether the preamble stabilizes over time;
- whether macros are reused across papers;
- whether a personal template emerges;
- whether working-paper → published-version transitions simplify the source;
- whether formatting macros clearly decline in the mature period;
- whether semantic macros become more common;
- which LaTeX habits are clearly attributable to coauthors or venue templates.

Output:

~~~text
MACRO_DICTIONARY
MATH_TYPESETTING_FINGERPRINT
LABEL_REFERENCE_POLICY
CITATION_CODING_STYLE
FIGURE_TABLE_STYLE
DOCUMENT_ARCHITECTURE
LATEX_STYLE_TRAJECTORY
~~~

---

# 6. Phase Two: Build the Temporal Trajectory

After completing the fingerprint for every paper, do not generate the final style TXT immediately.

First create:

~~~text
<corpus_directory>/.style_analysis/STYLE_TRAJECTORY.md
~~~

This file must answer the following questions.

## 6.1 Career Periods

Identify:

~~~text
Formation Period
Transition Period
Mature Period
~~~

Subdivide further if necessary.

Period boundaries must come from evidence of stylistic convergence, not arbitrary years.

---

## 6.2 Temporal Change in Each Spatial Layer

Build the matrix:

~~~text
Layer | Formation | Transition | Mature | Stable Core | Abandoned Traits
~~~

Complete all eight layers.

---

## 6.3 Criteria for Maturity

Do not define maturity as:

~~~text
a later year
~~~

Look instead for:

- convergence of rhetorical structure;
- convergence of sentence rhythm;
- convergence of paragraph engines;
- convergence of notation discipline;
- convergence of section architecture;
- convergence of claim calibration;
- convergence of the prose–math interface;
- lower stylistic variance.

---

# 7. Phase Three: Separate Authorial Identity from Mature Style

Create:

~~~text
<corpus_directory>/.style_analysis/STABLE_TRAITS.md
<corpus_directory>/.style_analysis/MATURE_STYLE.md
<corpus_directory>/.style_analysis/ABANDONED_TRAITS.md
<corpus_directory>/.style_analysis/COAUTHOR_EFFECTS.md
~~~

---

# 7.1 STABLE_TRAITS.md

Retain only:

> Features that persist across periods and cannot readily be explained by coauthors.

These features constitute the author's stylistic identity.

---

# 7.2 MATURE_STYLE.md

Retain only:

> Rules that appear consistently in the author's mature period and are suitable for present-day imitation.

If an early feature later disappears, do not include it in the mature style.

---

# 7.3 ABANDONED_TRAITS.md

Record patterns with this trajectory:

~~~text
prominent early
→ weaker later
→ largely absent in the mature period
~~~

Actively avoid them in final writing.

---

# 7.4 COAUTHOR_EFFECTS.md

Analyze:

- sole-authored work;
- long-term recurring coauthors;
- one-time coauthors;
- vocabulary, notation, LaTeX, and structural changes associated with particular coauthors.

Do not misclassify clearly coauthor-specific style as the target author's own style.

---

# 8. Weighting Model

Do not apply a fixed mathematical formula mechanically, but use the following model to guide internal judgment:

~~~text
Effective Evidence Weight
=
Source Fidelity
×
Temporal Relevance
× Authorship Purity
× Section Match
× Trait Stability
× Representativeness
× Topic Relevance
~~~

## Layer Priority

The multiplicative model evaluates the strength of an individual observation; it does not determine how much analytical attention each layer receives. Mathematical notation has a separate priority rule:

~~~text
Notation-rich corpus:
mathematical notation + symbol system + prose–math interface
= approximately 30-40% of evidence-stage analysis

FINAL STYLE FILE:
MATHEMATICAL NOTATION
= approximately 25-35% of the final file, and the largest or joint-largest
  operational section
~~~

This allocation is a default for a notation-rich corpus, not permission to inflate weak evidence. Reduce it only when the accepted native-TeX corpus contains little mathematical notation, and record the reason.

Suggested conceptual weights follow.

## Source Fidelity

~~~text
Native TeX source                 1.00
PDF text-layer transcription    <=0.45
PDF OCR transcription           <=0.25
Insufficient conversion           0.00
~~~

Source fidelity constrains what a sample can establish. A PDF transcription may contribute to prose and rhetoric after conversion noise is removed. It cannot establish notation, equation layout, LaTeX practice, typography, or exact punctuation.

## Temporal Relevance

~~~text
Stable identity trait        1.00
Mature-period trait          1.00
Transition trait retained    0.60
Formation trait retained     0.40
Abandoned early trait        0.05
~~~

## Authorship Purity

~~~text
Sole-authored                high
Long-term collaborator       medium-high
One-off collaborator         medium-low
Strong coauthor signature    low
~~~

## Section Match

When writing an Introduction:

~~~text
Mature Introduction example     very high
Mature Theory example           low
Early Introduction example      medium-low
~~~

At all times:

> A mature sample from the same section carries more weight than a mature sample from a different section.

---

# 9. Phase Four: Generate the Final Style File

Finally generate the publishable file outside the disposable corpus:

~~~text
<repository_root>/styles/<author-slug>.txt
~~~

This file must:

- work as a standalone resource;
- remain understandable without <code>.style_analysis/</code>;
- be short enough to remain in context over time;
- be specific enough to guide actual writing;
- avoid copying source sentences;
- consist primarily of rules rather than descriptions.

Recommended target length:

~~~text
approximately 4,000–10,000 words
~~~

It may be somewhat longer if the author's style is unusually complex.

---

# 10. Required Structure of the Final Style File

The final TXT should follow this structure closely:

~~~text
AUTHOR STYLE SKILL
==================

1. STYLE IDENTITY
2. MATURITY MODEL
3. GLOBAL WRITING PRINCIPLES
4. MATHEMATICAL NOTATION
5. PROSE–MATH INTERFACE
6. MATHEMATICAL NARRATIVE
7. VOCABULARY RULES
8. SENTENCE ARCHITECTURE
9. RHETORICAL MOVE ALGORITHMS
10. PARAGRAPH ENGINES
11. SECTION MODELS
12. FLOW AND TRANSITION RULES
13. LATEX CODING STYLE
14. CLAIM-STRENGTH CALIBRATION
15. REVIEWER-DEFENSE BEHAVIOR
16. DO / DO NOT
17. SECTION-SPECIFIC CHECKLIST
18. SELF-REVISION PROTOCOL
~~~

---

# 11. STYLE IDENTITY

This section answers:

> If only 10–20 features could be retained, which features of this author's writing are most distinctive and indispensable?

Include only high-confidence stable traits.

---

# 12. MATURITY MODEL

Briefly explain:

~~~text
what the author tends to do early
what the author later removes
what emerges in the mature period
which period present-day imitation should prioritize
~~~

In final writing:

> Imitate the mature style, not the author's developmental process itself.

---

# 13. GLOBAL WRITING PRINCIPLES

Compress the author's style into high-level decision principles. For example:

~~~text
Explain why the problem exists before stating the contribution.

Place the core claim near the beginning of the paragraph.

Provide intuition before a complex equation.

Prefer one central rhetorical task per paragraph.

When the evidence is insufficient, reduce verb strength explicitly.

After each technical result, recover its economic or statistical meaning.
~~~

These are examples of form only. The actual content must come from the corpus.

---

# 14. Section-Specific Models

Generate separate rules for at least:

~~~text
Introduction
Literature Review
Theory
Methods
Results
Discussion / Conclusion
Proof / Appendix
~~~

For each section, specify:

~~~text
Purpose
Opening behavior
Typical move sequence
Paragraph sequence
Claim strength
Math density
Citation behavior
Transition behavior
Closing behavior
Common mistakes to avoid
~~~

---

# 15. How to Invoke the Final Style File During Writing

When Codex later writes a new paper:

## Step 1

Read:

~~~text
<repository_root>/styles/<author-slug>.txt
~~~

## Step 2

Identify the current task:

~~~text
section
paragraph type
rhetorical purpose
technical depth
claim strength
~~~

## Step 3

If necessary, retrieve only a small number of exemplars from the original corpus.

Priority:

~~~text
1. same section
2. mature period
3. sole-authored
4. representative
5. topic-relevant
~~~

Recommended number per request:

~~~text
3–6 exemplars
~~~

Do not reload the entire corpus for every request.

---

# 16. Writing Generation Principles

When generating new text, prioritize:

~~~text
imitating decision rules
> imitating discourse structure
> imitating paragraph engines
> imitating sentence architecture
> imitating vocabulary choice
> imitating surface phrases
~~~

Surface phrase replication matters least.

The central question is:

~~~text
What writing decision would the author make in this situation?
~~~

---

# 17. Prevent Overfitting

The final text must actively avoid:

- reproducing source sentences;
- mechanically repeating frequent phrases;
- allowing one paper to dominate;
- allowing the newest papers to dominate;
- allowing one coauthor to dominate;
- allowing one topic to dominate;
- mistaking journal templates for authorial style;
- mistaking disciplinary conventions in mathematics for individual style.

---

# 18. Confidence System

Internally mark important rules in the final style by confidence whenever possible.

Suggested levels:

~~~text
HIGH
Persists across multiple periods, papers, and coauthors.

MEDIUM
Appears in multiple papers but is conditional on section, topic, or coauthor.

LOW
Supported by limited samples and represents only a weak preference.
~~~

In the final style file:

- HIGH: express as a firm rule;
- MEDIUM: express as a conditional rule;
- LOW: generally omit unless it is important for a specialized section.

---

# 19. Self-Check Protocol

Before generating the final style file, perform the following checks.

## Temporal Check

~~~text
Have you mistakenly treated newer as better?
Have you identified formation, transition, and mature periods?
Have you distinguished stable traits from mature-only traits?
Have you recorded abandoned traits?
~~~

## Spatial Check

~~~text
Are all eight layers covered?
Have section differences been flattened incorrectly?
Has mathematical style received sufficient analysis?
Has LaTeX been analyzed separately?
~~~

## Symbol-System Check

~~~text
Has every native-TeX paper received a typed symbol census?
Can every promoted symbol meaning be traced to a definition or mathematical use?
Are semantic role and paper-local domain meaning kept separate?
Have modifier, index, operator, delimiter, namespace, and collision rules all been recovered?
Are identical symbols with different meanings represented as conditioned entries?
Are custom macro invocations connected to their definitions?
Does each final specimen have DIRECT, ADAPT, or LOCAL_ONLY status?
Does the final specimen bank contain exact TeX rather than invented illustrations?
Is MATHEMATICAL NOTATION the largest or joint-largest operational section when justified?
Has raw symbol volume been converted into executable rules rather than merely dumped?
~~~

## Authorship Attribution Check

~~~text
Have sole-authored and coauthored works been distinguished?
Have venue effects been considered?
Have topic effects been considered?
Have template effects been considered?
~~~

## Style Quality Check

~~~text
Can the rules directly guide writing?
Does the analysis remain overly descriptive or statistical?
Have WHEN → DO → WHY rules been recovered?
Can the rules generate genuinely new text?
~~~

---

# 20. Final Execution Instructions

If you are Codex and you read this file, first select Quick Mode or full mode. Quick Mode follows Sections S1-S7 and overrides separate intermediate-file requirements. In full mode, execute the following:

~~~text
1. Scan all relevant .tex files in corpus_directory and its subdirectories.
2. Identify paper boundaries, years, authors, sections, and version relationships.
3. Do not begin imitation immediately.
4. Build a style fingerprint for every paper.
5. Analyze all eight spatial layers, beginning with Mathematical Notation Style;
   mathematical expression and notation are the first and highest-priority layer.
6. For every native-TeX paper, build the typed symbol census and retain exact
   compact TeX specimens before synthesizing cross-paper notation rules.
7. Complete the symbol grammar, namespace and collision map, and temporal
   notation analysis before generating the final style file.
8. Track temporal evolution within every spatial layer.
9. Distinguish stable / emerging / intensifying / weakening /
   abandoned / mature-only / paper-specific /
   coauthor-sensitive / venue-sensitive / topic-sensitive.
10. Build STYLE_TRAJECTORY.
11. Identify formation, transition, and mature periods.
12. Build STABLE_TRAITS.
13. Build MATURE_STYLE.
14. Build ABANDONED_TRAITS.
15. Build COAUTHOR_EFFECTS.
16. Generate <repository_root>/styles/<author-slug>.txt only after the preceding work is complete.
17. The final style file must be a skill that directly guides future paper writing,
    not an analytical report.
18. Do not copy long source passages. Exact compact native-TeX notation
    specimens are permitted under the transfer-label policy in Section 5.1.
19. Support every high-level style rule with evidence from multiple papers.
20. When writing, prioritize:
    stable identity + mature style + same-section exemplars.
~~~

---

# 21. Final Goal

The final deliverable should answer more than:

~~~text
How does this author write?
~~~

It should be able to answer:

~~~text
In an Introduction gap paragraph,
how does this author typically move from existing consensus to a puzzle?

In a Theory section,
when does this author provide intuition first, and when does the author formalize immediately?

When evidence supports association but not causality,
how does this author calibrate claim strength?

When one equation introduces several new objects,
how does this author arrange prose → notation → equation → intuition?

When the mature author faces a potential reviewer objection,
where in the argument does the author preempt it?

When a new paragraph is needed,
which paragraph engine, sentence architecture, and vocabulary strength should be selected?
~~~

If the final style file can answer these questions consistently,
the author's style has been successfully distilled into an executable skill.
