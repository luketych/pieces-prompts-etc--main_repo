#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_MANIFEST = "3rd_party/manifest.json"
DEFAULT_PRESERVE = {"metadata.json"}
DEFAULT_IGNORE = {".DS_Store"}
DEFAULT_PROMPT_EXTENSIONS = {".md"}


def ensure_uv():
    if os.environ.get("UV") or os.environ.get("UV_RUN_RECURSION_DEPTH"):
        return
    raise RuntimeError("Run with uv: uv run python scripts/update_3rd_party.py")


def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{stderr}")
    return result.stdout.strip()


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


def hash_tree(root, exclude):
    if not root.exists():
        return None
    digest = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if filename in DEFAULT_IGNORE:
                continue
            file_path = Path(dirpath) / filename
            rel_path = file_path.relative_to(root).as_posix()
            if rel_path in exclude:
                continue
            digest.update(rel_path.encode("utf-8"))
            digest.update(b"\0")
            with file_path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(8192), b""):
                    digest.update(chunk)
    return digest.hexdigest()


def remove_except(path, preserve):
    if not path.exists():
        return
    for entry in path.iterdir():
        if entry.name in preserve:
            continue
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def copy_tree(src, dest, preserve):
    for dirpath, dirnames, filenames in os.walk(src):
        rel_dir = Path(dirpath).relative_to(src)
        target_dir = dest / rel_dir if rel_dir != Path(".") else dest
        target_dir.mkdir(parents=True, exist_ok=True)
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if filename in DEFAULT_IGNORE:
                continue
            rel_file = (rel_dir / filename).as_posix()
            if rel_file in preserve:
                continue
            shutil.copy2(Path(dirpath) / filename, target_dir / filename)


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


def preserved_dirs(preserve):
    dirs = set()
    for item in preserve:
        parts = Path(item).parts
        if parts:
            dirs.add(parts[0])
    return dirs


def collect_prompt_files(root, extensions, exclude_dirs, prompt_root=None):
    base = root / prompt_root if prompt_root else root
    if not base.exists():
        return []
    prompt_files = []
    for dirpath, dirnames, filenames in os.walk(base):
        if not prompt_root:
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if filename in DEFAULT_IGNORE:
                continue
            if Path(filename).suffix.lower() in extensions:
                prompt_files.append(Path(dirpath) / filename)
    return prompt_files


def gather_prompt_files(root, extensions, exclude_dirs, prompts_dir):
    prompt_files = collect_prompt_files(root, extensions, exclude_dirs, prompts_dir)
    if not prompt_files and prompts_dir:
        prompt_files = collect_prompt_files(root, extensions, exclude_dirs)
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


def latest_snapshot_root(root, history_dir):
    history_path = root / history_dir
    if not history_path.exists():
        return None
    snapshots = [
        entry for entry in history_path.iterdir() if entry.is_dir()
    ]
    if not snapshots:
        return None
    snapshots.sort(key=lambda path: path.name)
    return snapshots[-1]


def snapshot_prompts(root, history_dir, prompt_files, dry_run):
    if not prompt_files:
        return None
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    snapshot_root = root / history_dir / timestamp
    if dry_run:
        return {
            "snapshot": snapshot_root.as_posix(),
            "count": len(prompt_files),
        }
    snapshot_root.mkdir(parents=True, exist_ok=True)
    for prompt_file in prompt_files:
        rel_path = prompt_file.relative_to(root)
        target_path = snapshot_root / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(prompt_file, target_path)
    return {
        "snapshot": snapshot_root.as_posix(),
        "count": len(prompt_files),
    }


def move_prompts_to_dir(root, prompts_dir, extensions, exclude_dirs):
    if not prompts_dir:
        return 0
    prompts_path = root / prompts_dir
    prompts_path.mkdir(parents=True, exist_ok=True)
    moved = 0
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        if rel_dir.parts and rel_dir.parts[0] in exclude_dirs:
            dirnames[:] = []
            continue
        if rel_dir.parts and rel_dir.parts[0] == prompts_dir:
            dirnames[:] = []
            continue
        dirnames[:] = [
            d for d in dirnames if d not in exclude_dirs and d != prompts_dir
        ]
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if filename in DEFAULT_IGNORE:
                continue
            if Path(filename).suffix.lower() not in extensions:
                continue
            source_path = Path(dirpath) / filename
            rel_path = source_path.relative_to(root)
            target_path = root / prompts_dir / rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), target_path)
            moved += 1
    return moved


