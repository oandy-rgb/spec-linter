# Seeded-ambiguity eval

Use this to check whether a review procedure finds more problems than a plain
request. Rerun it when the model or the procedure changes.

## Text

`participant-pool-policy.md`: a fictional 1,667-word university policy written
by a subagent for this eval, so no model can have memorised it. Do not use
famous public texts. A reviewer given the APA Ethics Code with seeded edits
compared it with the official wording from memory.

## Seeds

Apply these edits to a copy of the text. Each changes only existing words,
because seeds that add whole sentences are caught every time and measure
nothing. A review detects a seed when it names the issue the edit creates.

| # | Clause | Original → seeded | Issue created |
|---|---|---|---|
| F1 | 4(e) | 50% of a course's credit requirement → of the credit requirement | cap per course or over the student's total |
| F2 | 5(b) | up to 12 hours before → up to 24 hours before | cancellations 12–24 h ahead are neither free nor late |
| F3 | 6(c)(ii) | delete "for the course with the largest remaining requirement" | which course's requirement increases |
| F4 | 6(d) | within 5 business days → within 5 days | calendar vs business days |
| F5 | 8(c) | shall automatically grant → may automatically grant | automatic credit optional vs guaranteed |
| F6 | 6(a) | start time, or (iii) → start time, and (iii) | no-show needs all three conditions |
| F7 | 10(a) | for the same session → for the same study | credit for one session and pay for another |
| F8 | 3(c) | on the date of a session → on the date of sign-up | age date differs from 3(b) |

## Natural issues in the original (secondary metric)

M1 9(c) delayed debriefing vs 11(d) 14-day withdrawal window · M2 11(e)
anonymous data vs 9(d) notice · M3 14(b) automatic assignment vs 4(e) cap ·
M4 6(c)(iii) suspension and booked sessions · M5 8(c) automatic credit for an
unrecorded no-show · M6 4(e) what counts toward or exceeds the cap · M7 5(d)
online studies and no-shows · M8 15(a) vs 15(d) dispute windows · M9 11(b)
full credit on immediate withdrawal · M10 3(d) "cannot participate" · M11 12(b)
which course prescreen credit goes to · M12 7(d) instructor grading vs
13(a)(iv) totals only.

Many natural issues are vague judgment terms or gaps that a low-false-positive
procedure may drop on purpose, so weigh this metric with that in mind.

## Protocol

Give each reviewer only the seeded text and the instructions under test, with
no web access. The plain arm gets: "Review this specification for ambiguities,
contradictions, missing cases and hidden assumptions, and propose precise
revisions." Run each arm at least three times, and score every run against the
keys above before comparing.

## Results (2026-10-23, Claude Opus 5.5)

| Arm | Seeds | Natural | Tokens per run |
|---|---|---|---|
| Plain request | 7, 7, 7 | 9.5, 12, 9.5 | ~50k |
| `SKILL.md` (version 2) | 7, 7.5, 7 | 10, 12, 11 | ~80k for the lead agent, plus 3–6 subagents |

All six runs missed F7. See the README for the earlier tests.
