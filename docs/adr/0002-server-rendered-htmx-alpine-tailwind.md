# ADR-0002: Server-rendered UI with HTMX, Alpine.js and Tailwind (no SPA)

Decides how the user interface is built: Django templates rendered on the server, progressively enhanced with HTMX 2 and Alpine.js 3 (CSP build), styled with Tailwind CSS 4. There is no single-page application in the MVP.

Status: Draft v0.1 (2026-10-21)

| | |
|---|---|
| Decision status | Proposed |
| Date | 2026-10-21 |
| Deciders | Tech Lead (owner); PO acknowledges |
| Consulted | UX, Security, QA (accessibility) |
| Supersedes / superseded by | — |
| Requirements | SRS §4.1 (multi-step form, client-side validation), §4.4 (real-time metrics), §5.1, §5.4, §5.6 (Show Number states, toasts), §7.1 (dropdown "renders immediately"), §11.1–11.2 (credit visibility, mobile-first, fluid navigation), §12 (WCAG 2.1 AA); NFR-UX-01..07, NFR-A11Y-01, NFR-PERF-01 |
| Gap / open question | Client diagram: "Django Template Rendering", "Periodic HTTP Polling" |
| Related | [03 §8 Templates, HTMX, Alpine and CSP](../architecture/03-codebase-structure.md#8-templates-partials-htmx-alpine-and-csp-conventions) · [02 T4](../architecture/02-tech-stack.md#2-technology-choices-by-layer) · [Engineering standards §12](../delivery/03-engineering-standards.md#12-templates-htmx-alpine-and-tailwind-conventions) · [Security §6.3](../quality/01-security-and-compliance.md#63-http-security-headers-and-browser-controls) |

## Context and problem statement

The product is a public marketplace: most traffic is anonymous search and listing pages, which must be indexable by search engines and fast on mid-range phones (SRS §11.2 mobile-first). Interactive parts are modest: a multi-step listing wizard with drafts, filters that update results, a Show Number button whose state depends on login and balance, toasts, a profile dropdown with the live balance, photo upload with reordering and cropping, and dashboards that refresh metrics. The client diagram shows Django template rendering and "Periodic HTTP Polling", not a JavaScript client. The team is small and writes Python.

**Question:** should the UI be a server-rendered application with progressive enhancement, or a JavaScript single-page application talking to a JSON API?

## Decision drivers

1. **SEO and first-load performance** for public listing and search pages (organic acquisition; mobile-first).
2. **Accessibility** (WCAG 2.1 AA): semantic HTML, keyboard support, predictable focus.
3. **Security:** strict Content Security Policy; no tokens in browser storage; authorisation on the server for every fragment, including contact details that must never reach the DOM before payment (known issue #20).
4. **Team efficiency:** one language, one codebase, one deployable ([ADR-0001](0001-django-modular-monolith.md)).
5. **Interactivity good enough** for the SRS: partial updates, polling, toasts, dropdowns, upload progress.
6. **Small JavaScript budget** (≤ 50 KB gzipped on public pages; [01 §1.1](../architecture/01-system-architecture.md#11-measurable-quality-targets)).

## Considered options

1. **Django templates + HTMX 2 + Alpine.js 3 (CSP build) + Tailwind CSS 4** (progressive enhancement).
2. **React / Next.js** (SSR or SPA) with a DRF JSON API.
3. **Vue or Svelte islands** built with Vite, mounted into Django templates.
4. **Hotwire (Turbo + Stimulus)** or **Unpoly** instead of HTMX + Alpine.
5. **Plain Django templates** with no enhancement library.

## Decision outcome

**Chosen option 1**, because it delivers fully rendered, indexable, accessible HTML with a small script budget, keeps all authorisation and data shaping on the server, and needs no second codebase, while HTMX and Alpine cover every interaction the SRS requires.

Decision details (conventions in [03 §8](../architecture/03-codebase-structure.md#8-templates-partials-htmx-alpine-and-csp-conventions)):

| Topic | Rule |
|---|---|
| Progressive enhancement | Every page and action works as a normal link or form POST without JavaScript. HTMX swaps fragments when available; the same view serves both (Post/Redirect/Get fallback) |
| Fragments | `django-template-partials` (`{% partialdef %}`), so full page and HTMX response share markup. The same syntax is built into Django 6.0, which eases the 6.2 LTS upgrade |
| Alpine.js | **CSP build** only; components registered with `Alpine.data()`; local UI state only (dropdowns, dialogs, toasts, wizard helpers). Server data never lives in Alpine stores, except the toast queue |
| HTMX configuration | `allowEval=false`, `allowScriptTags=false`, `includeIndicatorStyles=false`; CSRF token through `hx-headers`; no trigger filters that need `eval` |
| Polling ("Periodic HTTP Polling") | Used where the server state changes without user action: payment status after redirect (every 2 s, up to 60 s), image processing tiles, My Properties metrics. The **header balance** updates through `HX-Trigger: credits-changed` after the user's own actions and on tab focus, not by constant polling ([NFR §7.3](../quality/02-nfr-performance-and-scalability.md#73-polling-cost-balance-badge)) |
| Styling | Tailwind CSS 4 via the pinned standalone CLI (no Node at runtime); design tokens in `@theme`; logical properties for future RTL |
| Rich widgets | Targeted, vendored libraries only where needed: SortableJS (photo order, with button alternatives), Cropper.js (in-browser crop). No framework runtime |
| No SPA, no JSON API in MVP | A versioned DRF API (`/api/v1/`) is post-MVP for a mobile app and calls the same services and selectors |

### Consequences

- **Positive:**
  - Public pages are complete HTML on first response: good for SEO, Core Web Vitals and low-end devices.
  - Authorisation and data minimisation happen in one place. Contact details are rendered only in the server-side `revealed` branch, so they can't leak through a JSON payload or a hidden DOM element.
  - A strict CSP (`script-src 'self'` with nonce capability, no `unsafe-eval`) is achievable ([03 §8.5](../architecture/03-codebase-structure.md#85-content-security-policy)).
  - One language and one test stack (pytest + Playwright); no API versioning burden in the MVP.
- **Negative:**
  - Highly dynamic client features (an interactive map with clustering, offline mode) are harder. *Mitigation:* the map is a static image or click-to-load in the MVP; a JS island can be added later for a specific feature.
  - The Alpine CSP build forbids inline expressions, so components need registered methods. *Mitigation:* component library in `static/src/js/components/` from M0.
  - A native mobile app needs an API later. *Mitigation:* services and selectors are UI-agnostic, so a DRF layer is additive.
  - Tailwind v4 sets a browser floor (Safari 16.4+, Chrome 111+, Firefox 128+). *Mitigation:* if launch markets need older browsers, an M0 ADR switches to Tailwind v3.4 ([engineering standards §12.4](../delivery/03-engineering-standards.md#124-tailwind-css-rules)).
- **Neutral:** each HTMX interaction is a server round trip; the latency budgets for partials (p95 ≤ 400 ms) and polling endpoints (≤ 100 ms) are set in [NFR §3](../quality/02-nfr-performance-and-scalability.md#3-latency-budgets-per-endpoint-class).

### Confirmation

- CI JavaScript budget check (≤ 50 KB gzipped on public pages) and Lighthouse CI budgets on key pages.
- axe-core checks in Playwright: zero serious or critical violations; manual audit in M7 (US-704).
- A Playwright "no-JavaScript" smoke run of search, listing detail and login (progressive enhancement holds).
- CSP enforced on staging and prod with violation reports monitored; any violation in E2E fails the test.
- Contact-leak regression test (contact strings never in HTML or JSON before a reveal).

## Pros and cons of the options

### 1. Django templates + HTMX + Alpine + Tailwind (chosen)

- Good, because HTML is complete on the first response.
- Good, because the server stays the single source of truth for state and permissions.
- Good, because the total script payload is small and mostly cacheable.
- Bad, because complex client-side state is awkward; it must be kept local and small.

### 2. React / Next.js with a DRF API

- Good, because of the rich component ecosystem and a natural path to mobile through a shared API.
- Bad, because it doubles the codebase (Python API + TypeScript client) and needs API versioning from day one.
- Bad, because SEO requires SSR (Next.js server in Node), adding a second runtime to deploy and secure.
- Bad, because larger JS payloads work against the mobile-first goal, and session/token handling moves into the browser.

### 3. Vue/Svelte islands

- Good, because islands give rich widgets where needed.
- Bad, because it introduces a Node build toolchain and a second component model for a handful of widgets that vendored libraries already cover.

### 4. Hotwire or Unpoly

- Good, because both follow the same server-rendered philosophy and are viable.
- Bad, because the Django ecosystem around HTMX (django-htmx, template partials, community patterns) is larger, and the team baseline names HTMX.

### 5. Plain templates

- Good, because it is the simplest option.
- Bad, because full-page reloads for filters, Show Number and toasts fall short of the SRS interaction recommendations (§11.1–11.2).

## Deviations from the SRS

None. The SRS does not prescribe a front-end technology. "Robust client-side validation" (§4.1) is met with HTML5 constraint validation plus small Alpine helpers, with the server always re-validating.

## Follow-ups

| # | Action | Owner | Milestone |
|---|---|---|---|
| 1 | Vendor HTMX, Alpine CSP build, SortableJS and Cropper.js with a hash manifest | Front-end lead | M0 (US-008) |
| 2 | JS budget check and Lighthouse CI in the pipeline | QA | M0 (US-013) |
| 3 | Decide the Tailwind v4 browser floor against launch-market analytics | UX + Tech Lead | M0 |

## More information

- Revisit if a native-app-like client experience becomes a product requirement, or if a specific feature (for example map-based search with clustering, US-907) needs a JS island.
