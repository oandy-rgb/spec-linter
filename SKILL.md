---
name: behavioral-spec-linter
description: Stress-test software requirements, product specifications, SDDs, API contracts, user stories, acceptance criteria, implementation plans, policies, and other rule-like texts for ambiguity, contradictions, missing cases, and hidden assumptions. Use when asked to review, lint, clarify, harden, or validate a specification, or when an underspecified request would make semantic mistakes costly.
---

# Behavioral Spec Linter

Report the places where two competent people applying the text would produce
different observable behavior, and propose minimal, testable revisions.

## Review

1. **Read word by word.** Articles (a/the), modals (may/must/is), quantifiers
   (all/any/only/each/once), and/or and list joins, negation scope, time words
   (before/after/until/prompt), degree words that gate a duty (seriously,
   significant), and whose/which references each change behavior. Then pair
   clauses that share an actor, object, or point in time and look for a case
   that satisfies one and violates the other.
2. **For each candidate**, state the competing readings and one concrete case
   where their outcomes differ. No case, no finding.
3. **Long texts** (roughly 800+ words or many clauses): with an Agent/Task tool,
   give each section of a few clauses to its own subagent, which reads the
   whole text but reports only its section. Then one pass checks pairs across
   sections, merges duplicates, and applies the rules below. Without subagents,
   review section by section, then across sections.
4. **Judge** every candidate with the rules, then write the output.

## Rules

- Only **observable** differences count; other wording for the same behavior is
  not ambiguity. Drop a reading that ignores explicit text, a defined term, or
  plausible domain behavior.
- **Permitted freedom** (`MAY`, explicit ranges, declared judgment standards
  such as "reasonable") is not a defect unless it contradicts another clause or
  decides whether a duty applies at all. A qualifier that leaves a case with no
  rule ("integral deception", "seriously harmed") is a `Missing contract`.
- A `Missing contract` is a choice an implementer is forced to make. Good
  practice the text does not imply goes under Open decisions, if anywhere.
- An outcome the text leaves undefined is a finding even if every reading
  agrees on it (a score with no band, an input with no rule).
- When unsure whether a drop rule applies, keep the candidate as Low or as an
  Open decision; do not silently drop it.

**Types** (first that applies): Contradiction · Undefined term · Missing
contract · Ambiguity · Unverifiable requirement · Scope leak · Hidden assumption.

**Severity:** Critical = security or data exposure, data loss, regulatory
breach, irreversible wrong state · High = core business behavior,
authorization, billing, data writes, compatibility · Medium = recoverability,
one limited flow · Low = testability, minor edges. **Verdict:** no findings →
`Implementation-ready`; any Critical, or High on the main state transition →
`Not implementable`; otherwise `Implementable with caveats`.

**Revisions** name the actor and trigger, use the text's own terms, set
boundaries and failure behavior, and can be tested. If a fix needs a product
or policy choice the text cannot make, write `Open decision` and ask it as a
question with the case that separates the readings.

## Output

Verdict with a one-sentence reason; a findings table, most severe first, at
most about 15 rows (the rest listed briefly after it):

| Severity | Type | Source / case | Readings disagree on | Proposed contract |
|---|---|---|---|---|

Then, omitting empty sections: Well-specified clauses not to touch, Hidden
assumptions, Acceptance tests, Open decisions.

## Verify (optional, rule-like texts)

To check a revision, have fresh subagents that did not write it answer the
same cases from the revised text. For numeric or state rules, each writes
`<name>.py` with `INPUTS = {name: [values]}` and `outcome(case) -> str` using
shared input names and label format; `python3 scripts/diff_readings.py <dir>`
lists the cases where they still disagree. This is bounded testing, not proof.
