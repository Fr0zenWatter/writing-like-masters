from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)*")

PHRASES = (
    "in this paper",
    "in this note",
    "in our previous paper",
    "the purpose of",
    "the main result",
    "we prove",
    "we show",
    "we claim",
    "we construct",
    "we consider",
    "we recall",
    "let us",
    "now let us",
    "now consider",
    "now suppose",
    "it follows that",
    "it follows from",
    "we conclude that",
    "we get a contradiction",
    "indeed",
    "clearly",
    "in particular",
    "moreover",
    "on the other hand",
    "however",
    "therefore",
    "thus",
    "hence",
    "finally",
    "first of all",
    "without loss of generality",
    "for simplicity",
    "for completeness",
    "more precisely",
    "recall that",
    "observe that",
    "note that",
    "it is easy to see",
    "it is clear that",
    "we may assume",
    "we are going to",
    "we will show",
    "we'll explain",
    "the idea is simple",
    "the problem with",
    "this is enough",
    "this proves",
    "the proof is complete",
)

CLAIM_FORMS = (
    "prove", "proves", "proved", "show", "shows", "shown",
    "claim", "claims", "claimed", "establish", "establishes", "established",
    "conclude", "concludes", "concluded", "imply", "implies", "implied",
    "deduce", "deduces", "deduced", "obtain", "obtains", "obtained",
)

HEDGE_FORMS = (
    "may", "might", "could", "perhaps", "possibly", "seem", "seems",
    "likely", "roughly", "approximately", "essentially", "usually",
)

TRANSITION_FORMS = (
    "now", "then", "thus", "hence", "therefore", "indeed", "however",
    "moreover", "finally", "otherwise", "instead", "similarly", "first",
)


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def strip_comments(text: str) -> str:
    output: list[str] = []
    for line in text.splitlines():
        cut = len(line)
        for index, char in enumerate(line):
            if char != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                cut = index
                break
        output.append(line[:cut])
    return "\n".join(output)


INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}")


def expand_local_inputs(path: Path, paper_root: Path, visited: set[Path] | None = None) -> str:
    """Expand TeX body components without ever leaving one paper directory."""
    visited = visited if visited is not None else set()
    resolved = path.resolve()
    try:
        resolved.relative_to(paper_root.resolve())
    except ValueError as exc:
        raise RuntimeError(f"TeX input escapes paper directory: {path}") from exc
    if resolved in visited:
        return ""
    visited.add(resolved)
    text = strip_comments(read_text(resolved))

    def replace(match: re.Match[str]) -> str:
        raw_target = match.group(1).strip()
        target = resolved.parent / raw_target
        if not target.suffix:
            target = target.with_suffix(".tex")
        target = target.resolve()
        try:
            target.relative_to(paper_root.resolve())
        except ValueError as exc:
            raise RuntimeError(f"TeX input escapes paper directory: {raw_target}") from exc
        if not target.is_file():
            # Acquisition has already classified known external package inputs.
            # Retain an empty placeholder rather than reading outside the paper.
            return " "
        return expand_local_inputs(target, paper_root, visited)

    return INPUT_RE.sub(replace, text)


def remove_balanced_environment(text: str, name: str) -> str:
    pattern = re.compile(
        rf"\\begin\s*\{{{re.escape(name)}\}}.*?\\end\s*\{{{re.escape(name)}\}}",
        re.IGNORECASE | re.DOTALL,
    )
    return pattern.sub(" ", text)


def body_text(raw: str) -> str:
    text = strip_comments(raw)
    match = re.search(r"\\begin\s*\{document\}", text, re.IGNORECASE)
    if match:
        text = text[match.end():]
    text = re.split(r"\\end\s*\{document\}", text, maxsplit=1, flags=re.IGNORECASE)[0]
    text = re.split(r"\\begin\s*\{thebibliography\}", text, maxsplit=1, flags=re.IGNORECASE)[0]
    return text


