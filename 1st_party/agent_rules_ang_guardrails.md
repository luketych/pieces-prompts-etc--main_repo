Use this as a lightweight architectural and frontend discipline guide for building a codebase that stays easy to navigate as it grows.
## Goals
- Keep files small enough to scan quickly.
- Organize code by responsibility and domain.
- Keep shared logic separated from app-specific code.
- Create a styling system that feels cohesive without becoming tangled.
- Make maintainability an enforced habit, not just a preference.
---
## 1. Organize the Repo by App vs Shared Logic
Structure the project so app entrypoints are separate from shared business logic.
Example:
```text
apps/
  ui/
  server/
  cli/
packages/
  core/
Guideline:
- Put user-facing apps in apps/.
- Put shared logic in packages/.
- Keep shared code reusable and framework-light where possible.
Why this works:
- Prevents UI, server, and CLI concerns from blending together.
- Makes it easier to reuse core logic across multiple surfaces.
- Gives the codebase a clear mental model.
---
2. Separate Shared Code by Domain
Inside shared code, group files by domain or capability rather than by arbitrary technical type.
Example domains:
- providers
- persistence
- runtime
- schemas
- cards
- pieces
- scoring
- workflows
Guideline:
- Keep each domain folder focused on one area of responsibility.
- Avoid dumping unrelated helpers into a generic utils folder too early.
- Export public APIs through a small top-level index/barrel file.
Why this works:
- Encourages clean boundaries.
- Makes files easier to find.
- Reduces cross-cutting sprawl.
---
3. Enforce File Size Limits
Do not rely on “we should keep files small.” Enforce it in tooling.
Recommended rule:
- Fail verification if JS/TS files exceed a max line count, such as 250.
Example policy:
- Include a script like check-max-lines.
- Run it in CI and local verification commands.
- Treat oversized files as a refactor signal.
Why this works:
- Prevents giant components and god-files from creeping in.
- Encourages extracting helpers, child components, and focused modules.
- Keeps code review and debugging faster.
Suggested verification pipeline:
- test
- typecheck
- lint
- check:max-lines
---
4. Keep UI Files Focused
Split UI code into small, intentional layers.
Recommended separation:
- App or route-level composition
- components/ for focused UI pieces
- api.ts for HTTP calls
- types.ts or ui-types.ts for frontend contracts
- data/ or content/config files for static definitions
Pattern:
- Container/composition components coordinate state and data.
- Presentational components render focused sections.
- Shared UI primitives handle repeated behavior.
Why this works:
- Reduces cognitive load inside React/Vue/etc. components.
- Makes testing easier.
- Prevents every component from owning markup, state, fetching, and formatting at once.
---
5. Extract Reusable UI Primitives
When a UI behavior appears more than once, turn it into a dedicated component.
Examples:
- collapsible sections
- modal wrappers
- list panels
- score/review forms
- artifact/image preview blocks
Guideline:
- If the same interaction pattern appears in multiple places, extract it.
- Keep primitives generic enough to reuse, but not abstract for abstraction’s sake.
Why this works:
- Keeps feature files smaller.
- Creates consistency in behavior and styling.
- Makes future UI improvements cheaper.
---
6. Separate Content/Data from Presentation
For dashboards, feature lists, status definitions, stories, examples, or static copy, store structured data separately from rendering components.
Pattern:
- feature-data.ts
- stories.ts
- status-definitions.ts
Why this works:
- Components stay focused on rendering.
- Static content becomes easier to update.
- Reduces noisy inline objects inside UI files.
---
7. Use a Cohesive Global Style System
Even if using a single stylesheet at first, make it systematic.
Recommended styling principles:
- Define a strong base visual direction.
- Use reusable semantic classes instead of one-off styling everywhere.
- Standardize:
  - typography
  - spacing
  - panels/cards
  - buttons
  - badges/pills
  - status colors
  - responsive breakpoints
Good signs:
- Clear app shell/container styles
- Reusable panel/card primitives
- Consistent status color system
- Shared button variants
- Mobile adjustments in media queries
Why this works:
- Gives the app a consistent feel.
- Reduces visual drift.
- Makes new screens faster to build.
---
8. But Don’t Let Styling Become One Giant File
A single stylesheet can work early, but it becomes a maintenance risk if it grows unchecked.
Recommended evolution path:
- Start with one stylesheet if velocity matters.
- Split later into modules such as:
  - tokens.css
  - layout.css
  - components.css
  - forms.css
  - modals.css
  - feature-*.css
Or use scoped CSS/modules if that matches the stack.
Why this matters:
- The same file-size discipline used for TS/JS should eventually apply to CSS.
- Styling should stay discoverable and easy to change.
---
9. Keep Architecture Rules Explicit
Document a few engineering guardrails and repeat them often.
Examples:
- Preserve separation between UI, server, runtime, providers, schemas, and persistence.
- Prefer shared abstractions over provider-specific hacks.
- Preserve raw outputs alongside normalized outputs.
- Respect file-size limits and lint/typecheck rules.
Why this works:
- Helps new contributors make decisions faster.
- Prevents architecture drift.
- Turns “project style” into shared operating rules.
---
10. Make the Good Path the Easy Path
Use scripts and conventions so maintainability happens by default.
Recommended top-level scripts:
{
  "lint": "...",
  "test": "...",
  "typecheck": "...",
  "check:max-lines": "...",
  "verify": "npm run test && npm run typecheck && npm run lint && npm run check:max-lines"
}
Why this works:
- Makes code quality habitual.
- Simplifies onboarding.
- Gives every change a predictable validation path.
---
Practical Checklist
Use this checklist when setting up a similar project:
- [ ] Split app entrypoints from shared packages.
- [ ] Organize shared code by domain.
- [ ] Create a small public export surface for shared code.
- [ ] Add lint, tests, typecheck, and max-lines verification.
- [ ] Enforce a file-size ceiling for JS/TS files.
- [ ] Separate API calls, types, and UI components.
- [ ] Extract reusable UI primitives early.
- [ ] Move static dashboard/content definitions out of render files.
- [ ] Build a deliberate visual system with reusable classes/tokens.
- [ ] Plan to modularize CSS before it becomes a monolith.
- [ ] Document architecture guardrails in a contributor-facing file.
---
What to Imitate Most
If you only copy a few ideas, copy these:
1. Clear repo separation between apps and shared core logic.
2. Domain-based folder structure inside shared code.
3. Hard enforcement of file-size limits.
4. UI split into components, API layer, and shared types.
5. Consistent styling primitives with a defined visual language.
---
Common Failure Modes to Avoid
- Giant App files that own everything.
- A catch-all utils folder that becomes a junk drawer.
- Inline static data inside components.
- Styling added ad hoc with no shared system.
- No enforcement for file size, so files slowly become unmanageable.
- A single oversized stylesheet with no plan to split it.
---
Bottom Line
A maintainable project usually does not come from one clever pattern. It comes from combining:
- small files
- explicit boundaries
- shared primitives
- enforced constraints
- a consistent styling system
The key is to make those practices structural and repeatable, not optional.
