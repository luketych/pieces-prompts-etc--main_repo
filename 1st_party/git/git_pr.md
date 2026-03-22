## gh CLI for interacting with GitHub

- Prefer to use the `gh` CLI to interact with GitHub for creating pull requests, reading issue/PR context, checking linked discussions, viewing comments, updating PR metadata, and linking related issues, commits, or prior pull requests.

## Pull Request Bodies

- The top of a PR body should assume the reader wants to quickly understand **what this PR does, why it exists, how risky it is, how complete it is, and whether it changes any safety or capability boundaries**. Start with a clear high-level summary that gives immediate context with minimal mental effort.
- Early in the PR body, make it obvious whether the PR is:
  - a feature,
  - a bug fix,
  - a refactor,
  - exploratory/prototyping work,
  - infrastructure/tooling work,
  - policy/guardrail work,
  - or a sync/merge/publish PR.
- Every PR body should clearly state the **intent** of the change. That includes what the PR is trying to accomplish, what problem it is meant to solve, what broader direction or goal it supports, and what this PR is intentionally **not** trying to do.
- If the PR is only partially complete, staged, or intentionally scoped down, say that explicitly near the top rather than burying it.

## Recommended Top-Down Structure

- After the summary, structure the PR body so the reader can progressively drill down into more detail. A good default flow is:
  1. **What / purpose**
  2. **Intent / motivation**
  3. **Risk level / sensitive surfaces**
  4. **Key choices and tradeoffs**
  5. **How / implementation approach**
  6. **Inputs and outputs**
  7. **Complexity introduced**
  8. **Side effects / failure modes / blast radius**
  9. **Testing / validation**
  10. **Rollback / recovery / containment**
  11. **Follow-ups / out of scope**

## Intent, Scope, and Reviewer Context

- The PR body should be optimized for scanability. Prefer strong section headers, grouped bullets where helpful, and a top-down structure that lets someone understand the PR even if they only read the first few sections.
- If the PR touches multiple distinct areas, organize the body into clear sub-sections by concern, subsystem, or user-visible impact rather than mixing everything into one long explanation.
- Clearly distinguish between:
  - user-visible behavior changes,
  - internal implementation changes,
  - refactors with no intended behavior change,
  - foundational work that mainly enables future changes,
  - and policy or capability changes that alter what the system is allowed to do.
- If the PR is part of a broader initiative, migration, architecture shift, or long-running theme, briefly explain that connection and link related issues, PRs, docs, or design notes where useful.
- If relevant, include reviewer guidance that helps the reader spend attention efficiently. For example:
  - where to start reading,
  - which files or commits matter most,
  - which parts are mechanical,
  - which parts are risky,
  - and which parts deserve deeper scrutiny.

## Choices, Tradeoffs, and Attribution

- Explicitly describe the important **choices that were made** during implementation. Do not just describe what was done; also explain why these choices were preferred over other plausible options when that context would help reviewers understand the design.
- Include important **tradeoffs** directly in the PR body. If something was optimized for simplicity, speed, compatibility, maintainability, incremental delivery, reduced risk, or faster rollback at the expense of some other quality, say so explicitly.
- Include attribution to the most relevant **commit hashes** when useful, especially when:
  - a PR is composed of several meaningful conceptual steps,
  - specific commits are good entry points for review,
  - certain commits introduced, reverted, or reshaped important behavior,
  - or a reviewer should inspect one commit more carefully than the rest.
- If prior commits, issues, incidents, regressions, or design discussions shaped this PR, mention them when that improves understanding.

## Inputs, Outputs, and Contracts

- The PR body should help the reviewer understand **inputs and outputs** where relevant. For example, describe:
  - what data, events, commands, state, configuration, or user actions flow into the changed code,
  - what outputs, side effects, persisted state, API responses, UI changes, logs, external calls, or downstream behaviors result,
  - and what invariants, contracts, assumptions, or constraints were added, changed, preserved, or relied on.
