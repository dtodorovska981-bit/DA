/* xPL Partners — interactions and motion. No dependencies. */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---- index children so CSS can stagger them ---- */
  $$('[data-stagger]').forEach(function (group) {
    Array.prototype.forEach.call(group.children, function (el, i) { el.style.setProperty('--i', i); });
  });
  $$('.tracker .trow').forEach(function (row, i) { row.style.setProperty('--i', i); });
  $$('.compare__col').forEach(function (col, c) {
    $$('.mark', col).forEach(function (mark, r) {
      mark.style.setProperty('--col', c);
      mark.style.setProperty('--row', r);
    });
  });

  /* ---- count-up numbers ---- */
  function countUp(el) {
    var to = parseFloat(el.getAttribute('data-count'));
    var from = parseFloat(el.getAttribute('data-count-from') || '0');
    if (reduce || isNaN(to)) { return; }
    var dur = 1500, t0 = null;
    el.textContent = from;
    function tick(t) {
      if (t0 === null) { t0 = t; }
      var p = Math.min((t - t0) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 4);
      el.textContent = Math.round(from + (to - from) * eased);
      if (p < 1) { requestAnimationFrame(tick); }
    }
    requestAnimationFrame(tick);
  }

  /* ---- reveal on scroll ---- */
  var targets = $$('[data-reveal], [data-stagger], .approach, .compare, [data-tracker], [data-count]');
  function show(el) {
    if (el.hasAttribute('data-count')) { countUp(el); return; }
    el.classList.add(el.classList.contains('approach') ? 'is-drawn' : 'is-in');
  }
  if (!('IntersectionObserver' in window)) {
    targets.forEach(show);
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) { return; }
        show(e.target);
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px 10% 0px', threshold: 0 });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* ---- nav: stays fixed at the top, turns solid after scrolling ---- */
  var nav = $('#nav');
  var toggle = $('#navToggle');
  var ticking = false;

  function onFrame() {
    ticking = false;
    var y = window.scrollY;
    nav.classList.toggle('is-stuck', y > 24);
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(onFrame); }
  }, { passive: true });
  onFrame();

  /* ---- mobile menu ---- */
  function setMenu(open) {
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
  }
  toggle.addEventListener('click', function () { setMenu(!nav.classList.contains('is-open')); });
  $$('#navLinks a').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { setMenu(false); } });

  /* ---- current section in the nav ---- */
  var links = $$('#navLinks a[href^="#"]');
  if ('IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) { return; }
        links.forEach(function (a) { a.classList.toggle('is-current', a.getAttribute('href') === '#' + e.target.id); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    links.forEach(function (a) { var s = $(a.getAttribute('href')); if (s) { spy.observe(s); } });
  }

  /* ---- FAQ accordion: one open at a time ---- */
  var items = $$('.qa');
  items.forEach(function (item) {
    $('.qa__head', item).addEventListener('click', function () {
      var open = !item.classList.contains('is-open');
      items.forEach(function (other) {
        other.classList.remove('is-open');
        $('.qa__head', other).setAttribute('aria-expanded', 'false');
      });
      if (open) {
        item.classList.add('is-open');
        $('.qa__head', item).setAttribute('aria-expanded', 'true');
      }
    });
  });

  /* ---- analytics: cookie consent + call-booking clicks ---- */
  var track = function () { if (typeof window.gtag === 'function') { window.gtag.apply(null, arguments); } };
  var consent = $('#consent');
  var choice = null;
  try { choice = localStorage.getItem('xpl-consent'); } catch (e) {}
  if (consent && !choice) { consent.hidden = false; }
  $$('[data-consent]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var value = btn.getAttribute('data-consent');
      try { localStorage.setItem('xpl-consent', value); } catch (e) {}
      track('consent', 'update', { analytics_storage: value });
      if (value === 'denied') {
        /* withdraw: remove the Google Analytics cookies already set for this site */
        document.cookie.split(';').forEach(function (c) {
          var name = c.split('=')[0].trim();
          if (name.indexOf('_ga') !== 0) { return; }
          var host = location.hostname;
          [host, '.' + host, '.' + host.split('.').slice(-2).join('.')].forEach(function (d) {
            document.cookie = name + '=; Max-Age=0; path=/; domain=' + d;
          });
          document.cookie = name + '=; Max-Age=0; path=/';
        });
      }
      consent.hidden = true;
    });
  });
  $$('[data-cookie-settings]').forEach(function (btn) {
    btn.addEventListener('click', function () { consent.hidden = false; });
  });
  $$('a[href*="cal.com"]').forEach(function (a) {
    a.addEventListener('click', function () {
      var section = a.closest('section, footer, header');
      track('event', 'book_call_click', {
        link_text: (a.textContent || '').split(/[ \n\t]+/).join(' ').trim().slice(0, 60),
        section: section ? (section.id || section.className.split(' ')[0]) : 'page'
      });
    });
  });
})();
