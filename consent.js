/* DNA Pro Plans — optional analytics, off until the visitor accepts.
   Loaded synchronously in <head>. Google's tag is NOT requested before consent ("basic" consent mode).
   Never pass names, emails, free text or file names to track(): only fixed labels. */
(function () {
  'use strict';
  var GA_ID = 'G-HCBH87S9EE';
  var KEY = 'dna-analytics-consent';   // "granted" | "denied"
  var LEAD_KEY = 'dna-lead-at';        // time of the last counted lead, to avoid counting one person twice
  var LEAD_WINDOW = 30 * 24 * 60 * 60 * 1000;
  var loaded = false, banner = null;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;
  gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied' });

  function read(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function write(k, v) { try { window.localStorage.setItem(k, v); } catch (e) {} }
  // Inside a frame (the thank-you page shown in the inquiry form) nothing is measured: the page around it reports.
  var framed = window.self !== window.top;
  function granted() { return !framed && read(KEY) === 'granted'; }

  // Official Google tag for this stream, injected once and only after consent.
  function loadTag() {
    if (loaded) return;
    loaded = true;
    gtag('consent', 'update', { analytics_storage: 'granted' });
    gtag('js', new Date());
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtm.js?id=' + GA_ID;
    document.head.appendChild(s);
  }

  function clearCookies() {
    document.cookie.split(';').forEach(function (c) {
      var name = c.split('=')[0].trim();
      if (name === '_ga' || name.indexOf('_ga_') === 0 || name === '_gid') {
        var host = location.hostname, base = host.replace(/^www\./, '');
        [host, '.' + host, '.' + base].forEach(function (d) {
          document.cookie = name + '=; Max-Age=0; path=/; domain=' + d;
        });
        document.cookie = name + '=; Max-Age=0; path=/';
      }
    });
  }

  function choose(value) {
    var was = granted();
    write(KEY, value);
    if (value === 'granted') loadTag();
    else {
      gtag('consent', 'update', { analytics_storage: 'denied' });
      clearCookies();
    }
    hide();
    // The tag cannot be unloaded from a page that already ran it, so start clean after a withdrawal.
    if (was && value !== 'granted' && loaded) location.reload();
  }

  function hide() { if (banner) { banner.hidden = true; } }

  function show() {
    if (!banner) {
      banner = document.createElement('section');
      banner.className = 'consent';
      banner.setAttribute('role', 'dialog');
      banner.setAttribute('aria-label', 'Analytics cookies');
      banner.innerHTML =
        '<h2 class="consent__title">Optional analytics</h2>' +
        '<p class="consent__text">We would like to use Google Analytics to see which pages are useful. It is off unless you accept. <a href="/privacy#cookies">How it works</a></p>' +
        '<p class="consent__state" aria-live="polite"></p>' +
        '<div class="consent__actions">' +
        '<button type="button" class="btn btn--ghost" data-consent="denied">Reject</button>' +
        '<button type="button" class="btn btn--ghost" data-consent="granted">Accept analytics</button>' +
        '</div>';
      banner.addEventListener('click', function (e) {
        var b = e.target.closest('[data-consent]');
        if (b) choose(b.getAttribute('data-consent'));
      });
      document.body.appendChild(banner);
    }
    var v = read(KEY);
    banner.querySelector('.consent__state').textContent =
      v === 'granted' ? 'Current choice: analytics accepted.' : v === 'denied' ? 'Current choice: analytics rejected.' : '';
    banner.hidden = false;
  }

  function track(name, params) {
    if (!granted()) return false;
    loadTag();
    gtag('event', name, params || {});
    return true;
  }

  // One new lead per person: a form inquiry and a booking by the same visitor count once.
  function lead(source) {
    if (!granted()) return false;
    var last = parseInt(read(LEAD_KEY) || '0', 10);
    if (last && Date.now() - last < LEAD_WINDOW) return false;
    write(LEAD_KEY, String(Date.now()));
    return track('generate_lead', { lead_source: source });
  }

  window.dnaConsent = { granted: granted, open: show, track: track, lead: lead };

  if (granted()) loadTag();

  document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('click', function (e) {
      if (e.target.closest('[data-consent-open]')) { e.preventDefault(); show(); }
    });
    // Ask once; inside a frame (the thank-you page in the inquiry form) never show the banner.
    if (read(KEY) === null && !framed) show();
  });
})();
