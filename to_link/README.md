# to_link

This directory is a local workspace for linking external prompt sources into
the repo during exploration or manual testing.

## Usage
- Add symlinks that point to local prompt directories you want to inspect.
- Keep links local only; do not commit symlinks to user-specific paths.
- Prefer stable, portable sources when you want content tracked in git.

## Examples
- ln -s /absolute/path/to/prompts ./to_link/source_name

## Notes
- This directory is intentionally empty in version control except for this README.
