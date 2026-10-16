# 🛡️ Behavioral Spec Linter

> **Stop letting AI agents "hallucinate" your business logic. Validate your specs before you write a single line of code.**

`behavioral-spec-linter` is an **agent skill** that acts as a **semantic linter** for software design documents (SDDs), requirement specs, API contracts, user stories, and implementation plans.

Instead of just generating code, it **stress-tests** your requirements with adversarial semantic perturbation to find the hidden ambiguities that lead to AI-generated bugs — and proposes minimal, testable revisions.

---

## ❌ The Problem: "The Guessing Game"

When you give a vague or ambiguous spec to an AI agent (Claude, GPT, Gemini):

1.  **The agent guesses**: it fills the logical gaps with its own assumptions.
2.  **The silent fail**: it writes 500 lines of technically correct but logically wrong code.
3.  **The debug loop**: you spend hours fixing bugs that all trace back to a single ambiguous sentence.

## ✅ The Solution: Behavioral Spec Linter

The skill breaks the cycle by forcing the spec to *prove* it is unambiguous **before** development starts. It treats a specification as a behavioral contract and finds the places where two competent implementers would produce different observable behavior.

### How it works

1.  **Model** — list the behavior the spec states and the assumptions an implementer would have to make.
2.  **Scenarios** — concrete probe cases at the limits, where clauses interact, where an assumption is flipped, and outside what the spec's own examples cover.
3.  **Blind readings** — `literal`, `operational`, and `adversarial` readings each predict the outcome of every scenario.
4.  **Probe the disagreements** — where the readings split, add follow-up scenarios aimed at the split and run them again.
5.  **Report** — a verdict, the findings traced to source clauses, minimal revisions, and acceptance tests. Optional reliability audits add repeated runs and finding-support metrics.

> The blind, multi-agent path is what reliably surfaces divergence. Run without subagents and the skill marks the review `single-context (lower confidence)` rather than pretending the readings were independent.

---

## 📦 What's in here

| Path | Purpose |
|---|---|
| `SKILL.md` | The skill: the full review procedure and output contract. |
| `references/review-rubric.md` | Finding types, severity, verdict, evidence standard, high-risk checks, revision quality. |
| `references/reliability-protocol.md` | Optional repeated-run finding matching and support-tier protocol. |
| `scripts/aggregate_reliability.py` | Deterministic aggregation for an optional reliability audit. |

---

## 🚀 Usage

Invoke the skill on any spec, design doc, or under-specified request:

```
Use behavioral-spec-linter to stress-test this specification and propose precise revisions.
```

You get back a structured review:

- a **verdict** with a one-line reason, and a summary: how many scenarios
  every reading agreed on, open findings by severity, and the review mode;
- a findings table: severity, type, source clause and scenarios, what the
  readings disagree on, and the proposed contract;
- **Well-specified** clauses that are already deterministic and should not be touched;
- **hidden assumptions**, **acceptance tests**, and **open decisions**
  (product or architecture choices the source cannot resolve).

A worked end-to-end example is included at the bottom of [`SKILL.md`](SKILL.md).
Repeated runs are opt-in; an ordinary review is one three-reading pass plus a follow-up round on the disagreements.

---

## 🎯 Design principle

The linter optimizes for **low false positives**. It does not nag about every conceivable missing feature, audit log, or best practice — it reports a problem only when two readings produce materially different behavior, or an omission forces an implementer to guess. Deliberate freedom (`MAY`, explicit ranges, implementation-defined choices) is not treated as a defect.
