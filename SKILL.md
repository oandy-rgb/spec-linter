---
name: behavioral-spec-linter
description: Stress-test software requirements, product specifications, SDDs, API contracts, user stories, acceptance criteria, and implementation plans for ambiguity, contradictions, missing edge cases, and hidden assumptions before coding. Use when asked to review, lint, clarify, harden, validate, or compare interpretations of a specification, or when an implementation request is underspecified and semantic mistakes would be costly.
---

# Behavioral Spec Linter

Find the places where competent implementers of a specification would build
different observable behavior, then propose minimal, testable revisions.
Read [references/review-rubric.md](references/review-rubric.md) for finding
types, severity, the evidence standard, and the high-risk checks.

The method has one idea: **several independent readings, run against the same
concrete scenarios, disagree exactly where the spec is ambiguous.** Most of the
work is making those readings and scenarios different enough to expose the
disagreements — a review fails mainly by never testing the case where the
readings would split, not by misjudging a split it found.

## Workflow

1. **Model and assumptions.** List the actors, inputs, state, outputs, side
   effects, ordering, failures, and invariants that the text states. Then list
   the **assumptions** an implementer must make that the text does not state
   (e.g. limits are cumulative, checks run before side effects, requests arrive
   one at a time, times are in one time zone, invalid input is rejected).
2. **Scenarios.** Write 5–7 concrete probe cases. Together they must include:
   - a value at and just past each stated limit;
   - two clauses that may conflict or interact;
   - an **assumption flip**: a case that only behaves well if one listed
     assumption holds (concurrent requests, a repeat, an out-of-range or empty
     input, an action that fails halfway, a time boundary);
   - if the spec gives examples, a case **outside what the examples cover**
     (examples that all share one shape — one item, one direction, one role —
     silently become the rule an implementer follows).
3. **Blind readings.** Produce three independent readings:
   - **literal**: the narrowest defensible reading;
   - **operational**: what an implementer must decide to ship it;
   - **adversarial**: alternative readings, boundary cases, conflicting clauses.
   If an Agent/Task tool is available, run each reading as a separate subagent
   that receives only the specification, the scenarios, and its one role, and
   declare `Mode: independent`. Otherwise run separate passes and declare
   `Mode: single-context (lower confidence)`; one context playing three roles
   tends to reconcile them and under-reports disagreement. Each reading returns
   a table `Scenario | Outcome | Assumption or decision it forced`, with an
   observable outcome per row, never prose.
4. **Compare, then probe the disagreements.** Merge the tables into
   `Scenario | Literal | Operational | Adversarial`. A scenario whose observable
   outcome differs between readings is a candidate finding. Then add 2–3
   **follow-up scenarios** aimed at what the first round surfaced — the
   "forced assumption" column and each split — and run the same three readings
   on them. The follow-up round usually finds the findings that matter most.
5. **Findings.** Trace each disagreement to the smallest source passage (or
   `Missing contract` for an omission), classify it with the rubric, and merge
   findings only when they are the same unresolved decision with the same
   consequence. Propose the smallest revision that makes behavior deterministic;
   if it needs a product or architecture choice the source cannot make, write
   `Open decision — prerequisite: ...` instead. Turn every definitive Critical
   or High revision into an acceptance test.

## Rules

- Disagreement counts only when observable behavior differs. Different wording
  for the same behavior is not ambiguity.
- Separate stated facts from inferred assumptions. Prefer a few defensible
  findings over many speculative ones.
- Explicitly permitted freedom (`MAY`, stated ranges, implementation-defined
  choices) is not a defect.
- Preserve product intent. Do not choose policy for the author; adjacent
  features the source does not imply go under `Open decisions`.
- Do not claim a rewrite is equivalent without testing it against the same
  scenarios; a rewrite can add its own defect.
- For long documents, review sections separately, then do one pass for
  terminology drift and cross-section contradictions.
- If asked to revise the spec, keep its structure unless restructuring is
  needed to remove the ambiguity.

## Output

Start with:

- **Verdict**: `Implementation-ready`, `Implementable with caveats`, or
  `Not implementable` (rule in the rubric), plus one sentence of reason.
- **Summary**: scenarios with identical outcomes across readings, e.g. `3/9`;
  open findings by severity; `Mode`.

Then the findings, highest severity first:

| Severity | Type | Source / scenarios | Readings disagree on | Proposed contract |
|---|---|---|---|---|

Then, omitting empty sections:

1. **Well-specified**: clauses that are already deterministic and should not
   be touched.
2. **Hidden assumptions**: assumptions any reading needed.
3. **Acceptance tests**: for definitive Critical/High revisions.
4. **Open decisions**: choices the source cannot resolve, with the criteria
   for choosing.

If nothing material is found, say so, keep the verdict and summary, and list
residual risks or missing context.

**Reliability audit (opt-in).** Only when the user asks for repeated runs,
calibration, or a reliability audit, follow
[references/reliability-protocol.md](references/reliability-protocol.md).

## Worked Example

> Users can withdraw money from their account. A withdrawal is rejected if the
> account has insufficient funds. Withdrawals over $10,000 require manager
> approval. The daily withdrawal limit is $5,000.

**Assumptions** an implementer must make: the daily limit is cumulative;
exceeding it rejects; checks run before any side effect; withdrawals are
processed one at a time.

**Scenarios** (round 1):

- S1 `$6,000`, balance `$20,000`, nothing withdrawn today (past the limit)
- S2 `$12,000`, balance `$50,000` (approval clause vs. limit clause)
- S3 `$4,000` after `$4,000` earlier today (flip: limit is cumulative)
- S4 `$11,000`, balance `$4,000` (flip: checks before side effects)
- S5 two `$3,000` at the same instant, balance `$5,000` (flip: one at a time)

| Scenario | Literal | Operational | Adversarial |
|---|---|---|---|
| S1 | Allowed (no reject stated) | Rejected | Allowed |
| S2 | Approval-gated | Rejected (limit wins) | Allowed, no approval |
| S3 | Allowed | Rejected (cumulative) | Allowed (per-withdrawal) |
| S4 | Rejected; approval unclear | Rejected before approval | Approval requested, then rejected |
| S5 | Undefined | One allowed | Both allowed, overdraft |

**Follow-up** (aimed at the S2 split): S6 `$12,000` with manager approval,
nothing withdrawn today → Literal: allowed; Operational: rejected by the
limit; Adversarial: allowed. Confirms the approval clause is unreachable under
a cumulative `$5,000` limit.

- **Verdict:** Not implementable — the core rule for accepting a withdrawal is
  unresolved.
- **Summary:** identical outcomes `0/6`; open findings `C=0, H=2, M=1, L=0`;
  `Mode: independent`

| Severity | Type | Source / scenarios | Readings disagree on | Proposed contract |
|---|---|---|---|---|
| High | Contradiction | "over $10,000 require approval"; "daily limit is $5,000" / S1–S3, S6 | whether the limit rejects, accumulates, or yields to approval | Open decision — prerequisite: whether approval exempts a withdrawal from the daily limit, and whether the limit is cumulative |
| High | Missing contract | Missing contract / S5 | whether both, one, or neither concurrent withdrawal commits | Open decision — prerequisite: the required concurrency invariant and what the storage layer can enforce |
| Medium | Missing contract | "insufficient funds"; "require approval" / S4 | whether a doomed withdrawal creates an approval request | Open decision — prerequisite: whether rejected withdrawals may create approval records |

**Well-specified:** "rejected if insufficient funds" fixes the final outcome of
S4; keep it and only specify whether approval has a side effect before it.
