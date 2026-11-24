/* EPL Group website interactions: reveals, counters, hero choreography, router, FAQ, embedded forms. */
(function () {
  'use strict';
  var doc = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  doc.classList.add('js');

  /* ---------- always open a page at the top ----------
     Browsers restore the last scroll position on reload/back, and a URL ending in #section
     opens mid-page. Every page starts at the top instead. The one exception: a link the
     visitor clicks that points at a section on another page (e.g. footer "xPL Ventures"
     -> platforms.html#xpl) still lands on that section. */
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  var JUMP_KEY = 'epl-jump';
  var wanted = null;
  try { wanted = sessionStorage.getItem(JUMP_KEY); sessionStorage.removeItem(JUMP_KEY); } catch (e) {}
  var hereWithHash = location.pathname + location.hash;
  var jumpTarget = (location.hash && wanted === hereWithHash) ? location.hash : null;
  if (location.hash && !jumpTarget) {
    try { history.replaceState(null, '', location.pathname + location.search); } catch (e) {}
  }
  function toTop() { window.scrollTo({ top: 0, left: 0, behavior: 'instant' }); }
  function settle() {
    if (jumpTarget) {
      var el = null;
      try { el = document.querySelector(jumpTarget); } catch (e) {}
      if (el) { el.scrollIntoView({ behavior: 'instant', block: 'start' }); return; }
    }
    toTop();
  }
  settle();
  window.addEventListener('load', settle);
  window.addEventListener('pageshow', function (e) { if (e.persisted) { jumpTarget = null; toTop(); } });
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="#"]');
    if (!a || a.target === '_blank') return;
    var url;
    try { url = new URL(a.getAttribute('href'), location.href); } catch (err) { return; }
    if (url.origin === location.origin && url.pathname !== location.pathname && url.hash) {
      try { sessionStorage.setItem(JUMP_KEY, url.pathname + url.hash); } catch (err) {}
    }
  });

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

  /* ---------- team cards: open the selection box on hover, focus, or (touch) when in view ---------- */
  var people = Array.prototype.slice.call(document.querySelectorAll('[data-person]'));
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  people.forEach(function (card) {
    card.addEventListener('mouseenter', function () { card.classList.add('is-open'); });
    card.addEventListener('mouseleave', function () { if (!card.contains(document.activeElement)) card.classList.remove('is-open'); });
    card.addEventListener('focusin', function () { card.classList.add('is-open'); });
    card.addEventListener('focusout', function () { if (!card.matches(':hover')) card.classList.remove('is-open'); });
    card.addEventListener('click', function () { if (!finePointer) card.classList.toggle('is-open'); });
  });
  if (!finePointer && 'IntersectionObserver' in window) {
    /* no hover on touch screens: open as each card comes into view, close when it leaves so it replays */
    var openIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { e.target.classList.toggle('is-open', e.isIntersecting); });
    }, { threshold: 0.6 });
    people.forEach(function (card) { openIO.observe(card); });
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

  /* ---------- embedded Pipefy forms (pitch, investors, events) ----------
     On the site itself each form loads in place. Inside another page's frame (such as a preview)
     outside content is usually blocked, so a picture of the form is shown in the box instead.
     Without JavaScript, or if the form never loads, the panel with its button stays. */
  document.querySelectorAll('[data-embed]').forEach(function (box) {
    var frame = box.querySelector('iframe');
    var framed = true;
    try { framed = window.self !== window.top; } catch (e) { framed = true; }
    if (!frame) return;
    if (framed) {
      /* a preview cannot load the form, so show a picture of it in the same box */
      var shot = box.getAttribute('data-shot');
      if (!shot) return;
      var link = document.createElement('a');
      link.className = 'ev-embed__shot';
      link.href = box.getAttribute('data-src').split('?')[0];
      link.target = '_blank'; link.rel = 'noopener';
      var note = document.createElement('span');
      note.className = 'ev-embed__shotnote';
      note.textContent = 'Preview picture. On eplgroup.co the live form loads right here.';
      var img = new Image();
      img.alt = 'Picture of the ' + (frame.title || 'registration') + ' form. Opens the form in a new tab.';
      img.onload = function () { box.classList.add('is-live', 'is-loaded', 'is-shot'); };
      img.src = box.clientWidth < 480 ? shot.replace('.webp', '-m.webp') : shot;
      link.appendChild(note); link.appendChild(img);
      box.appendChild(link);
      return;
    }
    var loaded = false;
    frame.addEventListener('load', function () { loaded = true; box.classList.add('is-live', 'is-loaded'); });
    box.classList.add('is-live');
    frame.src = box.getAttribute('data-src');
    /* If the form has not loaded a while after it scrolled into view, fall back to the panel;
       it switches back if the form arrives. (A lazy frame only starts loading near the viewport.) */
    function startTimer() { setTimeout(function () { if (!loaded) box.classList.remove('is-live'); }, 15000); }
    if ('IntersectionObserver' in window) {
      var seen = new IntersectionObserver(function (entries) {
        if (entries.some(function (en) { return en.isIntersecting; })) { seen.disconnect(); startTimer(); }
      });
      seen.observe(box);
    } else { startTimer(); }
  });

  /* ---------- events page: calendar dates and event cards light each other up ---------- */
  var evLinked = Array.prototype.slice.call(document.querySelectorAll('.ev-hero [data-ev]'));
  evLinked.forEach(function (el) {
    function set(on) {
      evLinked.forEach(function (other) { if (other !== el && other.getAttribute('data-ev') === el.getAttribute('data-ev')) other.classList.toggle('is-hot', on); });
    }
    el.addEventListener('mouseenter', function () { set(true); });
    el.addEventListener('mouseleave', function () { set(false); });
    el.addEventListener('focusin', function () { set(true); });
    el.addEventListener('focusout', function () { set(false); });
  });

  /* ---------- hero: cursor nudge on hover of the selection ---------- */
  var sel = document.querySelector('.sel');
  if (sel && !reduce) {
    sel.addEventListener('mouseenter', function () { sel.querySelector('.sel__cursor').style.transform = 'translate(-6px,-6px)'; });
    sel.addEventListener('mouseleave', function () { sel.querySelector('.sel__cursor').style.transform = ''; });
  }
  /* ---------- insights: read the newsletter feed so a new issue shows without a new upload ----------
     The page already carries the posts known when the site was built. Feed text is only ever
     written with textContent, never as HTML. */
  var ins = document.querySelector('[data-insights]');
  if (ins && window.fetch && window.DOMParser) {
    var MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    var bakedPosts = [];
    try { bakedPosts = JSON.parse(ins.querySelector('[data-insights-data]').textContent) || []; } catch (e) { bakedPosts = []; }
    var mk = function (tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
    var linkTo = function (a, post) { a.href = post.link; if (post.external) { a.target = '_blank'; a.rel = 'noopener'; } };
    var renderPosts = function (posts) {
      var featuredBox = ins.querySelector('[data-insights-featured]');
      var more = ins.querySelector('[data-insights-more]');
      var list = ins.querySelector('[data-insights-list]');
      var first = posts[0];
      var kind = first.external ? 'issue' : 'article';
      var card = mk('a', 'issue'); linkTo(card, first);
      var pic = mk('div', 'issue__img' + (first.img ? '' : ' is-empty'));
      if (first.img) {
        var img = new Image(); img.alt = ''; img.width = 1200; img.height = 630;
        img.onerror = function () { pic.classList.add('is-empty'); img.remove(); };
        img.src = first.img; pic.appendChild(img);
      }
      var body = mk('div', 'issue__body');
      var kicker = mk('p', 'issue__kicker', 'Latest ' + kind);
      kicker.appendChild(mk('span', '', first.external ? (ins.getAttribute('data-newsletter') || 'Newsletter') : first.tag));
      var meta = mk('p', 'issue__meta');
      var parts = first.date.split('-');
      var time = mk('time', '', parseInt(parts[2], 10) + ' ' + MONTH_NAMES[parseInt(parts[1], 10) - 1] + ' ' + parts[0]); time.dateTime = first.date;
      var read = mk('span', 'link-arrow', 'Read the ' + kind); read.appendChild(mk('span', 'arr', '→'));
      meta.appendChild(time); meta.appendChild(read);
      body.appendChild(kicker); body.appendChild(mk('h2', '', first.title)); body.appendChild(mk('p', '', first.summary)); body.appendChild(meta);
      card.appendChild(pic); card.appendChild(body);
      featuredBox.textContent = ''; featuredBox.appendChild(card);
      list.textContent = '';
      posts.slice(1).forEach(function (post) {
        var row = mk('a', 'post'); linkTo(row, post);
        var mid = mk('div'); mid.appendChild(mk('h3', '', post.title)); mid.appendChild(mk('p', '', post.summary));
        row.appendChild(mk('span', 'date', post.date.slice(0, 7))); row.appendChild(mid); row.appendChild(mk('span', 'tag', post.tag));
        list.appendChild(row);
      });
      more.hidden = posts.length < 2;
    };
    fetch(ins.getAttribute('data-feed'), { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error('feed'); return r.text(); })
      .then(function (xml) {
        var doc = new DOMParser().parseFromString(xml, 'application/xml');
        if (doc.querySelector('parsererror')) return;
        var feed = [];
        Array.prototype.forEach.call(doc.getElementsByTagName('item'), function (it) {
          var t = function (n) { var e = it.getElementsByTagName(n)[0]; return e ? (e.textContent || '').trim() : ''; };
          var link = t('link'), when = new Date(t('pubDate'));
          if (!/^https:\/\//.test(link) || isNaN(when.getTime())) return;
          var enc = it.getElementsByTagName('enclosure')[0];
          var pic = enc && /^image\//.test(enc.getAttribute('type') || '') ? (enc.getAttribute('url') || '') : '';
          feed.push({ title: t('title'), summary: t('description'), link: link, date: when.toISOString().slice(0, 10), img: /^https:\/\//.test(pic) ? pic : '', tag: 'Newsletter', external: true });
        });
        if (!feed.length) return;
        var posts = bakedPosts.filter(function (p) { return !p.external; }).concat(feed);
        posts.sort(function (a, b) { return a.date === b.date ? (a.title < b.title ? 1 : -1) : (a.date < b.date ? 1 : -1); });
        var same = posts.length === bakedPosts.length && posts.every(function (p, i) { var q = bakedPosts[i]; return p.link === q.link && p.title === q.title && p.summary === q.summary && p.img === q.img; });
        if (!same) renderPosts(posts);
      })
      .catch(function () { /* keep the posts already on the page */ });
  }
  /* ---------- EPL Circle: line map of host cities ----------
     A glow follows the mouse across the map. With no mouse on it (and on touch screens),
     the glow moves from city to city on its own. */
  var lineMap = document.querySelector('[data-linemap]');
  if (lineMap) {
    var lmStage = lineMap.querySelector('.cir-map__stage');
    var lmGlow = lineMap.querySelector('.cir-map__glow');
    var lmPins = Array.prototype.slice.call(lineMap.querySelectorAll('.cir-pin'));
    var lmPts = lmPins.map(function (p) { return { x: parseFloat(p.style.left), y: parseFloat(p.style.top) }; });
    var lmCur = { x: lmPts[0].x, y: lmPts[0].y }, lmTarget = lmPts[0], lmActive = 0, lmHold = false, lmSeen = false, lmRaf = 0;
    var lmDraw = function () {
      lmCur.x += (lmTarget.x - lmCur.x) * (reduce ? 1 : 0.14);
      lmCur.y += (lmTarget.y - lmCur.y) * (reduce ? 1 : 0.14);
      lmGlow.style.setProperty('--mx', lmCur.x.toFixed(2) + '%');
      lmGlow.style.setProperty('--my', lmCur.y.toFixed(2) + '%');
      lmRaf = (Math.abs(lmTarget.x - lmCur.x) + Math.abs(lmTarget.y - lmCur.y) > 0.05) ? requestAnimationFrame(lmDraw) : 0;
    };
    var lmGo = function (pt) { lmTarget = pt; if (!lmRaf) lmRaf = requestAnimationFrame(lmDraw); };
    var lmMark = function (i) {
      lineMap.querySelectorAll('[data-pin]').forEach(function (el) { el.classList.toggle('is-on', +el.getAttribute('data-pin') === i); });
    };
    var lmCity = function (i) { lmActive = i; lmMark(i); lmGo(lmPts[i]); };
    lmStage.addEventListener('pointermove', function (ev) {
      if (ev.pointerType === 'touch') return;
      var r = lmStage.getBoundingClientRect();
      var pt = { x: (ev.clientX - r.left) / r.width * 100, y: (ev.clientY - r.top) / r.height * 100 };
      lmHold = true; lmGo(pt);
      var near = -1;
      lmPts.forEach(function (c, i) { if (Math.abs(c.x - pt.x) < 9 && Math.abs(c.y - pt.y) * (r.height / r.width) < 9) near = i; });
      lmMark(near);
    });
    lmStage.addEventListener('pointerleave', function () { lmHold = false; lmCity(lmActive); });
    lineMap.querySelectorAll('[data-pin]').forEach(function (el) {
      var i = +el.getAttribute('data-pin');
      var on = function () { lmHold = true; lmCity(i); };
      el.addEventListener('mouseenter', on); el.addEventListener('focus', on); el.addEventListener('click', on);
      el.addEventListener('mouseleave', function () { lmHold = false; }); el.addEventListener('blur', function () { lmHold = false; });
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { lmSeen = es[0].isIntersecting; }, { threshold: 0.25 }).observe(lineMap);
    } else { lmSeen = true; }
    lmCity(0);
    if (!reduce) setInterval(function () { if (lmSeen && !lmHold) lmCity((lmActive + 1) % lmPts.length); }, 2800);
  }

  /* ---------- cookie consent: Analytics stays off until the visitor accepts ----------
     The choice is stored as "epl-cookies" = "yes" | "no". "Cookie settings" in the footer reopens the card. */
  (function () {
    var KEY = 'epl-cookies';
    var read = function () { try { return localStorage.getItem(KEY); } catch (e) { return null; } };
    var write = function (v) { try { localStorage.setItem(KEY, v); } catch (e) {} };
    var card = null;
    var close = function () { if (!card) return; card.classList.remove('is-open'); var c = card; card = null; setTimeout(function () { c.remove(); }, 450); };
    var decide = function (yes) {
      write(yes ? 'yes' : 'no');
      if (window.eplAnalytics) window.eplAnalytics(yes);
      if (!yes) {
        /* remove Analytics cookies already set */
        document.cookie.split(';').forEach(function (c) {
          var name = c.split('=')[0].trim();
          if (/^_ga/.test(name)) ['', '; domain=' + location.hostname, '; domain=.' + location.hostname.replace(/^www\./, '')].forEach(function (d) {
            document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + d;
          });
        });
      }
      close();
    };
    var open = function () {
      if (card) return;
      var choice = read();
      card = document.createElement('section');
      card.className = 'cookies';
      card.setAttribute('role', 'dialog');
      card.setAttribute('aria-label', 'Cookie choice');
      card.innerHTML =
        '<div class="cookies__icon" aria-hidden="true"><svg viewBox="0 0 32 32"><path d="M16 3a13 13 0 1 0 13 13 5.5 5.5 0 0 1-6.2-6.2A5.5 5.5 0 0 1 16 3z"/><circle cx="11.5" cy="13" r="1.6"/><circle cx="17.5" cy="20.5" r="1.6"/><circle cx="10.5" cy="20" r="1.1"/><circle cx="19" cy="13.5" r="1.1"/></svg></div>' +
        '<div class="cookies__text"><h2>A note on cookies</h2>' +
        '<p>We would like to use Google Analytics cookies to see how this site is used and improve it. No advertising cookies, and nothing is set unless you accept.</p>' +
        (choice ? '<p class="cookies__now">Your current choice: <b>' + (choice === 'yes' ? 'accepted' : 'declined') + '</b></p>' : '') + '</div>' +
        '<div class="cookies__actions"><button type="button" class="cookies__btn cookies__btn--yes" data-cookie="yes">Accept</button>' +
        '<button type="button" class="cookies__btn" data-cookie="no">Decline</button></div>';
      card.addEventListener('click', function (ev) {
        var b = ev.target.closest('[data-cookie]');
        if (b) decide(b.getAttribute('data-cookie') === 'yes');
      });
      document.body.appendChild(card);
      requestAnimationFrame(function () { requestAnimationFrame(function () { if (card) card.classList.add('is-open'); }); });
    };
    document.querySelectorAll('[data-cookie-settings]').forEach(function (b) { b.addEventListener('click', open); });
    if (!read()) setTimeout(open, 1200);
  })();
})();