def prune_empty_dirs(root, exclude_dirs):
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        rel_dir = Path(dirpath).relative_to(root)
        if rel_dir == Path("."):
            continue
        if rel_dir.parts and rel_dir.parts[0] in exclude_dirs:
            continue
        if not dirnames and not filenames:
            Path(dirpath).rmdir()


def update_metadata(metadata_path, git_dir, entry, dry_run):
    if not metadata_path.exists():
        return None
    try:
        with metadata_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None

    commit = run(["git", "-C", str(git_dir), "rev-parse", "HEAD"])
    author = run(["git", "-C", str(git_dir), "log", "-1", "--format=%an"])
    commit_date = run(["git", "-C", str(git_dir), "log", "-1", "--format=%cI"])

    source = data.get("source")
    if isinstance(source, dict):
        source["commit"] = commit
        source["last_updated"] = commit_date
        source["author"] = author

    if "downloaded" in data:
        data["downloaded"] = datetime.now(timezone.utc).date().isoformat()

    if dry_run:
        return {"commit": commit, "author": author, "last_updated": commit_date}

    with metadata_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=True)
        handle.write("\n")

    return {"commit": commit, "author": author, "last_updated": commit_date}


def update_git(entry, repo_root, preserve, dry_run, defaults):
    source = entry.get("source", {})
    repo_url = source.get("repo")
    if not repo_url:
        raise ValueError("git entry requires source.repo")

    ref = source.get("ref")
    subdir = source.get("subdir")
    dest = resolve_path(repo_root, entry["path"])
    preserve = set(preserve)
    metadata_file = entry.get("metadata_file", "metadata.json")
    preserve.add(metadata_file)

    history_enabled = bool(get_entry_setting(entry, defaults, "history", True))
    history_dir = get_entry_setting(entry, defaults, "history_dir", "history")
    prompts_dir = get_entry_setting(entry, defaults, "prompts_dir")
    prompt_extensions = normalize_extensions(
        get_entry_setting(entry, defaults, "prompt_extensions", [".md"])
    )
    if history_enabled and history_dir:
        preserve.add(history_dir)
    exclude_dirs = preserved_dirs(preserve)

    before_hash = hash_tree(dest, preserve)
    metadata_info = None

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        clone_cmd = ["git", "clone", "--depth", "1"]
        if ref:
            clone_cmd += ["--branch", ref]
        clone_cmd += [repo_url, str(tmpdir_path)]
        try:
            run(clone_cmd)
        except RuntimeError:
            run(["git", "clone", "--depth", "1", repo_url, str(tmpdir_path)])
            if ref:
                run(["git", "-C", str(tmpdir_path), "checkout", ref])

        src = tmpdir_path / subdir if subdir else tmpdir_path
        if not src.exists():
            raise FileNotFoundError(f"Source subdir not found: {src}")

        if history_enabled and history_dir and dest.exists():
            prompt_files = gather_prompt_files(
                dest, prompt_extensions, exclude_dirs, prompts_dir
            )
            if prompt_files:
                current_digest = prompt_digest(prompt_files, dest)
                latest_snapshot = latest_snapshot_root(dest, history_dir)
                snapshot_needed = True
                if latest_snapshot:
                    snapshot_files = gather_prompt_files(
                        latest_snapshot, prompt_extensions, set(), prompts_dir
                    )
                    snapshot_digest = prompt_digest(snapshot_files, latest_snapshot)
                    if snapshot_digest and snapshot_digest == current_digest:
                        snapshot_needed = False
                if snapshot_needed:
                    snapshot_prompts(dest, history_dir, prompt_files, dry_run)

        if not dry_run:
            dest.mkdir(parents=True, exist_ok=True)
            remove_except(dest, preserve)
            copy_tree(src, dest, preserve)
            move_prompts_to_dir(dest, prompts_dir, prompt_extensions, exclude_dirs)
            prune_excludes = set(exclude_dirs)
            if prompts_dir:
                prune_excludes.add(prompts_dir)
            prune_empty_dirs(dest, prune_excludes)

        metadata_path = dest / metadata_file
        metadata_info = update_metadata(metadata_path, tmpdir_path, entry, dry_run)

    after_hash = hash_tree(dest, preserve) if not dry_run else None
    changed = before_hash is None or after_hash is None or before_hash != after_hash

    return {
        "changed": changed,
        "commit": metadata_info.get("commit") if metadata_info else None,
        "author": metadata_info.get("author") if metadata_info else None,
        "last_updated": metadata_info.get("last_updated") if metadata_info else None,
    }


