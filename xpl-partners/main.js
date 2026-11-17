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
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* ---- nav: solid after scrolling, hides on the way down, returns on the way up ---- */
  var nav = $('#nav');
  var toggle = $('#navToggle');
  var parallax = reduce ? [] : $$('[data-parallax]');
  var hero = $('.hero');
  var lastY = window.scrollY, ticking = false;

  function onFrame() {
    ticking = false;
    var y = window.scrollY;
    nav.classList.toggle('is-stuck', y > 24);
    nav.classList.toggle('is-hidden', y > 640 && y > lastY && !nav.classList.contains('is-open'));
    lastY = y;
    if (parallax.length && y < hero.offsetHeight + 80) {
      parallax.forEach(function (el) {
        el.style.transform = 'translate3d(0,' + (y * parseFloat(el.getAttribute('data-parallax'))).toFixed(1) + 'px,0)';
      });
    }
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

  /* ---- hero: the photo and coral bands lean gently toward the pointer ---- */
  var img = $('.hero__img');
  if (!reduce && img && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    var bands = $('.hero__bands');
    var tx = 0, ty = 0, cx = 0, cy = 0, raf = null;
    function lean() {
      cx += (tx - cx) * 0.06; cy += (ty - cy) * 0.06;
      img.style.translate = (cx * -14).toFixed(2) + 'px ' + (cy * -10).toFixed(2) + 'px';
      bands.style.translate = (cx * 10).toFixed(2) + 'px ' + (cy * 6).toFixed(2) + 'px';
      raf = (Math.abs(tx - cx) + Math.abs(ty - cy) > 0.002) ? requestAnimationFrame(lean) : null;
    }
    hero.addEventListener('pointermove', function (e) {
      var r = hero.getBoundingClientRect();
      tx = (e.clientX - r.left) / r.width - 0.5;
      ty = (e.clientY - r.top) / r.height - 0.5;
      if (!raf) { raf = requestAnimationFrame(lean); }
    });
    hero.addEventListener('pointerleave', function () { tx = 0; ty = 0; if (!raf) { raf = requestAnimationFrame(lean); } });
  }
})();
