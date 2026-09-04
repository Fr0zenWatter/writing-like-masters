from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import re
import sys
import tarfile
import time
import zipfile
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


MANIFEST_FIELDS = [
    "paper_id",
    "year",
    "title",
    "authors",
    "source_url",
    "source_kind",
    "source_package",
    "canonical_main",
    "required_components",
    "sha256",
    "include_in_style",
    "exclusion_reason",
    "source_pdf",
    "source_container_pdf",
    "conversion_method",
    "conversion_quality",
    "evidence_weight",
    "conversion_warnings",
]

EXTERNAL_TEX_INPUTS = {
    "amssym",
    "amstex",
    "epsf",
    "epsfig",
    "pictex",
    "plain",
    "xypic",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download confirmed TeX source packages, extract them safely, identify "
            "main files and local dependencies, and write the acquisition manifest."
        )
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Prepared-corpus directory; normally <repository>/corpora/<author-slug>",
    )
    parser.add_argument(
        "--allow-output-outside-corpora",
        action="store_true",
        help="Allow an explicitly chosen non-canonical output directory",
    )
    parser.add_argument("--target-scholar", required=True)
    parser.add_argument("--identity-anchor", required=True)
    parser.add_argument("--discovery-sources", default="")
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--pause-seconds", type=float, default=3.0)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_candidates(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            payload: Any = list(csv.DictReader(handle))
    else:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("candidate file must contain a JSON array or be a CSV manifest")
    required = {"paper_id", "year", "title", "authors", "source_url", "source_kind"}
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for index, candidate in enumerate(payload, start=1):
        if not isinstance(candidate, dict):
            raise ValueError(f"candidate {index} is not an object")
        missing = sorted(required - candidate.keys())
        if missing:
            raise ValueError(f"candidate {index} is missing: {', '.join(missing)}")
        paper_id = str(candidate["paper_id"]).strip()
        if not paper_id or paper_id in seen:
            raise ValueError(f"candidate {index} has an empty or duplicate paper_id")
        if Path(paper_id).name != paper_id or any(c in paper_id for c in "\\/:*?\"<>|"):
            raise ValueError(f"candidate {index} has an unsafe paper_id: {paper_id!r}")
        seen.add(paper_id)
        rows.append(candidate)
    return rows


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def validate_output_directory(path: Path, allow_noncanonical: bool) -> Path:
    """Keep ordinary runs in the repository's disposable corpora workspace."""
    output = path.resolve()
    if allow_noncanonical:
        return output

    repository_root = Path(__file__).resolve().parent.parent
    corpora_root = (repository_root / "corpora").resolve()
    try:
        relative = output.relative_to(corpora_root)
    except ValueError as exc:
        raise ValueError(
            f"--output must be <repository>/corpora/<author-slug>; got {output}. "
            "Use --allow-output-outside-corpora only for an explicitly chosen exception."
        ) from exc
    if len(relative.parts) != 1:
        raise ValueError(
            f"--output must name one direct author directory below {corpora_root}; got {output}"
        )
    return output


def safe_extract_tar(data: bytes, destination: Path) -> bool:
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            members = archive.getmembers()
            for member in members:
                if member.issym() or member.islnk() or member.isdev():
                    raise RuntimeError(f"unsafe tar member type: {member.name}")
                if not is_within(destination / member.name, destination):
                    raise RuntimeError(f"tar member escapes destination: {member.name}")
            archive.extractall(destination, members=members)
        return True
    except tarfile.ReadError:
        return False


def safe_extract_zip(data: bytes, destination: Path) -> bool:
    stream = io.BytesIO(data)
    if not zipfile.is_zipfile(stream):
        return False
    stream.seek(0)
    with zipfile.ZipFile(stream) as archive:
        for info in archive.infolist():
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise RuntimeError(f"unsafe zip symlink: {info.filename}")
            if not is_within(destination / info.filename, destination):
                raise RuntimeError(f"zip member escapes destination: {info.filename}")
        archive.extractall(destination)
    return True


