## What & why
<!-- One paragraph. Link the story (US-xxx) and requirement IDs (FR-/NFR-). -->

## How it was tested
- [ ] Unit/integration tests added or updated (`make check` passes locally)
- [ ] Manually verified in the compose stack (describe)
- [ ] Accessibility: keyboard-only and axe checked for any UI change

## Checklist (docs/delivery/05-definition-of-done-and-workflow.md)
- [ ] Follows layering rules (services write, selectors read; no cross-app model imports)
- [ ] Migrations are reversible and zero-downtime safe (no schema + data change in one migration)
- [ ] No PII or secrets in logs, audit data, outbox payloads or fixtures
- [ ] User-facing strings wrapped for translation
- [ ] Docs/ADR/reconciliation register updated if a decision or behaviour changed
- [ ] Money path (credits/payments/reveal): second reviewer requested

## Screenshots (UI changes, 360 px and desktop)
