#!/usr/bin/env python3
"""Discover public scholar records in arXiv, HAL, and Zenodo.

The script deliberately stops at a native-TeX candidate list.  It records
PDF-only records for the later consent gate but never downloads their PDFs.
Identity confirmation remains a human/model decision made before this script
is run.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote, quote_plus

import requests
from bs4 import BeautifulSoup


ARCHIVE_SUFFIXES = (
    ".tex",
    ".ltx",
    ".zip",
    ".tar",
    ".tar.gz",
    ".tgz",
    ".gz",
)
PDF_SUFFIXES = (".pdf",)


@dataclass(frozen=True)
class DiscoveryRecord:
    repository: str
    stable_id: str
    year: int | None
    title: str
    authors: tuple[str, ...]
    landing_url: str
    direct_url: str | None
    file_kind: str
    doi: str | None = None
    topic: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Query arXiv, HAL, and Zenodo after scholar identity has been "
            "confirmed, then emit a representative native-TeX candidate list."
        )
    )
    parser.add_argument("--author", required=True)
    parser.add_argument("--official-url", required=True)
    parser.add_argument("--cache-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--pause-seconds", type=float, default=3.0)
    return parser.parse_args()


def compact_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def name_tokens(value: str) -> tuple[str, ...]:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return tuple(sorted(re.findall(r"[a-z0-9]+", value.casefold())))


def exact_author_match(candidate: str, target: str) -> bool:
    return name_tokens(candidate) == name_tokens(target)


def author_slug(author: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", author.casefold()).strip("-")
    if not slug:
        raise ValueError("author name does not produce a safe slug")
    return slug


def request_text(session: requests.Session, url: str, attempts: int = 2) -> str:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = session.get(url, timeout=(20, 120), allow_redirects=True)
            if response.status_code == 200 and response.content:
                # All three endpoints declare or document UTF-8.  Requests may
                # otherwise fall back to ISO-8859-1 for HTML and corrupt names
                # such as Turán or Erdős.
                return response.content.decode("utf-8", errors="replace")
            last_error = RuntimeError(f"HTTP {response.status_code} for {url}")
        except requests.RequestException as exc:
            last_error = exc
        if attempt < attempts:
            time.sleep(5 * attempt)
    raise RuntimeError(str(last_error))


def cached_text(
    session: requests.Session,
    path: Path,
    url: str,
    *,
    refresh: bool,
    offline: bool,
) -> str:
    if path.is_file() and not refresh:
        return path.read_text(encoding="utf-8")
    if offline:
        raise FileNotFoundError(f"offline cache is missing: {path}")
    text = request_text(session, url)
    path.write_text(text, encoding="utf-8")
    return text


def original_year(text: str) -> int | None:
    match = re.search(r"originally announced.*?((?:19|20)\d{2})", text, re.I)
    if match:
        return int(match.group(1))
    years = re.findall(r"(?:19|20)\d{2}", text)
    return int(years[0]) if years else None


def parse_arxiv(html: str, target_author: str) -> list[DiscoveryRecord]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[DiscoveryRecord] = []
    for item in soup.select("li.arxiv-result"):
        id_link = item.select_one("p.list-title a[href*='/abs/']")
        title_node = item.select_one("p.title")
        if id_link is None or title_node is None:
            continue
        authors = tuple(compact_space(node.get_text(" ", strip=True)) for node in item.select("p.authors a"))
        if not any(exact_author_match(author, target_author) for author in authors):
            continue
        stable_id = id_link.get_text(" ", strip=True).removeprefix("arXiv:")
        title = compact_space(title_node.get_text(" ", strip=True))
        date_node = item.find("p", class_="is-size-7")
        year = original_year(date_node.get_text(" ", strip=True) if date_node else "")
        topics = [
            compact_space(node.get_text(" ", strip=True))
            for node in item.select("span.tag[data-tooltip]")
        ]
        records.append(
            DiscoveryRecord(
                repository="arXiv",
                stable_id=stable_id,
                year=year,
                title=title,
                authors=authors,
                landing_url=str(id_link.get("href")),
                direct_url=f"https://arxiv.org/e-print/{stable_id}",
                file_kind="native-tex-source-package",
                topic="; ".join(topics) or None,
            )
        )
    return records


def list_value(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def parse_hal(payload: dict[str, Any], target_author: str) -> list[DiscoveryRecord]:
    records: list[DiscoveryRecord] = []
    for item in payload.get("response", {}).get("docs", []):
        authors = tuple(str(value) for value in list_value(item.get("authFullName_s")))
        if not any(exact_author_match(author, target_author) for author in authors):
            continue
        titles = list_value(item.get("title_s"))
        title = compact_space(str(titles[0])) if titles else ""
        base_id = str(item.get("halId_s") or item.get("docid") or "")
        files = [str(value) for value in list_value(item.get("files_s"))]
        if not files:
            direct_url = item.get("fileMain_s")
            records.append(
                DiscoveryRecord(
                    repository="HAL",
                    stable_id=base_id,
                    year=int(item["producedDateY_i"]) if item.get("producedDateY_i") else None,
                    title=title,
                    authors=authors,
                    landing_url=str(item.get("uri_s") or ""),
                    direct_url=str(direct_url) if direct_url else None,
                    file_kind="unknown-document" if direct_url else "metadata-only",
                    doi=str(item.get("doiId_s")) if item.get("doiId_s") else None,
                )
            )
            continue
        for file_url in files:
            filename = file_url.rsplit("/", 1)[-1]
            records.append(
                DiscoveryRecord(
                    repository="HAL",
                    stable_id=f"{base_id}-{filename}",
                    year=int(item["producedDateY_i"]) if item.get("producedDateY_i") else None,
                    title=title,
                    authors=authors,
                    landing_url=str(item.get("uri_s") or ""),
                    direct_url=file_url,
                    file_kind=suffix_kind(filename),
                    doi=str(item.get("doiId_s")) if item.get("doiId_s") else None,
                )
            )
    return records


def zenodo_creator_name(creator: dict[str, Any]) -> str:
    person = creator.get("person_or_org") or {}
    return str(person.get("name") or creator.get("name") or "")


def zenodo_file_url(file_record: dict[str, Any]) -> str | None:
    links = file_record.get("links") or {}
    return links.get("content") or links.get("self")


def suffix_kind(filename: str) -> str:
    lower = filename.casefold()
    if lower.endswith(ARCHIVE_SUFFIXES):
        return "native-tex-candidate"
    if lower.endswith(PDF_SUFFIXES):
        return "pdf"
    return "other"


def parse_zenodo(payload: dict[str, Any], target_author: str) -> list[DiscoveryRecord]:
    records: list[DiscoveryRecord] = []
    for item in payload.get("hits", {}).get("hits", []):
        metadata = item.get("metadata") or {}
        creators = tuple(zenodo_creator_name(value) for value in metadata.get("creators", []))
        if not any(exact_author_match(author, target_author) for author in creators):
            continue
        published = str(metadata.get("publication_date") or item.get("created") or "")
        year_match = re.search(r"(?:19|20)\d{2}", published)
        year = int(year_match.group(0)) if year_match else None
        files = item.get("files") or []
        if not files:
            records.append(
                DiscoveryRecord(
                    repository="Zenodo",
                    stable_id=str(item.get("id") or ""),
                    year=year,
                    title=compact_space(str(metadata.get("title") or "")),
                    authors=creators,
                    landing_url=str((item.get("links") or {}).get("self_html") or ""),
                    direct_url=None,
                    file_kind="metadata-only",
                )
            )
            continue
        for file_record in files:
            filename = str(file_record.get("key") or "")
            kind = suffix_kind(filename)
            if kind not in {"native-tex-candidate", "pdf"}:
                continue
            records.append(
                DiscoveryRecord(
                    repository="Zenodo",
                    stable_id=f"{item.get('id')}-{filename}",
                    year=year,
                    title=compact_space(str(metadata.get("title") or "")),
                    authors=creators,
                    landing_url=str((item.get("links") or {}).get("self_html") or ""),
                    direct_url=zenodo_file_url(file_record),
                    file_kind=kind,
                )
            )
    return records


def record_dict(record: DiscoveryRecord) -> dict[str, Any]:
    return {
        "repository": record.repository,
        "stable_id": record.stable_id,
        "year": record.year,
        "title": record.title,
        "authors": list(record.authors),
        "landing_url": record.landing_url,
        "direct_url": record.direct_url,
        "file_kind": record.file_kind,
        "doi": record.doi,
        "topic": record.topic,
    }


def dedupe(records: Iterable[DiscoveryRecord]) -> list[DiscoveryRecord]:
    priority = {"arXiv": 0, "HAL": 1, "Zenodo": 2}
    ordered = sorted(records, key=lambda item: (priority.get(item.repository, 9), item.year or 0))
    seen_titles: set[str] = set()
    seen_dois: set[str] = set()
    result: list[DiscoveryRecord] = []
    for record in ordered:
        title_key = normalized(record.title)
        doi_key = normalized(record.doi or "")
        if title_key and title_key in seen_titles:
            continue
        if doi_key and doi_key in seen_dois:
            continue
        result.append(record)
        if title_key:
            seen_titles.add(title_key)
        if doi_key:
            seen_dois.add(doi_key)
    return result


def evenly_spaced(records: list[DiscoveryRecord], count: int) -> list[DiscoveryRecord]:
    if count <= 0:
        return []
    if len(records) <= count:
        return records[:]
    if count == 1:
        return [records[len(records) // 2]]
    positions = [round(index * (len(records) - 1) / (count - 1)) for index in range(count)]
    return [records[position] for position in positions]


def representative_sample(records: list[DiscoveryRecord], limit: int) -> list[DiscoveryRecord]:
    ordered = sorted(records, key=lambda item: (item.year or 0, item.title.casefold()))
    if len(ordered) <= limit:
        return ordered
    # Preserve a substantial author-only signal when sole-authored material is
    # available, then fill the remainder evenly across the coauthored timeline.
    # Forty percent is a preference rather than a requirement; scarce solo work
    # never blocks completion.
    sole = [record for record in ordered if len(record.authors) == 1]
    coauthored = [record for record in ordered if len(record.authors) != 1]
    sole_quota = min(len(sole), math.ceil(limit * 0.4))
    selected = evenly_spaced(sole, sole_quota)
    selected.extend(evenly_spaced(coauthored, limit - len(selected)))
    return sorted(selected, key=lambda item: (item.year or 0, item.title.casefold()))


def acquisition_row(record: DiscoveryRecord, author: str, official_url: str) -> dict[str, Any]:
    slug = author_slug(author)
    year = record.year or 0
    stable = re.sub(r"[^a-zA-Z0-9.-]+", "-", record.stable_id).strip("-")
    coauthors = [value for value in record.authors if not exact_author_match(value, author)]
    return {
        "paper_id": f"{slug}-{year}-{stable}",
        "year": record.year,
        "title": record.title,
        "authors": "; ".join(record.authors),
        "source_url": record.direct_url,
        "source_kind": f"{record.repository} source package",
        "abstract_url": record.landing_url,
        "solo_or_coauthored": "sole-authored" if not coauthors else "coauthored",
        "coauthors": "; ".join(coauthors),
        "venue": None,
        "topic": record.topic,
        "version": None,
        "identity_evidence": (
            f"Exact author match in {record.repository}; scholar identity confirmed against {official_url}."
        ),
        "notes": "Selected by deterministic early/middle/recent sampling.",
    }


def write_report(
    path: Path,
    author: str,
    official_url: str,
    records: list[DiscoveryRecord],
    selected: list[DiscoveryRecord],
) -> None:
    repository_titles: dict[str, set[tuple[str, int | None]]] = {}
    native_counts: dict[str, int] = {}
    pdf_counts: dict[str, int] = {}
    other_counts: dict[str, int] = {}
    for record in records:
        repository_titles.setdefault(record.repository, set()).add((normalized(record.title), record.year))
        if record.file_kind in {"native-tex-source-package", "native-tex-candidate"}:
            native_counts[record.repository] = native_counts.get(record.repository, 0) + 1
        if record.file_kind == "pdf":
            pdf_counts[record.repository] = pdf_counts.get(record.repository, 0) + 1
        if record.file_kind not in {"native-tex-source-package", "native-tex-candidate", "pdf"}:
            other_counts[record.repository] = other_counts.get(record.repository, 0) + 1
    lines = [
        "# Multi-source Discovery Report",
        "",
        f"- Target scholar: {author}",
        f"- Confirmed identity page: {official_url}",
        f"- Queried at: {datetime.now(timezone.utc).isoformat()}",
        f"- Native-TeX candidates selected: {len(selected)}",
        "",
        "| repository | exact-author papers | native-TeX files | PDF files | other/unknown |",
        "|---|---:|---:|---:|---:|",
    ]
    for repository in ("arXiv", "HAL", "Zenodo"):
        lines.append(
            f"| {repository} | {len(repository_titles.get(repository, set()))} | "
            f"{native_counts.get(repository, 0)} | {pdf_counts.get(repository, 0)} | "
            f"{other_counts.get(repository, 0)} |"
        )
    lines.extend(
        [
            "",
            "PDFs were inventoried only. They were not downloaded. If fewer than 20 native-TeX papers "
            "survive acquisition, ask the user before enabling PDF fallback.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.limit < 1 or args.limit > 30:
        raise ValueError("--limit must be between 1 and 30")
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Codex scholar discovery for an individual research corpus",
            "Accept": "text/html, application/json;q=0.9, */*;q=0.5",
        }
    )

    arxiv_url = (
        "https://arxiv.org/search/?query="
        f"{quote_plus(args.author)}&searchtype=author&abstracts=show&"
        "order=-announced_date_first&size=200"
    )
    hal_query = quote(f'authFullName_t:"{args.author}"', safe="")
    hal_url = (
        "https://api.archives-ouvertes.fr/search/?q="
        f"{hal_query}&fl=docid,halId_s,title_s,authFullName_s,producedDateY_i,"
        "uri_s,fileMain_s,files_s,fileType_s,doiId_s&rows=100&wt=json"
    )
    parts = args.author.split()
    zenodo_name = f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else args.author
    zenodo_query = quote(
        f'metadata.creators.person_or_org.name:"{zenodo_name}"', safe=""
    )
    zenodo_url = f"https://zenodo.org/api/records/?q={zenodo_query}&size=25"

    arxiv_text = cached_text(
        session,
        args.cache_dir / "arxiv-search.html",
        arxiv_url,
        refresh=args.refresh,
        offline=args.offline,
    )
    if args.pause_seconds > 0 and (args.refresh or not (args.cache_dir / "hal.json").is_file()):
        time.sleep(args.pause_seconds)
    hal_text = cached_text(
        session,
        args.cache_dir / "hal.json",
        hal_url,
        refresh=args.refresh,
        offline=args.offline,
    )
    if args.pause_seconds > 0 and (args.refresh or not (args.cache_dir / "zenodo.json").is_file()):
        time.sleep(args.pause_seconds)
    zenodo_text = cached_text(
        session,
        args.cache_dir / "zenodo.json",
        zenodo_url,
        refresh=args.refresh,
        offline=args.offline,
    )

    records = [
        *parse_arxiv(arxiv_text, args.author),
        *parse_hal(json.loads(hal_text), args.author),
        *parse_zenodo(json.loads(zenodo_text), args.author),
    ]
    native = [
        record
        for record in records
        if record.direct_url
        and record.file_kind in {"native-tex-source-package", "native-tex-candidate"}
    ]
    selected = representative_sample(dedupe(native), args.limit)
    candidate_rows = [acquisition_row(record, args.author, args.official_url) for record in selected]
    args.output.write_text(
        json.dumps(candidate_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    all_records_path = args.output.with_name(args.output.stem + "_all_records.json")
    all_records_path.write_text(
        json.dumps([record_dict(record) for record in records], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path = args.output.with_name(args.output.stem + "_discovery_report.md")
    write_report(report_path, args.author, args.official_url, records, selected)

    counts: dict[str, int] = {}
    for record in records:
        counts[record.repository] = counts.get(record.repository, 0) + 1
    print(
        f"DONE arxiv={counts.get('arXiv', 0)} hal={counts.get('HAL', 0)} "
        f"zenodo={counts.get('Zenodo', 0)} selected_native_tex={len(selected)}"
    )
    print(f"candidates={args.output.resolve()}")
    print(f"report={report_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
