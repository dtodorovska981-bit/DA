/* DNA Pro Plans website interactions */
(function () {
  document.documentElement.classList.add('js');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- year ---------- */
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  /* ---------- nav ---------- */
  var nav = document.querySelector('.nav');
  var toggle = document.querySelector('.nav__toggle');
  function onScrollNav() { nav.classList.toggle('is-scrolled', window.scrollY > 20); }
  onScrollNav();
  window.addEventListener('scroll', onScrollNav, { passive: true });
  toggle.addEventListener('click', function () {
    var open = nav.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', open);
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
  nav.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () { nav.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false'); });
  });

  /* ---------- preselect form option from buttons ---------- */
  var need = document.getElementById('need');
  document.querySelectorAll('[data-need]').forEach(function (b) {
    b.addEventListener('click', function () { if (need) need.value = b.getAttribute('data-need'); });
  });

  /* ---------- map ---------- */
  var RLE = "0:0,6,17-20,23,25-29,35-42,56,67-83,85-89,91;1:5-10,13-14,17-23,28-30,34-42,54-56,65,67-91,95-96;2:0,4-17,20,22-24,26,29-30,35-40,53-58,63-66,68-96;3:0-1,5-26,29-31,34-39,53-59,62-96;4:1-2,4-25,29-31,35-37,43-44,52-54,56-57,60-96;5:5-24,29-30,35-37,43-44,52-96;6:4-23,26,30,35-36,50-53,55-92,94-96;7:4-22,28-29,50-53,55-90,93-94;8:6,12-23,28-31,52-53,55-86,92;9:13-24,28-31,47,51-53,55-85,91-92;10:4,14-32,48,51,53-85,91-92;11:14-26,28-33,46,48,50-87,91;12:14-30,33,49-86;13:15-30,33-34,48-87;14:15-31,49-51,53-56,58-61,63-85,87;15:15-29,47-49,51-52,54-56,60-61,63-83;16:15-28,47-48,51,53-54,56-61,63-80,83;17:16-27,47,50-51,56-57,59-81,83,86;18:17-27,47-51,59-81,84;19:18-26,46-81;20:18-22,45-57,59-61,63-81;21:20-22,45-64,67-80;22:20-22,24,28,45-58,60-64,69-72,74-77;23:22-24,45-63,69-70,75-77;24:25,44-59,61,69-70,76-78,82;25:26,30-31,45-62,77;26:28-32,46-61,76,80;27:28-34,52-60,75,79-80;28:27-36,51-59,76,79-81,84;29:27-38,52-59,77,81,86-88;30:28-39,53-59,81,87;31:28-38,53-59,85,87;32:29-37,52-59,61,83-85,87;33:30-37,52-58,61,82-88;34:30-37,53-58,61,80-89;35:30-35,53-57,80-89;36:30-35,54-56,80-90;37:30-34,54-56,80-82,85-89;38:29-32,87-89;39:29-32,88,96;40:29-30,88,96;41:29-30;42:29-30;43:29-30;44:29;45:29-30";
  // Client countries: US, Canada, Costa Rica, UK, France, Portugal, Switzerland, Croatia, Nigeria, DR Congo, Ethiopia, Kenya, South Africa, Oman, Australia (+ Montenegro next to HQ)
  var PINS = [[22,16,'United States'],[27,15,'Canada'],[26,25,'Costa Rica'],[48,11,'United Kingdom'],[49,13,'France'],[46,16,'Portugal'],[50,13,'Switzerland'],[53,14,'Croatia'],[51,25,'Nigeria'],[54,29,'DR Congo'],[59,25,'Ethiopia'],[59,28,'Kenya'],[55,36,'South Africa'],[64,21,'Oman'],[89,37,'Australia']];
  var HQ = [54,15];
  var S = 10, R = 3.2, NS = 'http://www.w3.org/2000/svg';
  var svg = document.querySelector('.map__svg');
  function el(tag, attrs, parent) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
  if (svg) {
    var land = el('g', {}, svg);
    // group dots by column band so they fade in as a left-to-right wave
    var bands = {};
    RLE.split(';').forEach(function (row) {
      var p = row.split(':'), cy = +p[0] * S + R;
      p[1].split(',').forEach(function (run) {
        var ab = run.split('-'), a = +ab[0], b = ab[1] !== undefined ? +ab[1] : a;
        for (var x = a; x <= b; x++) {
          var band = Math.floor(x / 6);
          (bands[band] = bands[band] || []).push('M' + (x * S) + ' ' + cy + 'a' + R + ' ' + R + ' 0 1 0 ' + 2 * R + ' 0a' + R + ' ' + R + ' 0 1 0 ' + -2 * R + ' 0');
        }
      });
    });
    Object.keys(bands).forEach(function (b) {
      var path = el('path', { d: bands[b].join(''), class: 'land' }, land);
      path.style.setProperty('--md', (b * 0.05) + 's');
    });
    function pin(x, y, cls, delay, label) {
      var g = el('g', { class: 'pin ' + cls }, svg);
      g.style.setProperty('--pd', delay + 's');
      var cx = x * S + R, cy = y * S + R;
      el('circle', { cx: cx, cy: cy, r: cls ? 15 : 12, class: 'pin__halo' }, g);
      el('circle', { cx: cx, cy: cy, r: cls ? 7 : 6, class: 'pin__core' }, g);
      if (label) { var t = el('title', {}, g); t.textContent = label; }
    }
    PINS.forEach(function (p, i) { pin(p[0], p[1], '', 0.6 + i * 0.07, p[2]); });
    pin(HQ[0], HQ[1], 'pin--hq', 0.4, 'Headquarters, North Macedonia');
    var hx = HQ[0] * S + R + 18, hy = HQ[1] * S + R - 44;
    var lbl = el('g', { class: 'hq-label' }, svg);
    var rect = el('rect', { x: hx, y: hy, width: 168, height: 28 }, lbl);
    var tx = el('text', { x: hx + 14, y: hy + 18.5 }, lbl);
    tx.textContent = 'HQ · North Macedonia';
    function fitLabel() { try { rect.setAttribute('width', Math.ceil(tx.getComputedTextLength()) + 28); } catch (e) {} }
    fitLabel();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitLabel);
  }

  /* ---------- count up ---------- */
  function countUp(dd) {
    var end = +dd.getAttribute('data-count'), suf = dd.getAttribute('data-suffix') || '';
    if (reduce) { dd.textContent = end + suf; return; }
    var start = null, dur = 1600;
    function step(t) {
      if (!start) start = t;
      var k = Math.min((t - start) / dur, 1), e = 1 - Math.pow(1 - k, 4);
      dd.textContent = Math.round(end * e).toLocaleString('en-US') + suf;
      if (k < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  /* ---------- sequences ---------- */
  function lightIndustries(line) {
    line.classList.add('is-lit');
    if (reduce) return;
    var spans = line.querySelectorAll('span');
    spans.forEach(function (s, i) { s.style.transitionDelay = (i * 70) + 'ms'; });
  }
  function tickChecks() {
    var items = document.querySelectorAll('#checks li');
    items.forEach(function (li, i) { setTimeout(function () { li.classList.add('is-on'); }, reduce ? 0 : 500 + i * 260); });
  }

  /* ---------- reveal observer ---------- */
  var revealEls = document.querySelectorAll('[data-reveal], .map, .sample-art');
  // stagger siblings that reveal together
  document.querySelectorAll('.services, .packages, .principles, .faq__list').forEach(function (group) {
    Array.prototype.forEach.call(group.children, function (c, i) { c.style.setProperty('--delay', (i * 0.08) + 's'); });
  });
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var t = en.target;
        t.classList.add('is-in');
        if (t.classList.contains('stats')) t.querySelectorAll('[data-count]').forEach(countUp);
        if (t.classList.contains('trust')) tickChecks();
        io.unobserve(t);
      });
    }, { threshold: 0.18, rootMargin: '0px 0px -8% 0px' });
    revealEls.forEach(function (e) { io.observe(e); });
  } else {
    revealEls.forEach(function (e) { e.classList.add('is-in'); });
    document.querySelectorAll('[data-count]').forEach(countUp);
    tickChecks();
  }

  /* ---------- timeline progress + hero parallax ---------- */
  var tl = document.getElementById('timeline');
  var steps = tl ? tl.querySelectorAll('.step') : [];
  var para = document.querySelectorAll('[data-parallax]');
  var ticking = false;
  var inds = document.querySelectorAll('#indList .ind');
  function onScroll() {
    var vh = window.innerHeight;
    if (inds.length) {
      var best = null, bestD = Infinity, mid = vh * 0.5;
      inds.forEach(function (li) { var b = li.getBoundingClientRect(); var d = Math.abs(b.top + b.height / 2 - mid); if (d < bestD) { bestD = d; best = li; } });
      var listBox = inds[0].parentNode.getBoundingClientRect();
      if (best && listBox.top < vh && listBox.bottom > 0) inds.forEach(function (li) { li.classList.toggle('is-active', li === best); });
    }
    if (tl) {
      var r = tl.getBoundingClientRect();
      var p = reduce ? 1 : Math.min(Math.max((vh * 0.8 - r.top) / (r.height + vh * 0.35), 0), 1);
      tl.style.setProperty('--progress', p.toFixed(3));
      steps.forEach(function (s, i) { s.classList.toggle('is-on', p >= (i / steps.length) + 0.02); });
    }
    if (!reduce && window.scrollY < vh * 1.2) {
      para.forEach(function (n) { n.style.transform = 'translateY(' + (window.scrollY * parseFloat(n.getAttribute('data-parallax'))).toFixed(1) + 'px)'; });
    }
    ticking = false;
  }
  window.addEventListener('scroll', function () { if (!ticking) { requestAnimationFrame(onScroll); ticking = true; } }, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();
})();
