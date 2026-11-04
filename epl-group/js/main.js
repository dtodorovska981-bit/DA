/* EPL Group website interactions: reveals, counters, hero choreography, router, FAQ, forms. */
(function () {
  'use strict';
  var doc = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  doc.classList.add('js');

  /* ---------- page ready (triggers hero choreography) ---------- */
  function ready() {
    document.body.classList.add('is-ready');
    var title = document.querySelector('.hero__title');
    if (title) setTimeout(function () { title.classList.add('is-settled'); }, reduce ? 0 : 1500);
  }
  if (document.fonts && document.fonts.ready) {
    var done = false;
    document.fonts.ready.then(function () { if (!done) { done = true; ready(); } });
    setTimeout(function () { if (!done) { done = true; ready(); } }, 900);
  } else { ready(); }

  /* ---------- year ---------- */
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  /* ---------- nav ---------- */
  var nav = document.querySelector('.nav');
  var toggle = document.querySelector('.nav__toggle');
  var navScrolled = false;
  function onScrollNav() {
    /* hysteresis: compact after 60px, expand again only near the top, so it never flickers */
    var y = window.scrollY;
    if (!navScrolled && y > 60) { navScrolled = true; nav.classList.add('is-scrolled'); }
    else if (navScrolled && y < 8) { navScrolled = false; nav.classList.remove('is-scrolled'); }
  }
  onScrollNav();
  window.addEventListener('scroll', onScrollNav, { passive: true });
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
    nav.querySelectorAll('.nav__mobile a').forEach(function (a) {
      a.addEventListener('click', function () { nav.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false'); });
    });
  }

  /* ---------- scroll reveals ---------- */
  var revealTargets = document.querySelectorAll('.r, [data-person], .journey');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    revealTargets.forEach(function (el) { io.observe(el); });
  } else {
    revealTargets.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- footer logo reveal (observe the footer, not the clipped svg) ---------- */
  var footer = document.querySelector('.footer');
  var footerLogo = document.querySelector('[data-logo-reveal]');
  if (footer && footerLogo) {
    if ('IntersectionObserver' in window && !reduce) {
      var fio = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) { footerLogo.classList.add('in'); fio.disconnect(); } });
      }, { threshold: 0.05 });
      fio.observe(footer);
    } else { footerLogo.classList.add('in'); }
  }

  /* ---------- pause the leaf animation whenever no tree is on screen ---------- */
  var windSvg = document.querySelector('.wind-defs');
  var windEls = Array.prototype.slice.call(document.querySelectorAll('[data-wind]'));
  if (windSvg && windEls.length && 'IntersectionObserver' in window) {
    var visibleTrees = new Set();
    var windIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        e.target.classList.toggle('is-offscreen', !e.isIntersecting);
        if (e.isIntersecting) visibleTrees.add(e.target); else visibleTrees.delete(e.target);
      });
      try { if (visibleTrees.size) windSvg.unpauseAnimations(); else windSvg.pauseAnimations(); } catch (err) {}
    });
    windEls.forEach(function (el) { windIO.observe(el); });
  }

  /* ---------- counters ---------- */
  function animateCount(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    var prefix = el.getAttribute('data-prefix') || '';
    var suffix = el.getAttribute('data-suffix') || '';
    var start = null, dur = 1600;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min(1, (ts - start) / dur);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = prefix + Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var counterGroups = document.querySelectorAll('[data-counters]');
  if ('IntersectionObserver' in window && !reduce) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.querySelectorAll('[data-count]').forEach(function (n, i) { setTimeout(function () { animateCount(n); }, i * 120); });
          cio.unobserve(e.target);
        }
      });
    }, { threshold: 0.4 });
    counterGroups.forEach(function (g) { cio.observe(g); });
  }

  /* ---------- parallax (subtle, rAF-throttled) ---------- */
  var px = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
  if (px.length && !reduce) {
    var ticking = false;
    function parallax() {
      var vh = window.innerHeight;
      px.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        var f = parseFloat(el.getAttribute('data-parallax')) || 0;
        var offset = (r.top + r.height / 2 - vh / 2) * f;
        var base = el.classList.contains('photo-panel__bg') ? ' scale(1.08)' : el.classList.contains('closing__bg') ? ' scale(1.06)' : '';
        el.style.transform = 'translate3d(0,' + offset.toFixed(1) + 'px,0)' + base;
      });
      ticking = false;
    }
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(parallax); } }, { passive: true });
    parallax();
  }

  /* ---------- partners: stacked words follow the hovered path ---------- */
  document.querySelectorAll('[data-paths]').forEach(function (grid) {
    var words = grid.querySelectorAll('[data-word]');
    grid.querySelectorAll('[data-path]').forEach(function (p) {
      var key = p.getAttribute('data-path');
      function on() { words.forEach(function (w) { w.classList.toggle('on', w.getAttribute('data-word') === key); }); }
      function off() { words.forEach(function (w) { w.classList.remove('on'); }); }
      p.addEventListener('mouseenter', on); p.addEventListener('focus', on);
      p.addEventListener('mouseleave', off); p.addEventListener('blur', off);
    });
  });

  /* ---------- router panel (which partner are you?) ---------- */
  document.querySelectorAll('[data-router]').forEach(function (router) {
    var opts = router.querySelectorAll('[data-opt]');
    var reply = router.querySelector('[data-router-reply]');
    opts.forEach(function (o) {
      o.addEventListener('click', function () {
        var already = o.classList.contains('on');
        opts.forEach(function (x) { x.classList.remove('on'); x.setAttribute('aria-checked', 'false'); });
        o.classList.add('on'); o.setAttribute('aria-checked', 'true');
        if (reply) {
          reply.style.opacity = '0';
          setTimeout(function () { reply.textContent = o.getAttribute('data-reply'); reply.style.opacity = '1'; }, 180);
        }
        if (already) window.location.href = o.getAttribute('data-href');
      });
      o.addEventListener('dblclick', function () { window.location.href = o.getAttribute('data-href'); });
    });
  });

  /* ---------- FAQ ---------- */
  document.querySelectorAll('[data-faq]').forEach(function (item) {
    var q = item.querySelector('.faq__q');
    q.addEventListener('click', function () {
      var open = item.classList.toggle('open');
      q.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  /* ---------- chips -> hidden input ---------- */
  document.querySelectorAll('[data-chips]').forEach(function (row) {
    var multi = row.hasAttribute('data-multi');
    var input = row.parentNode.querySelector('input[type="hidden"]');
    row.querySelectorAll('.chip').forEach(function (chip) {
      chip.addEventListener('click', function () {
        if (!multi) row.querySelectorAll('.chip').forEach(function (c) { if (c !== chip) c.classList.remove('on'); });
        chip.classList.toggle('on');
        var vals = Array.prototype.map.call(row.querySelectorAll('.chip.on'), function (c) { return c.getAttribute('data-value'); });
        if (input) input.value = vals.join(', ');
      });
    });
  });

  /* ---------- forms: progressive enhancement over Netlify forms ---------- */
  document.querySelectorAll('[data-form]').forEach(function (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      var label = btn.querySelector('span');
      var original = label.textContent;
      label.textContent = 'Sending…'; btn.disabled = true;
      var data = new FormData(form);
      fetch(form.getAttribute('action') || '/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(data).toString() })
        .then(function (res) { if (!res.ok) throw new Error('bad status'); form.classList.add('is-sent'); form.nextElementSibling.scrollIntoView({ behavior: 'smooth', block: 'center' }); })
        .catch(function () {
          /* Fallback when not deployed behind Netlify forms: open a pre-filled email instead. */
          var to = form.getAttribute('name') === 'investors' ? 'ir@eplgroup.co' : 'founders@eplgroup.co';
          var lines = [];
          data.forEach(function (v, k) { if (k !== 'form-name' && k !== 'company-website' && v) lines.push(k + ': ' + v); });
          window.location.href = 'mailto:' + to + '?subject=' + encodeURIComponent('EPL Group: ' + form.getAttribute('name')) + '&body=' + encodeURIComponent(lines.join('\n'));
          label.textContent = original; btn.disabled = false;
        });
    });
  });

  /* ---------- hero: cursor nudge on hover of the selection ---------- */
  var sel = document.querySelector('.sel');
  if (sel && !reduce) {
    sel.addEventListener('mouseenter', function () { sel.querySelector('.sel__cursor').style.transform = 'translate(-6px,-6px)'; });
    sel.addEventListener('mouseleave', function () { sel.querySelector('.sel__cursor').style.transform = ''; });
  }
})();
