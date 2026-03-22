# AGENTS.md

This folder contains a small prompt kit for JavaScript bloat work.

## Folder structure

- `./DESCRIPTION.md`
  - short human-readable description of the pack
- `./prompts/`
  - the actual prompt files to use with an LLM agent
- `./The Three Pillars of JavaScript Bloat.pdf`
  - primary source article material
- `./chatgpt_transcript-JavaScript Bloat Breakdown.pdf`
  - simplified supporting summary / synthesis

## Prompt files

Inside `./prompts/`:

- `bloat_audit_v4.md`
  - use when you want an agent to inspect code and classify kinds of JavaScript bloat
- `builder_minimal_v4.md`
  - use when you want an agent to generate smaller, more modern JavaScript
- `js_bloat_tooling_advisor_v3.md`
  - use when you want an agent to recommend tools for reducing bloat
- `js_bloat_tools.md`
  - use as supporting reference for the tool landscape

## How to access the prompts

If you are an agent working inside this repo, read files directly from:

- `cards/js-bloat-agent-prompt-pack/resources/prompts/`

Examples:

- `cards/js-bloat-agent-prompt-pack/resources/prompts/bloat_audit_v4.md`
- `cards/js-bloat-agent-prompt-pack/resources/prompts/builder_minimal_v4.md`
- `cards/js-bloat-agent-prompt-pack/resources/prompts/js_bloat_tooling_advisor_v3.md`

## Recommended usage order

1. Read `./DESCRIPTION.md` for the high-level purpose.
2. Choose the prompt that matches the task.
3. Read the relevant source PDFs if you need deeper context or citation grounding.
4. Use the selected prompt as the main instruction block for the agent.
5. Pass the task-specific code, repo context, or question into the prompt's input placeholder.

## Quick routing guide

Use:

- **audit prompt** when the task is: "What kind of bloat is in this code?"
- **builder prompt** when the task is: "Write or rewrite this in a minimal modern way."
- **tooling advisor prompt** when the task is: "Which tools should I use for this repo or situation?"

## Important note

These prompts are source-grounded and constraint-heavy on purpose.
They are most useful when you want:

- less generic LLM output
- more explicit reasoning
- modern-JS defaults
- decisions tied back to cited source material