def unpack_source(data: bytes, destination: Path) -> tuple[str, str]:
    if data.startswith(b"%PDF-"):
        raise RuntimeError("response is a PDF, not a TeX source package")
    if re.match(br"\s*<(?:!doctype\s+html|html)\b", data[:1024], re.IGNORECASE):
        raise RuntimeError("response is HTML, not a TeX source package")
    destination.mkdir(parents=True, exist_ok=False)
    if safe_extract_tar(data, destination):
        suffix = "tar.gz" if data[:2] == b"\x1f\x8b" else "tar"
        return "tar", f"source-package.{suffix}"
    if safe_extract_zip(data, destination):
        return "zip", "source-package.zip"
    if data[:2] == b"\x1f\x8b":
        raw = gzip.decompress(data)
        if safe_extract_tar(raw, destination):
            return "gzip-tar", "source-package.gz"
        (destination / "main.tex").write_bytes(raw)
        return "gzip-single-tex", "source-package.tex.gz"
    (destination / "main.tex").write_bytes(data)
    return "single-file", "source-package.tex"


def decode_tex(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def strip_comments(text: str) -> str:
    cleaned: list[str] = []
    for line in text.splitlines():
        cut = len(line)
        for match in re.finditer(r"%", line):
            backslashes = 0
            pos = match.start() - 1
            while pos >= 0 and line[pos] == "\\":
                backslashes += 1
                pos -= 1
            if backslashes % 2 == 0:
                cut = match.start()
                break
        cleaned.append(line[:cut])
    return "\n".join(cleaned)


def title_tokens(title: str) -> set[str]:
    stop = {"a", "an", "and", "for", "in", "of", "on", "the", "to", "with"}
    return {
        token
        for token in re.findall(r"[a-z0-9]+", title.lower())
        if len(token) > 2 and token not in stop
    }


def main_score(path: Path, text: str, title: str, target_scholar: str) -> float:
    cleaned = strip_comments(text)
    lower = cleaned.lower()
    score = math.log2(max(path.stat().st_size, 1))
    if "\\documentclass" in cleaned:
        score += 100
    if "\\documentstyle" in cleaned:
        score += 90
    if "\\begin{document}" in cleaned:
        score += 100
    if "\\bye" in cleaned:
        score += 35
    if "\\title" in cleaned:
        score += 20
    surname = target_scholar.split()[-1].lower()
    if surname and surname in lower:
        score += 15
    tokens = title_tokens(title)
    if tokens:
        score += 30 * len(tokens & set(re.findall(r"[a-z0-9]+", lower))) / len(tokens)
    name = path.name.lower()
    if re.search(r"rebuttal|response|cover|letter|slides?|poster|template|example", name):
        score -= 150
    return score


def choose_main(source_dir: Path, title: str, target_scholar: str) -> tuple[Path, list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    for path in sorted(source_dir.rglob("*.tex")):
        if not path.is_file():
            continue
        text = decode_tex(path)
        cleaned = strip_comments(text)
        is_driver = (
            ("\\begin{document}" in cleaned and ("\\documentclass" in cleaned or "\\documentstyle" in cleaned))
            or (
                "\\documentstyle" in cleaned
                and re.search(r"\\document(?:\s|$)", cleaned, re.MULTILINE) is not None
            )
            or "\\bye" in cleaned
        )
        candidates.append(
            {
                "path": path,
                "relative": path.relative_to(source_dir).as_posix(),
                "score": main_score(path, text, title, target_scholar),
                "is_driver": is_driver,
                "bytes": path.stat().st_size,
            }
        )
    if not candidates:
        raise RuntimeError("no .tex files found")
    drivers = [item for item in candidates if item["is_driver"]]
    pool = drivers
    if not pool:
        raise RuntimeError("no TeX document driver found")
    selected = max(pool, key=lambda item: (item["score"], item["bytes"]))
    evidence = [
        {
            "path": item["relative"],
            "score": round(float(item["score"]), 3),
            "is_driver": bool(item["is_driver"]),
            "bytes": int(item["bytes"]),
        }
        for item in sorted(candidates, key=lambda item: item["score"], reverse=True)
    ]
    return selected["path"], evidence


INPUT_PATTERN = re.compile(
    r"\\(?:input|include(?!graphics\b))\s*(?:\{([^}]+)\}|([^\s%{}]+))",
    re.IGNORECASE,
)


def resolve_dependencies(main_path: Path, source_dir: Path) -> tuple[list[str], list[str], list[str]]:
    required: set[Path] = set()
    blocking_missing: set[str] = set()
    external_missing: set[str] = set()
    queue = [main_path]
    visited: set[Path] = set()
    while queue:
        current = queue.pop(0).resolve()
        if current in visited:
            continue
        visited.add(current)
        text = strip_comments(decode_tex(current))
        for match in INPUT_PATTERN.finditer(text):
            raw = (match.group(1) or match.group(2) or "").strip().strip('"\'')
            if not raw or "#" in raw or "\\" in raw:
                continue
            relative = Path(raw)
            options = [current.parent / relative]
            if not relative.suffix:
                options.append(current.parent / f"{raw}.tex")
            found = next((p for p in options if p.is_file() and is_within(p, source_dir)), None)
            if found is not None:
                resolved = found.resolve()
                if resolved != main_path.resolve() and resolved not in required:
                    required.add(resolved)
                    if resolved.suffix.lower() == ".tex":
                        queue.append(resolved)
                continue
            token = relative.stem.lower()
            if token in EXTERNAL_TEX_INPUTS or (not relative.suffix and len(relative.parts) == 1):
                external_missing.add(raw)
            else:
                blocking_missing.add(raw)
    required_paths = sorted(path.relative_to(source_dir).as_posix() for path in required)
    return required_paths, sorted(blocking_missing), sorted(external_missing)


def download_with_retry(
    session: requests.Session,
    url: str,
    attempts: int,
) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        response: requests.Response | None = None
        try:
            response = session.get(url, timeout=(20, 180), allow_redirects=True)
            content_type = response.headers.get("Content-Type", "").lower()
            if response.status_code == 200 and response.content and "text/html" not in content_type:
                return response
            detail = response.text[:180].replace("\n", " ") if response.content else "empty response"
            last_error = RuntimeError(
                f"HTTP {response.status_code}, content-type {content_type!r}: {detail}"
            )
        except requests.RequestException as exc:
            last_error = exc
        if attempt < attempts:
            # Authentication/permission and permanent-missing responses are
            # not plausibly transient. Repeating them only adds avoidable load.
            if response is not None and response.status_code in {400, 401, 403, 404, 410}:
                break
            delay = 15 * (2 ** (attempt - 1))
            if response is not None:
                retry_after = response.headers.get("Retry-After", "").strip()
                if retry_after.isdigit():
                    delay = max(delay, int(retry_after))
                elif retry_after:
                    try:
                        retry_at = parsedate_to_datetime(retry_after)
                        now = datetime.now(retry_at.tzinfo or timezone.utc)
                        delay = max(delay, math.ceil((retry_at - now).total_seconds()))
                    except (TypeError, ValueError, OverflowError):
                        pass
            print(f"    retrying in {delay}s: {last_error}", flush=True)
            time.sleep(delay)
    raise RuntimeError(str(last_error))


def csv_bool(value: bool) -> str:
    return "true" if value else "false"


def manifest_row(candidate: dict[str, Any]) -> dict[str, str]:
    return {
        field: str(candidate.get(field, "") if candidate.get(field, "") is not None else "")
        for field in MANIFEST_FIELDS
    }


def write_manifest(output: Path, rows: list[dict[str, Any]]) -> None:
    path = output / "corpus_manifest.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(manifest_row(row))


def md_escape(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def write_exclusions(output: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Exclusions",
        "",
        "| paper_id | title | source | reason |",
        "|---|---|---|---|",
    ]
    for row in rows:
        if row.get("include_in_style") == "true":
            continue
        lines.append(
            f"| {md_escape(row.get('paper_id'))} | {md_escape(row.get('title'))} | "
            f"{md_escape(row.get('source_url'))} | {md_escape(row.get('exclusion_reason'))} |"
        )
    (output / "exclusions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(
    output: Path,
    rows: list[dict[str, Any]],
    args: argparse.Namespace,
    started_at: datetime,
    wall_seconds: float,
) -> None:
    accepted = [row for row in rows if row.get("include_in_style") == "true"]
    excluded = [row for row in rows if row.get("include_in_style") != "true"]
    years = [int(row["year"]) for row in accepted if str(row.get("year", "")).isdigit()]
    candidate_years = [int(row["year"]) for row in rows if str(row.get("year", "")).isdigit()]
    downloads = sum(float(row.get("download_seconds", 0) or 0) for row in accepted)
    extraction = sum(float(row.get("extract_seconds", 0) or 0) for row in accepted)
    inspection = sum(float(row.get("inspection_seconds", 0) or 0) for row in accepted)
    sole_authored = sum(row.get("solo_or_coauthored") == "sole-authored" for row in accepted)
    coauthored = sum(row.get("solo_or_coauthored") == "coauthored" for row in accepted)
    topics = sorted({str(row.get("topic") or "").strip() for row in accepted} - {""})
    venues = sorted({str(row.get("venue") or "").strip() for row in accepted} - {""})
    native_tex = sum(row.get("conversion_method") == "native-tex" for row in accepted)
    pdf_derived = len(accepted) - native_tex
    canonical_valid = all((output / str(row.get("canonical_main") or "")).is_file() for row in accepted)
    dependencies_valid = all(
        all((output / item).is_file() for item in str(row.get("required_components") or "").split(";") if item)
        for row in accepted
    )
    disposition: dict[str, list[int]] = {}
    for row in rows:
        counts = disposition.setdefault(str(row.get("source_kind") or "unknown"), [0, 0])
        counts[0 if row.get("include_in_style") == "true" else 1] += 1
    lines = [
        "# Acquisition Report",
        "",
        f"- Target scholar: {args.target_scholar}",
        f"- Identity anchor: {args.identity_anchor}",
        f"- Discovery sources: {args.discovery_sources or 'not recorded'}",
        f"- Run started: {started_at.isoformat()}",
        f"- Candidate papers: {len(rows)}",
        f"- Candidate year range: {min(candidate_years)}-{max(candidate_years)}" if candidate_years else "- Candidate year range: none",
        f"- Accepted TeX papers: {len(accepted)}",
        f"- Excluded papers: {len(excluded)}",
        f"- Accepted year range: {min(years)}-{max(years)}" if years else "- Accepted year range: none",
        f"- Sole-authored papers: {sole_authored}",
        f"- Coauthored papers: {coauthored}",
        f"- Topics represented: {', '.join(topics) if topics else 'not recorded'}",
        f"- Venues represented: {', '.join(venues) if venues else 'not recorded'}",
        f"- Native TeX papers: {native_tex}",
        f"- PDF-derived papers: {pdf_derived}",
        f"- Prepared corpus: {output.resolve()}",
        "",
        "## Validation",
        "",
        f"- Canonical main files exist: {'pass' if canonical_valid else 'FAIL'}",
        f"- Recorded local dependencies exist: {'pass' if dependencies_valid else 'FAIL'}",
        "- Every accepted item preserves its original source package and records its SHA-256 digest.",
        "- Excluded items do not enter the style corpus.",
        "",
        "## Candidate Disposition",
        "",
        "| source kind | accepted | excluded |",
        "|---|---:|---:|",
        *[
            f"| {kind} | {counts[0]} | {counts[1]} |"
            for kind, counts in sorted(disposition.items())
        ],
        "",
        "## Automated Timing",
        "",
        f"- Network download: {downloads:.3f} s",
        f"- Extraction and hashing: {extraction:.3f} s",
        f"- Main-file and dependency inspection: {inspection:.3f} s",
        f"- Current acquisition/resume pass wall time: {wall_seconds:.3f} s",
        "",
        "## Automation Assessment",
        "",
        "The repeated mechanical work is suitable for Python: downloading with bounded retries, "
        "content-type detection, safe archive extraction, SHA-256 calculation, TeX-driver scoring, "
        "local input-graph traversal, metadata serialization, manifest generation, exclusion-table "
        "generation, and resumable validation. These operations are performed by "
        "scripts/scholar_tex_acquire.py in this run.",
        "",
        "The model should retain responsibility for identity disambiguation, deciding whether a "
        "mixed archive contains a coherent authorial manuscript, selecting a representative time "
        "sample, and judging coauthor, topic, and venue contamination. In the later style stage, "
        "Python should extract section boundaries, sentence and paragraph measurements, macros, "
        "environments, labels, references, citations, and symbol candidates; the model should infer "
        "rhetorical function, temporal maturity, attribution, and executable writing rules.",
        "",
        "## Known Limitation",
        "",
    ]
    if len(accepted) < 20:
        lines.append(
            "This is a limited native-TeX corpus because fewer than 20 selected papers passed "
            "acquisition. PDF fallback requires the user's explicit approval before any PDF download."
        )
    else:
        lines.append(
            "The corpus meets the 20-paper native-TeX threshold. Selection is capped at 30 papers "
            "and preserves early, middle, and recent coverage. Venue values remain unknown where "
            "the official discovery record was not transcribed into the candidate list."
        )
    (output / "ACQUISITION_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def process_candidate(
    candidate: dict[str, Any],
    output: Path,
    session: requests.Session,
    args: argparse.Namespace,
) -> dict[str, Any]:
    row: dict[str, Any] = {**candidate}
    row.setdefault("source_package", "")
    row.setdefault("canonical_main", "")
    row.setdefault("required_components", "")
    row.setdefault("sha256", "")
    row.setdefault("source_pdf", "")
    row.setdefault("source_container_pdf", "")
    row.setdefault("conversion_method", "native-tex")
    row.setdefault("conversion_quality", "native")
    row.setdefault("evidence_weight", "0.00")
    row.setdefault("conversion_warnings", "")
    preset_reason = str(candidate.get("exclusion_reason") or "").strip()
    if preset_reason:
        row["include_in_style"] = "false"
        return row

    paper_dir = output / "tex" / str(candidate["paper_id"])
    metadata_path = paper_dir / "metadata.json"
    if metadata_path.is_file():
        existing = json.loads(metadata_path.read_text(encoding="utf-8"))
        canonical = output / str(existing.get("canonical_main", ""))
        if existing.get("include_in_style") == "true" and canonical.is_file():
            # Discovery metadata may improve between resumable runs (for
            # example, a cleaned title or subject classification). Preserve
            # the URL tied to the downloaded bytes, but refresh descriptive
            # fields from the current confirmed candidate list.
            for field in (
                "year",
                "title",
                "authors",
                "abstract_url",
                "solo_or_coauthored",
                "coauthors",
                "venue",
                "topic",
                "version",
                "identity_evidence",
                "notes",
            ):
                if field in candidate:
                    existing[field] = candidate[field]
            existing.setdefault("source_pdf", "")
            existing.setdefault("source_container_pdf", "")
            existing.setdefault("conversion_method", "native-tex")
            existing.setdefault("conversion_quality", "native")
            existing.setdefault("evidence_weight", "1.00")
            existing.setdefault("conversion_warnings", "")
            metadata_path.write_text(
                json.dumps(existing, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print("    using validated existing download", flush=True)
            return existing

    paper_dir.mkdir(parents=True, exist_ok=True)
    source_dir = paper_dir / "source"
    content_type = ""
    if source_dir.exists():
        packages = sorted(path for path in paper_dir.glob("source-package.*") if path.is_file())
        if len(packages) != 1:
            raise RuntimeError(f"unvalidated source directory cannot be resumed safely: {source_dir}")
        package_path = packages[0]
        data = package_path.read_bytes()
        digest = sha256_bytes(data)
        package_type = "resumed-existing"
        download_seconds = 0.0
        extract_seconds = 0.0
        print("    resuming inspection of preserved source package", flush=True)
    else:
        download_start = time.perf_counter()
        response = download_with_retry(session, str(candidate["source_url"]), args.attempts)
        data = response.content
        content_type = response.headers.get("Content-Type", "")
        download_seconds = time.perf_counter() - download_start

        extract_start = time.perf_counter()
        package_type, package_name = unpack_source(data, source_dir)
        package_path = paper_dir / package_name
        package_path.write_bytes(data)
        digest = sha256_bytes(data)
        extract_seconds = time.perf_counter() - extract_start

    inspect_start = time.perf_counter()
    main_path, main_evidence = choose_main(
        source_dir,
        str(candidate["title"]),
        args.target_scholar,
    )
    required, blocking_missing, external_missing = resolve_dependencies(main_path, source_dir)
    inspection_seconds = time.perf_counter() - inspect_start
    if blocking_missing:
        raise RuntimeError(f"missing local TeX dependencies: {', '.join(blocking_missing)}")

    row.update(
        {
            "source_package": package_path.relative_to(output).as_posix(),
            "canonical_main": main_path.relative_to(output).as_posix(),
            "required_components": ";".join(
                (source_dir / item).relative_to(output).as_posix() for item in required
            ),
            "sha256": digest,
            "include_in_style": "true",
            "exclusion_reason": "",
            "source_pdf": "",
            "source_container_pdf": "",
            "conversion_method": "native-tex",
            "conversion_quality": "native",
            "evidence_weight": "1.00",
            "conversion_warnings": "",
            "package_type": package_type,
            "content_type": content_type,
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
            "download_seconds": round(download_seconds, 6),
            "extract_seconds": round(extract_seconds, 6),
            "inspection_seconds": round(inspection_seconds, 6),
            "tex_file_count": sum(1 for path in source_dir.rglob("*.tex") if path.is_file()),
            "source_file_count": sum(1 for path in source_dir.rglob("*") if path.is_file()),
            "main_candidate_evidence": main_evidence,
            "nonblocking_external_inputs": external_missing,
            "target_scholar": args.target_scholar,
            "identity_anchor": args.identity_anchor,
        }
    )
    metadata_path.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    args = parse_args()
    if args.attempts < 1:
        raise ValueError("--attempts must be at least 1")
    output = validate_output_directory(args.output, args.allow_output_outside_corpora)
    candidates = load_candidates(args.candidates)
    if args.dry_run:
        print(f"validated {len(candidates)} candidates")
        print(f"output={output}")
        for candidate in candidates:
            action = "exclude" if candidate.get("exclusion_reason") else "download"
            print(f"{action:8} {candidate['paper_id']}  {candidate['title']}")
        return 0

    output.mkdir(parents=True, exist_ok=True)
    (output / "tex").mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Codex scholar TeX acquisition for an individual user",
            "Accept": "application/x-eprint-tar, application/gzip, application/octet-stream, text/plain;q=0.8",
        }
    )

    started_at = datetime.now(timezone.utc)
    wall_start = time.perf_counter()
    rows: list[dict[str, Any]] = []
    downloadable = [candidate for candidate in candidates if not candidate.get("exclusion_reason")]
    completed_downloads = 0
    for index, candidate in enumerate(candidates, start=1):
        print(f"[{index:02d}/{len(candidates):02d}] {candidate['paper_id']}", flush=True)
        try:
            row = process_candidate(candidate, output, session, args)
            if row.get("include_in_style") == "true":
                completed_downloads += 1
                print(
                    f"    accepted: {row.get('tex_file_count', 0)} TeX file(s), "
                    f"main={row.get('canonical_main')}",
                    flush=True,
                )
            else:
                print(f"    excluded: {row.get('exclusion_reason')}", flush=True)
        except Exception as exc:
            # A failed HTTP request can leave the paper directory empty because
            # it is created before download. Remove only that exact directory,
            # and only when it is empty, so excluded candidates do not leave
            # administrative debris in the canonical tree.
            failed_dir = output / "tex" / str(candidate["paper_id"])
            try:
                failed_dir.rmdir()
            except OSError:
                pass
            row = {
                **candidate,
                "source_package": "",
                "canonical_main": "",
                "required_components": "",
                "sha256": "",
                "include_in_style": "false",
                "exclusion_reason": f"acquisition_failed: {exc}",
                "source_pdf": "",
                "source_container_pdf": "",
                "conversion_method": "native-tex",
                "conversion_quality": "native",
                "evidence_weight": "0.00",
                "conversion_warnings": "",
            }
            print(f"    excluded after failure: {exc}", flush=True)
        rows.append(row)
        write_manifest(output, rows)
        write_exclusions(output, rows)
        if (
            not candidate.get("exclusion_reason")
            and completed_downloads < len(downloadable)
            and args.pause_seconds > 0
        ):
            time.sleep(args.pause_seconds)

    wall_seconds = time.perf_counter() - wall_start
    write_manifest(output, rows)
    write_exclusions(output, rows)
    write_report(output, rows, args, started_at, wall_seconds)
    accepted = sum(row.get("include_in_style") == "true" for row in rows)
    print(f"DONE candidates={len(rows)} accepted={accepted} excluded={len(rows)-accepted}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
