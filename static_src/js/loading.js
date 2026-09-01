/**
 * Site-wide loading feedback (CLAUDE.md §1: response time is the whole game,
 * and every page here is a server round trip — a full navigation, a plain
 * form POST, or an htmx partial swap. Nothing below computes or predicts an
 * outcome; it only shows that a request is in flight.
 *
 * No framework: this project doesn't ship an SPA router, so a top progress
 * bar for ordinary <a> navigation has to be hand-rolled instead of reused
 * from htmx (which only instruments its own requests).
 */
(function () {
  "use strict";

  var bar = document.getElementById("page-loader");

  function startBar() {
    if (!bar) return;
    bar.classList.remove("is-done");
    // Force a reflow so the width transition re-triggers on repeat navigations.
    void bar.offsetWidth;
    bar.classList.add("is-loading");
  }

  function finishBar() {
    if (!bar) return;
    bar.classList.remove("is-loading");
    bar.classList.add("is-done");
  }

  // Full-page navigation: clicking a same-tab, same-origin link. Anchors,
  // downloads, new-tab links and modified clicks are left alone — a
  // progress bar for those would just be a lie.
  document.addEventListener("click", function (event) {
    var link = event.target.closest("a[href]");
    if (!link) return;
    if (
      link.target === "_blank" ||
      link.hasAttribute("download") ||
      link.hasAttribute("hx-get") ||
      link.hasAttribute("hx-post") ||
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return;
    }
    var url;
    try {
      url = new URL(link.href, window.location.href);
    } catch (err) {
      return;
    }
    if (url.origin !== window.location.origin) return;
    if (url.pathname === window.location.pathname && url.hash) return;
    startBar();
  });

  // Plain (non-htmx) form submits — the booking request form and contact
  // form both do a full POST + redirect.
  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (form.hasAttribute("hx-post") || form.hasAttribute("hx-get")) return;
    if (event.defaultPrevented) return;
    startBar();
    setButtonLoading(form);
  });

  window.addEventListener("pageshow", function (event) {
    // bfcache restores (back/forward) don't re-run the request, so clear
    // any bar left mid-animation from before the user navigated away.
    finishBar();
    if (bar) bar.classList.remove("is-loading", "is-done");
  });

  // htmx partial requests: reuse the same bar so step changes in the tour
  // builder and any future hx-post form feel consistent with full page loads.
  document.body.addEventListener("htmx:beforeRequest", function (event) {
    startBar();
    setButtonLoading(event.target.closest("form") || event.target);
  });
  document.body.addEventListener("htmx:afterRequest", function () {
    finishBar();
  });

  /**
   * Puts the form's submit button into a disabled, spinner state so a
   * double-click can't fire the request twice while we're waiting on
   * Telegram/WhatsApp handoff. Restored automatically on the next full
   * page render (POST-redirect-GET) or, for htmx, by afterRequest below.
   */
  function setButtonLoading(scope) {
    if (!scope) return;
    var btn = scope.querySelector('button[type="submit"]');
    if (!btn || btn.disabled) return;
    btn.dataset.originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.classList.add("btn-loading");
    btn.innerHTML =
      '<span class="spinner h-4 w-4" aria-hidden="true"></span>' +
      '<span>' + btn.textContent.trim() + '</span>';
  }

  function resetButtonLoading(scope) {
    if (!scope) return;
    var btn = scope.querySelector('button[type="submit"].btn-loading');
    if (!btn || !btn.dataset.originalHtml) return;
    btn.innerHTML = btn.dataset.originalHtml;
    btn.disabled = false;
    btn.classList.remove("btn-loading");
    delete btn.dataset.originalHtml;
  }

  document.body.addEventListener("htmx:afterRequest", function (event) {
    resetButtonLoading(event.target.closest("form") || event.target);
  });
})();