def clean_pdf_artifacts(text: str) -> str:
    text = remove_balanced_environment(text, "pdfuncertain")
    text = re.sub(r"\\PdfExtractedHeading\s*\{[^{}]*\}", "\n\n", text)
    text = re.sub(r"\\pagebreak(?:\[[^\]]*\])?", "\n\n", text)
    text = re.sub(r"\[unreadable\]", " ", text, flags=re.IGNORECASE)
    # Remove common journal furniture that survives PDF text extraction.
    kept: list[str] = []
    for line in text.splitlines():
        normalized = re.sub(r"\s+", " ", line).strip()
        if re.match(r"^(?:Math\. Z\.|Received \d|G\. PERELMAN$)", normalized, re.IGNORECASE):
            continue
        if re.match(r"^\d+\s+G\.\s+Perelman$", normalized, re.IGNORECASE):
            continue
        kept.append(line)
    return "\n".join(kept)


def strip_math_and_tex(text: str) -> str:
    for env in (
        "equation", "equation*", "align", "align*", "alignat", "alignat*",
        "gather", "gather*", "multline", "multline*", "eqnarray", "eqnarray*",
        "displaymath", "figure", "figure*", "table", "table*",
    ):
        text = remove_balanced_environment(text, env)
    text = re.sub(r"\\\[.*?\\\]", " MATHDISPLAY ", text, flags=re.DOTALL)
    text = re.sub(r"\$\$.*?\$\$", " MATHDISPLAY ", text, flags=re.DOTALL)
    text = re.sub(r"\\\([^\n]*?\\\)", " MATH ", text)
    text = re.sub(r"(?<!\\)\$(?:\\.|[^$\n])*?(?<!\\)\$", " MATH ", text)
    text = re.sub(r"\\(?:cite|citep|citet|ref|eqref|label|pageref)\*?(?:\[[^\]]*\])?\{[^{}]*\}", " ", text)
    text = re.sub(r"\\(?:title|author|date|maketitle|thanks)\b(?:\{[^{}]*\})?", " ", text)
    text = re.sub(r"\\(?:section|subsection|subsubsection)\*?\s*\{([^{}]*)\}", r"\n\n\1\n\n", text)
    text = re.sub(r"\\par\b", "\n\n", text)
    for _ in range(6):
        newer = re.sub(
            r"\\(?:textbf|textit|emph|textrm|textsf|texttt|mathrm|mathbf|mathit|operatorname|mbox|bf|it)\s*\{([^{}]*)\}",
            r"\1",
            text,
        )
        if newer == text:
            break
        text = newer
    text = re.sub(r"\\begin\s*\{[^{}]+\}(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"\\end\s*\{[^{}]+\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"\\.", " ", text)
    text = text.replace("{", " ").replace("}", " ").replace("~", " ")
    text = text.replace("---", " - ").replace("--", " - ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    pieces = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", normalized)
    return [piece.strip() for piece in pieces if len(words(piece)) >= 3]


def extract_sections(raw: str, is_pdf: bool) -> list[str]:
    text = strip_comments(raw)
    titles = re.findall(r"\\(?:section|subsection|subsubsection)\*?\s*\{([^{}]*)\}", text)
    if is_pdf:
        titles.extend(re.findall(r"\\PdfExtractedHeading\s*\{([^{}]*)\}", text))
        # Plain converted headings are retained only when short and numbered.
        titles.extend(re.findall(r"(?m)^\s*\d+\.\s+([A-Z][^\n]{2,80})$", text))
    cleaned = []
    for title in titles:
        value = re.sub(r"\\[A-Za-z]+", " ", title)
        value = re.sub(r"[{}]", " ", value)
        value = re.sub(r"\s+", " ", value).strip()
        if value and not re.search(r"G\.\s*Perelman|PERELMAN|\d{3}$", value):
            cleaned.append(value)
    return cleaned


def percentile(values: list[int], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def count_forms(tokens: list[str], forms: tuple[str, ...]) -> int:
    counter = Counter(token.lower() for token in tokens)
    return sum(counter[form] for form in forms)


def display_punctuation(raw: str) -> dict[str, int]:
    body = body_text(raw)
    chunks: list[str] = []
    patterns = (
        r"\\begin\{(?:equation\*?|align\*?|gather\*?|multline\*?|eqnarray\*?)\}(.*?)\\end\{(?:equation\*?|align\*?|gather\*?|multline\*?|eqnarray\*?)\}",
        r"\$\$(.*?)\$\$",
        r"\\\[(.*?)\\\]",
    )
    for pattern in patterns:
        chunks.extend(re.findall(pattern, body, flags=re.DOTALL))
    counts = Counter()
    for chunk in chunks:
        normalized = re.sub(r"\s+", " ", chunk).strip()
        if normalized.endswith(","):
            counts["comma"] += 1
        elif normalized.endswith("."):
            counts["period"] += 1
        elif normalized.endswith(";"):
            counts["semicolon"] += 1
        else:
            counts["none"] += 1
    return dict(counts)


def analyze_paper(root: Path, row: dict[str, str]) -> dict:
    path = root / row["canonical_main"]
    raw = expand_local_inputs(path, path.parent)
    is_pdf = row["conversion_method"] != "native-tex"
    body = body_text(raw)
    if is_pdf:
        body = clean_pdf_artifacts(body)
    prose = strip_math_and_tex(body)
    paragraphs = [
        re.sub(r"\s+", " ", part).strip()
        for part in re.split(r"\n\s*\n+", prose)
        if len(words(part)) >= 8
    ]
    sentences = [sentence for paragraph in paragraphs for sentence in split_sentences(paragraph)]
    sentence_lengths = [len(words(sentence)) for sentence in sentences]
    paragraph_words = [len(words(paragraph)) for paragraph in paragraphs]
    paragraph_sentences = [len(split_sentences(paragraph)) for paragraph in paragraphs]
    paragraph_moves = []
    for index, paragraph in enumerate(paragraphs, start=1):
        local_sentences = split_sentences(paragraph)
        if not local_sentences:
            continue
        paragraph_moves.append({
            "index": index,
            "words": len(words(paragraph)),
            "sentences": len(local_sentences),
            "opening": local_sentences[0],
            "closing": local_sentences[-1],
        })
    token_list = words(" ".join(paragraphs))
    lower = " ".join(paragraphs).lower()
    total = len(token_list)
    phrases = {phrase: lower.count(phrase) for phrase in PHRASES}
    record = {
        "paper_id": row["paper_id"],
        "year": int(row["year"]),
        "title": row["title"],
        "source_kind": "native" if not is_pdf else "pdf-derived",
        "quality": row.get("conversion_quality", ""),
        "weight": float(row["evidence_weight"]),
        "canonical_main": row["canonical_main"],
        "word_count": total,
        "sentence_count": len(sentences),
        "sentence_mean_words": round(statistics.mean(sentence_lengths), 2) if sentence_lengths else 0,
        "sentence_median_words": round(statistics.median(sentence_lengths), 2) if sentence_lengths else 0,
        "sentence_p75_words": round(percentile(sentence_lengths, 0.75), 2),
        "sentence_p90_words": round(percentile(sentence_lengths, 0.90), 2),
        "long_sentence_share": round(sum(length >= 35 for length in sentence_lengths) / len(sentence_lengths), 3) if sentence_lengths else 0,
        "paragraph_count": len(paragraphs),
        "paragraph_mean_words": round(statistics.mean(paragraph_words), 2) if paragraph_words else 0,
        "paragraph_mean_sentences": round(statistics.mean(paragraph_sentences), 2) if paragraph_sentences else 0,
        "first_person_per_1000": round(1000 * count_forms(token_list, ("i", "we", "our", "us")) / total, 2) if total else 0,
        "claim_verbs_per_1000": round(1000 * count_forms(token_list, CLAIM_FORMS) / total, 2) if total else 0,
        "hedges_per_1000": round(1000 * count_forms(token_list, HEDGE_FORMS) / total, 2) if total else 0,
        "transitions_per_1000": round(1000 * count_forms(token_list, TRANSITION_FORMS) / total, 2) if total else 0,
        "phrase_counts": phrases,
        "section_map": extract_sections(raw, is_pdf),
        "opening_paragraphs": paragraphs[:3],
        "closing_paragraphs": paragraphs[-3:],
        "paragraph_moves": paragraph_moves,
    }
    if not is_pdf:
        uncommented = strip_comments(raw)
        preamble = uncommented.split(r"\begin{document}", 1)[0]
        record["native_tex"] = {
            "documentclass": (re.search(r"\\documentclass(?:\[[^\]]*\])?\{([^{}]+)\}", preamble) or [None, "unknown"])[1],
            "macro_names": re.findall(r"\\(?:newcommand|renewcommand)\s*\{?\\([A-Za-z@]+)", preamble),
            "theorem_declarations": re.findall(r"\\newtheorem\*?\s*\{([^{}]+)\}", preamble),
            "manual_numbered_blocks": len(re.findall(r"\\par\s*\{\\bf\s+\d+(?:\.\d+)+", uncommented)),
            "bold_theorem_labels": len(re.findall(r"\\par\s*\{\\bf\s+[^{}]*(?:Theorem|Lemma|Proposition|Claim|Corollary|Remark|Definition|Example)", uncommented, flags=re.IGNORECASE)),
            "equation_envs": dict(Counter(re.findall(r"\\begin\s*\{(equation\*?|align\*?|gather\*?|multline\*?|eqnarray\*?)\}", uncommented))),
            "double_dollar_displays": len(re.findall(r"\$\$", uncommented)) // 2,
            "inline_math_pairs": len(re.findall(r"(?<!\\)\$(?!\$)", uncommented)) // 2,
            "display_punctuation": display_punctuation(raw),
            "labels": len(re.findall(r"\\label\s*\{", uncommented)),
            "refs": len(re.findall(r"\\(?:ref|eqref)\s*\{", uncommented)),
            "cite_commands": len(re.findall(r"\\cite\w*\s*\{", uncommented)),
            "bracket_citations": len(re.findall(r"\[[A-Z][A-Za-z0-9 .,$\\-]*(?:,\s*\\S\s*\d+)?\]", body)),
            "par_commands": len(re.findall(r"\\par\b", body)),
            "section_commands": len(re.findall(r"\\section\*?\s*\{", body)),
            "subsection_commands": len(re.findall(r"\\subsection\*?\s*\{", body)),
            "input_include": len(re.findall(r"\\(?:input|include)\s*\{", uncommented)),
            "figure_envs": len(re.findall(r"\\begin\s*\{figure\*?\}", uncommented)),
            "table_envs": len(re.findall(r"\\begin\s*\{table\*?\}", uncommented)),
        }
    return record


def paper_level_phrase_summary(records: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for phrase in PHRASES:
        supporting = [record for record in records if record["phrase_counts"][phrase] > 0]
        rows.append({
            "phrase": phrase,
            "paper_count": len(supporting),
            "weighted_support": round(sum(record["weight"] for record in supporting), 2),
            "native_papers": sum(record["source_kind"] == "native" for record in supporting),
            "early_pdf_papers": sum(record["source_kind"] == "pdf-derived" for record in supporting),
            "total_occurrences": sum(record["phrase_counts"][phrase] for record in records),
            "papers": [record["paper_id"] for record in supporting],
        })
    return sorted(rows, key=lambda item: (-item["paper_count"], -item["weighted_support"], item["phrase"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Paper-level style metrics for a prepared scholar corpus")
    parser.add_argument("corpus", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    corpus = args.corpus.resolve()
    manifest = corpus / "corpus_manifest.csv"
    with manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    accepted = [row for row in rows if row.get("include_in_style", "").strip().lower() == "true"]
    excluded = [row for row in rows if row not in accepted]
    records = [analyze_paper(corpus, row) for row in accepted]
    records.sort(key=lambda item: (item["year"], item["paper_id"]))

    native = [record for record in records if record["source_kind"] == "native"]
    pdf = [record for record in records if record["source_kind"] == "pdf-derived"]
    result = {
        "corpus": str(corpus),
        "paper_count": len(records),
        "native_count": len(native),
        "pdf_derived_count": len(pdf),
        "effective_weight": round(sum(record["weight"] for record in records), 2),
        "accepted_papers": records,
        "excluded_papers": [
            {
                "paper_id": row.get("paper_id", ""),
                "year": row.get("year", ""),
                "title": row.get("title", ""),
                "reason": row.get("exclusion_reason", ""),
            }
            for row in excluded
        ],
        "phrase_support": paper_level_phrase_summary(records),
        "native_tex_aggregate": {
            "macro_support": dict(Counter(name for record in native for name in record["native_tex"]["macro_names"])),
            "theorem_declaration_support": dict(Counter(name for record in native for name in record["native_tex"]["theorem_declarations"])),
            "documentclasses": dict(Counter(record["native_tex"]["documentclass"] for record in native)),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("paper_count", "native_count", "pdf_derived_count", "effective_weight")}, indent=2))


if __name__ == "__main__":
    main()
