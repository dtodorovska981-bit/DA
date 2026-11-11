/* DNA Pro Plans — interactions and scroll motion (no dependencies) */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

  /* ---------- nav: mobile menu + hide on scroll down ---------- */
  var nav = $('.nav');
  var toggle = $('.nav__toggle');
  if (toggle) {
    var setOpen = function (open) {
      nav.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      document.documentElement.style.overflow = open ? 'hidden' : '';
    };
    toggle.addEventListener('click', function () { setOpen(!nav.classList.contains('is-open')); });
    $$('.nav__links a').forEach(function (a) { a.addEventListener('click', function () { setOpen(false); }); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
    window.addEventListener('resize', function () { if (window.innerWidth > 960) setOpen(false); });
  }

  /* ---------- reveal on scroll ---------- */
  $$('[data-stagger]').forEach(function (group) {
    $$(':scope > *', group).forEach(function (el, i) {
      if (!el.hasAttribute('data-reveal')) el.setAttribute('data-reveal', group.getAttribute('data-stagger') || '');
      el.style.setProperty('--d', i);
    });
  });
  $$('.lines').forEach(function (h) {
    $$('.line', h).forEach(function (l, i) { l.style.setProperty('--i', i); });
  });
  $$('.wordmark__text').forEach(function (w) {
    var text = w.textContent.trim();
    w.setAttribute('aria-label', text);
    w.textContent = '';
    var i = 0;
    text.split(' ').forEach(function (word) {
      var clip = document.createElement('span');
      clip.className = 'wordmark__clip';
      clip.setAttribute('aria-hidden', 'true');
      word.split('').forEach(function (ch) {
        var s = document.createElement('span');
        s.textContent = ch;
        s.style.setProperty('--i', i++);
        clip.appendChild(s);
      });
      w.appendChild(clip);
    });
  });

  var revealEls = $$('[data-reveal], .lines, .wordmark');
  if ('IntersectionObserver' in window) {
    // Elements that start fully clipped report no visible area, so watch their parent instead.
    var proxies = new Map();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        (proxies.get(e.target) || [e.target]).forEach(function (el) { el.classList.add('in'); });
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });
    revealEls.forEach(function (el) {
      if (el.getAttribute('data-reveal') === 'clip') {
        var parent = el.parentElement;
        if (!proxies.has(parent)) { proxies.set(parent, []); io.observe(parent); }
        proxies.get(parent).push(el);
      } else io.observe(el);
    });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- statement: words fill in as you scroll ---------- */
  var statement = $('.statement p');
  var words = [];
  if (statement) {
    var txt = statement.textContent.trim().split(/\s+/);
    statement.setAttribute('aria-label', txt.join(' '));
    statement.textContent = '';
    txt.forEach(function (w, i) {
      var s = document.createElement('span');
      s.className = 'w';
      s.setAttribute('aria-hidden', 'true');
      s.textContent = w;
      statement.appendChild(s);
      if (i < txt.length - 1) statement.appendChild(document.createTextNode(' '));
      words.push(s);
    });
    if (reduce) words.forEach(function (w) { w.classList.add('on'); });
  }

  /* ---------- services: accordion + showcase ---------- */
  var svcs = $$('.svc');
  var shows = $$('.show');
  function setService(i) {
    svcs.forEach(function (s, j) {
      s.classList.toggle('is-active', j === i);
      $('.svc__head', s).setAttribute('aria-expanded', String(j === i));
    });
    shows.forEach(function (s, j) { s.classList.toggle('is-active', j === i); });
  }
  svcs.forEach(function (s, i) {
    var head = $('.svc__head', s);
    head.addEventListener('click', function () { setService(i); });
    head.addEventListener('mouseenter', function () {
      if (window.matchMedia('(hover: hover)').matches) setService(i);
    });
  });

  /* ---------- tiers: highlight follows the pointer ---------- */
  var tiers = $$('.tier');
  var tiersBox = $('.tiers');
  if (tiersBox) {
    var defaultTier = tiers.findIndex(function (t) { return t.classList.contains('is-active'); });
    var setTier = function (i) { tiers.forEach(function (t, j) { t.classList.toggle('is-active', j === i); }); };
    tiers.forEach(function (t, i) {
      t.addEventListener('mouseenter', function () { setTier(i); });
      t.addEventListener('focusin', function () { setTier(i); });
    });
    tiersBox.addEventListener('mouseleave', function () { setTier(defaultTier); });
  }

  /* ---------- approach layers: one card open at a time, the rest tuck under ---------- */
  var layerEls = $$('.layer');
  var layersHover = false, layerOpen = -1;
  function setLayer(i) {
    if (i === layerOpen) return;
    layerOpen = i;
    var y = 0;
    layerEls.forEach(function (l, j) {
      l.style.setProperty('--y', y + 'px');
      l.classList.toggle('is-open', j === i);
      $('.layer__head', l).setAttribute('aria-expanded', String(j === i));
      y += j === i ? 380 : 180;
    });
  }
  if (layerEls.length) {
    setLayer(reduce ? 2 : 0);
    layerEls.forEach(function (l, i) {
      var head = $('.layer__head', l);
      head.addEventListener('click', function () { layersHover = true; setLayer(i); });
      head.addEventListener('focus', function () { setLayer(i); });
      l.addEventListener('mouseenter', function () {
        if (window.matchMedia('(hover: hover)').matches) { layersHover = true; setLayer(i); }
      });
    });
    $('.layers').addEventListener('mouseleave', function () { layersHover = false; });
  }

  /* ---------- sample plan reel: drag to scroll ---------- */
  $$('.reel').forEach(function (reel) {
    var down = false, startX = 0, startLeft = 0, moved = 0;
    reel.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse') return;
      down = true; moved = 0; startX = e.clientX; startLeft = reel.scrollLeft;
    });
    window.addEventListener('pointermove', function (e) {
      if (!down) return;
      moved = e.clientX - startX;
      if (Math.abs(moved) > 4) reel.classList.add('is-drag');
      reel.scrollLeft = startLeft - moved;
    });
    window.addEventListener('pointerup', function () { down = false; reel.classList.remove('is-drag'); });
  });

  /* ---------- count up ---------- */
  var counters = $$('[data-count]');
  if (counters.length && 'IntersectionObserver' in window && !reduce) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        cio.unobserve(e.target);
        var el = e.target, end = parseFloat(el.getAttribute('data-count')), suffix = el.getAttribute('data-suffix') || '';
        var t0 = performance.now(), dur = 1400;
        (function tick(now) {
          var p = clamp((now - t0) / dur, 0, 1), eased = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(end * eased) + suffix;
          if (p < 1) requestAnimationFrame(tick);
        })(t0);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (c) { cio.observe(c); });
  }

  /* ---------- scroll-linked motion ---------- */
  var parallax = $$('[data-parallax]');
  var drift = $$('[data-drift]');
  var layers = $('.layers');
  var rail = $('.rail');
  var steps = $$('.step');
  var ticking = false;

  // progress of an element through the viewport: 0 when its top hits `from` (fraction of
  // viewport height), 1 when its top hits `to`.
  function progress(el, from, to) {
    var r = el.getBoundingClientRect(), vh = window.innerHeight;
    return clamp((from * vh - r.top) / ((from - to) * vh), 0, 1);
  }

  function frame() {
    ticking = false;
    var y = window.scrollY, vh = window.innerHeight;


    if (rail) {
      var rp = progress(rail, 0.9, 0.42);
      if (!reduce) rail.style.setProperty('--p', rp.toFixed(4));
      steps.forEach(function (s, i) { s.classList.toggle('is-on', reduce || rp > i / steps.length + 0.02); });
    }
    if (reduce) return;

    if (words.length) {
      var sp = progress(statement, 0.85, 0.2);
      var n = Math.round(sp * words.length);
      words.forEach(function (w, i) { w.classList.toggle('on', i < n); });
    }
    if (layers && !layersHover) {
      // the open card follows the scroll: Research, then Projections, then Presentation
      setLayer(Math.min(2, Math.floor(progress(layers, 0.78, 0.12) * 3)));
    }
    parallax.forEach(function (el) {
      var r = el.parentElement.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) return;
      var off = (r.top + r.height / 2 - vh / 2) * parseFloat(el.getAttribute('data-parallax'));
      off = clamp(off, -0.11 * r.height, 0.11 * r.height);
      el.style.transform = 'translate3d(0,' + off.toFixed(1) + 'px,0)';
    });
    drift.forEach(function (el) {
      var r = el.parentElement.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) return;
      var off = (r.top + r.height / 2 - vh / 2) * parseFloat(el.getAttribute('data-drift'));
      el.style.transform = 'translate3d(' + off.toFixed(1) + 'px,0,0)';
    });
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  frame();

  /* ---------- contact: brief form, then booking ---------- */
  var form = $('#brief-form');
  if (form) {
    var CAL = form.getAttribute('data-calendly');
    var params = new URLSearchParams(location.search);
    var need = params.get('need');
    if (need) {
      var sel = form.elements.need;
      $$('option', sel).forEach(function (o) { if (o.value.toLowerCase() === need.toLowerCase()) sel.value = o.value; });
    }

    var showBooking = function (name, email) {
      var q = '?hide_gdpr_banner=1&primary_color=5271ff';
      if (name) q += '&name=' + encodeURIComponent(name);
      if (email) q += '&email=' + encodeURIComponent(email);
      var first = (name || '').trim().split(' ')[0];
      $('#step-form').hidden = true;
      var b = $('#step-book');
      $('#book-title').textContent = first ? 'Thank you, ' + first + '. Now pick a time.' : 'Thank you. Now pick a time.';
      $('#book-frame').src = CAL + q;
      $('#book-link').href = CAL;
      b.hidden = false;
      b.classList.add('swap-in');
      $$('.flow li').forEach(function (li, i) { li.classList.toggle('is-on', i === 1); });
      b.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
      $('#book-title').focus();
    };

    form.addEventListener('submit', function (e) {
      if (!window.fetch || !window.FormData) return; // no-JS / old browsers: plain POST to thanks.html
      e.preventDefault();
      var btn = $('button[type=submit]', form), err = $('#form-error');
      err.hidden = true;
      btn.disabled = true;
      var label = btn.textContent;
      btn.textContent = 'Sending…';
      var body = new URLSearchParams(new FormData(form)).toString();
      fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body
      }).then(function (res) {
        if (!res.ok) throw new Error(res.status);
        showBooking(form.elements.name.value, form.elements.email.value);
      }).catch(function () {
        btn.disabled = false;
        btn.textContent = label;
        err.hidden = false;
      });
    });
  }

  var year = $('#year');
  if (year) year.textContent = new Date().getFullYear();
})();
