# Project Upstream Roadmap

Outcome-based roadmap. External review and maintainer response times are not
ours to control, so there are no calendar promises here — only ordered
outcomes and verifiable milestones. Division of labor: `README.md` holds the
charter and rules, `STATUS.md` holds the current state and the single NEXT
ACTION, `BACKLOG.md` holds candidates, `LOG.md` holds history. This file
holds direction and progress.

## Mission

Move from being only a user of open-source software I admire to becoming a
legitimate upstream contributor to:

1. Astro
2. The Linux kernel

while documenting the real process for luismarrero.me.

## Success levels

### Minimum success

- A legitimate Astro contribution is submitted upstream as a PR.
- A legitimate Linux kernel patch is submitted through the appropriate
  upstream process.
- At least two evidence-based articles are published: the Astro journey and
  the Linux kernel journey.

### Target success

- Astro contribution accepted upstream.
- Linux kernel contribution accepted into the relevant maintainer/subsystem
  path or upstream.
- At least three strong articles published: Astro, Linux kernel, and AI
  agents & open-source responsibility.

### Stretch success

- Continue iterating until both Astro and the Linux kernel have accepted
  upstream contributions.
- Pursue a small real C contribution to the kernel if the first accepted
  kernel contribution is documentation, testing, or tooling.
- [x] Extract reusable methodology into the `upstream-contributor` Claude
  Code Skill — done early (2026-07-05): eval-hardened across 3 iterations,
  published at https://github.com/luismarrer/upstream-contributor-skill.

## Phase 0 — Project Operating System

**Outcome:** project state survives interruptions and can be resumed with
minimal cognitive load.

- [x] Project charter exists (`README.md`, LOG 001)
- [x] `STATUS.md` exists and has exactly one NEXT ACTION
- [x] `BACKLOG.md` exists
- [x] `LOG.md` exists
- [x] `EVIDENCE.md` exists
- [x] `AI-USAGE.md` exists
- [x] `ARTICLE-NOTES.md` exists
- [x] `ROADMAP.md` exists (this file)
- [x] Upstream Contributor Skill V1 exists
      (`~/.claude/skills/upstream-contributor/`, versioned on GitHub)
- [x] Skill has been safely tested (3 eval iterations, sandboxed runs;
      `artifacts/skill-eval-2026-07-05/`, LOG 002–003)

**Phase 0 is complete.**

## Track A — Astro

### A1 — Environment verified

**Outcome:** Astro upstream development environment works locally.

- [ ] Current official contributor guidance inspected
- [ ] Correct runtime/tool versions verified
- [ ] Dependencies installed
- [ ] Relevant build succeeds
- [ ] At least one targeted test succeeds
- [ ] Baseline evidence recorded

### A2 — Candidate discovery

**Outcome:** at most three current, legitimate contribution candidates.

- [ ] Current upstream state checked
- [ ] Duplicate/competing work checked
- [ ] Candidates scored (see `BACKLOG.md` rubric)
- [ ] Exactly one candidate selected

### A3 — Problem understood

**Outcome:** the selected problem is understood well enough to defend the work.

- [ ] Expected behavior documented
- [ ] Actual behavior documented
- [ ] Relevant code path mapped narrowly
- [ ] Analogous tests identified
- [ ] Reproduction or equivalent evidence established where applicable

### A4 — Minimal implementation

**Outcome:** the smallest useful change exists locally.

- [ ] Scope remains narrow
- [ ] No unrelated refactor
- [ ] Regression coverage added where applicable
- [ ] Every changed line understood

### A5 — Validation

**Outcome:** the contribution has appropriate evidence.

- [ ] Targeted tests run
- [ ] Broader checks run only where justified
- [ ] Exact commands and outcomes recorded
- [ ] Changeset requirements checked
- [ ] Diff manually reviewed

### A6 — Submitted upstream

**Outcome:** a legitimate Astro PR is publicly submitted.

- [ ] PR title prepared
- [ ] PR description prepared
- [ ] Evidence and tests documented
- [ ] Remaining uncertainty disclosed
- [ ] Luis explicitly approved public submission
- [ ] PR submitted
- [ ] PR URL recorded in `EVIDENCE.md`

### A7 — Review iterations

**Outcome:** maintainer feedback is handled professionally.

- [ ] Review feedback recorded
- [ ] Requested changes understood
- [ ] Revisions tested
- [ ] Follow-up evidence recorded

### A8 — Accepted upstream

**Outcome:** the Astro contribution is accepted upstream.

- [ ] Acceptance/merge evidence recorded
- [ ] Public claims updated accurately
- [ ] Article material finalized

## Track B — Linux Kernel

Activates once the Astro PR is SUBMITTED (see README track order).

### B1 — Process orientation

**Outcome:** only the necessary kernel contribution process is understood.

- [ ] Current official development-process guidance inspected
- [ ] Current patch-submission guidance inspected
- [ ] Submission checklist inspected
- [ ] Signed-off-by requirements understood
- [ ] Tool-generated-content guidance inspected
- [ ] Subsystem-specific rules checked when target is known

