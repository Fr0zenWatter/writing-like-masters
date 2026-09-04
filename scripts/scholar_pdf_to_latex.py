from __future__ import annotations

import argparse
import csv
import hashlib
import html
from html.parser import HTMLParser
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin

import requests
from pypdf import PdfReader, PdfWriter


EXTRA_MANIFEST_FIELDS = [
    "source_pdf",
    "source_container_pdf",
    "conversion_method",
    "conversion_quality",
    "evidence_weight",
    "conversion_warnings",
]

MATH_UNICODE = {
    "±": r"\ensuremath{\pm}",
    "×": r"\ensuremath{\times}",
    "÷": r"\ensuremath{\div}",
    "α": r"\ensuremath{\alpha}",
    "β": r"\ensuremath{\beta}",
    "γ": r"\ensuremath{\gamma}",
    "δ": r"\ensuremath{\delta}",
    "ε": r"\ensuremath{\epsilon}",
    "θ": r"\ensuremath{\theta}",
    "λ": r"\ensuremath{\lambda}",
    "μ": r"\ensuremath{\mu}",
    "π": r"\ensuremath{\pi}",
    "ρ": r"\ensuremath{\rho}",
    "σ": r"\ensuremath{\sigma}",
    "τ": r"\ensuremath{\tau}",
    "φ": r"\ensuremath{\phi}",
    "ψ": r"\ensuremath{\psi}",
    "ω": r"\ensuremath{\omega}",
    "Γ": r"\ensuremath{\Gamma}",
    "Δ": r"\ensuremath{\Delta}",
    "Σ": r"\ensuremath{\Sigma}",
    "Ω": r"\ensuremath{\Omega}",
    "→": r"\ensuremath{\to}",
    "←": r"\ensuremath{\leftarrow}",
    "⇒": r"\ensuremath{\Rightarrow}",
    "∈": r"\ensuremath{\in}",
    "∉": r"\ensuremath{\notin}",
    "−": "-",
    "∞": r"\ensuremath{\infty}",
    "∫": r"\ensuremath{\int}",
    "∑": r"\ensuremath{\sum}",
    "≤": r"\ensuremath{\leq}",
    "≥": r"\ensuremath{\geq}",
    "≠": r"\ensuremath{\neq}",
    "≈": r"\ensuremath{\approx}",
    "⊂": r"\ensuremath{\subset}",
    "⊃": r"\ensuremath{\supset}",
    "⊆": r"\ensuremath{\subseteq}",
    "⊇": r"\ensuremath{\supseteq}",
}

PUNCTUATION_TRANSLATION = str.maketrans(
    {
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "--",
        "…": "...",
        " ": " ",
        "ﬀ": "ff",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
    }
)


class PdfLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "meta" and values.get("name", "").lower() in {
            "citation_pdf_url",
            "wkhealth_pdf_url",
        }:
            self.links.append(values.get("content", ""))
        if tag.lower() in {"a", "iframe", "embed", "object"}:
            for key in ("href", "src", "data"):
                value = values.get(key, "")
                if value and (".pdf" in value.lower() or "download" in value.lower()):
                    self.links.append(value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download PDF-only papers, preserve the PDF, extract text or OCR, create a "
            "provenance-marked LaTeX transcription, and update corpus evidence weights."
        )
    )
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-download-mb", type=int, default=300)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--rebuild-latex", action="store_true")
    parser.add_argument("--report-only", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_pdf_bytes(data: bytes) -> bool:
    return data[:1024].lstrip().startswith(b"%PDF-")


def unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        value = str(value or "").strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def read_manifest(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    for field in EXTRA_MANIFEST_FIELDS:
        if field not in fields:
            fields.append(field)
    return fields, rows


def write_manifest(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def update_native_rows(corpus: Path, rows: list[dict[str, Any]]) -> None:
    for row in rows:
        if "pdf" in str(row.get("source_kind", "")).lower():
            continue
        row.update(
            {
                "source_pdf": "",
                "source_container_pdf": "",
                "conversion_method": "native-tex",
                "conversion_quality": "original-source",
                "evidence_weight": "1.00",
                "conversion_warnings": "",
            }
        )
        metadata_path = corpus / "tex" / row["paper_id"] / "metadata.json"
        if metadata_path.is_file():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata.update({field: row[field] for field in EXTRA_MANIFEST_FIELDS})
            metadata_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )


def html_pdf_links(base_url: str, data: bytes) -> list[str]:
    text = data.decode("utf-8", errors="replace")
    parser = PdfLinkParser()
    parser.feed(text)
    regex_links = re.findall(
        r"https?://[^\s\"'<>]+(?:\.pdf(?:\?[^\s\"'<>]*)?|/download/[^\s\"'<>]+)",
        html.unescape(text),
        flags=re.IGNORECASE,
    )
    return unique(urljoin(base_url, link) for link in [*parser.links, *regex_links])


def request_candidate(
    session: requests.Session,
    url: str,
    destination: Path,
    attempts: int,
    timeout: int,
    max_bytes: int,
    verify_tls: bool,
) -> tuple[str, str]:
    queue = [url]
    tried: set[str] = set()
    errors: list[str] = []
    while queue and len(tried) < 12:
        current = queue.pop(0)
        if current in tried:
            continue
        tried.add(current)
        response: requests.Response | None = None
        for attempt in range(1, attempts + 1):
            try:
                response = session.get(
                    current,
                    timeout=(20, timeout),
                    allow_redirects=True,
                    verify=verify_tls,
                    stream=True,
                )
                response.raise_for_status()
                break
            except requests.RequestException as exc:
                errors.append(f"{current}: {exc}")
                response = None
                if attempt < attempts:
                    time.sleep(2 * attempt)
        if response is None:
            continue
        content_type = response.headers.get("Content-Type", "").lower()
        content_length = int(response.headers.get("Content-Length", 0) or 0)
        if content_length > max_bytes:
            errors.append(f"{current}: response exceeds size limit")
            response.close()
            continue
        data = bytearray()
        try:
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    data.extend(chunk)
                    if len(data) > max_bytes:
                        raise RuntimeError("response exceeds size limit")
        except Exception as exc:
            errors.append(f"{current}: {exc}")
            continue
        final_url = str(response.url)
        payload = bytes(data)
        if is_pdf_bytes(payload):
            destination.write_bytes(payload)
            return final_url, content_type
        if "html" in content_type or payload.lstrip().startswith((b"<!DOCTYPE", b"<html")):
            queue.extend(link for link in html_pdf_links(final_url, payload) if link not in tried)
            errors.append(f"{current}: returned HTML rather than PDF")
            continue
        errors.append(f"{current}: response is not a PDF ({content_type or 'unknown type'})")
    tail = "; ".join(errors[-6:])
    raise RuntimeError(tail or "no working PDF URL")


def download_pdf(
    session: requests.Session,
    urls: list[str],
    destination: Path,
    attempts: int,
    timeout: int,
    max_bytes: int,
    verify_tls: bool,
) -> tuple[str, str]:
    errors: list[str] = []
    destination.parent.mkdir(parents=True, exist_ok=True)
    for url in unique(urls):
        try:
            return request_candidate(
                session,
                url,
                destination,
                attempts,
                timeout,
                max_bytes,
                verify_tls,
            )
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError(" | ".join(errors))


def normalize_search(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def title_tokens(title: str) -> set[str]:
    stop = {"a", "an", "and", "for", "in", "of", "on", "the", "to", "with"}
    return {token for token in normalize_search(title).split() if len(token) > 2 and token not in stop}


def page_text(reader: PdfReader, index: int) -> str:
    try:
        return reader.pages[index].extract_text() or ""
    except Exception:
        return ""


def locate_article_start(
    reader: PdfReader,
    title: str,
    authors: str,
    printed_page_start: int | None,
) -> tuple[int, list[dict[str, Any]]]:
    tokens = title_tokens(title)
    surname = normalize_search(authors).split()[-1] if normalize_search(authors) else ""
    exact = normalize_search(title)
    evidence: list[dict[str, Any]] = []
    for index in range(len(reader.pages)):
        text = page_text(reader, index)
        normalized = normalize_search(text)
        page_tokens = set(normalized.split())
        coverage = len(tokens & page_tokens) / max(1, len(tokens))
        score = coverage
        if exact and exact in normalized:
            score += 1.5
        if surname and surname in page_tokens:
            score += 0.25
        if printed_page_start is not None and re.search(
            rf"(?:^|\s){printed_page_start}(?:\s|$)", normalized
        ):
            score += 0.2
        if score >= 0.5:
            evidence.append(
                {"pdf_page": index + 1, "score": round(score, 3), "title_coverage": round(coverage, 3)}
            )
    if not evidence:
        raise RuntimeError("could not locate article title inside container PDF")
    evidence.sort(key=lambda item: (-item["score"], item["pdf_page"]))
    best = evidence[0]
    if best["score"] < 0.8:
        raise RuntimeError(f"article page match is too weak: {best}")
    return int(best["pdf_page"]) - 1, evidence[:10]


def validate_pdf(path: Path) -> tuple[PdfReader, int]:
    reader = PdfReader(str(path))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise RuntimeError(f"encrypted PDF cannot be opened: {exc}") from exc
    count = len(reader.pages)
    if count < 1:
        raise RuntimeError("PDF has no pages")
    return reader, count


def crop_article(
    source: Path,
    destination: Path,
    title: str,
    authors: str,
    page_count: int,
    printed_page_start: int | None,
) -> tuple[int, list[dict[str, Any]]]:
    reader, total = validate_pdf(source)
    start, evidence = locate_article_start(reader, title, authors, printed_page_start)
    end = start + page_count
    if end > total:
        raise RuntimeError(f"article page range {start + 1}-{end} exceeds {total}-page PDF")
    writer = PdfWriter()
    for index in range(start, end):
        writer.add_page(reader.pages[index])
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        writer.write(handle)
    return start, evidence


def bundled_binary(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    home = Path.home()
    candidates = sorted(
        home.glob(
            f".cache/codex-runtimes/codex-primary-runtime/dependencies/native/**/{name}.exe"
        )
    )
    return str(candidates[0]) if candidates else None


def extract_with_pdftotext(pdf: Path, output: Path) -> list[str]:
    executable = bundled_binary("pdftotext")
    if not executable:
        raise RuntimeError("pdftotext is unavailable")
    completed = subprocess.run(
        [executable, "-layout", "-enc", "UTF-8", str(pdf), str(output)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=240,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "pdftotext failed")
    text = output.read_text(encoding="utf-8", errors="replace")
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\f")


def extract_with_pypdf(pdf: Path) -> list[str]:
    reader, _ = validate_pdf(pdf)
    return [page_text(reader, index) for index in range(len(reader.pages))]


def find_tesseract() -> str | None:
    found = shutil.which("tesseract")
    if found:
        return found
    for path in (
        Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
        Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
    ):
        if path.is_file():
            return str(path)
    return None


def ocr_pdf(pdf: Path, work: Path) -> list[str]:
    pdftoppm = bundled_binary("pdftoppm")
    tesseract = find_tesseract()
    if not pdftoppm or not tesseract:
        raise RuntimeError("OCR is required but pdftoppm or Tesseract is unavailable")
    prefix = work / "ocr-page"
    rendered = subprocess.run(
        [pdftoppm, "-r", "300", "-png", str(pdf), str(prefix)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=900,
    )
    if rendered.returncode != 0:
        raise RuntimeError(rendered.stderr.strip() or "pdftoppm failed for OCR")
    pages: list[str] = []
    for image_path in sorted(work.glob("ocr-page-*.png")):
        completed = subprocess.run(
            [tesseract, str(image_path), "stdout", "-l", "eng", "--psm", "6"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or f"OCR failed for {image_path.name}")
        pages.append(completed.stdout)
    if not pages:
        raise RuntimeError("OCR rendered no pages")
    return pages


def text_metrics(pages: list[str]) -> dict[str, Any]:
    cleaned = [re.sub(r"\s+", "", page) for page in pages]
    chars = sum(len(page) for page in cleaned)
    alpha = sum(sum(char.isalpha() for char in page) for page in cleaned)
    replacement = sum(page.count("�") for page in pages)
    text_pages = sum(len(page) >= 80 for page in cleaned)
    page_count = max(1, len(pages))
    return {
        "page_count": len(pages),
        "text_pages": text_pages,
        "text_page_ratio": round(text_pages / page_count, 4),
        "extracted_characters": chars,
        "alphabetic_ratio": round(alpha / max(1, chars), 4),
        "replacement_characters": replacement,
        "characters_per_page": round(chars / page_count, 1),
    }


def recurrent_margin_lines(pages: list[str]) -> set[str]:
    counts: Counter[str] = Counter()
    for page in pages:
        lines = [re.sub(r"\s+", " ", line).strip() for line in page.splitlines()]
        nonempty = [line for line in lines if line]
        candidates = unique([*nonempty[:3], *nonempty[-3:]])
        counts.update(line for line in candidates if 2 < len(line) < 140)
    threshold = max(2, math.ceil(len(pages) * 0.5))
    return {line for line, count in counts.items() if count >= threshold}


def clean_lines(page: str, repeated: set[str]) -> list[str]:
    lines: list[str] = []
    for raw in page.translate(PUNCTUATION_TRANSLATION).splitlines():
        line = re.sub(r"[ \t]+", " ", raw).strip()
        if line in repeated:
            continue
        if re.fullmatch(r"[-\u2013\u2014]?\s*\d+\s*[-\u2013\u2014]?", line):
            continue
        lines.append(line)
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def blockify(lines: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line:
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def join_prose(lines: list[str]) -> str:
    result = ""
    for line in lines:
        if not result:
            result = line
        elif result.endswith("-") and line[:1].islower():
            result = result[:-1] + line
        else:
            result += " " + line
    return re.sub(r"\s+", " ", result).strip()


def looks_like_heading(text: str) -> bool:
    if len(text) > 120 or text.endswith((".", ",", ";", ":")):
        return False
    if re.match(r"^(?:\d+(?:\.\d+)*\.?|[IVXLC]+\.)\s+\S", text):
        return True
    letters = [char for char in text if char.isalpha()]
    return bool(letters) and len(text.split()) <= 12 and sum(char.isupper() for char in letters) / len(letters) > 0.72


def looks_like_math(lines: list[str]) -> bool:
    text = " ".join(lines)
    if not text:
        return False
    math_marks = sum(text.count(mark) for mark in "=<>+±∑∫√≤≥∈⊂→")
    letters = sum(char.isalpha() for char in text)
    visible = sum(not char.isspace() for char in text)
    isolated = len(re.findall(r"(?:^|\s)[A-Za-z](?:\s|$)", text))
    return (math_marks >= 2 and letters / max(1, visible) < 0.65) or (
        math_marks >= 1 and isolated >= 4 and len(text) < 500
    )


def latex_escape(text: str) -> str:
    text = unicodedata.normalize("NFC", text.translate(PUNCTUATION_TRANSLATION))
    special = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "#": r"\#",
        "$": r"\$",
        "%": r"\%",
        "&": r"\&",
        "_": r"\_",
        "^": r"\textasciicircum{}",
        "~": r"\textasciitilde{}",
    }
    output: list[str] = []
    for char in text:
        if char == "�" or (unicodedata.category(char).startswith("C") and char not in "\t\n"):
            output.append("[unreadable]")
        elif char in MATH_UNICODE:
            output.append(MATH_UNICODE[char])
        else:
            output.append(special.get(char, char))
    return "".join(output)


def render_latex(
    row: dict[str, Any],
    pages: list[str],
    method: str,
    weight: float,
) -> tuple[str, int, int]:
    repeated = recurrent_margin_lines(pages)
    body: list[str] = []
    prose_blocks = 0
    uncertain_blocks = 0
    for page_number, page in enumerate(pages, start=1):
        body.append(f"% PDF page {page_number}")
        for lines in blockify(clean_lines(page, repeated)):
            joined = join_prose(lines)
            if not joined:
                continue
            if looks_like_math(lines):
                uncertain_blocks += 1
                body.append(f"% UNCERTAIN_PDF_MATH page={page_number}")
                body.append(r"\begin{pdfuncertain}")
                body.extend(latex_escape(line) + r"\par" for line in lines)
                body.append(r"\end{pdfuncertain}")
            elif looks_like_heading(joined):
                body.append(r"\PdfExtractedHeading{" + latex_escape(joined) + "}")
            else:
                prose_blocks += 1
                body.append(latex_escape(joined) + "\n")
        body.append(r"\pagebreak[1]")
    title = latex_escape(str(row.get("title", "")))
    authors = latex_escape(str(row.get("authors", "")))
    paper_id = str(row.get("paper_id", ""))
    header = [
        "% PDF-DERIVED TRANSCRIPTION FOR STYLE EVIDENCE",
        f"% paper_id: {paper_id}",
        f"% conversion_method: {method}",
        f"% evidence_weight: {weight:.2f}",
        "% Mathematical notation, equation layout, page furniture, hyphenation, and section markup",
        "% are not authoritative. Consult source_pdf in metadata.json before using a claim.",
        r"\documentclass[11pt]{article}",
        r"\usepackage{fontspec}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage{microtype}",
        r"\setmainfont{Latin Modern Roman}",
        r"\newcommand{\PdfExtractedHeading}[1]{\par\medskip\noindent\textbf{#1}\par\smallskip}",
        r"\newenvironment{pdfuncertain}{\begin{quote}\small\ttfamily}{\end{quote}}",
        r"\title{" + title + "}",
        r"\author{" + authors + "}",
        r"\date{" + latex_escape(str(row.get("year", ""))) + "}",
        r"\begin{document}",
        r"\maketitle",
        "% The visible body below is mechanically recovered from the cited PDF.",
        *body,
        r"\end{document}",
        "",
    ]
    return "\n".join(header), prose_blocks, uncertain_blocks


def conversion_quality(metrics: dict[str, Any]) -> str:
    ratio = float(metrics["text_page_ratio"])
    chars_per_page = float(metrics["characters_per_page"])
    alpha = float(metrics["alphabetic_ratio"])
    if ratio >= 0.9 and chars_per_page >= 800 and alpha >= 0.55:
        return "text-layer-good"
    if ratio >= 0.7 and chars_per_page >= 350 and alpha >= 0.45:
        return "text-layer-partial"
    return "text-layer-poor"


def relative(path: Path, corpus: Path) -> str:
    return path.relative_to(corpus).as_posix()


def warning_text(method: str, quality: str, formula_blocks: int) -> list[str]:
    warnings = [
        "PDF-derived text is secondary evidence and may contain extraction errors",
        "mathematical notation and layout are not authoritative",
    ]
    if method == "ocr-to-latex":
        warnings.append("OCR may alter spelling, punctuation, symbols, and word boundaries")
    if quality.endswith("partial") or quality.endswith("poor"):
        warnings.append("text recovery is incomplete or noisy")
    if formula_blocks:
        warnings.append(f"{formula_blocks} formula-like block(s) are marked uncertain")
    return warnings


def write_exclusions(corpus: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Exclusions",
        "",
        "| paper_id | title | source | reason |",
        "|---|---|---|---|",
    ]
    for row in rows:
        if str(row.get("include_in_style", "")).lower() == "true":
            continue
        escape = lambda value: str(value or "").replace("|", r"\|").replace("\n", " ")
        lines.append(
            f"| {escape(row.get('paper_id'))} | {escape(row.get('title'))} | "
            f"{escape(row.get('source_url'))} | {escape(row.get('exclusion_reason'))} |"
        )
    (corpus / "exclusions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_acquisition_report(corpus: Path, rows: list[dict[str, Any]], elapsed: float) -> None:
    report_path = corpus / "ACQUISITION_REPORT.md"
    text = report_path.read_text(encoding="utf-8") if report_path.is_file() else "# Acquisition Report\n"
    prior_elapsed = re.search(r"^- Conversion run time: ([0-9.]+) s$", text, flags=re.MULTILINE)
    if elapsed <= 0 and prior_elapsed:
        elapsed = float(prior_elapsed.group(1))
    text = re.sub(
        r"\n<!-- PDF_FALLBACK_START -->[\s\S]*?<!-- PDF_FALLBACK_END -->\n?",
        "\n",
        text,
    ).rstrip()
    native = [row for row in rows if row.get("conversion_method") == "native-tex" and row.get("include_in_style") == "true"]
    converted = [
        row
        for row in rows
        if str(row.get("conversion_method", "")).endswith("-to-latex")
        and row.get("include_in_style") == "true"
    ]
    failed = [
        row
        for row in rows
        if "pdf" in str(row.get("source_kind", "")).lower()
        and row.get("include_in_style") != "true"
    ]
    accepted = [row for row in rows if row.get("include_in_style") == "true"]
    accepted_years = [
        int(str(row.get("year")))
        for row in accepted
        if str(row.get("year", "")).isdigit()
    ]
    text = re.sub(
        r"^- Accepted TeX papers:.*$",
        f"- Accepted papers: {len(accepted)}\n- Native TeX papers: {len(native)}\n- PDF-derived LaTeX papers: {len(converted)}",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^- Excluded papers:.*$",
        f"- Excluded papers: {len(failed)}",
        text,
        flags=re.MULTILINE,
    )
    if accepted_years:
        text = re.sub(
            r"^- Accepted year range:.*$",
            f"- Accepted year range: {min(accepted_years)}-{max(accepted_years)}",
            text,
            flags=re.MULTILINE,
        )
    dispositions: dict[str, list[int]] = {}
    for row in rows:
        values = dispositions.setdefault(str(row.get("source_kind") or "unknown"), [0, 0])
        values[0 if row.get("include_in_style") == "true" else 1] += 1
    disposition_lines = "\n".join(
        f"| {kind} | {values[0]} | {values[1]} |"
        for kind, values in sorted(dispositions.items())
    )
    text = re.sub(
        r"(\| source kind \| accepted \| excluded \|\n\|---\|---:\|---:\|\n)(?:\|.*\|\n)+",
        lambda match: match.group(1) + disposition_lines + "\n",
        text,
    )
    text = re.sub(
        r"Every accepted item has one canonical main TeX file, a preserved source package, "
        r"a SHA-256 digest, and a checked local dependency graph\. Excluded items do not enter "
        r"the style corpus\.",
        "Every accepted item has one canonical main TeX file, a preserved source package or PDF, "
        "a SHA-256 digest, and recorded source fidelity. Native TeX inputs have checked local "
        "dependencies. PDF-derived inputs preserve their conversion method, quality, warnings, "
        "and reduced evidence weight. Excluded items do not enter the style corpus.",
        text,
    )
    limitation = (
        f"The corpus contains {len(accepted)} usable papers: {len(native)} native-TeX paper(s) "
        f"and {len(converted)} PDF-derived transcription(s). The PDF-derived papers carry reduced "
        f"source-fidelity weight, and {len(failed)} inaccessible or insufficient PDF item(s) remain "
        "excluded. Temporal conclusions that depend mainly on converted early papers must therefore "
        "remain qualified."
    )
    text = re.sub(
        r"(## Known Limitation\n\n)[\s\S]*$",
        lambda match: match.group(1) + limitation,
        text,
    ).rstrip()
    section = [
        "",
        "<!-- PDF_FALLBACK_START -->",
        "## PDF Fallback Conversion",
        "",
        "PDF-only items were handled as a separate acquisition fallback. The original PDF is preserved, "
        "and the generated LaTeX is explicitly marked as a secondary transcription.",
        "",
        f"- Native TeX papers: {len(native)} at evidence weight 1.00",
        f"- PDF-derived LaTeX papers accepted: {len(converted)}",
        f"- PDF conversion failures: {len(failed)}",
        f"- Conversion run time: {elapsed:.3f} s",
        "",
        "| paper_id | method | quality | weight |",
        "|---|---|---|---:|",
        *[
            f"| {row['paper_id']} | {row.get('conversion_method', '')} | "
            f"{row.get('conversion_quality', '')} | {row.get('evidence_weight', '')} |"
            for row in converted
        ],
        "",
        "The PDF-derived rows may support prose and rhetorical observations at reduced weight. They "
        "must not be used as authoritative evidence for notation, equations, LaTeX macros, environments, "
        "or layout. Formula-like blocks in each conversion are marked as uncertain.",
        "<!-- PDF_FALLBACK_END -->",
        "",
    ]
    report_path.write_text(text + "\n" + "\n".join(section), encoding="utf-8")


def concise_failure(exc: Exception) -> str:
    message = str(exc)
    if "mathunion.org" in message and "Springer" not in message:
        return (
            "official ICM volume connection failed after bounded retries; "
            "the Springer fallback returned HTML rather than a PDF"
        )
    if "mathunion.org" in message and "link.springer.com" in message:
        return (
            "official ICM volume connection failed after bounded retries; "
            "the Springer fallback returned HTML rather than a PDF"
        )
    if "projecteuclid.org" in message:
        return "Project Euclid returned access-control HTML rather than a PDF at all verified endpoints"
    compact = re.sub(r"\s+", " ", message).strip()
    return compact[:480] + ("..." if len(compact) > 480 else "")


def remove_empty_failed_directory(corpus: Path, paper_id: str) -> None:
    paper_dir = corpus / "tex" / paper_id
    for directory in (paper_dir / "source", paper_dir):
        try:
            directory.rmdir()
        except (FileNotFoundError, OSError):
            pass


def process_row(
    corpus: Path,
    row: dict[str, Any],
    settings: dict[str, Any],
    defaults: dict[str, Any],
    session: requests.Session,
    args: argparse.Namespace,
) -> dict[str, Any]:
    paper_id = str(row["paper_id"])
    paper_dir = corpus / "tex" / paper_id
    source_dir = paper_dir / "source"
    metadata_path = paper_dir / "metadata.json"
    package_path = paper_dir / "source-package.pdf"
    article_path = source_dir / "article.pdf"
    tex_path = source_dir / "converted_from_pdf.tex"
    existing: dict[str, Any] = {}
    if metadata_path.is_file():
        existing = json.loads(metadata_path.read_text(encoding="utf-8"))
    if existing and not args.overwrite and not args.rebuild_latex:
        existing_main = corpus / str(existing.get("canonical_main", ""))
        existing_pdf = corpus / str(existing.get("source_pdf", ""))
        if (
            existing.get("include_in_style") == "true"
            and existing_main.is_file()
            and existing_pdf.is_file()
        ):
            print("    using validated existing PDF conversion", flush=True)
            return {**row, **existing}
    paper_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    if args.overwrite:
        for path in (package_path, article_path, tex_path):
            if path.is_file():
                path.unlink()
    if args.rebuild_latex and package_path.is_file():
        resolved_url = str(existing.get("resolved_pdf_url") or row.get("source_url", ""))
        content_type = str(existing.get("content_type") or "application/pdf")
        download_seconds = float(existing.get("download_seconds") or 0.0)
    else:
        download_urls = [*settings.get("download_urls", []), str(row.get("source_url", ""))]
        verify_tls = bool(settings.get("verify_tls", True))
        download_start = time.perf_counter()
        resolved_url, content_type = download_pdf(
            session,
            download_urls,
            package_path,
            args.attempts,
            args.timeout,
            args.max_download_mb * 1024 * 1024,
            verify_tls,
        )
        download_seconds = time.perf_counter() - download_start
    reader, container_pages = validate_pdf(package_path)
    article_page_count = settings.get("article_page_count")
    article_start = 0
    article_evidence: list[dict[str, Any]] = []
    if article_page_count:
        article_start, article_evidence = crop_article(
            package_path,
            article_path,
            str(row.get("title", "")),
            str(row.get("authors", "")),
            int(article_page_count),
            int(settings["printed_page_start"]) if settings.get("printed_page_start") else None,
        )
        conversion_pdf = article_path
        source_container_pdf = relative(package_path, corpus)
    else:
        conversion_pdf = package_path
        source_container_pdf = ""
    _, article_pages = validate_pdf(conversion_pdf)
    with tempfile.TemporaryDirectory(prefix="scholar-pdf-") as raw_work:
        work = Path(raw_work)
        extraction_start = time.perf_counter()
        try:
            pages = extract_with_pdftotext(conversion_pdf, work / "extracted.txt")
        except Exception:
            pages = extract_with_pypdf(conversion_pdf)
        if pages and not pages[-1].strip() and len(pages) > article_pages:
            pages.pop()
        metrics = text_metrics(pages)
        method = "pdf-text-layer-to-latex"
        if (
            metrics["text_page_ratio"] < 0.65
            or metrics["characters_per_page"] < 250
            or metrics["alphabetic_ratio"] < 0.35
        ):
            pages = ocr_pdf(conversion_pdf, work)
            metrics = text_metrics(pages)
            method = "ocr-to-latex"
        extraction_seconds = time.perf_counter() - extraction_start
    if metrics["text_page_ratio"] < 0.5 or metrics["extracted_characters"] < 500:
        raise RuntimeError(f"recovered text is insufficient for style evidence: {metrics}")
    quality = str(settings.get("conversion_quality") or conversion_quality(metrics))
    default_weight = defaults["ocr_weight"] if method == "ocr-to-latex" else defaults["text_layer_weight"]
    weight = float(settings.get("evidence_weight", default_weight))
    cap = defaults["ocr_weight"] if method == "ocr-to-latex" else defaults["text_layer_weight"]
    if weight > cap:
        raise RuntimeError(f"configured evidence weight {weight} exceeds source-fidelity cap {cap}")
    latex, prose_blocks, formula_blocks = render_latex(row, pages, method, weight)
    tex_path.write_text(latex, encoding="utf-8")
    warnings = unique(
        [
            *warning_text(method, quality, formula_blocks),
            *[str(item) for item in settings.get("conversion_warnings", [])],
        ]
    )
    result: dict[str, Any] = {
        **row,
        "source_package": relative(package_path, corpus),
        "canonical_main": relative(tex_path, corpus),
        "required_components": "",
        "sha256": sha256_file(package_path),
        "include_in_style": "true",
        "exclusion_reason": "",
        "source_pdf": relative(conversion_pdf, corpus),
        "source_container_pdf": source_container_pdf,
        "conversion_method": method,
        "conversion_quality": quality,
        "evidence_weight": f"{weight:.2f}",
        "conversion_warnings": "; ".join(warnings),
        "resolved_pdf_url": resolved_url,
        "content_type": content_type,
        "downloaded_at": (
            str(existing.get("downloaded_at"))
            if args.rebuild_latex and existing.get("downloaded_at")
            else datetime.now(timezone.utc).isoformat()
        ),
        "download_seconds": round(download_seconds, 6),
        "extraction_seconds": round(extraction_seconds, 6),
        "container_page_count": container_pages,
        "article_page_count": article_pages,
        "article_pdf_start_page": article_start + 1,
        "article_location_evidence": article_evidence,
        "text_metrics": metrics,
        "prose_blocks": prose_blocks,
        "uncertain_formula_blocks": formula_blocks,
        "target_scholar": "Grigori Perelman",
    }
    metadata_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    args = parse_args()
    corpus = args.corpus.resolve()
    manifest_path = corpus / "corpus_manifest.csv"
    fields, rows = read_manifest(manifest_path)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    settings_by_id = dict(plan.get("papers", {}))
    defaults = {
        "text_layer_weight": float(plan.get("text_layer_weight", 0.45)),
        "ocr_weight": float(plan.get("ocr_weight", 0.25)),
    }
    update_native_rows(corpus, rows)
    if args.report_only:
        for row in rows:
            if str(row.get("exclusion_reason", "")).startswith("pdf_conversion_failed:"):
                failure = concise_failure(RuntimeError(str(row.get("exclusion_reason", ""))))
                row["exclusion_reason"] = f"pdf_conversion_failed: {failure}"
                row["conversion_warnings"] = failure
        write_manifest(manifest_path, fields, rows)
        write_exclusions(corpus, rows)
        update_acquisition_report(corpus, rows, 0.0)
        print("DONE report-only", flush=True)
        return 0
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Codex scholar PDF acquisition for an individual user",
            "Accept": "application/pdf,text/html;q=0.7,*/*;q=0.2",
        }
    )
    selected = set(args.only)
    started = time.perf_counter()
    failures = 0
    for index, row in enumerate(rows, start=1):
        paper_id = str(row.get("paper_id", ""))
        if paper_id not in settings_by_id or (selected and paper_id not in selected):
            continue
        if args.rebuild_latex and not (corpus / "tex" / paper_id / "source-package.pdf").is_file():
            print(f"[{index:02d}/{len(rows):02d}] {paper_id}: no local PDF; skipped", flush=True)
            continue
        print(f"[{index:02d}/{len(rows):02d}] {paper_id}", flush=True)
        try:
            result = process_row(
                corpus,
                row,
                settings_by_id[paper_id],
                defaults,
                session,
                args,
            )
            row.clear()
            row.update(result)
            print(
                f"    accepted: method={row['conversion_method']} "
                f"quality={row['conversion_quality']} weight={row['evidence_weight']}",
                flush=True,
            )
        except Exception as exc:
            failures += 1
            failure = concise_failure(exc)
            row.update(
                {
                    "canonical_main": "",
                    "required_components": "",
                    "include_in_style": "false",
                    "exclusion_reason": f"pdf_conversion_failed: {failure}",
                    "source_pdf": "",
                    "source_container_pdf": "",
                    "conversion_method": "",
                    "conversion_quality": "failed",
                    "evidence_weight": "0.00",
                    "conversion_warnings": failure,
                }
            )
            remove_empty_failed_directory(corpus, paper_id)
            print(f"    failed: {failure}", flush=True)
        write_manifest(manifest_path, fields, rows)
        write_exclusions(corpus, rows)
    elapsed = time.perf_counter() - started
    write_manifest(manifest_path, fields, rows)
    write_exclusions(corpus, rows)
    update_acquisition_report(corpus, rows, 0.0 if args.rebuild_latex else elapsed)
    accepted = sum(
        row.get("include_in_style") == "true"
        and str(row.get("conversion_method", "")).endswith("-to-latex")
        for row in rows
    )
    print(f"DONE converted={accepted} failures={failures} elapsed={elapsed:.3f}s")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
