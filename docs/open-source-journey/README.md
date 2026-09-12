# Project Upstream

Charter for a real, long-running project. This directory is internal working
documentation inside `luismarrero.me` — it is not site content and is never
rendered.

## Mission

Move Luis Marrero from user of open-source software to legitimate upstream
contributor, and document the journey honestly enough to produce at least two
high-quality articles for luismarrero.me.

## Targets

1. **Astro** (`withastro/astro`) — the framework this site is built on.
2. **The Linux kernel** (`kernel.org`, mainline process) — the kernel itself,
   not an adjacent ecosystem project.

## Definition of done

**Minimum:**
- One legitimate, tested PR submitted to Astro upstream.
- One legitimate patch submitted to the Linux kernel process (correct tree,
  correct recipients, Signed-off-by, honest testing statement).
- Two article drafts in `src/posts/` backed by evidence in `EVIDENCE.md`.

**Ideal:**
- Astro PR merged.
- Kernel patch accepted into the relevant maintainer/subsystem tree, ideally
  reaching mainline.
- A third article on AI agents and open-source contribution, grounded in what
  actually happened.

## Constraints

Optimize for: legitimate upstream value, smallest useful scope, shortest path
to a real submission, low cognitive load, strong technical understanding,
evidence-driven work, honest public documentation.

Never optimize for: fake productivity, vanity commits, typo hunting for
credit, AI-generated patches Luis does not understand, speculative refactors,
unnecessary architecture, excessive process files, whole-codebase study before
action, or articles claiming outcomes that did not happen.

## WIP limit

**WIP = 1.** Exactly one task is ACTIVE at any moment. Backlog candidates may
exist (max three per track), but only one thing is being worked. Every session
ends with exactly one concrete NEXT ACTION in `STATUS.md`, executable without
reconstructing context.

## State machine

```
DISCOVERED → SELECTED → UNDERSTOOD → REPRODUCED → IMPLEMENTING
→ TESTED → SUBMITTED → IN_REVIEW → ACCEPTED_UPSTREAM
```

Not every contribution requires every state (e.g. a docs fix may skip
REPRODUCED), but transitions must be honest: never mark a state that did not
actually occur.

## Track order

1. **Track A: Astro** — until a legitimate PR is submitted.
2. **Track B: Linux kernel** — becomes active once the Astro PR is SUBMITTED
   and waiting on external review.

Actionable Astro review feedback becomes high priority when it arrives, but
WIP stays at 1: pause the kernel task, handle the feedback, resume.

Never actively debug Astro and the kernel simultaneously.

## Session protocol

**Start:** read `STATUS.md` → check `git status` → verify whether external
state for the active task changed (issue closed? competing PR? review
arrived?) → state the one active task. Do not reopen settled decisions
without new evidence.

**During:** preserve WIP = 1, update hypotheses when evidence changes, record
meaningful failures, keep scope narrow.

**End:** update `LOG.md`; update `EVIDENCE.md` / `AI-USAGE.md` /
`ARTICLE-NOTES.md` if warranted; rewrite `STATUS.md`; leave exactly one
NEXT ACTION.

## Stop rules

- **Candidate search:** cap at three candidates per track, score, pick, or
  deliberately switch surface. No endless browsing.
- **Debugging:** after two failed implementation hypotheses, stop editing and
  return to reproduction/evidence.
- **Scope:** if a change grows significantly, stop and split; prefer the
  smaller contribution.
- **Cognitive load:** if the next step needs many disconnected facts, update
  `STATUS.md`, shrink the task to one executable action.
- **AI confidence:** if a proposed change cannot be explained from source,
  behavior, tests, and project conventions, do not implement or submit it.

## Article strategy

Articles are drafted in the existing content system (`src/posts/`, schema in
`src/content.config.ts`): Spanish, `lang: es`, `published: false` by default.
Raw material is captured in `ARTICLE-NOTES.md` **during** the work.

1. **Article 1** — the Astro contribution journey.
2. **Article 2** — the Linux kernel contribution journey.
3. **Optional article 3** — AI agents lower the cost of entering large
   codebases, but not the contributor's responsibility. Only if the evidence
   from articles 1–2 supports it.

Nothing is published automatically. Publishing requires Luis's explicit
approval.

## Honesty rules for public claims

- Never claim "merged" when merely submitted, or "accepted" when merely
  reviewed.
- Never claim "contributed to the Linux kernel" if only a local patch exists.
- Never claim "fixed Astro" without upstream evidence.
- Never claim a test passed unless it actually ran successfully.
- `EVIDENCE.md` keeps prepared / submitted / under review / merged strictly
  separate; articles must match it.
- AI assistance is recorded in `AI-USAGE.md` and disclosed where the upstream
  project's current policy requires it. For kernel work: Luis must understand
  and be able to defend every changed line, and current official kernel
  guidance on tool-generated content must be re-checked before submission.

## Public action boundary

Autonomous: inspecting files, internal docs, local branches, local edits,
running tests, preparing commits, drafting PR text / patches / emails.

Requires Luis's explicit approval: public comments, opening upstream PRs,
sending kernel patches or mailing-list email, public claims on the website,
publishing an article.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This charter. Durable; rarely changes. |
| `ROADMAP.md` | Outcome-based direction: milestones, success levels, progress. |
| `STATUS.md` | Resumption file. Extremely short. Rewritten every session. |
| `BACKLOG.md` | Scored candidates, max three per track. |
| `LOG.md` | Append-only session log. |
| `EVIDENCE.md` | Links/IDs for every claim, by status. |
| `AI-USAGE.md` | Append-only record of material AI assistance. |
| `ARTICLE-NOTES.md` | Raw article material, captured during the work. |

No additional planning files without a concrete need.
