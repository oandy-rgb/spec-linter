# Behavioral Spec Linter Review Rubric

Use this reference to classify findings consistently.

## Finding Types

Choose the first type that applies.

| Type | Definition | Typical signal |
|---|---|---|
| Contradiction | Two clauses require incompatible behavior, or one makes another unreachable. | one section permits what another forbids; a threshold no input can reach |
| Undefined term | The outcome turns on a noun, state, threshold, or unit with no stable definition. | "recent", "large", "owner", "day" |
| Missing contract | Implementation requires a decision the document never addresses. | no timeout, default, tie-breaker, or failure behavior |
| Ambiguity | One passage supports more than one outcome. | "active users", "after validation", unclear pronoun |
| Unverifiable requirement | Compliance has no objective test. | "fast", "user-friendly", "secure" without criteria |
| Scope leak | A requirement affects actors or data outside its stated scope. | tenant boundary or inherited permission unspecified |
| Hidden assumption | An unstated fact selects the outcome. | one currency, one time zone, synchronous processing |

## Severity

| Severity | When |
|---|---|
| Critical | Security exposure, data loss, regulatory breach, or irreversible incorrect state. |
| High | Material business behavior, API compatibility, billing, authorization, or data writes. |
| Medium | Recoverability, operational behavior, or one limited user flow. |
| Low | Testability or low-impact edge behavior. |

Base severity on a consequence the scenarios demonstrate, not on a speculative
one. A finding is **core** when it changes the primary state transition or an
invariant of the feature under review.

## Verdict

| Condition | Verdict |
|---|---|
| No open findings | `Implementation-ready` |
| Any Critical finding, or any core High finding | `Not implementable` |
| Otherwise | `Implementable with caveats` |

## Evidence Standard

A finding must show:

1. the exact source passage, or `Missing contract`;
2. at least two plausible behaviors, each produced by some reading;
3. an observable consequence;
4. a revision that closes the decision without adding unrelated policy.

Drop or downgrade a finding when one reading requires ignoring explicit text,
violating a defined term, or implausible domain behavior.

Report a `Missing contract` only if an implementer must make the choice to
deliver the stated feature **and** two plausible choices change observable
behavior. Otherwise it is an `Open decision` or nothing. Do not treat every
conceivable feature, control, or good practice (audit logs, fees,
notifications, retention, approval flows) as missing.

## Deliberate Freedom

Multiple outcomes are not ambiguity when the spec permits them: `MAY`
behavior, explicit ranges ("at most N", "between X and Y"),
implementation-defined choices, output declared unordered. Report such freedom
only when it breaks interoperability, conflicts with another clause, or makes
a stated acceptance criterion impossible — and then as a tradeoff, not
noncompliance.

## High-Risk Checks

Use these as a source of assumptions to flip when writing scenarios. Apply the
relevant ones, not all of them mechanically.

- authorization before or after resource lookup; information leaked through
  different errors;
- transaction boundaries and partial writes; what happens when a step fails
  halfway;
- duplicate requests, retries, idempotency keys;
- concurrent updates, locking, conflict resolution;
- null, empty, omitted, malformed, duplicate, and out-of-range inputs;
- limits: per-item vs cumulative, inclusive vs exclusive, reset boundary;
- ordering of checks and side effects; pagination and sort tie-breakers;
- clock source, time zone, daylight saving, inclusive time boundaries;
- rounding, currency, units, overflow, precision;
- deletion, retention, restoration, cascading effects;
- event ordering, delivery guarantees, deduplication, replay;
- versioning, backward compatibility, migration rollback.

## Revision Quality

A strong proposed contract names the actor and trigger, uses terms the
document already defines, fixes ordering where it changes results, defines
defaults and boundary values, states failure behavior and side effects, and can
be turned directly into a test.

Before proposing one, check that it does not contradict another requirement,
exceed what the stated platform can do (distributed atomicity, exact timing,
stronger isolation, permanent retention), introduce an undefined term, or add a
feature instead of clarifying behavior. If any of these cannot be answered from
the available context, write `Open decision — prerequisite: ...`, list the
alternatives under `Open decisions` with criteria for choosing, and do not
write acceptance tests for an unselected alternative.

Weak: "The request should fail when the token is invalid."

Strong: "The API MUST validate the bearer token before querying the requested
resource. For an absent, expired, or invalid token, it MUST return HTTP 401 with
error code `invalid_token` and MUST NOT reveal whether the resource exists."
