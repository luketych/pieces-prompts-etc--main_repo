# AGENTS.md

This folder contains a small prompt kit for prompt analysis and prompt improvement work.

## Folder structure

- `./DESCRIPTION.md`
  - short human-readable description of the pack
- `./TOC.md`
  - raw file URL index for the pack
- `./prompts/`
  - the actual prompt files to use with an LLM agent

## Prompt files

Inside `./prompts/`:

- `prompt_analyzer.md`
  - use when you want an agent to inspect, score, and critique a prompt without rewriting it
- `prompt_analyzer_v2_self_improving.md`
  - use when you want an agent to inspect, score, and rewrite a prompt into a stronger version

## How to access the prompts

If you are an agent working inside this repo, read files directly from:

- `prompt-analysis-pack/prompts/`

Examples:

- `prompt-analysis-pack/prompts/prompt_analyzer.md`
- `prompt-analysis-pack/prompts/prompt_analyzer_v2_self_improving.md`

## Recommended usage order

1. Read `./DESCRIPTION.md` for the high-level purpose.
2. Start with `prompt_analyzer.md` when you want a baseline evaluation.
3. Use `prompt_analyzer_v2_self_improving.md` when you want the prompt repaired or upgraded.
4. If you generate an improved prompt, run it back through `prompt_analyzer.md` to compare before/after quality.
5. Pass the task-specific prompt text into the `{{PROMPT}}` placeholder.

## Quick routing guide

Use:

- **prompt analyzer** when the task is: "What is weak, missing, or unclear in this prompt?"
- **self-improving prompt analyzer** when the task is: "Fix this prompt and give me a better version."

## Important note

These prompts are structure-heavy and JSON-oriented on purpose.
They are most useful when you want:

- machine-readable prompt evaluation
- repeatable prompt QA
- clearer input/output contracts
- lower drift through explicit scoring criteria
- a simple analyze → rewrite → re-analyze workflow
