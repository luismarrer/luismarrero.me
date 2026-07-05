# Backlog

Max **three active candidates per track**. Candidates enter as DISCOVERED;
exactly one may be SELECTED at a time (WIP = 1). Never select a task merely
because an AI can solve it. Re-verify candidate state (issue open? competing
PR? already fixed?) at selection time — never trust a stale snapshot.

## Scoring

Each criterion 0–2. **Astro threshold: ≥ 8/12.**

| Criterion | 0 | 2 |
| --- | --- | --- |
| Reproducibility | can't reproduce | reliable minimal repro |
| Scope | sprawling | few files, clear boundary |
| Skill fit | far from Luis's stack | TS/JS/Python/C/tooling he knows |
| Maintainer signal | no interest shown | explicit "PR welcome" / triaged |
| Testability | no test path | clear targeted test exists |
| Conflict/duplication risk | active competing PR | nobody working on it |

Kernel candidates add three criteria (0–2 each; equivalent evidence-based
threshold: **≥ 12/18**, and document uncertainty explicitly):

| Criterion | 0 | 2 |
| --- | --- | --- |
| Ownership clarity | unclear MAINTAINERS entry | obvious maintainer + list |
| Subsystem clarity | crosses subsystems | one subsystem, one tree |
| Line-by-line defensibility | Luis can't defend the diff | every line explainable |

## Track A: Astro

Discovery not started (blocked on Phase A1 environment baseline).

| # | Candidate | Source/link | Repro | Scope | Fit | Signal | Test | Conflict | Total | State |
| - | --------- | ----------- | ----- | ----- | --- | ------ | ---- | -------- | ----- | ----- |
| — | *(none yet)* | | | | | | | | | |

## Track B: Linux kernel

Discovery not started (Track B activates after Astro PR is SUBMITTED).

| # | Candidate | Tree/subsystem | Repro | Scope | Fit | Signal | Test | Conflict | Own | Subsys | Defend | Total | State |
| - | --------- | -------------- | ----- | ----- | --- | ------ | ---- | -------- | --- | ------ | ------ | ----- | ----- |
| — | *(none yet)* | | | | | | | | | | | | |

## Rejected candidates

Record rejections with one-line reasons so they are not re-litigated.

*(none yet)*
