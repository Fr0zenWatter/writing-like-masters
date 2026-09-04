# Scholar Style Workflow

When asked to create a scholar style, run the two stages in order. Read the referenced skill file completely before executing that stage.

## 1. Acquire TeX only when needed

Skip acquisition when `corpora/<author-slug>/corpus_manifest.csv` and its accepted TeX sources already exist. Otherwise read `SCHOLAR_TEX_ACQUISITION_SKILL.md` and invoke it with:

```text
Target scholar: <canonical name>
Identity anchor: <confirmed official page, identifier, or titles>
Repository root: <repository_root>
Author slug: <lowercase-kebab-case>
Output: <repository_root>/corpora/<author-slug>
```

Confirm an ambiguous identity before downloading. Keep discovery work in `.acquisition_work/<author-slug>/`. Do not place an author directory at the repository root. Ask before PDF fallback. Stop after the prepared corpus, manifest, exclusions, and acquisition report are complete.

## 2. Choose and run the style distillation

After the corpus is ready, determine whether the user already selected a
distillation protocol. If not, ask one short question and wait before starting:

```text
请选择风格提炼方式：
1. 简洁版：选读代表性 TeX，概括符号、词汇、句法、段落和篇章，不分析时间演化。
2. 标准版：完整证据审计、符号系统和时间演化分析。
```

Do not read both skill files. Read the selected file completely before
executing the stage.

### Concise protocol

Use this route when the user selects `简洁版`, `精简版`, `lite`, `minimal`, or
explicitly names `SCHOLAR_STYLE_DISTILLATION_LITE_SKILL.md`.

Read `SCHOLAR_STYLE_DISTILLATION_LITE_SKILL.md` and invoke it with:

```text
Repository root: <repository_root>
Author slug: <author-slug>
Prepared corpus: <repository_root>/corpora/<author-slug>
Evidence output: <repository_root>/corpora/<author-slug>/STYLE_EVIDENCE_LITE.md
Final output: <repository_root>/styles/<author-slug>.txt
Temporal analysis: disabled
```

### Standard protocol

Use this route when the user selects `标准版`, `严格版`, `完整版本`, explicitly
names `SCHOLAR_STYLE_DISTILLATION_SKILL.md`, or asks for temporal evolution.
Read `SCHOLAR_STYLE_DISTILLATION_SKILL.md` and use Quick Mode unless the user
explicitly requests full mode:

```text
Repository root: <repository_root>
Author slug: <author-slug>
Prepared corpus: <repository_root>/corpora/<author-slug>
Evidence output: <repository_root>/corpora/<author-slug>/STYLE_EVIDENCE.md
Final output: <repository_root>/styles/<author-slug>.txt
```

Do not search, download, replace papers, or modify source TeX during distillation. The final TXT must be standalone. Treat `corpora/`, `.acquisition_work/`, `tmp/`, and `output/` as generated local data; do not add them to Git.
