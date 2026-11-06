# Article notes

Raw material captured **during** the work. No polished drafting here.
Every claim destined for an article needs a matching `EVIDENCE.md` entry.

## Astro

- Starting point (2026-07-05): Luis runs Astro 6.0.8 in production on this
  site — the contribution target is a tool he genuinely depends on, not a
  random repo. Possible opening hook.

## Linux kernel

*(nothing yet — track not active)*

## AI agents and open source

- Meta-observation (2026-07-05): the project itself began with an AI agent
  auditing the repo and catching that the repo's own AI-guidance file
  (`CLAUDE.md`) was already stale (missing `test:js`, missing the `lang`
  schema field). Even AI-oriented documentation rots; evidence beats
  documentation. Possible seed for article 3.
- Process discipline came from the human (2026-07-05): the agent hand-built
  the `upstream-contributor` skill with file writes instead of using the
  dedicated skill-creator tooling; Luis caught it ("no llamaste a la skill
  /skill-creator. Lo cual me preocupa"). The correction paid off measurably:
  the tool's eval loop found a real defect the agent's single manual test
  had missed. Direct evidence for the article-3 thesis — agents lower
  friction, responsibility stays human.
- A passing manual test proved nothing about stability (2026-07-05): one
  manual run of `resume` behaved correctly; multi-run evals showed the same
  prompt sometimes made the agent start *executing* the next action instead
  of reporting it (nondeterministic, wording-dependent). Fixing one line of
  the skill ("the report is the deliverable — do not execute") made the
  behavior consistent and ~5x faster (14s vs 74s). Lesson: with agents,
  behavioral contracts need multiple runs to verify — anecdote ≠ evidence.
- The honesty rules propagated downward (2026-07-05): eval subagents
  refused to claim a sandbox-blocked test had passed ("status: NOT
  CONFIRMED"), and one flagged the planted fixture repo as not a real
  upstream target and declined to treat submission as actionable. Written
  integrity constraints in a skill do shape downstream agent behavior.

## Quotes / thoughts

*(nothing yet)*

## Mistakes

*(nothing yet)*

## Surprises

*(nothing yet)*

## Emotional moments

- 2026-07-05, ante el primer commit público del proyecto: "me da 1. Un poco
  de vergüenza, 2. Un poco de miedo." Vergüenza por cómo se ve participar en
  open source con tanta IA ("no sé qué piensa la gente de esta forma de
  participar"); miedo a un leak por documentarlo todo. Nada se había
  publicado aún — el peso llegó antes que la primera acción pública. El
  miedo se respondió con un audit (cero secretos); la vergüenza, con el
  propio sistema: las reglas de honestidad, AI-USAGE.md y los approval
  gates existen exactamente para eso. Material directo para el artículo 3:
  la parte emocional de contribuir con agentes no es teórica.

## Technical discoveries

*(nothing yet)*

## Possible titles

Deliberately empty — no final titles until the real story exists.

## Claims requiring evidence

Running list of claims that must NOT appear in an article until backed:

- "I contributed to Astro" — requires a submitted PR URL in `EVIDENCE.md`.
- "My PR was merged" — requires the merge commit / merged PR state.
- "I sent a patch to the Linux kernel" — requires a mailing-list message ID.
- "My patch was accepted" — requires subsystem-tree or mainline commit ID.
- Any "the tests pass" — requires the actual command + run recorded in `LOG.md`.
