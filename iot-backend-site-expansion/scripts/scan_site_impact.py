#!/usr/bin/env python3
"""Scan a Java/JVM or Rust/Cargo repository for site-specific clues.

The script is read-only with respect to the repository. It writes a JSON report
only when --output is provided. Sensitive assignments, URI userinfo, and
sensitive URI query parameters are redacted.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Pattern

DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    ".kiro",
    ".codegraph",
    ".gradle",
    ".venv",
    "__pycache__",
    "target",
    "build",
    "dist",
    "out",
    "node_modules",
    "coverage",
    "vendor",
}

MAX_FILE_SIZE = 2 * 1024 * 1024
SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)(password|passwd|pwd|secret|token|credential|api[-_]?key|"
    r"access[-_]?key|private[-_]?key)(\s*[:=]\s*)"
    r"([^\s,;#]+|\"[^\"]*\"|'[^']*')"
)
URI_SCHEME = r"(?:jdbc:[a-z][a-z0-9+.-]*|[a-z][a-z0-9+.-]*)"
URI_PATTERN = re.compile(rf"(?i)\b{URI_SCHEME}://[^\s\"'<>]+")
URI_USERINFO = re.compile(rf"(?i)(\b{URI_SCHEME}://)([^/@\s\"'<>]+)@")
SENSITIVE_URI_QUERY = re.compile(
    r"(?i)([?&](?:password|passwd|pwd|secret|token|api[-_]?key|"
    r"access[-_]?key)=)([^&#\s\"'<>]+)"
)
HOST_PORT_PATTERN = re.compile(
    r"(?i)\b(?:[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?|"
    r"(?:\d{1,3}\.){3}\d{1,3}):\d{2,5}\b"
)


@dataclass(frozen=True)
class Match:
    reference: str
    line: int
    excerpt: str
    endpoints: list[str]


@dataclass(frozen=True)
class FileResult:
    path: str
    path_references: list[str]
    matches: list[Match]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find reference-site paths, code/config lines, and endpoint clues."
    )
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument(
        "--reference",
        action="append",
        required=True,
        help="Reference site/application-profile token; repeat for multiple references",
    )
    parser.add_argument(
        "--scope",
        action="append",
        default=[],
        help="Relative module/package/directory to scan; repeat as needed; defaults to root",
    )
    parser.add_argument("--new-site", help="New site token to report separately")
    parser.add_argument("--output", help="JSON report path; stdout when omitted")
    parser.add_argument(
        "--max-matches-per-file", type=int, default=50, help="Per-file match cap"
    )
    parser.add_argument(
        "--max-files", type=int, default=20000, help="Safety cap for scanned files"
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Additional directory name to exclude (for example a custom Cargo target-dir)",
    )
    parser.add_argument(
        "--include-dir",
        action="append",
        default=[],
        help="Directory name to remove from the default exclusion set when it contains source",
    )
    return parser.parse_args()


def token_variants(token: str) -> set[str]:
    pieces = [part for part in re.split(r"[-_\s]+", token.strip()) if part]
    if not pieces:
        return set()
    lower = "".join(part.lower() for part in pieces)
    pascal = "".join(part[:1].upper() + part[1:].lower() for part in pieces)
    return {
        token.strip(),
        token.strip().lower(),
        token.strip().upper(),
        lower,
        pascal,
        "-".join(part.lower() for part in pieces),
        "_".join(part.lower() for part in pieces),
    }


def compile_token_pattern(token: str) -> Pattern[str]:
    alternatives: list[str] = []
    for variant in sorted(token_variants(token), key=len, reverse=True):
        escaped = re.escape(variant)
        if variant.islower():
            alternatives.append(rf"(?<![A-Za-z0-9]){escaped}(?=$|[^a-z0-9]|[A-Z])")
        elif variant.isupper():
            alternatives.append(rf"(?<![A-Za-z0-9]){escaped}(?=$|[^A-Za-z0-9]|[A-Z])")
        else:
            alternatives.append(rf"{escaped}(?=$|[^a-z0-9]|[A-Z])")
    return re.compile("(?:" + "|".join(dict.fromkeys(alternatives)) + ")")


def redact(text: str) -> str:
    redacted = SENSITIVE_ASSIGNMENT.sub(
        lambda match: f"{match.group(1)}{match.group(2)}<redacted>", text
    )
    redacted = URI_USERINFO.sub(
        lambda match: f"{match.group(1)}REDACTED@", redacted
    )
    return SENSITIVE_URI_QUERY.sub(
        lambda match: f"{match.group(1)}REDACTED", redacted
    )


def extract_endpoints(text: str) -> list[str]:
    redacted = redact(text)
    values = URI_PATTERN.findall(redacted) + HOST_PORT_PATTERN.findall(redacted)
    return sorted(dict.fromkeys(value.rstrip(".,);]") for value in values))


def is_probably_text(path: Path) -> bool:
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return False
        with path.open("rb") as handle:
            sample = handle.read(4096)
        return b"\x00" not in sample
    except OSError:
        return False


def iter_files(
    roots: Iterable[Path], excluded_dirs: set[str], max_files: int
) -> Iterable[Path]:
    count = 0
    for root in roots:
        if root.is_file():
            candidates = [root]
        elif root.exists():
            candidates = root.rglob("*")
        else:
            raise FileNotFoundError(f"Scope does not exist: {root}")
        for path in candidates:
            if not path.is_file():
                continue
            if any(part in excluded_dirs for part in path.parts):
                continue
            count += 1
            if count > max_files:
                raise RuntimeError(f"File safety cap exceeded ({max_files})")
            if is_probably_text(path):
                yield path


def relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def resolve_scopes(root: Path, scopes: list[str]) -> list[Path]:
    resolved: list[Path] = []
    for scope in scopes or ["."]:
        candidate = (root / scope).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Scope escapes repository root: {scope}") from exc
        resolved.append(candidate)
    return resolved


def scan_file(
    path: Path,
    root: Path,
    patterns: dict[str, Pattern[str]],
    max_matches: int,
) -> FileResult | None:
    relative_path = relative_or_absolute(path, root)
    path_references = [
        name for name, pattern in patterns.items() if pattern.search(relative_path)
    ]
    matches: list[Match] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line_number, line in enumerate(text.splitlines(), start=1):
        for reference, pattern in patterns.items():
            if pattern.search(line):
                safe_excerpt = redact(line.strip())[:500]
                matches.append(
                    Match(
                        reference=reference,
                        line=line_number,
                        excerpt=safe_excerpt,
                        endpoints=extract_endpoints(safe_excerpt),
                    )
                )
                if len(matches) >= max_matches:
                    break
        if len(matches) >= max_matches:
            break
    if not path_references and not matches:
        return None
    return FileResult(path=relative_path, path_references=path_references, matches=matches)


def build_report(args: argparse.Namespace) -> dict:
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Root does not exist: {root}")

    scope_paths = resolve_scopes(root, args.scope)
    included_dirs = set(getattr(args, "include_dir", []))
    excluded_dirs = (
        DEFAULT_EXCLUDED_DIRS | set(getattr(args, "exclude_dir", []))
    ) - included_dirs
    references = list(
        dict.fromkeys(ref.strip() for ref in args.reference if ref.strip())
    )
    if not references:
        raise ValueError("At least one non-empty reference token is required")
    tokens = references + (
        [args.new_site.strip()] if args.new_site and args.new_site.strip() else []
    )
    patterns = {token: compile_token_pattern(token) for token in tokens}
    files: list[FileResult] = []
    for path in iter_files(scope_paths, excluded_dirs, args.max_files):
        result = scan_file(path, root, patterns, args.max_matches_per_file)
        if result:
            files.append(result)
    files.sort(key=lambda item: item.path)

    endpoint_index: dict[str, list[dict[str, object]]] = {}
    counts = {token: 0 for token in tokens}
    for file_result in files:
        for token in file_result.path_references:
            counts[token] += 1
        for match in file_result.matches:
            counts[match.reference] += 1
            for endpoint in match.endpoints:
                endpoint_index.setdefault(endpoint, []).append(
                    {
                        "path": file_result.path,
                        "line": match.line,
                        "reference": match.reference,
                    }
                )

    return {
        "root": root.as_posix(),
        "scopes": [relative_or_absolute(scope, root) for scope in scope_paths],
        "references": references,
        "newSite": args.new_site,
        "excludedDirectories": sorted(excluded_dirs),
        "explicitlyIncludedDirectories": sorted(included_dirs),
        "counts": counts,
        "matchedFileCount": len(files),
        "files": [asdict(item) for item in files],
        "endpointIndex": endpoint_index,
        "notes": [
            "Counts are token-based discovery clues, not a complete impact inventory.",
            "Inspect Java/Gradle/Maven or Rust/Cargo manifests, config loaders, migrations, CI, and deployment entries separately even when they contain no reference token.",
            "Sensitive assignments, URI userinfo, and sensitive URI query parameters are redacted from excerpts and endpoint clues.",
            "Review external configuration systems separately; this report only scans repository files.",
        ],
    }


def main() -> int:
    args = parse_args()
    try:
        report = build_report(args)
        payload = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            output = Path(args.output).expanduser()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"scan_site_impact: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
