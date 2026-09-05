<p align="center">
  <a href="./README.md">简体中文</a> · <strong>English</strong>
</p>

# Writing Like Masters

Distill a scholar's academic writing style from public research papers into a practical writing guide that AI agents can use directly.

The project is inspired by autoregressive language modeling: $`p(x_{n+1} \mid x_1, \ldots, x_n)`$. Better prompts and higher-quality input text can substantially improve the quality of the generated text. High-quality TeX manuscripts by leading scholars, publicly available on preprint platforms such as arXiv, give us an opportunity to distill individual writing styles from notation, language, and argument structure. By using these styles to guide AI-generated proofs, we aim to offer a reading experience closer to having the masters explain the mathematics themselves.

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

All styles put mathematical correctness first. They differ mainly in how they frame problems, explain ideas, and advance arguments:

- [Grigori Perelman](styles/grigori-perelman.txt): works in geometric analysis, differential geometry, and topology, especially Ricci flow; his prose is **austere and minimalist**, with little preamble, a direct entry into proofs, dependency-ordered reasoning, and restrained statements of assumptions, gaps, and unfinished points.
- [Noga Alon](styles/noga-alon.txt): works in combinatorics, graph theory, the probabilistic method, and theoretical computer science; his prose is **precise and economical**, putting the problem first, moving quickly to theorems and proofs, and leaving almost no room for unnecessary exposition.
- [Peter Scholze](styles/peter-scholze.txt): works in arithmetic geometry, algebraic geometry, p-adic geometry, cohomology, and the Langlands program; his prose is **conceptual and architectural**, identifying the central obstruction before introducing exactly the object needed to resolve it, while moving between formal statements and conceptual intuition.
- [Saharon Shelah](styles/saharon-shelah.txt): works in mathematical logic, model theory, and set theory; his prose is **dense and construction-driven**, with strong numbering, notation, and dependency structures that break long proofs into locatable local tasks and technical obstacles.
- [Sourav Chatterjee](styles/sourav-chatterjee.txt): works in probability, statistics, mathematical physics, and analysis; his prose is **intuition-led and explanatory**, emphasizing mechanisms and motivation, often beginning with a concrete problem or simple model before moving gradually toward abstraction and explaining why each step is needed.
- [Terence Tao](styles/terence-tao.txt): works across harmonic analysis, partial differential equations, combinatorics, number theory, and many other fields; his prose offers **tutorial-style navigation**, alternating rigorous statements with intuitive explanations and organizing complex proofs as a sequence of clearly motivated reductions.

## Style examples from the same source

The two documents below were generated from the same mathematical source, illustrating how Peter Scholze's and Terence Tao's styles organize the material differently.

### Peter Scholze

<p align="center">
  <img src="assets/readme/peter-scholze-blueprint-example.png" alt="A one-page mathematical document in Peter Scholze's style" width="760">
</p>

### Terence Tao

<p align="center">
  <img src="assets/readme/terence-tao-blueprint-example.png" alt="A section-free one-page mathematical document in Terence Tao's style" width="760">
</p>

## Setup

Use Python 3.10 or newer, then install the required packages:

```powershell
python -m pip install -r requirements.txt
```

Public paper sources are normally enough. Extra PDF-reading tools are needed only when no usable source files are available.

## A few important notes

- Use public sources and confirm the scholar's identity first.
- The final TXT is a writing aid, not a guarantee that the mathematics is correct.
- This is an independent project and is not affiliated with, sponsored by, or endorsed by any scholar whose style is discussed.
- Do not commit downloaded papers, cached web pages, or working files.
- Review each final TXT before publishing it so it does not contain long copied passages, private information, or third-party template text.

## License

The code, workflow guides, and style files in this repository are released under the [MIT License](LICENSE). Downloaded papers, corpora, cached web pages, and other third-party materials are not part of this repository and are not covered by this license.

For the rules, read the [paper collection guide](SCHOLAR_TEX_ACQUISITION_SKILL.md), the [concise style guide](SCHOLAR_STYLE_DISTILLATION_LITE_SKILL.md), and the [standard style guide](SCHOLAR_STYLE_DISTILLATION_SKILL.md).
