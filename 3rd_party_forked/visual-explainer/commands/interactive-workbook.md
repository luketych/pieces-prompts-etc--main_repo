---
description: Generate an interactive HTML workbook for decisions, questionnaires, sign-off reviews, or any page where the user should answer inside the browser
---
Load the visual-explainer skill, then generate a self-contained interactive HTML workbook for: `$@`

Use this workflow when the page is not just explanatory, but also a response surface where the user should make choices, type notes, review assumptions, and export a structured answer set.

Follow the visual-explainer skill workflow. Before generating, read:
- `./templates/interactive-workbook.html`
- `./references/css-patterns.md` (the **Interactive Workbook Pages** section)
- `./references/responsive-nav.md` if the page will have 4+ sections

## Workbook design rules

1. **Choose the interaction model per prompt.** Not every question should be A/B/C.
   - Use **single-select** when the answer is mutually exclusive.
   - Use **multi-select** when several conditions can be true.
   - Use **text-only** when presets would be fake precision.
   - Use **mixed preset + notes** when canonical options exist but the user may need nuance.

2. **Separate what is already aligned from what is still open.**
   If the source material clearly distinguishes locked assumptions from open decisions, show that distinction explicitly.

3. **If presets exist, let notes coexist.**
   When a user selects a preset and types notes, the export summary should combine both.

4. **Provide reset controls.**
   Include a clear/reset action per question when the page has multiple inputs. Include a global clear action when the page is substantial.

5. **Always include a bottom export surface** when the workbook has multiple prompts.
   The export area should aggregate all answers into plain text or markdown that the user can copy back into chat or a doc.

6. **Persist drafts locally by default** via `localStorage`, unless the user explicitly wants an ephemeral page.

7. **Clipboard must work on local files.**
   For `file://` pages, implement:
   - `navigator.clipboard.writeText(...)` when available
   - `document.execCommand('copy')` fallback
   - manual selection fallback if automatic copy still fails

8. **Use real controls.**
   Interactive choice cards should be `<button type="button">`, not clickable `<div>`s.

## Validation requirements

If the page includes custom JavaScript:
- syntax-check the generated script before delivery (for example, extract it and run `node --check`)
- open the page and verify there are no console errors
- verify selections actually toggle
- verify clear/reset works
- verify the export summary updates live
- verify copy/export works or at least falls back gracefully

Write to `~/.agent/diagrams/` and open the result in the browser. Tell the user the file path.
