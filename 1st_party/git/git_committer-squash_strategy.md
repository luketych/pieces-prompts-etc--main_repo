# Commit Messages (STRICT + MACHINE-VALIDATED)

This format is **mandatory and CI-enforced**. Commits that do not match the required
structure will fail validation.

Goal:
- Enable squash → **complete PR body**
- Preserve **intent, reasoning, decisions**
- Ensure **uniform, parseable structure**

If a section does not apply, write: `N/A`

---

## REQUIRED FORMAT (EXACT)

Use **exact headings** and **order** below:

```
<Summary line>

## What Changed
- ...

## Intent / Motivation
...

## Implementation Approach
...

## Key Decisions & Tradeoffs
...

## Risk / Impact
- Risk Level: LOW|MEDIUM|HIGH
- Areas Affected: runtime|state|ci|permissions|none
- Notes: ...

## State of Completion
- Status: COMPLETE|PARTIAL|EXPLORATORY|REFACTOR_ONLY
- Not Done: ...

## Follow-ups
- ...

## Context / Links
- Task: T<task> or N/A
- Related: <hashes/links> or N/A
```

---

## SUMMARY LINE FORMAT (STRICT)

```
T<task> <type>: <what changed> — <why>
```

Where:
- `T<task>` = optional (omit if not using tasks)
- `<type>` ∈ {feature, fix, refactor, infra, exploratory, policy}
- `—` (em dash) is required separator before reason

Examples:
- `T12.3 refactor: introduce gmux session registry — stabilize cross-session lookup`
- `fix: guard nil pointer in loader — prevent crash on empty config`

---

## REGEX (CANONICAL)

Use this regex to validate the entire commit message:

```
^(?:T\d+(?:\.\d+)?\s+)?(feature|fix|refactor|infra|exploratory|policy):\s.+\s—\s.+\n\n## What Changed\n(?:- .+\n)+\n## Intent / Motivation\n(?:.+\n)+\n## Implementation Approach\n(?:.+\n)+\n## Key Decisions & Tradeoffs\n(?:.+\n)+\n## Risk / Impact\n- Risk Level: (LOW|MEDIUM|HIGH)\n- Areas Affected: (runtime|state|ci|permissions|none)(?:\|(?:runtime|state|ci|permissions|none))*\n- Notes: .+\n\n## State of Completion\n- Status: (COMPLETE|PARTIAL|EXPLORATORY|REFACTOR_ONLY)\n- Not Done: .+\n\n## Follow-ups\n(?:- .+\n)+\n## Context / Links\n- Task: (T\d+(?:\.\d+)?|N/A)\n- Related: (.+|N/A)\n?$
```

Notes:
- Enforces section order and presence
- Enforces enums for type, risk, status
- Requires bullets in “What Changed” and “Follow-ups”

---

## COMMITLINT CONFIG (EXAMPLE)

`commitlint.config.cjs`
```js
module.exports = {
  rules: {
    'body-max-line-length': [0],
    'header-max-length': [0],
    'type-enum': [
      2,
      'always',
      ['feature', 'fix', 'refactor', 'infra', 'exploratory', 'policy'],
    ],
  },
  plugins: [
    {
      rules: {
        'matches-template': ({ raw }) => {
          const re = new RegExp(
            '^(?:T\\d+(?:\\.\\d+)?\\s+)?(feature|fix|refactor|infra|exploratory|policy):\\s.+\\s—\\s.+\\n\\n## What Changed\\n(?:- .+\\n)+\\n## Intent / Motivation\\n(?:.+\\n)+\\n## Implementation Approach\\n(?:.+\\n)+\\n## Key Decisions & Tradeoffs\\n(?:.+\\n)+\\n## Risk / Impact\\n- Risk Level: (LOW|MEDIUM|HIGH)\\n- Areas Affected: (runtime|state|ci|permissions|none)(?:\\|(?:runtime|state|ci|permissions|none))*\\n- Notes: .+\\n\\n## State of Completion\\n- Status: (COMPLETE|PARTIAL|EXPLORATORY|REFACTOR_ONLY)\\n- Not Done: .+\\n\\n## Follow-ups\\n(?:- .+\\n)+\\n## Context / Links\\n- Task: (T\\d+(?:\\.\\d+)?|N/A)\\n- Related: (.+|N/A)\\n?$'
          );
          const ok = re.test(raw);
          return [
            ok,
            'commit message does not match STRICT template',
          ];
        },
      },
    },
  ],
};
```

---

## HUSKY HOOK (EXAMPLE)

`.husky/commit-msg`
```sh
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx commitlint --edit "$1"
```

---

## QUICK CHECK (LOCAL)

Validate a message file:
```sh
node -e "const fs=require('fs');const re=new RegExp(process.argv[1]);const s=fs.readFileSync(process.argv[2],'utf8');console.log(re.test(s)?'OK':'FAIL')" "<PASTE_REGEX_HERE>" commit.txt
```

---

## HARD RULES

- No missing sections
- No reordered sections
- No vague summaries
- Use exact headings and enums
- Use em dash (—) in summary
- Bullet lists where required

---

## CORE PRINCIPLE

The commit message must be:
- **Parseable by machines**
- **Sufficient for PR reconstruction**
- **Readable in isolation**