def update_url(entry, repo_root, preserve, dry_run, defaults):
    source = entry.get("source", {})
    url = source.get("url")
    if not url:
        raise ValueError("url entry requires source.url")

    dest_path = resolve_path(repo_root, entry["path"])
    filename = source.get("filename")
    if filename:
        dest_file = dest_path / filename
    elif dest_path.exists():
        if dest_path.is_dir():
            dest_file = dest_path / (Path(url).name or "downloaded")
        else:
            dest_file = dest_path
    elif dest_path.suffix:
        dest_file = dest_path
    else:
        dest_file = dest_path / (Path(url).name or "downloaded")

    if dry_run:
        return {"changed": True, "bytes": None}

    dest_file.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        content = response.read()
    with dest_file.open("wb") as handle:
        handle.write(content)

    return {"changed": True, "bytes": len(content)}


def update_manual(entry, repo_root, preserve, dry_run, defaults):
    _ = (entry, repo_root, preserve, dry_run, defaults)
    return {"changed": False, "note": "manual source"}


def main():
    parser = argparse.ArgumentParser(description="Update third-party sources")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--only", action="append", default=[], help="Update only these entry ids")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change")
    parser.add_argument("--report", help="Write a JSON report to this path")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = resolve_path(repo_root, args.manifest)
    manifest = load_manifest(manifest_path)

    entries = manifest.get("entries", [])
    defaults = manifest.get("defaults", {})
    base_preserve = set(defaults.get("preserve", [])) | DEFAULT_PRESERVE

    only_ids = set()
    for item in args.only:
        for part in item.split(","):
            part = part.strip()
            if part:
                only_ids.add(part)

    report = {
        "manifest": str(manifest_path),
        "dry_run": args.dry_run,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "results": [],
    }

    for entry in entries:
        entry_id = entry.get("id")
        if not entry_id:
            continue
        if only_ids and entry_id not in only_ids:
            continue

        result = {
            "id": entry_id,
            "path": entry.get("path"),
            "type": entry.get("type"),
            "status": "ok",
        }
        entry_preserve = set(entry.get("preserve", [])) | base_preserve
        try:
            entry_type = entry.get("type")
            if entry_type == "git":
                info = update_git(entry, repo_root, entry_preserve, args.dry_run, defaults)
            elif entry_type == "url":
                info = update_url(entry, repo_root, entry_preserve, args.dry_run, defaults)
            elif entry_type == "manual":
                info = update_manual(entry, repo_root, entry_preserve, args.dry_run, defaults)
            else:
                raise ValueError(f"Unknown entry type: {entry_type}")
            result.update(info)
        except Exception as exc:
            result["status"] = "error"
            result["error"] = str(exc)

        report["results"].append(result)

    report["finished_at"] = datetime.now(timezone.utc).isoformat()

    if args.report:
        report_path = resolve_path(repo_root, args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=True)
            handle.write("\n")

    summary = {
        "ok": len([r for r in report["results"] if r["status"] == "ok"]),
        "error": len([r for r in report["results"] if r["status"] == "error"]),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        ensure_uv()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
    sys.exit(main())