- If the PR changes interfaces, contracts, or assumptions between components, say so explicitly, even if the visible diff looks small.

## Complexity Introduced

- Call out any **complexity introduced** by the PR, especially complexity that may compound over time. This includes:
  - new abstractions or indirection layers,
  - branching behavior or expanded configuration surface area,
  - temporary compatibility paths,
  - coupled systems or duplicated logic,
  - state that must now be synchronized,
  - and any foundation that future work will need to build on.
- Pay special attention to **cascading complexity**. If the PR introduces complexity that other already-complex pieces will sit on top of, or complexity that could multiply when combined with future changes, make that explicit so reviewers can evaluate long-term cost, not just immediate correctness.
- If the PR introduces a new center of gravity that future code will depend on, say so directly.

## Risk, Sensitive Surfaces, and Capability Boundaries

- If the PR touches safety-sensitive or high-blast-radius areas, explicitly call that out near the top. Sensitive areas include, but are not limited to:
  - permissions or approval flows,
  - tool wrappers or execution harnesses,
  - sandbox or container boundaries,
  - filesystem scope,
  - network access,
  - secrets, credentials, or token exposure paths,
  - CI/workflow files,
  - deployment or environment configuration,
  - migrations,
  - lockfiles or dependency install behavior,
  - branch protections, push/promotion rules, or release paths.
- State whether the PR changes **capability boundaries**, **trust boundaries**, **approval scope**, or **execution authority**. Make clear what is now allowed, denied, gated, restricted, or newly reachable that was not before.
- If the PR weakens, bypasses, or relocates a safety check, guardrail, validator, wrapper, or review boundary, that must be called out explicitly and justified.
- If the PR does not change authority or safety boundaries, that can also be stated explicitly when useful.

## Side Effects, Failure Modes, and Blast Radius

- Clearly describe **side effects** and **potential side effects** introduced by the PR. This includes intended side effects, plausible unintended consequences, behavioral edge cases, performance implications, migration impact, operational risk, and changes that may affect adjacent systems indirectly.
- Describe likely **failure modes** or misuse cases where relevant. Explain what could go wrong if assumptions fail, which safeguards still stand, and where a bad interaction could emerge.
- Describe the **blast radius** of the change:
  - which systems, workflows, or users are affected,
  - what downstream dependencies may feel the effect,
  - whether failures stay local or propagate,
  - and whether future changes will now have to route through this new logic or abstraction.

## Validation and Enforcement

- Include a testing/validation section that explains how the change was checked. This can include manual testing, automated tests, lint/typecheck results, screenshots, example commands, benchmarks, or notes about what was not tested.
- If the PR affects validation or enforcement layers, say so explicitly. That includes changes to:
  - local validators,
  - policy checks,
  - CI checks,
  - branch protections,
  - wrappers,
  - plugins,
  - audit logging,
  - approval gates,
  - or other mechanisms that constrain or verify behavior.
- Distinguish between:
  - validation of the feature itself,
  - validation of the safety/enforcement mechanism,
  - and assumptions that are still unverified.

## Rollback, Recovery, and Containment

- Where applicable, explain how to **revert**, **contain**, or **recover** from this PR if it behaves badly.
- If the PR affects rollback paths, known-good refs, approved refs, migration safety, checkpointing, quarantine flows, or restore procedures, make that explicit.
- If special recovery steps would be required, state them clearly rather than assuming they are obvious.
- If the PR is intentionally designed to be easy to revert or isolate, say so.

## Follow-Ups and Out of Scope

- If the PR includes follow-up work that is intentionally deferred, list that near the end so reviewers understand what is out of scope for this PR.
- Optional clarifications, edge cases, caveats, or nuanced behavior can appear near the bottom and may use bullets or footnote-style markers if that improves readability.

## Core Principle

- In all cases, begin with a concise summary of what this PR changes. The rest of the body should then elaborate on intent, scope, design choices, implementation, tradeoffs, complexity, risk, validation, side effects, recovery, and remaining considerations.
