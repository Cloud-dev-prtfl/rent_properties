// Front-end bootstrap (docs/architecture/03-codebase-structure.md §8.2–8.3).
// Loaded with `defer` after htmx and before the Alpine CSP build.
(function () {
  "use strict";

  // CSP-safe htmx configuration: no eval, no inline scripts, no inline indicator styles.
  htmx.config.allowEval = false;
  htmx.config.allowScriptTags = false;
  htmx.config.includeIndicatorStyles = false;
  // Pages may show personal data (revealed contacts); never snapshot them into localStorage.
  htmx.config.historyCacheSize = 0;
  htmx.config.responseHandling = [
    { code: "204", swap: false },
    { code: "[23]..", swap: true },
    { code: "422", swap: true }, // form validation errors re-render the form partial
    { code: "[45]..", swap: false, error: true },
  ];

  // Poll only while the tab is visible: elements opt in with `data-poll` (register R-43).
  document.body.addEventListener("htmx:beforeRequest", function (event) {
    var source = event.detail.elt;
    if (document.hidden && source && source.hasAttribute("data-poll")) {
      event.preventDefault();
    }
  });

  // Server-driven focus moves after swaps: `HX-Trigger: {"focus": "#id"}`.
  document.body.addEventListener("focus", function (event) {
    if (!event.detail || typeof event.detail.value !== "string") {
      return; // a native focus event, not the server trigger
    }
    var target = document.querySelector(event.detail.value);
    if (target) {
      target.focus();
    }
  });

  // Alpine components are registered here; the CSP build forbids inline expressions.
  document.addEventListener("alpine:init", function () {
    Alpine.data("disclosure", function () {
      return {
        open: false,
        toggle: function () {
          this.open = !this.open;
        },
        close: function () {
          this.open = false;
        },
      };
    });
  });
})();
