# AI usage record

Append-only. Records material AI assistance: date, tool/model, task, prompt
summary, output category, files/reasoning affected, what Luis independently
verified, tests performed, and whether the assistance touched an upstream
contribution.

Kernel rule: Luis must understand the entire submission; human review is not
a rubber stamp. Current official kernel guidance on tool-generated content
must be re-checked before any kernel submission, and assistance must be
disclosable accurately. Never fabricate human authorship.

---

## 2026-07-05 — Workspace initialization

- **Tool/model:** Claude Code, Claude Fable 5.
- **Task:** Inspect `luismarrero.me` repo; create the Project Upstream
  workspace (Phase 0).
- **Prompt summary:** Luis provided the full project charter (mission,
  constraints, WIP = 1, state machine, track order, honesty rules) and
  instructed: inspect first, then create `docs/open-source-journey/` with
  seven files of real content.
- **Output category:** internal project documentation (no code, no upstream
  material).
- **Files affected:** the seven files in `docs/open-source-journey/`.
- **Independently verified by Luis:** pending — Luis should skim the seven
  files and confirm the charter matches his intent.
- **Tests performed:** none applicable (documentation only).
- **Upstream contribution affected:** no.

## 2026-07-05 — upstream-contributor skill: extraction, audit, eval loop

- **Tool/model:** Claude Code, Claude Fable 5; `skill-creator` skill for the
  audit/eval methodology; headless `claude -p` sessions as eval subjects.
- **Task:** Extract the reusable methodology from this project into a
  personal Claude Code skill (`~/.claude/skills/upstream-contributor/`),
  then audit and iterate it with skill-creator after Luis flagged that
  skill-creator had not been used for the initial creation.
- **Prompt summary:** Luis specified the skill design (modes, context
  detection, progressive disclosure, safety boundary) and later corrected
  the process ("no llamaste a la skill /skill-creator").
- **Output category:** internal tooling (skill files) + eval infrastructure
  (test prompts, assertions, graded runs, benchmarks). No upstream material.
- **Files affected:** `~/.claude/skills/upstream-contributor/` (5 files);
  eval artifacts copied to `docs/open-source-journey/artifacts/`.
- **Independently verified by Luis:** reviewed iteration-1 results in the
  eval viewer before authorizing iteration 2.
- **Tests performed:** 14 real headless runs across 2 iterations (3
  behavioral evals, improved-skill vs pre-audit snapshot), graded against
  explicit assertions with quoted evidence. Key finding: a manual test had
  passed while multi-run evals exposed nondeterministic over-execution in
  `resume` mode; wording fix applied and re-verified.
- **Upstream contribution affected:** no (Project Upstream state and NEXT
  ACTION unchanged).

## 2026-07-05 — skill v1.1: close mode, state pointer, GitHub publication

- **Tool/model:** Claude Code, Claude Fable 5 + skill-creator loop.
- **Task:** Add `close` mode and state-directory resolution to the skill;
  publish to https://github.com/luismarrer/upstream-contributor-skill
  (private) at Luis's request.
- **Output category:** internal tooling + eval infrastructure; one public
  action (GitHub repo creation/push) explicitly requested by Luis.
- **Tests performed:** eval iteration 3 — `close` validated only against
  sandboxed copies of this directory (2/2), `resume` regression 1/1; the
  old-skill baseline run self-contaminated and was excluded from stats.
- **Independently verified by Luis:** pending — review iteration 3 in the
  eval viewer; the sandbox runs' honesty behavior ("not recorded" instead
  of invented values) is worth seeing firsthand.
- **Upstream contribution affected:** no.
