# Prompts & Agents Collection

A searchable repository of prompts, agents, and configurations from various external sources.

Uses `uv` for running maintenance and test scripts. Script entry points will exit
with a helpful message if run without `uv`.

## Structure

Each source is stored in its own directory with:
- Original files preserved with enhanced YAML frontmatter
- `metadata.json` containing source information, dates, and inventory
- Third-party source collections live under `3rd_party/` (see `3rd_party/README.md`)

## Metadata Schema

Each prompt/agent file includes comprehensive YAML frontmatter with auto-generated metadata derived from content analysis:

### Core Properties
- **`source`** - Origin of the prompt (e.g., humanlayer, anthropic)
  - *How it's derived:* Manually set based on the source repository
  
- **`type`** - Classification: agent | command | prompt
  - *How it's derived:* Detected from file location (agents/ vs commands/ directory)
  
- **`author`** - Creator or contributor
  - *How it's derived:* Extracted from git commit author or set to source team name
  
- **`created_date`** - Initial creation date (YYYY-MM-DD)
  - *How it's derived:* From git log or download date
  
- **`updated_date`** - Last modification date (YYYY-MM-DD)
  - *How it's derived:* From git log last commit date

### Workflow & Classification
- **`workflow_stage`** - Primary phase: plan | research | execute | review | debug | finalize | unknown
  - *How it's derived:* Detected from filename and content keywords
    - 'plan' in filename/content → `plan`
    - 'research'/'analyze'/'locator' → `research`
    - 'implement'/'execute' → `execute`
    - 'review'/'validate' → `review`
    - 'commit'/'pr' → `finalize`
    - 'debug' → `debug`
  
- **`labels`** - High-level categories: [planning, research, execution, review, debug, git]
  - *How it's derived:* Based on workflow_stage and content analysis
  
- **`tags`** - Specific functionality keywords
  - *How it's derived:* Keyword detection in content:
    - 'analyze'/'analyzer' → `analysis`
    - 'locator'/'find' → `search`
    - 'pattern' → `patterns`
    - 'commit' → `commit`
    - 'pr' → `pull-request`
    - 'test' → `testing`
    - 'database'/'migration' → `database`
    - 'worktree' → `worktree`
    - 'handoff' → `handoff`
    - 'web search' → `web-search`
    - 'founder mode'/'ralph' → `automation`, `full-cycle`
  
- **`scope`** - Operating context: [codebase, git, external, project-management, documentation]
  - *How it's derived:* Content keyword detection:
    - 'codebase'/'code' in content → `codebase`
    - 'git'/'commit'/'pr' → `git`
    - 'web'/'search' → `external`
    - 'linear'/'ticket' → `project-management`
    - 'thoughts' → `documentation`

### Capabilities
- **`requires_human`** - Needs human input/confirmation (true/false)
  - *How it's derived:* Content search for: 'ask', 'user', 'approval', 'confirm', 'manual verification'
  
- **`autonomous`** - Can run fully autonomously (true/false)
  - *How it's derived:* `!requires_human` AND (type=agent OR 'autonomous'/'automated' in content)
  
- **`complexity`** - simple | medium | complex
  - *How it's derived:* Content length and structure:
    - Has 'phase' OR >5000 chars → `complex`
    - >2000 chars OR has 'sub-task' → `medium`
    - Otherwise → `simple`

### Technical Details
- **`model`** - LLM model used (sonnet, opus, etc.)
  - *How it's derived:* Extracted from original YAML frontmatter if present
  
- **`tools`** - Available tools/functions
  - *How it's derived:* Extracted from original YAML frontmatter if present
  
- **`dependencies`** - Other .md files (commands/agents) that this file references or calls
  - *How it's derived:* Pattern matching for references to other files in the same directory:
    - Slash commands: `/ralph_research`, `/commit`, etc.
    - File path references: `.claude/commands/linear.md`
    - Direct mentions: `implement_plan.md`
  - *Only includes files that actually exist in the collection*
  - *Self-references are excluded*
  
- **`output_format`** - Expected output type (markdown, json, code, etc.)
  - *How it's derived:* Content analysis:
    - Default → `markdown`
    - Contains 'json' → `markdown+json`
    - Has code blocks with language → `markdown+code`

### Discoverability
- **`use_cases`** - Specific scenarios where it's useful
  - *How it's derived:* Based on workflow_stage and content keywords:
    - plan stage → `feature-planning`
    - research stage → `codebase-exploration`
    - debug → `troubleshooting`
    - commit/pr → `version-control`
    - test content → `testing`
    - refactor content → `refactoring`
    - database/migration → `database-changes`
    - handoff → `collaboration`
    - worktree → `parallel-development`
  
- **`related`** - Links to similar prompts/agents (filename references)
  - *How it's derived:* Logical relationships:
    - locator ↔ analyzer
    - create_plan ↔ implement_plan ↔ validate_plan
    - commit ↔ describe_pr
    - ralph_plan ↔ ralph_research ↔ ralph_impl

## Metadata Quality Note

All metadata is **auto-generated** from content analysis. While generally accurate, some fields may need manual curation for precision. The derivation logic is transparent (see above) so you can understand how each property was determined.

## Third-Party Sources

Source inventory, update workflow, and per-source stats live in `3rd_party/README.md`.

## Maintenance and Tests

- Update third-party sources: `uv run python scripts/update_3rd_party.py`
- Cleanup duplicate history snapshots: `uv run python scripts/cleanup_3rd_party_history.py`
- E2E fixture and local-repo walkthrough: `tests/e2e/README.md`
