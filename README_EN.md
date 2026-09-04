<p align="center">
  <a href="./README.md">简体中文</a> · <strong>English</strong>
</p>

# Writing Like Masters

Turn a scholar's public papers into a practical writing guide that an AI agent can use directly.

Tell the agent who the scholar is. It will first make sure it has the right person, collect public paper sources, study how the author explains ideas, uses formulas, and builds arguments, then save the result as one plain TXT file.

## Easiest way to use it

Ask an agent from this folder:

```text
Create a writing style for <scholar name>. Confirm the scholar's identity first, then follow AGENTS.md from start to finish.
```

If the papers are already available, say:

```text
Use corpora/<author-slug>/ as it is. Do not download the papers again. Create the final style.
```

The agent will do four things:

1. Confirm the scholar and find public paper sources.
2. Once the corpus is ready, ask you to choose concise or standard distillation.
3. Summarize the author's writing choices with the selected protocol; the concise protocol omits temporal analysis.
4. Save the final result as `styles/<author-slug>.txt`.

If too few source files are available, the agent will ask before using PDFs.

## Where things go

- `styles/`: finished style files that can be committed to Git.
- `corpora/`: downloaded papers kept only on your computer.
- `scripts/`: small helpers for downloading and checking material.
- `SCHOLAR_TEX_ACQUISITION_SKILL.md`: detailed paper-collection instructions.
- `SCHOLAR_STYLE_DISTILLATION_LITE_SKILL.md`: concise, non-temporal style-building instructions.
- `SCHOLAR_STYLE_DISTILLATION_SKILL.md`: standard instructions with full evidence and temporal analysis.
- `AGENTS.md`: the short guide that tells an agent which stage to run next.

Download records, temporary files, and working notes also stay local and are excluded by `.gitignore`.

## Included styles

- [Grigori Perelman](styles/grigori-perelman.txt)
- [Yuwen Li](styles/liyuwen.txt)
- [Noga Alon](styles/noga-alon.txt)
- [Peter Scholze](styles/peter-scholze.txt)
- [Saharon Shelah](styles/saharon-shelah.txt)
- [Sourav Chatterjee](styles/sourav-chatterjee.txt)
- [Terence Tao](styles/terence-tao.txt)

## Setup

Use Python 3.10 or newer, then install the required packages:

```powershell
python -m pip install -r requirements.txt
```

Public paper sources are normally enough. Extra PDF-reading tools are needed only when no usable source files are available.

## A few important notes

- Use public sources and confirm the scholar's identity first.
- The final TXT is a writing aid, not a guarantee that the mathematics is correct.
- Do not commit downloaded papers, cached web pages, or working files.
- Review each final TXT before publishing it so it does not contain long copied passages, private information, or third-party template text.

For the rules, read the [paper collection guide](SCHOLAR_TEX_ACQUISITION_SKILL.md), the [concise style guide](SCHOLAR_STYLE_DISTILLATION_LITE_SKILL.md), and the [standard style guide](SCHOLAR_STYLE_DISTILLATION_SKILL.md).
