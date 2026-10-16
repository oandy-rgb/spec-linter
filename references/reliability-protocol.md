# Reliability Protocol

Use this protocol after blind interpretations produce candidate findings. It
separates semantic adjudication from deterministic aggregation.

## Review Units

A review unit is one interpretation role in one independent run. A full
reliability review uses at least two runs of the literal, operational, and
adversarial roles, for at least six units. A brief review may use one run, but
must report selection frequency as unavailable across runs.

Keep the specification, scope, external assumptions, and scenario set fixed
across runs. Permute scenario order and role launch order between
runs when practical; do not change scenario content.

## Canonical Finding Fields

Each candidate finding must provide:

```text
actor
trigger
unresolved_decision
observable_consequence
source_clauses
scenario_ids
type
severity_vector
```

The identity of a finding is `Actor | Trigger | Unresolved decision |
Observable consequence`; normalize these four fields before comparing.

The severity vector is `Impact / Reach / Reversibility / Exposure / Evidence`,
using only these values:

| Field | Values | Rule |
|---|---|---|
| Impact | `catastrophic`, `major`, `moderate`, `minor` | Maps to the rubric's severity: Critical, High, Medium, Low. |
| Reach | `core`, `boundary`, `edge` | `core` changes the primary state transition or an invariant (the rubric's "core"); `boundary` changes caller-visible exceptional behavior; `edge` is an uncommon, limited path. |
| Reversibility | `irreversible`, `recoverable`, `transient` | Whether normal corrective action restores the state, an explicit correction is needed, or the effect disappears by itself. |
| Exposure | `external`, `internal` | `external` affects a user, caller, persisted contract, or cross-component interface. |
| Evidence | `explicit`, `inferred` | `explicit` is shown directly by conflicting or missing clauses; `inferred` needs stated domain or architecture facts. |

When merging, keep the highest value any member demonstrated
(`catastrophic > major > moderate > minor`, `core > boundary > edge`,
`irreversible > recoverable > transient`, `external > internal`,
`explicit > inferred`), and choose the type by the order of the rubric's type
table.

## Contradiction-Aware Matching

Compare candidate findings pairwise using their four identity fields. Assign
exactly one relation:

- `same`: same required decision and same observable consequence;
- `related`: overlapping source or repair, but a different decision or
  consequence;
- `contradictory`: merging them would hide incompatible claims about the
  decision or consequence;
- `different`: no material identity overlap.

Merge only `same`. Similar wording, shared sources, shared revisions, or high
embedding similarity are insufficient. Before merging, run a counterfactual
check: if resolving one candidate could leave the other unresolved, they are
not the same finding.

The orchestrator assigns a stable `cluster_id` after adjudication. Preserve all
member identities, sources, and scenarios in the cluster audit trail.

## Aggregation Artifact

The deterministic aggregator accepts JSON with:

```json
{
  "review_units": [{"id": "r1-literal", "run": "r1"}],
  "scenario_results": [
    {"unit": "r1-literal", "scenario": "S1", "outcome": "rejected"}
  ],
  "findings": [
    {
      "unit": "r1-literal",
      "cluster_id": "F1",
      "type": "Missing contract",
      "vector": {
        "impact": "major",
        "reach": "core",
        "reversibility": "recoverable",
        "exposure": "external",
        "evidence": "explicit"
      }
    }
  ]
}
```

The `outcome` field must be a canonical observable label, not free-form prose.
Each review unit may support a cluster at most once.

Run:

```bash
python3 scripts/aggregate_reliability.py artifact.json
```

## Support Tiers

For each cluster:

```text
unit_support = distinct supporting review units / total review units
run_support = distinct supporting runs / total runs
```

Until calibrated on a human-adjudicated corpus, use:

- `Core`: `unit_support >= 0.80` and the cluster appears in every run;
- `Supported`: `unit_support >= 0.50`;
- `Contested`: `unit_support < 0.50`.

These thresholds are provisional engineering defaults. Report them as
uncalibrated. Core and Supported findings drive the verdict; Contested findings
are preserved as disagreement and do not drive the verdict.

## Agreement

For each cluster, report:

- type agreement among supporting units;
- agreement for each severity-vector field among supporting units;
- the modal type and vector values;
- unit and run support.

For scenarios, canonicalize each outcome to observable behavior before
aggregation. Compute convergence per scenario-run, not by comparing prose.
Scenario convergence is secondary evidence; finding support is the primary
reliability signal.

Do not report Cohen's kappa, Fleiss' kappa, or Krippendorff's alpha unless the
sample contains enough independently labeled items and the calculation method
is declared. Raw agreement on a handful of findings is more honest than an
unstable chance-corrected statistic.

## Verdict

Apply the verdict table in `review-rubric.md` to Core and Supported findings
only, reading "core" from `Reach: core`. Always list Contested findings
separately.

## Calibration

A review remains `uncalibrated` until evaluated against a human-adjudicated
corpus containing at least these pair labels:

- same finding;
- related but separate;
- contradictory;
- unsupported or speculative.

Track matching precision/recall, support-tier precision, type agreement, and
severity-vector agreement. Do not convert these metrics into a 0-100 stability
score without an explicit calibration model.
