/**
 * Site-wide scroll-reveal animation.
 *
 * Auto-applies the `.reveal` treatment to the section-level building blocks
 * every template already uses (`.section-title`, `.card`, `[data-reveal]`)
 * instead of requiring each template to opt in by hand. Runs once on
 * DOMContentLoaded; anything added later (HTMX swaps, Alpine-rendered
 * partials) can opt in explicitly with `data-reveal`.
 *
 * No-JS / reduced-motion / crawler safety: `.reveal`'s hidden starting state
 * (input.css) is scoped under `.motion-ready`, a class this script is the
 * only thing that adds to <html>. If this file fails to load, or
 * prefers-reduced-motion is set, content simply renders at its final state —
 * it is never permanently invisible.
 */
(function () {
  "use strict";

  var prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  function markRevealTargets(root) {
    var selector = [
      ".section-title",
      ".section-lead",
      ".card",
      "[data-reveal]",
    ].join(", ");
    var nodes = root.querySelectorAll(selector);
    nodes.forEach(function (node) {
      if (node.closest("header, .reveal, [x-cloak]")) return;
      node.classList.add("reveal");
    });

    // Group siblings that reveal together (e.g. destination/package cards)
    // so CSS can stagger them via .reveal-group > .reveal:nth-child(n).
    // :has() is unsupported in a few older browsers — degrade to "no
    // stagger" there rather than breaking the whole script.
    try {
      var grids = root.querySelectorAll(
        ".grid:has(> .card), .grid:has(> [data-reveal])"
      );
      grids.forEach(function (grid) {
        grid.classList.add("reveal-group");
      });
    } catch (err) {
      /* :has() unsupported — cards still reveal individually. */
    }
  }

  function init() {
    if (prefersReducedMotion || !("IntersectionObserver" in window)) return;

    markRevealTargets(document);
    document.documentElement.classList.add("motion-ready");

    var revealed = new WeakSet();
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting || revealed.has(entry.target)) return;
          entry.target.classList.add("is-revealed");
          revealed.add(entry.target);
          observer.unobserve(entry.target);
        });
      },
      { root: null, rootMargin: "0px 0px -8% 0px", threshold: 0.1 }
    );

    document.querySelectorAll(".reveal").forEach(function (el) {
      observer.observe(el);
    });

    // HTMX partials (e.g. the tour builder / quote summary) render new
    // content after the initial pass — pick those up too.
    document.body.addEventListener("htmx:afterSwap", function (evt) {
      markRevealTargets(evt.target);
      evt.target.querySelectorAll(".reveal:not(.is-revealed)").forEach(
        function (el) {
          observer.observe(el);
        }
      );
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