### B2 — Environment verified

**Outcome:** a real kernel development environment is usable.

- [ ] Appropriate source tree obtained
- [ ] Git identity verified
- [ ] Correct base/tree strategy understood
- [ ] Baseline build or relevant validation succeeds
- [ ] Patch tooling available
- [ ] Maintainer discovery process understood

### B3 — Candidate discovery

**Outcome:** at most three legitimate kernel candidates (surfaces:
documentation, kselftest/tests, scripts/tooling, small C fixes).

- [ ] Current evidence gathered
- [ ] Meaningless typo hunting rejected
- [ ] Ownership/subsystem identified where possible
- [ ] Duplication risk checked (lore.kernel.org)
- [ ] Testability assessed
- [ ] Exactly one candidate selected

### B4 — Evidence established

**Outcome:** the reason for the patch is technically defensible.

- [ ] Baseline established
- [ ] Problem reproduced where applicable
- [ ] Relevant history inspected where useful
- [ ] Scope understood
- [ ] Test strategy defined
- [ ] Luis can explain why the behavior is wrong

### B5 — Minimal patch

**Outcome:** the smallest defensible patch exists locally.

- [ ] Every changed line understood
- [ ] No unrelated cleanup
- [ ] Commit message explains why
- [ ] Signed-off-by handled correctly
- [ ] AI assistance recorded accurately
- [ ] Subsystem conventions respected

### B6 — Validation

**Outcome:** validation matches the changed area.

- [ ] Targeted validation run
- [ ] Relevant build/test run
- [ ] Style/check tools run where appropriate
- [ ] Exact results recorded
- [ ] Remaining limitations stated honestly

### B7 — Submission prepared

**Outcome:** the patch is ready for human approval before sending.

- [ ] Correct subsystem/tree identified
- [ ] Recipients identified (`get_maintainer.pl`)
- [ ] Subject reviewed
- [ ] Commit message reviewed
- [ ] Diff reviewed
- [ ] Tests documented
- [ ] AI/tool-assistance implications reviewed
- [ ] Exact send process prepared

### B8 — Submitted upstream

**Outcome:** a legitimate kernel patch is sent through the appropriate process.

- [ ] Luis explicitly approved sending
- [ ] Patch sent
- [ ] Message identifiers / public archive links recorded where available
- [ ] State updated to SUBMITTED

### B9 — Review iterations

**Outcome:** review feedback is incorporated through proper revisions.

- [ ] Feedback recorded
- [ ] v2 prepared if needed
- [ ] v3+ prepared if needed
- [ ] Revision changelog preserved where appropriate
- [ ] Testing repeated after relevant changes

### B10 — Accepted upstream

**Outcome:** the kernel contribution is accepted into the relevant upstream path.

- [ ] Acceptance evidence recorded
- [ ] Exact acceptance level stated accurately
- [ ] Subsystem-tree vs mainline status distinguished
- [ ] Public claims updated
- [ ] Article material finalized

## Publishing Track

Publishing follows evidence; it never precedes it. Raw material accumulates
in `ARTICLE-NOTES.md` during the work.

### Article 1 — Astro

Potential themes: entering the source code of a framework I already use;
first upstream contribution; agents as codebase-navigation tools;
reproduction, testing, and review.

Status: raw material only (one starting note). No draft — Track A has not
produced a story yet.

### Article 2 — Linux Kernel

Potential themes: GitHub PR culture vs patch/email culture; first kernel
patch; AI-assisted exploration; responsibility and transparency; review
iterations.

Status: nothing — Track B not active.

### Article 3 — AI Agents and Open Source

Potential thesis: AI agents reduce the cost of navigating large codebases,
but they do not remove contributor responsibility.

Status: strongest early material — four evidence-backed notes in
`ARTICLE-NOTES.md` (stale AI-docs, human process correction, manual-test vs
eval-loop, honesty rules propagating to subagents). Do not draft yet.

## Current critical path

1. **Current phase:** Track A — Astro, Phase A1 (Environment).
2. **Current track:** Astro.
3. **Current milestone:** A1 first checkbox — inspect current official
   contributor guidance in `withastro/astro`.
4. **Next major milestone:** A1 complete (environment verified with a clean
   baseline), unlocking A2 candidate discovery.

The exact executable step lives in `STATUS.md` → NEXT ACTION.

## Roadmap maintenance rules

- Update milestone checkboxes only from verified evidence (recorded in
  `LOG.md` / `EVIDENCE.md`).
- Never mark SUBMITTED when merely prepared; never ACCEPTED when merely
  reviewed; never MERGED without upstream evidence.
- Do not turn this file into a daily log — that is `LOG.md`'s job.
- No speculative dates for maintainer-controlled outcomes.
- Preserve WIP = 1.
- `STATUS.md` remains the source of truth for the single NEXT ACTION.
