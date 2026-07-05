# Project log

Append-only. One entry per meaningful session: date, objective, actions,
commands worth preserving, observations, failed hypotheses, result, evidence,
AI assistance, exact next action.

---

## Session 001 — 2026-07-05

**Objective:** Inspect the repository and initialize the Project Upstream
workspace (Phase 0).

**Actions:**
- Inspected `README.md`, `package.json`, `astro.config.mjs`,
  `src/content.config.ts`, `src/posts/*`, `tests/`, git state.
- Created `docs/open-source-journey/` with the seven project files.

**Observations:**
- Working tree clean on `main`; recent work is the poem pipeline
  (fallback reserve, DeepSeek cost controls).
- Site runs Astro **6.0.8** with Svelte 5, Tailwind v4, pnpm. Relevant when
  choosing Astro candidates: Luis is a real 6.x user.
- `CLAUDE.md` is slightly stale vs. reality: `package.json` now has
  `test:js` (`vitest run`, covering `tests/ai_poems.test.ts`) and the posts
  schema includes `lang: z.enum(["en","es"]).default("es")`.
- Post conventions for future articles: kebab-case filename in `src/posts/`,
  frontmatter `title`, `published`, `description`, `tags`, `date` (e.g.
  `"Jul 3 2026"`), optional `lang`; Spanish, first-person, practical tone.
- No `docs/` directory existed; `docs/open-source-journey/` is new and
  touches nothing else.

**Failed hypotheses:** none (no implementation work this session).

**Result:** Workspace initialized. Active track set to Astro, Phase A1.

**Evidence produced:** the seven files in `docs/open-source-journey/`.

**AI assistance:** Claude Code (Fable 5) performed the inspection and wrote
the workspace files; Luis directed structure and rules. See `AI-USAGE.md`
entry 2026-07-05.

**Next action:** Read current `withastro/astro` `main` contributor guidance
(`CONTRIBUTING.md` + linked required reading); record required Node version,
pnpm version, install/build commands, and how to run a single package's
tests in `LOG.md`.

---

## Session 002 — 2026-07-05

**Objective:** Extract the reusable methodology into a personal Claude Code
skill (`upstream-contributor`), then audit and harden it with the
skill-creator eval loop. Meta/tooling session — no upstream work.

**Actions:**
- Created `~/.claude/skills/upstream-contributor/` (SKILL.md + 3 reference
  files + candidate-scorecard template), format verified against current
  official Claude Code skills docs. Methodology lives in the skill;
  project state stays in this directory (source of truth unchanged).
- Luis flagged that `/skill-creator` was not used for the initial creation.
  Re-did the process properly: snapshot baseline, audit, 3 behavioral evals
  (resume with state, resume without state, prepare-submission approval
  boundary), improved-skill vs snapshot, real headless `claude -p` runs,
  graded assertions, aggregated benchmarks, human review via eval viewer.

**Commands worth preserving:**
- `claude -p "/upstream-contributor <mode>" --allowedTools "Read,Glob,Grep,Bash(git status:*),Bash(git log:*)" --output-format json`
- skill-creator's `python -m scripts.aggregate_benchmark <iteration-dir> --skill-name <name>` and `eval-viewer/generate_review.py`.

**Observations:**
- Iteration 1 (6 runs): 88.9% both configs. Real defect found that the
  earlier single manual test missed: `resume` sometimes started *executing*
  the NEXT ACTION instead of reporting it (nondeterministic).
- Fix: one line in resume mode — "the report is the deliverable; do not
  execute". Iteration 2 (8 runs): 100% both configs; fixed-skill resume runs
  ~14.5s vs 74s for the iteration-1 failing run.
- Honest caveat: the old wording also passed eval-0 twice in iteration 2 —
  the iteration-1 failure was run-to-run variance; the fix removes the
  ambiguity rather than curing a constant failure.
- Eval subagents honored the honesty rules: refused to claim a
  sandbox-blocked test passed; detected the planted fixture repo as not a
  real upstream.

**Failed hypotheses:** "A passing manual test means resume behaves
correctly" — disproven by multi-run evals.

**Result:** Skill v1 hardened and installed. Residual known weaknesses: no
mechanical enforcement (no hooks by design in V1); one run labeled a section
"State: TESTED" while tests were unconfirmed (qualified inline) — candidate
future clarification.

