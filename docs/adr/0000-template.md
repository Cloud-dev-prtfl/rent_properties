# ADR-0000: ADR template (MADR)

The template for every Architecture Decision Record in `docs/adr/`. Copy it to `NNNN-short-kebab-title.md`, fill every section, and add the new ADR to the index in [01 §19](../architecture/01-system-architecture.md#19-adr-index) in the same PR.

Status: Draft v0.1 (2026-10-21)

---

## How to use this template

| Rule | Detail |
|---|---|
| When an ADR is required | A change that chooses or replaces a technology, library with runtime impact, cloud service or provider; changes module boundaries, data ownership, transaction or consistency strategy; **deviates from the SRS or the baseline**; changes a security control, retention rule or PCI/PII scope; or is expensive to reverse ([engineering standards §20.2](../delivery/03-engineering-standards.md#202-when-an-adr-is-required)) |
| Numbering | Four digits, sequential, never reused. The file name is `NNNN-short-kebab-title.md` |
| Lifecycle | `Proposed` → `Accepted` / `Rejected`; later `Superseded by ADR-NNNN` or `Deprecated` ([§20.3](../delivery/03-engineering-standards.md#203-adr-lifecycle)). Accepted ADRs are never rewritten; a change of mind is a new ADR that supersedes the old one, with links both ways |
| Approval | Tech Lead approves. The PO also acknowledges any ADR that deviates from the SRS |
| Length | Long enough to be understood in two years by someone who wasn't there; one to three pages is typical |
| Evidence | Spikes (for example US-012) attach numbers, graphs or report links to the ADR |
| Language | Plain, precise, no marketing. Mark SRS deviations with `**Deviation from SRS:**` and assumptions with `**Assumption:**` |

The two status lines are different things. `Status: Draft v0.1 (date)` is the document's editorial status, used by every file in `docs/`. **Decision status** in the table is the ADR lifecycle state.

---

## Template (copy from here)

```markdown
# ADR-NNNN: <Decision title, as a short noun phrase>

<One or two lines: what this ADR decides and why it matters.>

Status: Draft v0.1 (YYYY-MM-DD)

| | |
|---|---|
| Decision status | Proposed |
| Date | YYYY-MM-DD |
| Deciders | Tech Lead (owner); PO acknowledges SRS deviations |
| Consulted | <roles: security, platform, QA, product> |
| Supersedes / superseded by | — |
| Requirements | <SRS §x.y; FR-/NFR- IDs> |
| Gap / open question | <GAP-nn, OQ-nn, A-n> |
| Related | <links to architecture/design docs and other ADRs> |

## Context and problem statement

<The forces at play: SRS text, constraints, scale, team, timeline. End with the question being decided.>

## Decision drivers

1. <Driver, with its source (SRS §, NFR ID, risk ID)>
2. ...

## Considered options

1. <Option A>
2. <Option B>
3. <Option C>

## Decision outcome

**Chosen option: <Option X>**, because <one-paragraph justification tied to the drivers>.

<Decision details: the rules, settings, interfaces or invariants that implementers must follow.>

### Consequences

- **Positive:** ...
- **Negative:** ... (and how each is mitigated)
- **Neutral / follow-on:** ...

### Confirmation

<How we will know the decision is implemented and still holds: CI checks, tests, metrics, load tests, reviews, with milestone.>

## Pros and cons of the options

### <Option A>

- Good, because ...
- Bad, because ...

### <Option B>

- ...

## Deviations from the SRS

<"None", or each deviation as **Deviation from SRS:** with the SRS text, what we do instead and why.>

## Follow-ups

| # | Action | Owner | Milestone |
|---|---|---|---|
| 1 | ... | ... | ... |

## More information

<Links: design documents, spike reports, vendor documentation, related ADRs. Conditions under which this decision should be revisited.>
```
