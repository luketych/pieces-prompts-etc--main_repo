#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


REVISION_NOTES_HEADING = "## Revision Notes"


def ensure_uv():
    if os.environ.get("UV") or os.environ.get("UV_RUN_RECURSION_DEPTH"):
        return
    raise RuntimeError("Run with uv: uv run python scripts/revise_prompt.py")


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def normalize_feedback(feedback):
    if feedback is None:
        return ""
    return feedback.strip()


def parse_frontmatter(content):
    if not content.startswith("---\n"):
        return None, content
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, content
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            frontmatter = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            return frontmatter, body
    return None, content


def strip_revision_keys(frontmatter):
    if frontmatter is None:
        return None
    lines = frontmatter.splitlines()
    cleaned = []
    skip_block = False
    for line in lines:
        stripped = line.strip()
        if skip_block:
            if stripped and (line.startswith(" ") or line.startswith("\t")):
                continue
            skip_block = False

        if re.match(r"^(revision_of|revision_timestamp|revision_notes):", stripped):
            if stripped.startswith("revision_notes:") and (stripped.endswith("|") or stripped.endswith(">")):
                skip_block = True
            continue

        cleaned.append(line)
    return "\n".join(cleaned).strip("\n")


def build_revision_frontmatter(frontmatter, revision_of, timestamp, feedback):
    base = strip_revision_keys(frontmatter) if frontmatter is not None else ""
    lines = []
    if base:
        lines.append(base)
    lines.append(f"revision_of: {revision_of}")
    lines.append(f"revision_timestamp: {timestamp}")
    lines.append("revision_notes: |")
    for line in feedback.splitlines() or [""]:
        lines.append(f"  {line}")
    return "\n".join(lines).strip("\n")


def inject_revision_notes(body, feedback):
    if REVISION_NOTES_HEADING in body:
        return body
    body = body.rstrip()
    notes_block = f"\n\n{REVISION_NOTES_HEADING}\n\n{feedback}\n"
    return body + notes_block


def resolve_prompt_path(prompt_arg, repo_root):
    prompt_path = prompt_arg.strip()
    if prompt_path.startswith("qmd://"):
        return resolve_qmd_path(prompt_path, repo_root)
    path = Path(prompt_path).expanduser()
    if not path.is_absolute():
        path = resolve_by_normalized_path(repo_root, path.as_posix())
    return path.resolve()


def normalize_name(name):
    return name.replace("_", "-").lower()


def resolve_by_normalized_path(base, rel_path):
    current = base
    for part in [p for p in rel_path.split("/") if p]:
        candidate = current / part
        if candidate.exists():
            current = candidate
            continue

        if not current.exists() or not current.is_dir():
            return candidate

        norm_target = normalize_name(part)
        matches = [entry for entry in current.iterdir() if normalize_name(entry.name) == norm_target]
        if len(matches) == 1:
            current = matches[0]
            continue
        if matches:
            matches.sort(key=lambda p: p.name)
            current = matches[0]
            continue

        current = candidate
    return current


def resolve_qmd_path(qmd_path, repo_root):
    parts = qmd_path.split("/", 3)
    if len(parts) < 4:
        raise RuntimeError(f"Invalid QMD path: {qmd_path}")
    rel_path = parts[3]
    resolved = resolve_by_normalized_path(repo_root, rel_path)
    if resolved.exists():
        return resolved.resolve()
    raise RuntimeError(f"Prompt file not found for QMD path: {qmd_path}")


def find_version_root(prompt_path, repo_root):
    for parent in [prompt_path.parent, *prompt_path.parents]:
        if parent == repo_root.parent:
            break
        if (parent / "metadata.json").exists():
            return parent
        viscera_path = parent / "viscera"
        if viscera_path.exists():
            try:
                prompt_path.relative_to(viscera_path)
            except ValueError:
                pass
            else:
                return parent
    return prompt_path.parent


def snapshot_prompt(prompt_path, version_root, history_dir, timestamp, dry_run):
    rel_path = None
    try:
        rel_path = prompt_path.relative_to(version_root)
    except ValueError:
        rel_path = Path(prompt_path.name)

    snapshot_root = version_root / history_dir / timestamp
    snapshot_path = snapshot_root / rel_path

    if dry_run:
        return snapshot_path

    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(prompt_path, snapshot_path)
    return snapshot_path


def main():
    parser = argparse.ArgumentParser(
        description="Create a revised prompt with versioned history snapshot"
    )
    parser.add_argument("--prompt", required=True, help="Path to the prompt file")
    parser.add_argument("--feedback", help="Feedback text for the revision")
    parser.add_argument("--feedback-file", help="Path to feedback file")
    parser.add_argument("--content", help="Revised prompt content (overwrites)")
    parser.add_argument("--content-file", help="Path to revised prompt content")
    parser.add_argument("--output", help="Optional output path for revised prompt")
    parser.add_argument("--history-dir", default="history", help="History directory name")
    parser.add_argument("--allow-history", action="store_true", help="Allow editing history snapshots")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without writing")
    args = parser.parse_args()

    try:
        ensure_uv()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    repo_root = Path(__file__).resolve().parents[1]
    prompt_path = resolve_prompt_path(args.prompt, repo_root)

    if not prompt_path.exists():
        print(f"Prompt not found: {prompt_path}", file=sys.stderr)
        return 1

    if "/history/" in str(prompt_path) and not args.allow_history:
        print("Refusing to edit history snapshots without --allow-history", file=sys.stderr)
        return 1

    feedback_text = args.feedback
    if args.feedback_file:
        feedback_text = read_text(args.feedback_file)
    feedback_text = normalize_feedback(feedback_text)

    if not feedback_text:
        print("Feedback is required (--feedback or --feedback-file)", file=sys.stderr)
        return 1

    content = None
    if args.content_file:
        content = read_text(args.content_file)
    elif args.content:
        content = args.content

    original_content = read_text(prompt_path)
    frontmatter, body = parse_frontmatter(original_content)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    revision_of = prompt_path.relative_to(repo_root).as_posix()
    updated_frontmatter = build_revision_frontmatter(frontmatter, revision_of, timestamp, feedback_text)

    if content is None:
        updated_body = inject_revision_notes(body, feedback_text)
        new_content = f"---\n{updated_frontmatter}\n---\n\n{updated_body.lstrip()}"
    else:
        new_frontmatter, new_body = parse_frontmatter(content)
        if new_frontmatter is None:
            new_content = f"---\n{updated_frontmatter}\n---\n\n{content.lstrip()}"
        else:
            merged_frontmatter = build_revision_frontmatter(new_frontmatter, revision_of, timestamp, feedback_text)
            new_content = f"---\n{merged_frontmatter}\n---\n\n{new_body.lstrip()}"

    output_path = Path(args.output).expanduser() if args.output else prompt_path
    if not output_path.is_absolute():
        output_path = repo_root / output_path

    version_root = find_version_root(prompt_path, repo_root)
    history_path = snapshot_prompt(prompt_path, version_root, args.history_dir, timestamp, args.dry_run)

    if args.dry_run:
        print(f"Would snapshot: {history_path}")
        print(f"Would write: {output_path}")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(new_content, encoding="utf-8")

    print("Revision complete")
    print(f"Snapshot: {history_path}")
    print(f"Updated:  {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
