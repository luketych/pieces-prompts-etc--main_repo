#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_MANIFEST = "3rd_party/manifest.json"
DEFAULT_IGNORE = {".DS_Store"}
DEFAULT_PROMPT_EXTENSIONS = {".md"}


def ensure_uv():
    if os.environ.get("UV") or os.environ.get("UV_RUN_RECURSION_DEPTH"):
        return
    raise RuntimeError(
        "Run with uv: uv run python scripts/cleanup_3rd_party_history.py"
    )


def load_manifest(path):
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or "entries" not in data:
        raise ValueError("Manifest must be a JSON object with an 'entries' list")
    return data


def resolve_path(repo_root, path_value):
    path = Path(path_value)
    if not path.is_absolute():
        path = repo_root / path
    return path


def normalize_extensions(extensions):
    if not extensions:
        return set(DEFAULT_PROMPT_EXTENSIONS)
    normalized = set()
    for item in extensions:
        if not item:
            continue
        ext = str(item).lower()
        if not ext.startswith("."):
            ext = f".{ext}"
        normalized.add(ext)
    return normalized or set(DEFAULT_PROMPT_EXTENSIONS)


def get_entry_setting(entry, defaults, key, fallback=None):
    if key in entry:
        return entry.get(key)
    return defaults.get(key, fallback)


def collect_prompt_files(root, extensions, prompt_root=None):
    base = root / prompt_root if prompt_root else root
    if not base.exists():
        return []
    prompt_files = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if filename in DEFAULT_IGNORE:
                continue
            if Path(filename).suffix.lower() in extensions:
                prompt_files.append(Path(dirpath) / filename)
    return prompt_files


def gather_prompt_files(root, extensions, prompts_dir):
    prompt_files = collect_prompt_files(root, extensions, prompts_dir)
    if not prompt_files and prompts_dir:
        prompt_files = collect_prompt_files(root, extensions)
    return prompt_files


def prompt_digest(prompt_files, root):
    if not prompt_files:
        return None
    digest = hashlib.sha256()
    sorted_files = sorted(
        prompt_files, key=lambda path: path.relative_to(root).as_posix()
    )
    for prompt_file in sorted_files:
        rel_path = prompt_file.relative_to(root).as_posix()
        digest.update(rel_path.encode("utf-8"))
        digest.update(b"\0")
        with prompt_file.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
    return digest.hexdigest()


def list_snapshots(history_root):
    if not history_root.exists():
        return []
    snapshots = [entry for entry in history_root.iterdir() if entry.is_dir()]
    snapshots.sort(key=lambda path: path.name)
    return snapshots


def cleanup_entry(entry, repo_root, defaults, dry_run, keep_mode):
    if not entry.get("id"):
        return None
    if not bool(get_entry_setting(entry, defaults, "history", True)):
        return {
            "id": entry.get("id"),
            "status": "skipped",
            "reason": "history disabled",
        }

    dest = resolve_path(repo_root, entry["path"])
    history_dir = get_entry_setting(entry, defaults, "history_dir", "history")
    prompts_dir = get_entry_setting(entry, defaults, "prompts_dir")
    prompt_extensions = normalize_extensions(
        get_entry_setting(entry, defaults, "prompt_extensions", [".md"])
    )

    history_root = dest / history_dir
    snapshots = list_snapshots(history_root)
    if not snapshots:
        return {
            "id": entry.get("id"),
            "status": "skipped",
            "reason": "no snapshots",
        }

    if keep_mode == "latest":
        ordered = list(reversed(snapshots))
    else:
        ordered = snapshots

    seen = {}
    duplicates = []
    empty = 0

    for snapshot in ordered:
        prompt_files = gather_prompt_files(snapshot, prompt_extensions, prompts_dir)
        if not prompt_files:
            empty += 1
            continue
        digest = prompt_digest(prompt_files, snapshot)
        if not digest:
            empty += 1
            continue
        if digest in seen:
            duplicates.append(snapshot)
        else:
            seen[digest] = snapshot

    if not dry_run:
        for snapshot in duplicates:
            shutil.rmtree(snapshot)

    return {
        "id": entry.get("id"),
        "status": "ok",
        "snapshots": len(snapshots),
        "duplicates": len(duplicates),
        "removed": 0 if dry_run else len(duplicates),
        "kept": len(seen),
        "empty": empty,
    }


def main():
    parser = argparse.ArgumentParser(description="Cleanup duplicate history snapshots")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--only", action="append", default=[], help="Update only these entry ids")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change")
    parser.add_argument("--report", help="Write a JSON report to this path")
    parser.add_argument(
        "--keep",
        choices=["oldest", "latest"],
        default="oldest",
        help="Which snapshot to keep when duplicates exist",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = resolve_path(repo_root, args.manifest)
    manifest = load_manifest(manifest_path)

    entries = manifest.get("entries", [])
    defaults = manifest.get("defaults", {})

    only_ids = set()
    for item in args.only:
        for part in item.split(","):
            part = part.strip()
            if part:
                only_ids.add(part)

    report = {
        "manifest": str(manifest_path),
        "dry_run": args.dry_run,
        "keep": args.keep,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "results": [],
    }

    for entry in entries:
        entry_id = entry.get("id")
        if not entry_id:
            continue
        if only_ids and entry_id not in only_ids:
            continue
        result = cleanup_entry(entry, repo_root, defaults, args.dry_run, args.keep)
        if result:
            report["results"].append(result)

    report["finished_at"] = datetime.now(timezone.utc).isoformat()

    if args.report:
        report_path = resolve_path(repo_root, args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=True)
            handle.write("\n")

    summary = {
        "ok": len([r for r in report["results"] if r.get("status") == "ok"]),
        "skipped": len([r for r in report["results"] if r.get("status") == "skipped"]),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        ensure_uv()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
    sys.exit(main())
