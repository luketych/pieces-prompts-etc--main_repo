#!/usr/bin/env python3
"""Verify raw GitHub URLs for markdown files under card_linked/.

By default this script:
1. Recurses through card_linked/ for every .md file.
2. Builds the expected raw.githubusercontent.com URL for each file.
3. Verifies the URL is accessible.
4. Also scans markdown files for raw.githubusercontent.com URLs and verifies those too.

It prints loud WARNING lines for any inaccessible URL or scan issue and reports the
local file path plus the URL involved.

Note: local files that have not been committed/pushed to the configured ref yet will
correctly show up as warnings.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote
from urllib.request import Request, urlopen


DEFAULT_SCAN_ROOT = "card_linked"
DEFAULT_REPO = "luketych/pieces-prompts-etc--main_repo"
DEFAULT_REF = "refs/heads/main"
DEFAULT_TIMEOUT = 15
RAW_URL_RE = re.compile(r"https://raw\.githubusercontent\.com/[^\s)\]>]+")
USER_AGENT = "pieces-prompts-etc-url-verifier/1.0"


@dataclass(frozen=True)
class UrlCheckResult:
    ok: bool
    status: int | None = None
    error: str | None = None
    final_url: str | None = None


@dataclass(frozen=True)
class GeneratedFileCheck:
    path: Path
    url: str


@dataclass(frozen=True)
class EmbeddedUrlCheck:
    source_path: Path
    url: str
    target_path: Path | None


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def raw_base_url(repo: str, ref: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{ref}/"


def rel_repo_path(path: Path, root: Path) -> Path:
    return path.resolve().relative_to(root.resolve())


def display_path(path: Path, root: Path) -> str:
    try:
        return rel_repo_path(path, root).as_posix()
    except ValueError:
        return path.as_posix()


def build_raw_url(path: Path, root: Path, repo: str, ref: str) -> str:
    rel_path = rel_repo_path(path, root).as_posix()
    return raw_base_url(repo, ref) + quote(rel_path, safe="/")


def unique_in_order(items: Iterable[str]) -> list[str]:
    seen = set()
    ordered = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def iter_markdown_files(scan_paths: list[str], root: Path) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    warnings: list[str] = []

    for raw_path in scan_paths:
        candidate = Path(raw_path).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate

        if not candidate.exists():
            warnings.append(f"Scan path does not exist: {raw_path}")
            continue

        if candidate.is_file():
            if candidate.suffix.lower() == ".md":
                files.append(candidate.resolve())
            else:
                warnings.append(f"Skipping non-markdown file: {display_path(candidate, root)}")
            continue

        for file_path in sorted(candidate.rglob("*.md")):
            if file_path.is_file():
                files.append(file_path.resolve())

    unique_files = sorted(set(files), key=lambda p: display_path(p, root))
    return unique_files, warnings


def extract_raw_urls(path: Path) -> tuple[list[str], str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], str(exc)
    urls = RAW_URL_RE.findall(text)
    return unique_in_order(urls), None


def path_from_raw_url(url: str, repo: str, ref: str) -> Path | None:
    base = raw_base_url(repo, ref)
    if not url.startswith(base):
        return None
    rel = unquote(url[len(base) :])
    return Path(rel)


def check_url(url: str, timeout: int, cache: dict[str, UrlCheckResult]) -> UrlCheckResult:
    cached = cache.get(url)
    if cached is not None:
        return cached

    def perform_request(method: str) -> UrlCheckResult:
        headers = {"User-Agent": USER_AGENT}
        if method == "GET":
            headers["Range"] = "bytes=0-0"
        request = Request(url, headers=headers, method=method)
        with urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None) or response.getcode()
            return UrlCheckResult(
                ok=200 <= status < 400,
                status=status,
                final_url=response.geturl(),
            )

    try:
        result = perform_request("HEAD")
        cache[url] = result
        return result
    except HTTPError as exc:
        if exc.code not in {400, 403, 405, 429, 500, 501}:
            result = UrlCheckResult(
                ok=False,
                status=exc.code,
                error=f"HTTP {exc.code}: {exc.reason}",
                final_url=exc.geturl(),
            )
            cache[url] = result
            return result
    except URLError:
        pass
    except Exception as exc:  # pragma: no cover - defensive
        result = UrlCheckResult(ok=False, error=f"{type(exc).__name__}: {exc}")
        cache[url] = result
        return result

    try:
        result = perform_request("GET")
    except HTTPError as exc:
        result = UrlCheckResult(
            ok=False,
            status=exc.code,
            error=f"HTTP {exc.code}: {exc.reason}",
            final_url=exc.geturl(),
        )
    except URLError as exc:
        result = UrlCheckResult(ok=False, error=f"URL error: {exc.reason}")
    except Exception as exc:  # pragma: no cover - defensive
        result = UrlCheckResult(ok=False, error=f"{type(exc).__name__}: {exc}")

    cache[url] = result
    return result


def print_warning(message: str) -> None:
    print(f"WARNING: {message}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that raw GitHub URLs for markdown files under card_linked/ are accessible"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=[DEFAULT_SCAN_ROOT],
        help="Directories or markdown files to scan (default: card_linked)",
    )
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub owner/repo")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Git ref used in raw URLs")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds")
    parser.add_argument(
        "--skip-embedded-urls",
        action="store_true",
        help="Only verify generated raw URLs for local markdown files",
    )
    parser.add_argument("--verbose", action="store_true", help="Print successful checks too")
    args = parser.parse_args()

    root = repo_root()
    markdown_files, scan_warnings = iter_markdown_files(args.paths, root)

    warning_count = 0
    for warning in scan_warnings:
        print_warning(warning)
        warning_count += 1

    if not markdown_files:
        print_warning("No markdown files found to verify")
        return 1

    print(f"Scanning {len(markdown_files)} markdown files under: {', '.join(args.paths)}")
    print(f"Raw base URL: {raw_base_url(args.repo, args.ref)}")

    generated_checks = [
        GeneratedFileCheck(path=file_path, url=build_raw_url(file_path, root, args.repo, args.ref))
        for file_path in markdown_files
    ]

    embedded_checks: list[EmbeddedUrlCheck] = []
    if not args.skip_embedded_urls:
        for file_path in markdown_files:
            urls, error = extract_raw_urls(file_path)
            if error is not None:
                print_warning(
                    f"Could not read markdown file | path={display_path(file_path, root)} | error={error}"
                )
                warning_count += 1
                continue
            for url in urls:
                target_rel = path_from_raw_url(url, args.repo, args.ref)
                target_path = (root / target_rel).resolve() if target_rel is not None else None
                embedded_checks.append(
                    EmbeddedUrlCheck(source_path=file_path, url=url, target_path=target_path)
                )

    cache: dict[str, UrlCheckResult] = {}
    generated_ok = 0
    embedded_ok = 0

    for check in generated_checks:
        result = check_url(check.url, args.timeout, cache)
        rel_path = display_path(check.path, root)
        if result.ok:
            generated_ok += 1
            if args.verbose:
                print(f"OK: {rel_path} -> {check.url}")
            continue

        print_warning(
            f"Raw URL is not accessible | path={rel_path} | url={check.url}"
            + (f" | status={result.status}" if result.status is not None else "")
            + (f" | error={result.error}" if result.error else "")
        )
        warning_count += 1

    for check in embedded_checks:
        result = check_url(check.url, args.timeout, cache)
        source_rel = display_path(check.source_path, root)
        if result.ok:
            embedded_ok += 1
            if args.verbose:
                target_rel = display_path(check.target_path, root) if check.target_path else "(external/unknown target)"
                print(f"OK: embedded URL in {source_rel} -> {target_rel} -> {check.url}")
            continue

        target_rel = display_path(check.target_path, root) if check.target_path else "(external/unknown target)"
        print_warning(
            f"Embedded raw URL is not accessible | listed_in={source_rel} | target={target_rel} | url={check.url}"
            + (f" | status={result.status}" if result.status is not None else "")
            + (f" | error={result.error}" if result.error else "")
        )
        warning_count += 1

    print("")
    print("Summary")
    print(f"- Markdown files checked: {len(generated_checks)}")
    print(f"- Generated raw URLs OK: {generated_ok}/{len(generated_checks)}")
    if args.skip_embedded_urls:
        print("- Embedded raw URL checks: skipped")
    else:
        print(f"- Embedded raw URLs checked: {len(embedded_checks)}")
        print(f"- Embedded raw URLs OK: {embedded_ok}/{len(embedded_checks)}")
    print(f"- Warnings: {warning_count}")

    return 1 if warning_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
