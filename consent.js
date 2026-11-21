/* DNA Pro Plans — analytics choice.
   Google's tag is in the page <head> with analytics_storage "denied" by default, so no analytics cookies are
   set until the visitor accepts ("advanced" consent mode). This file shows the choice, stores it and sends
   our own events only after acceptance.
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

  function read(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function write(k, v) { try { window.localStorage.setItem(k, v); } catch (e) {} }
  // Inside a frame (the thank-you page shown in the inquiry form) nothing is measured: the page around it reports.
  var framed = window.self !== window.top;
  function granted() { return !framed && read(KEY) === 'granted'; }

  // Pages without the tag in their <head> (the thank-you page) get it here, once, and never inside a frame.
  function loadTag() {
    if (loaded || framed) return;
    loaded = true;
    if (document.querySelector('script[src*="googletagmanager.com/gtm.js"]')) return;
    gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'granted' });
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
    write(KEY, value);
    gtag('consent', 'update', { analytics_storage: value === 'granted' ? 'granted' : 'denied' });
    if (value === 'granted') loadTag();
    else clearCookies();
    hide();
  }

  function hide() { if (banner) { banner.hidden = true; } }

  function show() {
    if (!banner) {
      banner = document.createElement('section');
      banner.className = 'consent';
      banner.setAttribute('role', 'dialog');
      banner.setAttribute('aria-label', 'Analytics cookies');
      banner.innerHTML =
        '<div class="consent__head"><span class="consent__icon" aria-hidden="true"></span><h2 class="consent__title">Cookies and analytics</h2></div>' +
        '<p class="consent__text">We use Google Analytics to see which pages are useful. It uses cookies only if you accept. <a class="consent__link" href="/privacy#cookies">Details</a></p>' +
        '<p class="consent__state" aria-live="polite"></p>' +
        '<div class="consent__actions">' +
        '<button type="button" class="consent__btn" data-consent="denied">Reject</button>' +
        '<button type="button" class="consent__btn consent__btn--accept" data-consent="granted">Accept</button>' +
        '</div>';
      banner.addEventListener('click', function (e) {
        var b = e.target.closest('[data-consent]');
        if (b) choose(b.getAttribute('data-consent'));
      });
      document.body.appendChild(banner);
    }
    var v = read(KEY);
    banner.querySelector('.consent__state').textContent =
      v === 'granted' ? 'Your current choice: accepted' : v === 'denied' ? 'Your current choice: rejected' : '';
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
