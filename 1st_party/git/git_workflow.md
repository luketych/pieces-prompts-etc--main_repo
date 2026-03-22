## gh CLI for interacting with GitHub
- Prefer to use the `gh` CLI to interact with GitHub for creating issues, opening pull requests, reading comments, and related GitHub actions.
## Commit Messages
- The top of a commit message should assume the reader wants to quickly and easily understand what changed, why it was done, and how it was approached. Start with a clear, high-level summary that gives immediate context.
- Write a detailed description of what changed since the previous commit. If multiple areas were modified or distinct conceptual changes were made, separate these into clear sub-sections.
- If a particular component or feature is partially complete or known issues remain, note that clearly toward the end of the message so the reader knows what to expect.
- If the work being committed aligns with broader goals, concepts, or ongoing areas of development, briefly describe that connection. Include references or links to where further information can be found if applicable.
- If the changes are exploratory, refactor-only, or not part of any ongoing development theme, note that near the top of the message for transparency.
- In all cases, the commit message should begin with a concise summary of what was completed or changed since the last commit. Subsequent sections can elaborate on rationale, implementation, and remaining considerations.
- If the project is using milestone/task tracking in a system like `backlog.md` or a similar or custom  task system, prefix the commit subject with the short task identifier format `T<task>` such as `T10.1 Improve card render composition`.
- When using the `T<task>` prefix, remove redundant task references from the rest of the subject line. For example, prefer `T10.1 Improve card render composition and task context` over `Improve card render composition and task context for TASK-10.1`.
- Use the task prefix only when the commit clearly maps to a tracked task in that external task system. Do not add it to commits in repos or workflows that are not using milestone/task tracking.