**Evidence produced:** `artifacts/skill-eval-2026-07-05/` (benchmarks for
both iterations, eval definitions, analyst notes).

**AI assistance:** Entire session AI-executed (Claude Fable 5 + skill-creator)
under Luis's direction and correction; Luis reviewed iteration 1 in the eval
viewer before iteration 2. See `AI-USAGE.md` entry 2026-07-05 (skill).

**Next action (project — unchanged):** Read current `withastro/astro` `main`
contributor guidance (`CONTRIBUTING.md` + linked required reading); record
required Node version, pnpm version, install/build commands, and how to run
a single package's tests in `LOG.md`.

---

## Session 003 — 2026-07-05

**Objective:** Add a `close` mode (end-of-session documentation protocol) to
the `upstream-contributor` skill via skill-creator, make the skill always
write state to this directory, and publish the skill to GitHub. Meta/tooling
session — no upstream work.

**Actions:**
- Added to the skill: `close` mode (LOG append → conditional EVIDENCE /
  AI-USAGE / ARTICLE-NOTES updates → STATUS rewrite with exactly one NEXT
  ACTION; "not recorded" beats guessing) and a state-directory resolution
  rule: cwd `docs/open-source-journey/` first, else the pointer file
  `~/.claude/upstream-contributor.state` (created, points here), else no
  state — never scaffold or invent.
- Eval iteration 3 (sandboxed copies of this directory, never the real one):
  `close` 2/2, `resume` regression 1/1 — 9/9 assertions.
- Published the skill: https://github.com/luismarrer/upstream-contributor-skill
  (private; `git clone` into `~/.claude/skills/upstream-contributor`).

**Observations:**
- `close` run-1 wrote "not recorded" for version values it wasn't given and
  logged what was NOT done — the honesty rules held under delegation.
- The eval loop caught a flaw in my own eval design: an assertion treated
  EVIDENCE.md's Local-artifacts table as upstream evidence; graded on
  intent, flaw documented in analyst notes.
- Baseline contamination lesson: a prompt-injected snapshot is not a
  reliable baseline when the improved skill is auto-discoverable — the
  baseline session announced it was using the installed skill instead.
- A skill-registry re-read silently dropped the `argument-hint` frontmatter
  line at some point; restored. Watch for it after skill edits.

**Failed hypotheses:** "A prompt-injected old-skill snapshot isolates the
baseline from the installed skill" — disproven (see contamination note).

**Result:** Skill v1.1: seven modes, state always lands in this directory
regardless of where work happens, versioned on GitHub.

**Evidence produced:** `artifacts/skill-eval-2026-07-05/`
(benchmark-iteration-3.md, analyst notes); the GitHub repo.

**AI assistance:** AI-executed under Luis's direction (skill-creator loop);
Luis defined the requirements (close mode, GitHub backup, fixed state
directory). See `AI-USAGE.md`.

**Next action (project — unchanged):** Read current `withastro/astro` `main`
contributor guidance (`CONTRIBUTING.md` + linked required reading); record
required Node version, pnpm version, install/build commands, and how to run
a single package's tests in `LOG.md`.

---

## Session 004 — 2026-07-05

**Objective:** Add the missing durable roadmap artifact.

**Actions:** Created `ROADMAP.md` (outcome-based: mission, three success
levels, Phase 0 + A1–A8 + B1–B10 + publishing track with verifiable
milestone checkboxes, current critical path, maintenance rules). Linked it
from `README.md`'s file table. No dates promised for maintainer-controlled
outcomes.

**Observations:** Phase 0 is now verifiably complete (all ten milestones,
including the skill and its safe testing). One stretch-success item landed
early: the methodology extraction into the `upstream-contributor` skill.
Track A has zero checkboxes — the sandbox eval sessions that "set up Astro"
were fictional fixtures and were NOT counted as evidence. Process slip
worth recording: the first attempt inserted this entry out of chronological
order (between sessions 002 and 003); corrected to a true append.

**Result:** Roadmap exists; checkbox state derived only from repository
evidence.

**Evidence produced:** `ROADMAP.md`.

**AI assistance:** AI-drafted from the existing project files under Luis's
specification; no upstream contribution affected.

**Next action (project — unchanged):** Read current `withastro/astro` `main`
contributor guidance (`CONTRIBUTING.md` + linked required reading); record
required Node version, pnpm version, install/build commands, and how to run
a single package's tests in `LOG.md`.
