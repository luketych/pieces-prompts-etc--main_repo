---
description: Generate a beautiful standalone HTML diagram and open it in the browser
---
Load the visual-explainer skill, then generate an HTML diagram for: $@

Follow the visual-explainer skill workflow. Read the reference template and CSS patterns before generating. Pick a distinctive aesthetic that fits the content — vary fonts, palette, and layout style from previous diagrams.

If the request is really an interactive review surface — a decision workbook, questionnaire, sign-off page, or anything where the user should answer inside the browser — switch to the interactive workbook pattern instead of a static explanation page. Read `./templates/interactive-workbook.html` and the "Interactive Workbook Pages" section in `./references/css-patterns.md`. Choose the answer model per prompt (`single`, `multi`, `text-only`, or `preset + notes`) rather than forcing everything into A/B/C. Include a bottom summary/export area, local persistence when appropriate, and clipboard fallback for `file://` pages. If you add custom JS, syntax-check it before delivery.

If `surf` CLI is available (`which surf`), consider generating an AI illustration via `surf gemini --generate-image` when an image would genuinely enhance the page — a hero banner, conceptual illustration, or educational diagram that Mermaid can't express. Match the image style to the page's palette. Embed as base64 data URI. See css-patterns.md "Generated Images" for container styles. Skip images when the topic is purely structural or data-driven.

Write to `~/.agent/diagrams/` and open the result in the browser.
