#!/usr/bin/env python3
"""Assembles the EPL Group static pages from shared header/footer + per-page bodies.
Run: python3 build.py   Output: ../epl-group/ (plain static files, nothing to build at deploy time).
Articles: one Markdown file per article in ./insights/ (see insights/README.md)."""
import re, pathlib, json, subprocess, datetime, html as htmllib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "epl-group"
# every <path> of the logo file (traced letters with their transform + the Growth Partners lockup)
LOGO_INNER = "".join(re.findall(r"<path[^>]*/>", (OUT / "assets/logo-stencil.svg").read_text()))

def logo_svg(cls=""):
    return f'<svg class="{cls}" viewBox="0 0 1200 563" aria-hidden="true" focusable="false">{LOGO_INNER}</svg>'

ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 12L7.2 8.8" stroke="white" stroke-width="2" stroke-linecap="square"/><path d="M9 7L12 4M12 10V4H6" stroke="white" stroke-width="2" stroke-linecap="square"/></svg>'

def btn(label, href, kind="black", extra=""):
    return f'<a class="btn btn--{kind} {extra}" href="{href}"><span>{label}</span><span class="btn__icon">{ARROW}</span></a>'

def ext_btn(label, href, kind="ghost"):
    return f'<a class="btn btn--{kind}" href="{href}" target="_blank" rel="noopener"><span>{label}</span><span class="btn__icon">{ARROW}</span></a>'

NAV = [("Platforms", "platforms.html"), ("Team", "team.html"), ("Track record", "track-record.html"),
       ("Partners", "partners.html"), ("Insights", "insights.html"), ("Events", "events.html"), ("EPL Circle", "circle.html")]

SITE = "https://eplgroup.co"
LINKEDIN = "https://www.linkedin.com/company/epl-group-inc"
JOIN = "https://join.com/companies/eplgroup"
OG_IMAGE = SITE + "/assets/og-image.jpg"
BOILERPLATE = ("EPL Group is a Miami-based multi-strategy investment platform that backs companies from the first check to the factory floor "
               "through four platforms: xPL Ventures, xpansionIQ, the Permanent Capital Platform and GP Stackers. Its investors are "
               "single-family offices, high-net-worth individuals and allocators who qualify as accredited or qualified investors. "
               "Securities are offered through Finalis Securities LLC, Member FINRA / SIPC.")
ADDRESS = {"@type": "PostalAddress", "streetAddress": "1000 Brickell Avenue, Suite 715", "addressLocality": "Miami",
           "addressRegion": "FL", "postalCode": "33131", "addressCountry": "US"}
ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "EPL Group", "legalName": "EPL Group Inc.", "url": SITE + "/",
       "logo": SITE + "/apple-touch-icon.png", "description": BOILERPLATE, "address": ADDRESS, "sameAs": [LINKEDIN],
       "founder": {"@type": "Person", "name": "Jerome Davant", "jobTitle": "Managing Partner & CIO", "sameAs": ["https://www.linkedin.com/in/jeromevd/"]}}

def clean_url(path):
    return SITE + "/" if path in ("index.html", "") else SITE + "/" + path[:-5]

def ld(*items):
    graph = {"@context": "https://schema.org", "@graph": list(items)}
    return '\n  <script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False) + '</script>'

def webpage(path, title, desc, kind="WebPage"):
    return {"@type": kind, "@id": clean_url(path) + "#page", "url": clean_url(path), "name": title, "description": desc,
            "isPartOf": {"@id": SITE + "/#site"}, "about": {"@id": SITE + "/#org"}}

OG_TITLES = {}   # pages whose share title differs from the browser title

# Google Analytics 4 (EPL Group property), with Google's consent mode.
# The tag is the exact code from Analytics > Data streams > Install manually: the container
# GTM-W9FDVN8D, which is published with the Analytics ID G-CBT69W3QW3 inside it.
# The script before it sets the consent defaults, so no Analytics cookies are used until the visitor
# accepts in the cookie card (js/main.js). The choice is kept in localStorage as "epl-cookies" = "yes" | "no".
# Visitors who decline, and any copy of the site not on eplgroup.co, send nothing at all.
GA_ID = "G-CBT69W3QW3"
GTM_ID = "GTM-W9FDVN8D"
GA_TAG = f'''  <!-- Cookie consent defaults: no Analytics cookies until the visitor accepts -->
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    (function () {{
      var id = '{GA_ID}', live = /(^|\\.)eplgroup\\.co$/.test(location.hostname), choice = null;
      try {{ choice = localStorage.getItem('epl-cookies'); }} catch (e) {{}}
      window['ga-disable-' + id] = !live || choice === 'no';
      gtag('consent', 'default', {{ analytics_storage: choice === 'yes' ? 'granted' : 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' }});
      window.eplAnalytics = function (allow) {{
        window['ga-disable-' + id] = !live || !allow;
        gtag('consent', 'update', {{ analytics_storage: allow ? 'granted' : 'denied' }});
      }};
    }})();
  </script>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtm.js?id={GTM_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
  </script>
'''

def head(title, desc, path, extra_css=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{GA_TAG}  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{OG_TITLES.get(path, title)}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="EPL Group">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="EPL Group, growth partners from the first check to the factory floor">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="{OG_IMAGE}">{f"""
  <link rel="canonical" href="{clean_url(path)}">
  <meta property="og:url" content="{clean_url(path)}">""" if path != "404.html" else ""}
  <meta name="theme-color" content="#2c3a4b">
  <link rel="icon" href="favicon.ico" sizes="48x48">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="icon" href="favicon-32x32.png" type="image/png" sizes="32x32">
  <link rel="apple-touch-icon" href="apple-touch-icon.png" sizes="180x180">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/styles.css">{extra_css}
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
'''

def header(current):
    links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == current else ""}>{l}</a>' for l, h in NAV)
    mobile = "".join(f'<a href="{h}">{l}</a>' for l, h in NAV) + '<a href="investors.html">Investors</a>' + btn("Pitch us", "pitch.html")
    return f'''  <header class="nav" id="top">
    <div class="nav__inner">
      <a href="index.html" class="logo" aria-label="EPL Group home">{logo_svg()}</a>
      <nav class="nav__links" aria-label="Main">{links}</nav>
      <div class="nav__cta">
        {btn("Investors", "investors.html", "ghost")}
        {btn("Pitch us", "pitch.html")}
        <button class="nav__toggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span><span></span></button>
      </div>
      <nav class="nav__mobile" id="mobile-menu" aria-label="Mobile">{mobile}</nav>
    </div>
  </header>
'''

CLOSING = f'''
    <!-- CLOSING BAND -->
    <section class="closing" id="contact-band">
      <img class="closing__bg" src="assets/closing-band.jpg" alt="" data-parallax="0.08" width="1440" height="640" loading="lazy">
      <div class="closing__veil" aria-hidden="true"></div>
      <div class="wrap">
        <p class="closing__kicker r">Start a conversation</p>
        <h2 class="r" style="--d:1">One conversation.<br><span class="dim">A partner for decades.</span></h2>
        <p class="r" style="--d:2">Tell us about your mandate, your company or your fund. A senior partner replies personally, and every conversation stays confidential.</p>
        <div class="closing__actions r" style="--d:3">
          {btn("Pitch us", "pitch.html")}
          {btn("Investors", "investors.html", "ghost")}
        </div>
      </div>
    </section>
'''

FOOTER = f'''  <footer class="footer">
    <div class="wrap">
      <div class="footer__logo" data-logo-reveal aria-hidden="true">{logo_svg()}</div>
      <div class="footer__cols">
        <p>A Miami-based multi-strategy investment platform backing innovation from the first check to the factory floor.</p>
        <div><h4>Platforms</h4><ul>
          <li><a href="platforms.html#xpl">xPL Ventures</a></li>
          <li><a href="platforms.html#xpansioniq">xpansionIQ</a></li>
          <li><a href="platforms.html#pcp">Permanent Capital Platform</a></li>
          <li><a href="platforms.html#gp">GP Stackers</a></li></ul></div>
        <div><h4>Company</h4><ul>
          <li><a href="about.html">About</a></li>
          <li><a href="team.html">Team</a></li>
          <li><a href="track-record.html">Track record</a></li>
          <li><a href="insights.html">Insights</a></li>
          <li><a href="events.html">Events</a></li>
          <li><a href="circle.html">EPL Circle</a></li>
          <li><a href="faq.html">FAQ</a></li>
          <li><a href="{JOIN}" target="_blank" rel="noopener">Careers</a></li></ul></div>
        <div><h4>Connect</h4><ul>
          <li><a href="pitch.html">Start a conversation</a></li>
          <li><a href="investors.html">Investors: complete the form</a></li>
          <li><a href="https://xpl.partners/" rel="noopener" target="_blank">xPL Partners</a></li>
          <li><a href="{LINKEDIN}" rel="noopener" target="_blank">LinkedIn</a></li>
          <li><a href="https://epls-newsletter.beehiiv.com/" rel="noopener" target="_blank">Newsletter</a></li></ul></div>
      </div>
      <div class="footer__legal">
        <p>Securities are offered through Finalis Securities LLC, Member FINRA / SIPC. EPL Group is not a registered broker-dealer, and Finalis Securities LLC and EPL Group are separate, unaffiliated entities. This website is for information only and is not an offer or solicitation to buy or sell any security.</p>
        <p>© <span id="year">2026</span> EPL Group Inc. All rights reserved. <button type="button" class="footer__cookies" data-cookie-settings>Cookie settings</button></p>
      </div>
    </div>
  </footer>
  <script src="js/main.js" defer></script>
</body>
</html>
'''

PAGES = []   # every page written, for the sitemap

def rebase(html, prefix):
    """Pages in a sub-folder reach the shared files one level up."""
    return re.sub(r'\b(href|src|srcset|data-href|data-shot)="(?!https?:|mailto:|tel:|#|/|data:)', r'\1="' + prefix, html)

def page(filename, title, desc, current, body, closing=True, jsonld=""):
    html = head(title, desc, filename, jsonld) + header(current) + '  <main id="main">\n' + body + (CLOSING if closing else "") + '  </main>\n' + FOOTER
    depth = filename.count("/")
    if depth:
        html = rebase(html, "../" * depth)
    (OUT / filename).parent.mkdir(parents=True, exist_ok=True)
    (OUT / filename).write_text(html)
    if filename != "404.html":
        PAGES.append(filename)
    print("wrote", filename, len(html))

# ---------------------------------------------------------------- shared fragments
def section_head(num, eyebrow, title_html, side_html="", side_right=False, gap56=False, extra_cls=""):
    side = f'<div class="side{" side--right" if side_right else ""} r" style="--d:2">{side_html}</div>' if side_html else ""
    return f'''      <div class="section__head{" section__head--gap56" if gap56 else ""} {extra_cls}">
        <div class="title">
          <p class="eyebrow r">{f'<span class="num">{num}</span>' if num else ""}{eyebrow}</p>
          <h2 class="display r" style="--d:1">{title_html}</h2>
        </div>
        {side}
      </div>
'''

C = {"coral": "#eb5a5d", "navy": "#2c3a4b", "slate": "#5b6476", "light": "#e1e5eb"}
def blk(l1, lp, l2, r1, rp, r2, i=0):
    return (f'<span class="blk" aria-hidden="true" style="--l1:{C[l1]};--lp:{lp}%;--l2:{C[l2]};'
            f'--r1:{C[r1]};--rp:{rp}%;--r2:{C[r2]};--i:{i}"></span>')

FIG_BLK = [blk("coral", 62.13, "navy", "navy", 40.24, "coral", 0), blk("navy", 50.3, "coral", "coral", 55.03, "slate", 1),
           blk("slate", 57.99, "coral", "coral", 34.91, "navy", 2), blk("coral", 40.24, "navy", "light", 59.76, "coral", 3)]

FIGURES = f'''      <div class="figures r" data-counters>
        <div class="figure">{FIG_BLK[0]}<p class="figure__n coral" data-count="900" data-prefix="$" data-suffix="M+">$900M+</p><p class="figure__l">Transaction value advised</p></div>
        <div class="figure">{FIG_BLK[1]}<p class="figure__n" data-count="80" data-prefix="$" data-suffix="B+">$80B+</p><p class="figure__l">Capital formation and sell-side exposure</p></div>
        <div class="figure">{FIG_BLK[2]}<p class="figure__n" data-count="30" data-suffix="+">30+</p><p class="figure__l">Years of combined investment banking experience</p></div>
        <div class="figure">{FIG_BLK[3]}<p class="figure__n" data-count="150" data-suffix="+">150+</p><p class="figure__l">Experts in our network across three continents</p></div>
      </div>
'''

def mono(letters):
    return '<span class="pill__mono">' + "".join(f'<img src="assets/letter-{l}.svg" alt="" width="{w}" height="24">' for l, w in letters) + '</span>'

PILLS = [
    ("xpl", "xPL Ventures", "First check to pre-seed", mono([("x", 21)]), 180, 206),
    ("xpansioniq", "xpansionIQ", "Series A, US landing", mono([("i", 5), ("q", 20)]), 256, 308),
    ("pcp", "Permanent Capital Platform", "Established businesses", mono([("p", 17), ("c", 22)]), 332, 410),
    ("gp", "GP Stackers", "Emerging managers", mono([("g", 23), ("p", 17)]), 408, 512),
]

def mesh_panel(link=True):
    pills = ""
    for i, (slug, name, sub, mon, x, y) in enumerate(PILLS, start=1):
        href = f'platforms.html#{slug}'
        tag = "a" if link else "div"
        pills += f'        <{tag} class="pill" style="left:{x}px;top:{y}px;--i:{i}"{f" href=\"{href}\"" if link else ""}>{mon}<span class="pill__sep"></span><span class="pill__name">{name}</span><span class="pill__sub">{sub}</span></{tag}>\n'
    return f'''      <div class="mesh r r--fade" data-reveal-group>
        <img class="mesh__bg" src="assets/mesh.jpg" alt="" width="1200" height="640" loading="lazy">
        <svg class="mesh__connectors" viewBox="0 0 607 424" fill="none" aria-hidden="true"><path d="M0 0.75H236.093C245.426 0.75 250.093 5.41667 250.093 14.75V103.25C250.093 112.583 245.426 117.25 236.093 117.25H202.093M0 0.75H278C287.333 0.75 292 5.41667 292 14.75V205.25C292 214.583 287.333 219.25 278 219.25H244M0 0.75H555.674C565.008 0.75 569.674 5.41667 569.674 14.75V307.25C569.674 316.583 565.008 321.25 555.674 321.25H521.674M0 0.75H591.674C601.008 0.75 605.674 5.41667 605.674 14.75V409.25C605.674 418.583 601.008 423.25 591.674 423.25H423.233" stroke="white" stroke-opacity="0.75" stroke-width="1.5"/></svg>
        <div class="pill pill--root" style="left:88px;top:88px;--i:0"><span>EPL Group</span><span class="dim">One thesis</span></div>
{pills}        <p class="mesh__caption">Capital + operating advantage + software</p>
      </div>
'''

PLATFORM_NOTES = '''      <div class="platform-notes">
        <div class="r" style="--d:0"><h3>01&nbsp; xPL Ventures</h3><p>A venture studio that builds or buys software for innovation gaps in regulated industries.</p></div>
        <div class="r" style="--d:1"><h3>02&nbsp; xpansionIQ</h3><p>Series A growth capital for international B2B tech scale-ups entering the US market.</p></div>
        <div class="r" style="--d:2"><h3>03&nbsp; Permanent Capital</h3><p>Permanent capital for lower-middle-market roll-ups in established US industries, strengthened by software and AI.</p></div>
        <div class="r" style="--d:3"><h3>04&nbsp; GP Stackers</h3><p>GP-level venture co-investments alongside emerging fund managers.</p></div>
      </div>
'''

PEOPLE = [
    # name, photo, large background text, role, credential, focus, small photo, LinkedIn shown
    ("Jerome Davant", "team-jerome.png", "$200M+", "Managing Partner &amp; CIO", "30+ M&amp;A deals closed", "All platforms", False, "https://www.linkedin.com/in/jeromevd/"),
    ("Romulo Justa", "team-romulo.png", "15+ yrs", "Venture Partner, Latin America", "Founded and sold Grupo Omni", "Latin America", False, False),
    ("Geoffroy de Clisson", "team-geoffroy.png", "M&amp;A", "Venture Partner, Europe", "Ex Dalkia / Veolia Energy M&amp;A", "Europe", True, False),
    ("Sebastian Fidilio", "team-sebastian.png", "CPA", "Chief Financial Officer", "Certified Public Accountant", "Finance", False, False),
    ("James White", "team-james.png", "JW", "Investment Manager", "Deal flow and portfolio support", "Investments", False, False),
    ("Dragana Todorovska Janeva", "team-dragana.png", "7+ yrs", "Financial Models and Investor Materials", "Business planning and modelling", "Analysis", False, False),
]

def people_cards(bios=None):
    out = f'      <div class="people{" people--bios" if bios else ""}">\n'
    for i, (name, img, big, role, cred, focus, small, linkedin) in enumerate(PEOPLE):
        link = (f'\n          <a class="person__link" href="{linkedin}" target="_blank" rel="noopener">LinkedIn<span class="arr">→</span><span class="sr"> ({name})</span></a>'
                if linkedin else "")
        card = f'''        <article class="person r" style="--d:{i % 3}" data-person tabindex="0" aria-label="{name}, {role}">
          <div class="person__photo{" person__photo--sm" if small else ""}"><img src="assets/{img}" alt="Portrait of {name}" loading="lazy" width="210" height="240"></div>
          <div class="person__fade" aria-hidden="true"></div>
          <p class="person__big" aria-hidden="true">{big}</p>
          <div class="person__sel" aria-hidden="true"><b></b><b></b><b></b><b></b><i></i><i></i><i></i><i></i></div>
          <img class="person__cursor" src="assets/cursor.svg" alt="" aria-hidden="true" width="24" height="26">
          <span class="person__tag" aria-hidden="true">{name}</span>
          {"" if bios else f'<h3 class="sr">{name}</h3>'}
          <p class="person__role">{role}</p>
          <p class="person__cred">{cred}</p>
          <p class="person__focus">{focus.upper()}</p>{link}
        </article>
'''
        if bios:
            card = f'''        <div class="member">
{card}          <div class="member__text r" style="--d:{i % 3}">
            <h3>{name}</h3>
            <p class="member__role">{role}</p>
            <p>{bios[name]}</p>
          </div>
        </div>
'''
        out += card
    return out + '      </div>\n'

BARS = [("Capital raise", 32, False), ("Private credit", 50, False), ("Fund allocation", 70, False), ("Private placement", 75, True)]

def chart():
    bars = ""
    for i, (label, v, hi) in enumerate(BARS):
        left = ([200, 430, 660, 890][i] - 100) / 1010 * 100
        h = v / 75 * 330
        bars += f'        <div class="bar{" bar--hi" if hi else ""}" style="left:{left:.2f}%;height:{h:.0f}px;--i:{i}"><span class="bar__val">${v}M</span><span class="bar__label">{label}</span></div>\n'
    return f'''      <div class="chart-card r r--fade" data-reveal-group>
        <div class="chart" role="img" aria-label="Bar chart of four recent mandates: capital raise 32 million dollars, private credit 50 million, fund allocation 70 million, private placement 75 million.">
          <div class="chart__grid" aria-hidden="true"><i style="top:90px"></i><i style="top:200px"></i><i style="top:310px"></i><i style="top:420px"></i></div>
          <span class="chart__y" style="top:420px">$0M</span><span class="chart__y" style="top:310px">$25M</span><span class="chart__y" style="top:200px">$50M</span><span class="chart__y" style="top:90px">$75M</span>
          <div class="chart__bars">
{bars}          </div>
        </div>
      </div>
'''

PATHS = [
    ("Founder-owner looking for a long-term partner?", "Pitch us", "pitch.html", "founder"),
    ("Family office or allocator?", "Investors: complete the form", "investors.html", "allocator"),
    ("Early-stage founder or idea-stage team?", "Pitch us", "pitch.html", "founder"),
    ("Corporate or strategic co-investor?", "Investors: complete the form", "investors.html", "corporate"),
    ("Operator or prospective venture partner?", "Join the EPL network", "careers.html", "operator"),
]
WORDS = [("Founder-owners", "founder"), ("Allocators", "allocator"), ("Family offices", "allocator"), ("Corporates", "corporate"), ("Operators", "operator")]

def paths_grid():
    words = "".join(f'<span data-word="{k}">{w}</span>' for w, k in WORDS)
    rows = ""
    for i, (q, a, href, k) in enumerate(PATHS, start=1):
        rows += f'          <a class="path" href="{href}" data-path="{k}"><span class="n">{i:02d}</span><span class="q">{q}</span><span class="link-arrow">{a}<span class="arr">→</span></span></a>\n'
    return f'''      <div class="paths-grid r r--fade" data-paths>
        <div class="stacked">{words}<small>Work with us</small></div>
        <div class="paths">
{rows}        </div>
      </div>
'''

ROUTER_OPTS = [
    ("Founder-owner looking for a long-term partner?", "Pitch us", "pitch.html", "Great fit. Start a confidential conversation: a senior partner reads it and replies personally."),
    ("Family office or allocator?", "Investors: complete the form", "investors.html", "Tell us about your mandate and typical ticket size. We route you to the platform that fits and a partner follows up."),
    ("Early-stage founder or idea-stage team?", "Pitch us", "pitch.html", "xPL Ventures writes first checks in regulated industries. Pitch us in a few lines and we take it from there."),
    ("Corporate or strategic co-investor?", "Investors: complete the form", "investors.html", "We co-invest alongside strategics across our platforms. Complete the short form and a partner follows up."),
    ("Operator or prospective venture partner?", "Join the EPL network", "careers.html", "Operators first. Tell us where you have built, run or advised, and which platform you would strengthen."),
]

def router_panel():
    opts = ""
    for i, (q, a, href, reply) in enumerate(ROUTER_OPTS):
        opts += f'            <button type="button" class="opt{" on" if i == 0 else ""}" data-opt data-href="{href}" data-reply="{reply}" data-cta="{a}" role="radio" aria-checked="{"true" if i == 0 else "false"}"><span class="dot"></span><span class="q">{q}</span><span class="a">{a} →</span></button>\n'
    return f'''      <div class="photo-panel r r--fade" data-reveal-group>
        <img class="photo-panel__bg" src="assets/photo-motion.jpg" alt="" width="1200" height="720" loading="lazy" data-parallax="0.06">
        <figure class="pcard pcard--l"><img src="assets/partner-founder.jpg" alt="A founder-owner standing on a factory floor" loading="lazy"><figcaption><b>Founder-owner</b><a class="link-arrow" href="pitch.html">Pitch us<span class="arr">→</span></a></figcaption></figure>
        <div class="router" data-router>
          <div class="router__logo">{logo_svg()}</div>
          <h3>Which partner are you?</h3>
          <p>Pick the line that sounds like you. We route you to the right partner.</p>
          <div class="router__panel">
            <div class="router__head"><b>First conversation</b><span>Partner routing</span></div>
            <div role="radiogroup" aria-label="Which partner are you?">
{opts}            </div>
            <div class="router__reply"><img src="assets/avatar.svg" alt="" width="22" height="22"><p data-router-reply>{ROUTER_OPTS[0][3]}</p></div>
          </div>
        </div>
        <figure class="pcard pcard--r"><img src="assets/partner-family.jpg" alt="A family office principal reading at a desk" loading="lazy"><figcaption><b>Family office</b><a class="link-arrow" href="investors.html">Investors: complete the form<span class="arr">→</span></a></figcaption></figure>
      </div>
'''

def process_section(as_section=True):
    return f'''    <section class="process" id="process">
      <img class="process__bg" src="assets/photo-motion.jpg" alt="" width="1200" height="720" loading="lazy">
      <div class="process__veil" aria-hidden="true"></div>
      <div class="wrap">
        <div class="section__head">
          <div class="title">
            <p class="eyebrow r"><span class="num">06</span>What happens next?</p>
            <h2 class="display r" style="--d:1">A simple process.<br><span class="dim">Confidential from the first message.</span></h2>
          </div>
          <p class="process__note r" style="--d:2">/indicative week. every mandate<br>moves at its own pace.</p>
        </div>
        <div class="cal r r--fade" data-reveal-group>
          <div class="cal__cols" aria-hidden="true"><div>MON</div><div>TUE</div><div>WED</div><div>THU</div><div>FRI</div></div>
          <div class="cal__rule" aria-hidden="true"></div>
          <div class="cal__today" aria-hidden="true"></div>
          <ol>
            <li class="ev ev--hi ev1" style="--i:0"><b>/01 tell us about you</b><p>Short form, about<br>five minutes.</p><small>...</small></li>
            <li class="ev ev2" style="--i:1"><b>/02 partner reads it</b><p>A senior partner reads<br>it personally.</p><small>...</small></li>
            <li class="ev ev3" style="--i:2"><b>/03 first conversation</b><p>A confidential call about your mandate, company or fund.</p><small>...</small></li>
            <li class="ev ev4" style="--i:3"><b>/04 shape the partnership</b><p>Platform, structure and<br>next steps, agreed together.</p><small>...</small></li>
          </ol>
        </div>
        <div class="process__actions r">
          {btn("Pitch us", "pitch.html")}
          {btn("Investors", "investors.html", "ghost")}
        </div>
      </div>
    </section>
'''

FAQ = [
    ("Who can invest with EPL?", "Our vehicles are open to qualified and accredited investors only, including family offices and allocators. Securities are offered through Finalis Securities LLC, Member FINRA / SIPC."),
    ("Where are you based, and where do you invest?", "EPL Group is a Miami-based investment platform with venture partners in Europe and Latin America. We invest in US businesses and in international founders landing in the US, and we source through a network of experts across three continents."),
    ("What ticket sizes do you work with?", "It depends on the platform. xPL Ventures writes first checks and pre-seed rounds, xpansionIQ leads or joins Series A rounds, the Permanent Capital Platform acquires established lower-middle-market businesses, and GP Stackers co-invests at the GP level alongside emerging managers. Tell us about your mandate and we will point you to the right one."),
    ("How do you work alongside management teams?", "Operators first. Every partner has built, run or advised companies, so we work beside management on the decisions that compound: pricing, hiring, systems and software. We are not a passive cheque, and we are not a replacement for the team."),
    ("How quickly will I hear back?", "A senior partner reads every message personally. You will normally hear back within a few working days, and if your mandate is a fit we move to a first confidential conversation the same week."),
    ("Is my information kept confidential?", "Yes. Everything you share with us stays between you and the partners reviewing it. We do not circulate decks or data to third parties without your written permission."),
]

def faq_block(items=None, note="Common questions", more=True):
    items_html = ""
    for i, (q, a) in enumerate(items or FAQ):
        items_html += f'''        <div class="faq__item{" open" if i == 0 else ""}" data-faq>
          <button class="faq__q" aria-expanded="{"true" if i == 0 else "false"}"><span>{q}</span><span class="pm" aria-hidden="true"></span></button>
          <div class="faq__a"><div><p>{a}</p></div></div>
        </div>
'''
    more_html = '        <p class="faq__more"><a class="link-arrow" href="faq.html">See all questions<span class="arr">→</span></a></p>\n' if more else ""
    return f'''      <div class="faq r r--fade">
        <p class="note">{note}</p>
{items_html}{more_html}      </div>
'''

AUDIENCES = '''      <div class="audiences r r--fade">
        <div class="audience">
          <h3>For founders and operators</h3>
          <p>Tell us what you are building, where you are in your journey and what you need from a partner.</p>
          <a class="email" href="pitch.html">Pitch us<span class="arr">→</span></a>
        </div>
        <div class="audience">
          <h3>For allocators and family offices</h3>
          <p>Tell us about your mandate, typical ticket size and which platform interests you.</p>
          <a class="email" href="investors.html">Investors: complete the form<span class="arr">→</span></a>
        </div>
      </div>
'''

# ---------------------------------------------------------------- HOME
hero_words = ["EPL", "Group", "backs", "innovation", "from", "the"]
def w(text, i, dim=False):
    return f'<span class="w{" dim" if dim else ""}"><span style="--i:{i}">{text}</span></span>'

HOME_HERO = f'''    <svg class="wind-defs" width="0" height="0" aria-hidden="true" focusable="false">
      <filter id="wind" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency="0.014 0.021" numOctaves="2" seed="4" result="noise">
          <animate attributeName="baseFrequency" dur="16s" values="0.014 0.021;0.019 0.026;0.012 0.018;0.014 0.021" repeatCount="indefinite"/>
        </feTurbulence>
        <feDisplacementMap in="SourceGraphic" in2="noise" scale="9" xChannelSelector="R" yChannelSelector="G"/>
      </filter>
    </svg>
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero__grid" aria-hidden="true"><i class="h1"></i></div>
      <div class="wrap">
        <p class="hero__meta hero__meta--l">Working across the full company lifecycle</p>
        <p class="hero__meta hero__meta--r">Capital + operating advantage + software</p>
        <h1 class="hero__title" id="hero-title">
          {"".join(w(t, i) for i, t in enumerate(hero_words))}
          <span class="ann" style="--i:0">{w('<span class="ann__u">first check</span>', 6)}<a class="ann__label" href="platforms.html#xpl">xPL Ventures<span class="arr">→</span></a></span>
          {w("to", 7)}{w("the", 8)}
          <span class="ann sel-wrap">{w('<span class="sel"><span class="sel__box" aria-hidden="true"><i class="sel__h tl"></i><i class="sel__h tr"></i><i class="sel__h bl"></i><i class="sel__h br"></i></span>factory floor,<img class="sel__cursor" src="assets/cursor.svg" alt="" aria-hidden="true" width="26" height="28"><a class="sel__tag" href="platforms.html#pcp">Permanent Capital Platform</a></span>', 9)}</span>
          {w("through", 10, True)}
          <span class="ann" style="--i:1">{w('<span class="ann__u">four platforms</span>', 11, True)}<a class="ann__label" href="platforms.html">See the platforms<span class="arr">→</span></a></span>
          {w("and", 12, True)}
          <span class="ann" style="--i:2">{w('<span class="ann__u">one thesis.</span>', 13, True)}<a class="ann__label" href="#partners">Why it works<span class="arr">→</span></a></span>
        </h1>
        <p class="hero__lead">We invest across the whole life of a company, from an idea in a regulated industry to an established American business. <span class="dim">Capital works harder with operating advantage and software.</span></p>
        <div class="hero__actions">
          {btn("Pitch us", "pitch.html")}
          {btn("Investors", "investors.html", "ghost")}
        </div>
        <p class="hero__fine">Pitch us is for entrepreneurs. Investors complete a short form and a partner follows up.</p>
      </div>
      <div class="hero__tree" aria-hidden="true" data-wind>
        <div class="hero__ground"></div>
        <div class="tree-stage">
          <picture class="tl tl--trunk"><source srcset="assets/tree-stage.webp" type="image/webp"><img src="assets/tree-stage.png" alt="" width="1114" height="916"></picture>
          <picture class="tl tl--canopy"><source srcset="assets/tree-stage.webp" type="image/webp"><img src="assets/tree-stage.png" alt="" width="1114" height="916"></picture>
          <picture class="tl tl--flutter"><source srcset="assets/tree-stage.webp" type="image/webp"><img src="assets/tree-stage.png" alt="" width="1114" height="916"></picture>
          <span class="petal p1"></span><span class="petal p2"></span><span class="petal p3"></span><span class="petal p4"></span><span class="petal p5"></span><span class="petal p6"></span>
        </div>
      </div>
      <p class="hero__lockup" aria-hidden="true">EPL GROUP &nbsp;·&nbsp; GROWTH PARTNERS</p>
    </section>

    <nav class="journey" aria-label="Page sections">
      <div class="journey__band" aria-hidden="true"><i></i><i></i></div>
      <div class="journey__panel"><div class="wrap"><ol>
        <li><a href="#trust"><span class="blk" aria-hidden="true" style="--l1:#eb5a5d;--lp:64.58%;--l2:#2c3a4b;--r1:#2c3a4b;--rp:35.42%;--r2:#eb5a5d;--i:0"></span><span class="t"><span class="n" style="--i:0">01</span><span class="q" style="--i:0">Can I trust them?</span></span></a></li>
        <li><a href="#platforms"><span class="blk" aria-hidden="true" style="--l1:#2c3a4b;--lp:50%;--l2:#eb5a5d;--r1:#eb5a5d;--rp:50%;--r2:#2c3a4b;--i:1"></span><span class="t"><span class="n" style="--i:1">02</span><span class="q" style="--i:1">What do they do?</span></span></a></li>
        <li><a href="#team"><span class="blk" aria-hidden="true" style="--l1:#5b6476;--lp:60.42%;--l2:#eb5a5d;--r1:#eb5a5d;--rp:39.58%;--r2:#eb5a5d;--i:2"></span><span class="t"><span class="n" style="--i:2">03</span><span class="q" style="--i:2">Who is behind it?</span></span></a></li>
        <li><a href="#track-record"><span class="blk" aria-hidden="true" style="--l1:#eb5a5d;--lp:39.58%;--l2:#2c3a4b;--r1:#2c3a4b;--rp:60.42%;--r2:#2c3a4b;--i:3"></span><span class="t"><span class="n" style="--i:3">04</span><span class="q" style="--i:3">What have they done?</span></span></a></li>
        <li><a href="#partners"><span class="blk" aria-hidden="true" style="--l1:#2c3a4b;--lp:69.79%;--l2:#e1e5eb;--r1:#e1e5eb;--rp:30.21%;--r2:#eb5a5d;--i:4"></span><span class="t"><span class="n" style="--i:4">05</span><span class="q" style="--i:4">Is this for me?</span></span></a></li>
        <li><a href="#process"><span class="blk" aria-hidden="true" style="--l1:#e1e5eb;--lp:44.79%;--l2:#eb5a5d;--r1:#eb5a5d;--rp:55.21%;--r2:#2c3a4b;--i:5"></span><span class="t"><span class="n" style="--i:5">06</span><span class="q" style="--i:5">What happens next?</span></span></a></li>
        <li><a href="#contact"><span class="blk" aria-hidden="true" style="--l1:#eb5a5d;--lp:55.21%;--l2:#5b6476;--r1:#5b6476;--rp:44.79%;--r2:#eb5a5d;--i:6"></span><span class="t"><span class="n" style="--i:6">07</span><span class="q" style="--i:6">Anything else?</span></span></a></li>
      </ol></div></div>
    </nav>
'''

HOME = HOME_HERO + f'''
    <!-- 01 TRUST -->
    <section class="section trust" id="trust">
      <div class="trust__veil" aria-hidden="true"></div>
      <div class="wrap">
{section_head("01", "Can I trust them?", "Experience you can check. <strong>Built over careers, not cycles.</strong>")}
        <div class="trust__figures">
          <div class="trust__art" aria-hidden="true">
            <div class="trust__ground"></div>
            <div class="trust__tree" data-wind>
              <div class="tree-stage">
                <picture class="tl tl--trunk"><source srcset="assets/tree-stage.webp" type="image/webp"><img src="assets/tree-stage.png" alt="" width="1114" height="916"></picture>
                <picture class="tl tl--canopy"><source srcset="assets/tree-stage.webp" type="image/webp"><img src="assets/tree-stage.png" alt="" width="1114" height="916"></picture>
                <picture class="tl tl--flutter"><source srcset="assets/tree-stage.webp" type="image/webp"><img src="assets/tree-stage.png" alt="" width="1114" height="916"></picture>
                <span class="petal p1"></span><span class="petal p2"></span><span class="petal p3"></span><span class="petal p4"></span><span class="petal p5"></span><span class="petal p6"></span>
              </div>
            </div>
          </div>
{FIGURES}        </div>
      </div>
    </section>

    <!-- 02 PLATFORMS -->
    <section class="section" id="platforms">
      <div class="wrap">
{section_head("02", "What do they do?", "Four platforms. <strong>One connected system.</strong>", '<div class="side-row"><p class="lead" style="max-width:227px;text-align:left">Every platform plugs into the same base: capital paired with operating advantage and software.</p>' + btn("Pitch us", "pitch.html") + '</div>')}
{mesh_panel()}{PLATFORM_NOTES}      </div>
    </section>

    <!-- 03 TEAM -->
    <section class="section section--line" id="team">
      <div class="wrap">
{section_head("03", "Who is behind it?", "Operators first. <strong>Capital second.</strong>", '<p class="lead">A small senior team in Miami. Every partner has built, run or advised companies, and every partner is reachable.</p>', gap56=True)}
{people_cards()}      </div>
    </section>

    <!-- 04 TRACK RECORD -->
    <section class="section section--line" id="track-record">
      <div class="wrap">
      <div class="section__head section__head--gap56">
        <div class="title title--wide">
          <p class="eyebrow r"><span class="num">04</span>What have they done?</p>
          <h2 class="display display--md r" style="--d:1">$227M across four recent mandates. <strong>Advised by EPL partners.</strong></h2>
        </div>
        <div class="side side--narrow r" style="--d:2"><p class="lead" style="font-size:15px">Private placements, fund allocations, private credit and capital raises across software, construction and climate.</p></div>
      </div>
{chart()}      </div>
    </section>

    <!-- 05 PARTNERS (report style) -->
    <section class="section section--line report" id="partners">
      <div class="wrap">
        <div class="section__head">
          <div class="title">
            <p class="eyebrow r"><span class="num">05</span>Is this for me?</p>
            <h2 class="display r" style="--d:1;text-align:center">Five kinds of partners.<br><strong>One clear next step each.</strong></h2>
          </div>
        </div>
{router_panel()}        <div class="report__under r">
          <p>Not sure which fits? Tell us in a sentence <br>and we will route you to the right partner.</p>
          {btn("Pitch us", "pitch.html")}
        </div>
      </div>
    </section>

    <!-- 06 PROCESS -->
{process_section()}
    <!-- 07 CONTACT -->
    <section class="section" id="contact">
      <div class="wrap">
{section_head("07", "Anything else?", "Talk to us. <strong>A senior partner replies personally.</strong>", gap56=True)}
{AUDIENCES}{faq_block()}      </div>
    </section>
'''

HOME_TITLE = "EPL Group | Multi-Strategy Investment Platform in Miami"
HOME_DESC = "EPL Group is a Miami investment platform for family offices and accredited investors: venture studio, US growth capital, permanent capital and GP co-investment."
page("index.html", HOME_TITLE, HOME_DESC, "index.html", HOME,
     jsonld=ld(ORG, {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "EPL Group", "publisher": {"@id": SITE + "/#org"}},
               webpage("index.html", HOME_TITLE, HOME_DESC)))

# ---------------------------------------------------------------- PLATFORMS
PLATFORM_DETAIL = [
    ("xpl", "xPL Ventures", "First check to pre-seed", mono([("x", 21)]),
     "A venture studio that builds or buys software for innovation gaps in regulated industries.",
     ["Regulated industries move slowly because the cost of being wrong is high. That is exactly where focused software, built with people who know the rules, creates durable advantage.",
      "xPL Ventures writes the first check. We co-found, build or acquire software businesses with operators who have lived inside the industry they are now changing, and we stay through pre-seed with hands-on operating support."],
     [("Stage", "First check to pre-seed"), ("Focus", "Software in regulated industries"), ("How we help", "Build, buy and operate alongside founders")], "Pitch us", "pitch.html"),
    ("xpansioniq", "xpansionIQ", "Series A, US landing", mono([("i", 5), ("q", 20)]),
     "Series A growth capital for international B2B tech scale-ups entering the US market.",
     ["The US is the largest market for most B2B software, and the hardest to land in from abroad. Go-to-market, pricing, hiring and compliance all change at the border.",
      "xpansionIQ pairs Series A capital with a landing team: partners in Europe and Latin America who source, and a US network of operators and customers who open doors once the company is here."],
     [("Stage", "Series A"), ("Focus", "International B2B tech scale-ups"), ("How we help", "US landing, go-to-market and network")], "Pitch us", "pitch.html"),
    ("pcp", "Permanent Capital Platform", "Established businesses", mono([("p", 17), ("c", 22)]),
     "Permanent capital for lower-middle-market roll-ups in established US industries, strengthened by software and AI.",
     ["Thousands of profitable American businesses are run by founder-owners thinking about what comes next. Many have never had the software, data or systems that larger competitors take for granted.",
      "The Permanent Capital Platform acquires and combines these businesses with a long hold, then strengthens them with the software and AI tooling built across the group. Founder-owners stay involved as long as they want to."],
     [("Stage", "Established, profitable businesses"), ("Focus", "Lower-middle-market US industries"), ("How we help", "Long-hold capital, software and AI")], "Investors: complete the form", "investors.html"),
    ("gp", "GP Stackers", "Emerging managers", mono([("g", 23), ("p", 17)]),
     "GP-level venture co-investments alongside emerging fund managers.",
     ["Emerging managers see deals first, but building a firm is expensive and lonely. GP Stackers invests at the general-partner level, sharing the economics and the operating load.",
      "In return, our platforms gain a wider aperture on early-stage innovation, and our allocators gain diversified exposure to managers they could not otherwise reach."],
     [("Stage", "Emerging fund managers"), ("Focus", "GP-level venture co-investments"), ("How we help", "Capital, operations and allocator access")], "Investors: complete the form", "investors.html"),
]

def platforms_body():
    body = f'''    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow r">Platforms</p>
        <h1 class="display r" style="--d:1">Four platforms. <strong>One connected system.</strong></h1>
        <p class="lead r" style="--d:2">Every platform plugs into the same base: capital paired with operating advantage and software. Together they cover the whole life of a company: a venture studio, US market entry, permanent capital and GP-level co-investment.</p>
        <div class="page-hero__actions r" style="--d:3">{btn("Pitch us", "pitch.html")}{btn("Investors", "investors.html", "ghost")}</div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
{mesh_panel(link=False)}      </div>
    </section>
    <section class="section" style="padding-top:0">
      <div class="wrap">
'''
    for i, (slug, name, sub, mon, summary, paras, specs, cta, href) in enumerate(PLATFORM_DETAIL, start=1):
        spec = "".join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in specs)
        body += f'''        <article class="platform-detail" id="{slug}">
          <div class="platform-detail__id r">
            <p class="stage">0{i}&nbsp; {sub}</p>
            <div class="pill">{mon}<span class="pill__sep"></span><span class="pill__name">{name}</span></div>
            <h2>{summary}</h2>
          </div>
          <div class="platform-detail__body r" style="--d:1">
            {"".join(f"<p>{p}</p>" for p in paras)}
            <dl class="spec">{spec}</dl>
            <div>{btn(cta, href)}</div>
          </div>
        </article>
'''
    body += '''      </div>
    </section>
'''
    return body

PLAT_TITLE = "EPL Group Platforms | Venture, Growth, Permanent Capital, GP"
PLAT_DESC = "Four EPL Group platforms: xPL Ventures venture studio, xpansionIQ for US market entry, the Permanent Capital Platform and GP Stackers for emerging managers."
page("platforms.html", PLAT_TITLE, PLAT_DESC, "platforms.html", platforms_body(),
     jsonld=ld(webpage("platforms.html", PLAT_TITLE, PLAT_DESC), *[
         {"@type": "Service", "@id": clean_url("platforms.html") + "#" + d[0], "name": d[1], "description": d[4],
          "provider": {"@id": SITE + "/#org"}, "url": clean_url("platforms.html") + "#" + d[0]} for d in PLATFORM_DETAIL]))

# ---------------------------------------------------------------- TEAM
BIOS = [
    ("Jerome Davant", "Founder and Managing Partner", "Works across all platforms. Has closed 30+ M&amp;A deals, covering sell-side and buy-side mandates for founder-owned and sponsor-backed companies in the US and Europe. Holds a Ph.D. in International Economics Law from the University of Montpellier. Based in Miami."),
    ("Romulo Justa", "Venture Partner, Latin America", "Founded and sold Grupo Omni, after building and exiting an operating business in Latin America. Sources and leads opportunities in the region."),
    ("Geoffroy de Clisson", "Venture Partner, Europe", "Brings corporate development and acquisitions experience in energy M&amp;A from Dalkia / Veolia Energy, one of Europe's largest energy services groups. Sources and leads opportunities in Europe."),
    ("Sebastian Fidilio", "Chief Financial Officer", "Certified Public Accountant. Leads finance."),
    ("James White", "Investment Manager", "Manages deal flow and portfolio support."),
    ("Dragana Todorovska Janeva", "Associate", "Builds the financial models, business plans and investor materials."),
]
TEAM = f'''    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow r">Team</p>
        <h1 class="display r" style="--d:1">Operators first. <strong>Capital second.</strong></h1>
        <p class="lead r" style="--d:2">A small senior team in Miami. Every partner has built, run or advised companies, and every partner is reachable.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
{people_cards({n: b for n, _, b in BIOS})}      </div>
    </section>
    <section class="section section--line">
      <div class="wrap">
{section_head("", "How we work", "Three habits. <strong>Kept on every mandate.</strong>", gap56=True)}
        <div class="cards">
          <div class="card r" style="--d:0"><p class="tag">01</p><h3>A partner reads it</h3><p>No associate screens, no form letters. Every pitch, mandate and question is read by a senior partner and answered personally.</p></div>
          <div class="card r" style="--d:1"><p class="tag">02</p><h3>Operating advantage first</h3><p>We bring the software, data and people that make capital work harder, and we stay involved in the decisions that compound.</p></div>
          <div class="card r" style="--d:2"><p class="tag">03</p><h3>Confidential from the first message</h3><p>Nothing you share leaves the partners reviewing it. We do not circulate decks or data without your written permission.</p></div>
        </div>
      </div>
    </section>
    <section class="section section--line">
      <div class="wrap">
{FIGURES}      </div>
    </section>
    <section class="section section--line">
      <div class="wrap two-col">
        <div class="sticky-aside">
          <p class="eyebrow r">Join the network</p>
          <h2 class="display r" style="--d:1">150+ experts. <strong>Three continents.</strong></h2>
          <p class="lead r" style="--d:2">Operators, venture partners and industry experts work with us on sourcing, diligence and the hard operating problems inside our portfolio.</p>
          <div class="r" style="--d:3">{btn("Join the EPL network", "careers.html")}</div>
        </div>
        <div class="cards" style="grid-template-columns:1fr">
          <div class="card r"><p class="tag">Venture partners</p><h3>Source and lead in your region</h3><p>Partners in Europe and Latin America find the founders who should be landing in the US, and help them do it.</p></div>
          <div class="card r" style="--d:1"><p class="tag">Operators</p><h3>Run what we build and buy</h3><p>Leaders for the software businesses xPL Ventures builds and the companies the Permanent Capital Platform acquires.</p></div>
          <div class="card r" style="--d:2"><p class="tag">Industry experts</p><h3>Know the rules we are changing</h3><p>Regulated industries reward people who know how they really work. Diligence, introductions and advisory roles.</p></div>
        </div>
      </div>
    </section>
'''
TEAM_TITLE = "EPL Group Team | Partners, Operators and Experts"
TEAM_DESC = "Meet the EPL Group partners in Miami: M&A, energy, venture and finance leaders who have built, run or advised companies and answer personally."
page("team.html", TEAM_TITLE, TEAM_DESC, "team.html", TEAM,
     jsonld=ld(webpage("team.html", TEAM_TITLE, TEAM_DESC, "AboutPage"), *[
         {"@type": "Person", "name": pp[0], "jobTitle": htmllib.unescape(pp[3]), "worksFor": {"@id": SITE + "/#org"}, **({"sameAs": [pp[7]]} if pp[7] else {})} for pp in PEOPLE]))

# ---------------------------------------------------------------- TRACK RECORD
TRACK = f'''    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow r">Track record</p>
        <h1 class="display r" style="--d:1">$227M across four recent mandates. <strong>Advised by EPL partners.</strong></h1>
        <p class="lead r" style="--d:2">Private placements, fund allocations, private credit and capital raises across software, construction and climate.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
{FIGURES}      </div>
    </section>
    <section class="section" style="padding-top:0">
      <div class="wrap">
{section_head("", "Selected transactions", "Four mandates. <strong>One standard of care.</strong>", gap56=True)}
{chart()}        <div class="r" style="margin-top:48px">
          <table class="table">
            <thead><tr><th>Mandate</th><th>Sector</th><th>Role</th><th>Value</th></tr></thead>
            <tbody>
              <tr><td>Private placement</td><td>Climate</td><td>Advised by EPL partners</td><td class="v">$75M</td></tr>
              <tr><td>Fund allocation</td><td>Multi-strategy</td><td>Allocator mandate</td><td class="v">$70M</td></tr>
              <tr><td>Private credit</td><td>Construction</td><td>Advised by EPL partners</td><td class="v">$50M</td></tr>
              <tr><td>Capital raise</td><td>Software</td><td>Advised by EPL partners</td><td class="v">$32M</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
    <section class="section section--line">
      <div class="wrap">
{section_head("", "Before EPL", "Thirty years of <strong>capital formation and sell-side work.</strong>", '<p class="lead">Before founding EPL, the partners advised on more than $900M of transaction value and worked on capital formation and sell-side mandates with more than $80B of exposure across investment banking careers.</p>', gap56=True)}
        <div class="cards">
          <div class="card r"><p class="tag">M&amp;A</p><h3>30+ deals closed</h3><p>Sell-side and buy-side mandates for founder-owned and sponsor-backed companies in the US and Europe.</p><p class="meta">Jerome Davant, Managing Partner &amp; CIO</p></div>
          <div class="card r" style="--d:1"><p class="tag">Energy</p><h3>Ex Dalkia / Veolia Energy M&amp;A</h3><p>Corporate development and acquisitions inside one of Europe's largest energy services groups.</p><p class="meta">Geoffroy de Clisson, Venture Partner</p></div>
          <div class="card r" style="--d:2"><p class="tag">Founder</p><h3>Founded and sold Grupo Omni</h3><p>Fifteen years building and exiting an operating business in Latin America before joining EPL.</p><p class="meta">Romulo Justa, Venture Partner</p></div>
        </div>
      </div>
    </section>
'''
TRACK_TITLE = "EPL Group Track Record | $227M Across Four Recent Mandates"
TRACK_DESC = "$227M across four recent mandates advised by EPL partners: private placements, fund allocations, private credit and capital raises."
page("track-record.html", TRACK_TITLE, TRACK_DESC, "track-record.html", TRACK, jsonld=ld(webpage("track-record.html", TRACK_TITLE, TRACK_DESC)))

# ---------------------------------------------------------------- PARTNERS
PARTNERS = f'''    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow r">Partners</p>
        <h1 class="display r" style="--d:1">Five kinds of partners. <strong>One clear next step each.</strong></h1>
        <p class="lead r" style="--d:2">Founder-owners, allocators, family offices, corporates and operators each have one clear way in. Pick the line that sounds like you.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
{paths_grid()}      </div>
    </section>
    <section class="section report" style="padding-top:0">
      <div class="wrap">
{router_panel()}        <div class="report__under r">
          <p>Not sure which fits? Tell us in a sentence <br>and we will route you to the right partner.</p>
          {btn("Pitch us", "pitch.html")}
        </div>
      </div>
    </section>
{process_section()}    <section class="section">
      <div class="wrap">
{AUDIENCES}{faq_block()}      </div>
    </section>
'''
PART_TITLE = "Partner with EPL Group | Founders, Family Offices, Allocators"
PART_DESC = "Founder-owners, family offices, allocators, corporates and operators: find your next step with EPL Group, a Miami multi-strategy investment platform."
page("partners.html", PART_TITLE, PART_DESC, "partners.html", PARTNERS, jsonld=ld(webpage("partners.html", PART_TITLE, PART_DESC)))

# ---------------------------------------------------------------- INSIGHTS
# Every Markdown file in ./insights/ becomes an article page and a card on the Insights page, newest first.
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def load_articles():
    arts = []
    for f in sorted((HERE / "insights").glob("*.md")):
        if f.name.lower() == "readme.md":
            continue
        raw = f.read_text().replace("\r\n", "\n")
        m = re.match(r"\s*---\n(.*?)\n---\n(.*)", raw, re.S)
        meta, body = {}, raw
        if m:
            body = m.group(2)
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip().strip('"')
        h1 = re.match(r"\s*#\s+(.+)\n", body)
        if h1:                                   # a leading "# Title" is the title, not body text
            meta.setdefault("title", h1.group(1).strip())
            body = body[h1.end():]
        title = meta.get("title") or f.stem.replace("-", " ").capitalize()
        try:
            date = datetime.date.fromisoformat(meta.get("date", ""))
        except ValueError:
            date = datetime.date.fromtimestamp(f.stat().st_mtime)
        out = subprocess.run(["pandoc", "-f", "markdown", "-t", "html", "--no-highlight"],
                             input=body, text=True, capture_output=True, check=True).stdout
        out = re.sub(r"<(/?)h1\b", r"<\1h2", out)   # the page title is the only H1
        text = re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", out))).strip()
        summary = meta.get("summary") or (text[:177].rsplit(" ", 1)[0] + "…" if len(text) > 180 else text)
        arts.append({"slug": slugify(meta.get("slug") or f.stem), "title": title, "date": date, "tag": meta.get("tag", "Insight"),
                     "author": meta.get("author", "EPL Group"), "summary": summary, "html": out,
                     "minutes": max(1, round(len(text.split()) / 220))})
    return sorted(arts, key=lambda a: (a["date"], a["title"]), reverse=True)

ARTICLES = load_articles()

def esc(t):
    return htmllib.escape(t, quote=True)

for a in ARTICLES:
    path = f'insights/{a["slug"]}.html'
    nice = f'{a["date"].day} {MONTHS[a["date"].month - 1]} {a["date"].year}'
    others = [o for o in ARTICLES if o is not a][:3]
    more = ""
    if others:
        more = '''    <section class="section section--line">
      <div class="wrap">
        <p class="eyebrow r">More insights</p>
        <div class="post-list">
''' + "".join(f'''          <a class="post r" href="insights/{o["slug"]}.html"><span class="date">{o["date"]:%Y-%m}</span><div><h3>{esc(o["title"])}</h3><p>{esc(o["summary"])}</p></div><span class="tag">{esc(o["tag"])}</span></a>
''' for o in others) + '''        </div>
      </div>
    </section>
'''
    body = f'''    <section class="page-hero article-hero">
      <div class="wrap">
        <p class="eyebrow r"><a href="insights.html">Insights</a><span aria-hidden="true"> / </span>{esc(a["tag"])}</p>
        <h1 class="display r" style="--d:1">{esc(a["title"])}</h1>
        <p class="article__meta r" style="--d:2"><time datetime="{a["date"].isoformat()}">{nice}</time><span>{esc(a["author"])}</span><span>{a["minutes"]} min read</span></p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <article class="article">
{a["html"]}        </article>
        <p class="article__back"><a class="link-arrow" href="insights.html"><span class="arr">←</span>All insights</a></p>
      </div>
    </section>
{more}'''
    title = f'{a["title"]} | EPL Group'
    author = ({"@type": "Person", "name": a["author"]} if a["author"] != "EPL Group" else {"@id": SITE + "/#org"})
    page(path, esc(title), esc(a["summary"]), "insights.html", body,
         jsonld=ld({"@type": "Article", "@id": clean_url(path) + "#article", "headline": a["title"], "description": a["summary"],
                    "datePublished": a["date"].isoformat(), "author": author, "publisher": {"@id": SITE + "/#org"},
                    "mainEntityOfPage": clean_url(path), "articleSection": a["tag"]}, ORG))

# ---- newsletter feed (beehiiv). Posts are baked in at build time and refreshed in the visitor's browser,
# so a new issue shows on the Insights page without a new upload.
FEED_URL = "https://rss.beehiiv.com/feeds/4HLKRQItkZ.xml"
NEWSLETTER_URL = "https://epls-newsletter.beehiiv.com/"
NEWSLETTER_NAME = "Operating Advantage"
FEED_CACHE = HERE / "insights" / "feed-cache.xml"

def load_feed():
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime
    try:
        raw = subprocess.run(["curl", "-sS", "-f", "-m", "25", FEED_URL], capture_output=True, text=True, check=True).stdout
        ET.fromstring(raw)
        FEED_CACHE.write_text(raw)
    except Exception as e:                      # offline build: use the last copy
        print("feed not reachable, using the saved copy:", type(e).__name__)
        raw = FEED_CACHE.read_text() if FEED_CACHE.exists() else "<rss><channel></channel></rss>"
    posts = []
    for it in ET.fromstring(raw).iter("item"):
        get = lambda t: (it.findtext(t) or "").strip()
        link = get("link")
        if not link.startswith("https://"):
            continue
        try:
            date = parsedate_to_datetime(get("pubDate")).date()
        except Exception:
            continue
        enc = it.find("enclosure")
        img = enc.get("url", "") if enc is not None and enc.get("type", "").startswith("image/") else ""
        posts.append({"title": get("title"), "summary": get("description"), "link": link, "date": date,
                      "img": img if img.startswith("https://") else "", "tag": "Newsletter", "external": True})
    return posts

FEED_POSTS = load_feed()
ALL_POSTS = sorted(FEED_POSTS + [{"title": a["title"], "summary": a["summary"], "link": f'insights/{a["slug"]}.html', "date": a["date"],
                                  "img": "", "tag": a["tag"], "external": False} for a in ARTICLES],
                   key=lambda x: (x["date"], x["title"]), reverse=True)

def long_date(d):
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"

def post_row(x, i=0):
    ext = ' target="_blank" rel="noopener"' if x["external"] else ""
    return (f'          <a class="post r" style="--d:{i % 3}" href="{esc(x["link"])}"{ext}><span class="date">{x["date"]:%Y-%m}</span>'
            f'<div><h3>{esc(x["title"])}</h3><p>{esc(x["summary"])}</p></div><span class="tag">{esc(x["tag"])}</span></a>\n')

def featured(x):
    ext = ' target="_blank" rel="noopener"' if x["external"] else ""
    img = (f'<img src="{esc(x["img"])}" alt="" width="1200" height="630" onerror="this.parentNode.classList.add(\'is-empty\');this.remove()">'
           if x["img"] else "")
    return f'''        <a class="issue r" href="{esc(x["link"])}"{ext}>
          <div class="issue__img{"" if x["img"] else " is-empty"}">{img}</div>
          <div class="issue__body">
            <p class="issue__kicker">Latest {"issue" if x["external"] else "article"}<span>{NEWSLETTER_NAME if x["external"] else esc(x["tag"])}</span></p>
            <h2>{esc(x["title"])}</h2>
            <p>{esc(x["summary"])}</p>
            <p class="issue__meta"><time datetime="{x["date"].isoformat()}">{long_date(x["date"])}</time><span class="link-arrow">Read the {"issue" if x["external"] else "article"}<span class="arr">→</span></span></p>
          </div>
        </a>
'''

rows = "".join(post_row(x, i) for i, x in enumerate(ALL_POSTS[1:]))
baked = json.dumps([{**x, "date": x["date"].isoformat()} for x in ALL_POSTS], ensure_ascii=False).replace("</", "<\\/")
INSIGHTS = f'''    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow r">Insights</p>
        <h1 class="display r" style="--d:1">Notes from the partners. <strong>One thesis, written down.</strong></h1>
        <p class="lead r" style="--d:2">{NEWSLETTER_NAME} is the EPL Group newsletter on venture, permanent capital and US expansion. Where capital meets operating know-how, with one question a week answered with data.</p>
        <div class="page-hero__actions r" style="--d:3">{ext_btn("Subscribe to the newsletter", NEWSLETTER_URL, "black")}</div>
      </div>
    </section>
    <section class="section">
      <div class="wrap" data-insights data-feed="{FEED_URL}" data-newsletter="{NEWSLETTER_NAME}">
        <div data-insights-featured>
{featured(ALL_POSTS[0]) if ALL_POSTS else '        <p class="lead">The first issue is on its way.</p>' + chr(10)}        </div>
        <div class="post-wrap" data-insights-more{"" if rows else " hidden"}>
          <p class="eyebrow">Earlier issues and articles</p>
          <div class="post-list" data-insights-list>
{rows}          </div>
        </div>
        <script type="application/json" data-insights-data>{baked}</script>
      </div>
    </section>
'''
INS_TITLE = "EPL Group Insights | Venture, Permanent Capital, US Expansion"
INS_DESC = "Operating Advantage, the EPL Group newsletter: notes from the partners on venture studios, permanent capital, US market entry and emerging fund managers."
page("insights.html", INS_TITLE, INS_DESC, "insights.html", INSIGHTS,
     jsonld=ld(webpage("insights.html", INS_TITLE, INS_DESC, "CollectionPage"), *[
         {"@type": "BlogPosting", "headline": x["title"], "description": x["summary"], "datePublished": x["date"].isoformat(),
          "url": x["link"] if x["external"] else clean_url(x["link"]), "publisher": {"@id": SITE + "/#org"}} for x in ALL_POSTS]))

FAQ_ALL = [
    ("What is EPL Group?", "EPL Group is a multi-strategy investment platform based in Miami, Florida. It runs four platforms, xPL Ventures, xpansionIQ, the Permanent Capital Platform and GP Stackers, that back companies from the first check to the factory floor."),
    ("Who invests with EPL Group?", "Single-family offices, high-net-worth individuals and allocators who are qualified or accredited investors. Onboarding is by approval."),
    ("What platforms does EPL Group operate?", "xPL Ventures builds or buys software for regulated industries. xpansionIQ pairs Series A capital with a landing team for international B2B tech companies entering the US. The Permanent Capital Platform acquires and holds founder-owned lower-middle-market US businesses. GP Stackers co-invests at the general-partner level alongside emerging fund managers."),
    ("What is a venture studio?", "A venture studio builds companies in-house, rather than only investing in companies founders have already started. xPL Ventures is EPL Group's venture studio for software in regulated industries."),
    ("What does permanent capital mean?", "Permanent capital is capital with no fixed exit date. The Permanent Capital Platform buys profitable, founder-owned US businesses to hold for the long term, and founder-owners can stay involved as long as they wish."),
    ("What is GP-level co-investment?", "It means investing alongside a fund manager at the general-partner level, sharing the manager's economics and operating load. GP Stackers applies this to emerging fund managers."),
    ("Is EPL Group a broker-dealer?", "No. EPL Group is not a registered broker-dealer. Securities are offered through Finalis Securities LLC, Member FINRA / SIPC. Finalis Securities LLC and EPL Group are separate, unaffiliated entities."),
    ("What are the minimums, fees and expected returns?", "This website does not state them. They vary by vehicle and are disclosed in the definitive offering documents to eligible investors. EPL Group does not promise returns."),
    ("What are the risks?", "Private investments can lose value and you can lose the entire amount invested. Early-stage ventures carry a high risk of total loss. Private investments are generally illiquid."),
    ("How do I get started?", "Complete the investor form, which takes about five minutes. A partner follows up about your mandate, and a senior partner replies personally. Conversations are confidential."),
    ("I am a founder. Can I pitch EPL Group?", "Yes. Use the Pitch us page. Senior partners read every pitch and reply personally, and nothing is shared beyond the reviewing partners without your written permission."),
    ("Where is EPL Group located?", "EPL Group Inc. is based at 1000 Brickell Avenue, Suite 715, Miami, Florida 33131."),
]
# ---------------------------------------------------------------- ABOUT
FACTS = [("Legal name", "EPL Group Inc."), ("What it is", "A multi-strategy investment platform"),
         ("Headquarters", "1000 Brickell Avenue, Suite 715, Miami, Florida 33131"),
         ("Platforms", "xPL Ventures, xpansionIQ, Permanent Capital Platform, GP Stackers"),
         ("Investor base", "Single-family offices, high-net-worth individuals and allocators who are qualified or accredited"),
         ("Leadership", "Jerome Davant, Managing Partner &amp; CIO"), ("Advisory practice", "EPL Advisory, founded in 2019"),
         ("Regulatory structure", "Securities offered through Finalis Securities LLC, Member FINRA/SIPC"),
         ("Investor contact", '<a href="investors.html">Investor onboarding form</a>'), ("Facts current as of", '<time datetime="2026-11-12">12 November 2026</time>')]
LIFE = [
    ("xpl", "First check to pre-seed", "A founder with an idea", "xPL Ventures", mono([("x", 21)])),
    ("xpansioniq", "Series A, US landing", "An international scale-up", "xpansionIQ", mono([("i", 5), ("q", 20)])),
    ("pcp", "Established businesses", "A business owner planning succession", "Permanent Capital Platform", mono([("p", 17), ("c", 22)])),
    ("gp", "Emerging managers", "A fund manager raising capital", "GP Stackers", mono([("g", 23), ("p", 17)])),
]
LIFE_HTML = "".join(
    f'''            <li style="--i:{i}"><span class="ab-life__dot">{m}</span><p class="ab-life__stage">0{i + 1}&nbsp; {st}</p><h3>{who}</h3><a class="link-arrow" href="platforms.html#{slug}">{plat}<span class="arr">→</span></a></li>
''' for i, (slug, st, who, plat, m) in enumerate(LIFE))
WORK = [("read", "A partner reads your message and replies personally."),
        ("choose", "You choose the platform that fits your mandate, and we explain how it decides what to fund."),
        ("lock", "Your conversation stays confidential, and nothing is circulated without your written permission.")]
ICONS = {'read': '<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="5" y="8" width="22" height="16" rx="2"/><path d="M5 10l11 8 11-8"/></svg>', 'choose': '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="11"/><path d="M20.5 11.5l-2.8 6.2-6.2 2.8 2.8-6.2z"/></svg>', 'lock': '<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="7" y="14" width="18" height="13" rx="2"/><path d="M11 14v-3a5 5 0 0 1 10 0v3"/><path d="M16 19v3"/></svg>'}
WORK_HTML = "".join(
    f'''          <div class="ab-work__item r" style="--d:{i}"><span class="ab-work__icon">{ICONS[k]}</span><span class="ab-work__n">0{i + 1}</span><p>{t}</p></div>
''' for i, (k, t) in enumerate(WORK))
ABOUT = f'''    <section class="page-hero page-hero--dark ab-hero">
      <picture><source srcset="assets/miami-skyline.webp" type="image/webp"><img class="page-hero__photo" src="assets/miami-skyline.jpg" alt="" width="1600" height="900"></picture>
      <div class="page-hero__veil" aria-hidden="true"></div>
      <div class="wrap">
        <p class="eyebrow r">About EPL Group</p>
        <h1 class="display r" style="--d:1">Operators first. <strong>Capital second.</strong></h1>
        <p class="lead r" style="--d:2">EPL Group is a small senior team in Miami investing across a company's whole life.</p>
        <p class="ab-hero__pin r" style="--d:3"><span aria-hidden="true"></span>1000 Brickell Avenue, Miami, Florida</p>
      </div>
    </section>

    <section class="section ab-def">
      <div class="wrap">
        <div class="ab-def__grid r">
          <span class="ab-def__blk" aria-hidden="true">{FIG_BLK[0]}</span>
          <p class="definition r">EPL Group is a multi-strategy investment platform based in Miami, Florida. It runs four platforms, xPL Ventures, xpansionIQ, the Permanent Capital Platform and GP Stackers, so that capital, operating advantage and software reach a company at the stage where they matter most.</p>
        </div>
        <div class="ab-stats r" style="--d:1">
          <div><b>4</b><span>Platforms, one connected system</span></div>
          <div><b>2019</b><span>EPL Advisory founded</span></div>
          <div><b>Miami</b><span>Headquarters on Brickell Avenue</span></div>
        </div>
      </div>
    </section>

    <section class="section section--line">
      <div class="wrap">
{section_head("", "Why we built it this way", "One senior team <strong>across a company's whole life.</strong>", '<p class="lead">Most investors meet a company at one stage and leave at the next. We chose to build one connected system instead.</p>', gap56=True)}
        <div class="ab-life r r--fade" data-reveal-group>
          <img class="ab-life__bg" src="assets/mesh.jpg" alt="" width="1200" height="640" loading="lazy">
          <ol class="ab-life__track">
{LIFE_HTML}          </ol>
          <div class="ab-life__base"><b>One senior team</b><span>One base of capital, operating advantage and software</span></div>
        </div>
        <div class="two-col ab-life__text">
          <p class="lead r">A founder with an idea, an international scale-up, a business owner planning succession and a fund manager raising capital each work with one senior team, on one base of capital, operating advantage and software.</p>
          <p class="lead r" style="--d:1">Every partner has built, run or advised companies. We stay involved in the decisions that compound, and we use software, data and people to make capital work harder.</p>
        </div>
      </div>
    </section>

    <section class="section ab-work">
      <img class="process__bg" src="assets/photo-motion.jpg" alt="" width="1200" height="720" loading="lazy">
      <div class="process__veil" aria-hidden="true"></div>
      <div class="wrap">
{section_head("", "What working with us looks like", "A partner, a clear choice <strong>and your confidence kept.</strong>", gap56=True)}
        <div class="ab-work__grid">
{WORK_HTML}        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap ab-split">
        <div class="ab-panel r">
          <p class="eyebrow">Who invests with us</p>
          <ul class="ab-who">
            <li>{FIG_BLK[0]}Single-family offices</li>
            <li>{FIG_BLK[1]}High-net-worth individuals</li>
            <li>{FIG_BLK[2]}Allocators</li>
          </ul>
          <p>Single-family offices, high-net-worth individuals and allocators. Our vehicles are open to qualified and accredited investors only, by approval.</p>
          <p class="ab-badge">Qualified and accredited investors only</p>
        </div>
        <div class="ab-panel ab-panel--dark r" style="--d:1">
          <p class="eyebrow">How we are regulated</p>
          <div class="ab-reg" aria-hidden="true">
            <div class="ab-reg__box"><b>EPL Group</b><span>Not a registered broker-dealer</span></div>
            <div class="ab-reg__gap"><i></i><span>Separate, unaffiliated entities</span><i></i></div>
            <div class="ab-reg__box ab-reg__box--alt"><b>Finalis Securities LLC</b><span>Member FINRA / SIPC</span></div>
          </div>
          <p>EPL Group is not a registered broker-dealer. Securities are offered through Finalis Securities LLC, Member FINRA / SIPC. Finalis Securities LLC and EPL Group are separate, unaffiliated entities.</p>
        </div>
      </div>
    </section>

    <section class="section section--line">
      <div class="wrap">
{section_head("", "Facts", "EPL Group <strong>at a glance.</strong>", gap56=True)}
        <div class="ab-facts r">
          <table class="table table--facts">
            <caption class="sr">EPL Group at a glance</caption>
            <thead><tr><th scope="col">Fact</th><th scope="col">Detail</th></tr></thead>
            <tbody>
''' + "".join(f'              <tr><th scope="row">{k}</th><td>{v}</td></tr>\n' for k, v in FACTS) + f'''            </tbody>
          </table>
        </div>
        <div class="page-hero__actions r">{btn("Meet the team", "team.html")}{btn("Investors: complete the form", "investors.html", "ghost")}</div>
      </div>
    </section>
'''
ABOUT_TITLE = "About EPL Group | Miami Multi-Strategy Investment Platform"
ABOUT_DESC = "Meet EPL Group: a small senior team in Miami running four investment platforms, who invests with it and how it is regulated."
page("about.html", ABOUT_TITLE, ABOUT_DESC, "about.html", ABOUT,
     jsonld=ld(ORG, webpage("about.html", ABOUT_TITLE, ABOUT_DESC, "AboutPage")))

# ---------------------------------------------------------------- FAQ
FAQ_PAGE = f'''    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow r">FAQ</p>
        <h1 class="display r" style="--d:1">Frequently asked <strong>questions.</strong></h1>
        <p class="lead r" style="--d:2">What EPL Group is, who can invest, how its four platforms work, how it is regulated and how to get started.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
{faq_block(FAQ_ALL, note="All questions", more=False)}      </div>
    </section>
    <section class="section section--line" style="padding-top:0">
      <div class="wrap">
{AUDIENCES}      </div>
    </section>
'''
FAQ_TITLE = "EPL Group FAQ | Platforms, Eligibility and Regulation"
FAQ_DESC = "Answers on what EPL Group is, who can invest, how its four platforms work, how it is regulated and how to get started."
page("faq.html", FAQ_TITLE, FAQ_DESC, "faq.html", FAQ_PAGE,
     jsonld=ld(webpage("faq.html", FAQ_TITLE, FAQ_DESC), {"@type": "FAQPage", "@id": clean_url("faq.html") + "#faq", "mainEntity": [
         {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_ALL]}))


# ---------------------------------------------------------------- FORMS
def pipefy_embed(form_id, title, height, height_mobile, height_small, kicker, heading, text, button, card_title, card_sub, help_mail, shot):
    # The form loads in place on the site. Inside another page's frame (a preview) or without
    # JavaScript, the panel with a button to the same form stays instead of an empty frame.
    url = f"https://app.pipefy.com/public/form/{form_id}"
    # heights given: the frame shows the whole form. None: fixed box, the form scrolls inside it.
    sizes = f' style="--embed-h:{height}px;--embed-h-m:{height_mobile}px;--embed-h-s:{height_small}px"' if height else ""
    return f'''<div class="ev-formcard ev-formcard--page">
          <div class="ev-formcard__head">
            <div>
              <h3>{card_title}</h3>
              <p>{card_sub}</p>
            </div>
            <a class="ev-formcard__open" href="{url}" target="_blank" rel="noopener">Open in a new tab<span class="arr">→</span></a>
          </div>
          <div class="ev-embed ev-embed--page" data-embed data-src="{url}?embedded=true" data-shot="assets/form-{shot}.webp"{sizes}>
            <div class="ev-embed__fallback">
              <p class="ev-kicker">{kicker}</p>
              <h4>{heading}</h4>
              <p class="ev-embed__hint">{text}</p>
              {ext_btn(button, url, "coral")}
              <p class="ev-embed__fine">Opens in a new tab.</p>
            </div>
            <p class="ev-embed__loading" aria-hidden="true">Loading the form…</p>
            <iframe title="{title}" loading="lazy" frameborder="0"></iframe>
          </div>
          <p class="ev-formcard__foot">Trouble seeing the form? <a href="{url}" target="_blank" rel="noopener">Open it in a new tab</a>.</p>
          </div>'''

def form_page(filename, title, desc, eyebrow, h1, lead, main_html, sidebar):
    body = f'''    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow r">{eyebrow}</p>
        <h1 class="display r" style="--d:1">{h1}</h1>
        <p class="lead r" style="--d:2">{lead}</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap two-col two-col--form">
        <div>
          {main_html}
        </div>
        <aside class="sticky-aside">{sidebar}</aside>
      </div>
    </section>
'''
    page(filename, title, desc, filename, body, jsonld=ld(webpage(filename, title, desc)))

PITCH_SIDE = f'''
          <p class="eyebrow r">What happens next</p>
          <h2 class="display r" style="--d:1">A simple process. <strong>Confidential from the first message.</strong></h2>
          <ol class="r" style="--d:2;display:flex;flex-direction:column;gap:14px;font-family:var(--mono);font-size:13px;color:var(--ink-soft)">
            <li>/01 &nbsp;tell us about you (about five minutes)</li>
            <li>/02 &nbsp;a senior partner reads it personally</li>
            <li>/03 &nbsp;a confidential first conversation</li>
            <li>/04 &nbsp;platform, structure and next steps, agreed together</li>
          </ol>
'''
form_page("pitch.html", "Pitch EPL Group | Venture and Growth Capital for Founders", "Founders and operators: pitch EPL Group. A senior partner reads every pitch personally, from first checks to Series A US landing and long-term capital.",
          "Pitch us", "Tell us what you are building. <strong>A partner reads it personally.</strong>",
          "For founders and operators. Tell us what you are building, where you are in your journey and what you need from a partner.",
          pipefy_embed("czfdp_CJ", "Pitch EPL", 820, 850, 870, "Pitch form", "Tell us what you are building",
                       "Name, company, a link to your site or deck, your stage, and a few lines on what you need from a partner.", "Open the pitch form",
                       "Pitch form", "For founders and operators. Takes about 5 minutes.", "", "pitch"),
          PITCH_SIDE)

INV_SIDE = f'''
          <p class="eyebrow r">For allocators and family offices</p>
          <h2 class="display r" style="--d:1">Tell us about your mandate. <strong>A partner follows up.</strong></h2>
          <p class="lead r" style="--d:2">Our vehicles are open to qualified and accredited investors only. Securities are offered through Finalis Securities LLC, Member FINRA / SIPC.</p>
'''
form_page("investors.html", "Invest with EPL Group | Family Office and Allocator Access", "Family offices, allocators and accredited investors: complete the EPL Group onboarding form and a partner follows up about your mandate.",
          "Investors", "Complete the form. <strong>A partner follows up.</strong>",
          "For allocators and family offices. Tell us about your mandate, typical ticket size and which platform interests you.",
          pipefy_embed("qyeXlWs4", "Investor onboarding", None, None, None, "Investor onboarding", "Tell us about your mandate",
                       "For qualified investors only, by approval. The form takes about 5 minutes and includes the December events in Miami.", "Open the investor form",
                       "Investor onboarding", "For qualified investors only, by approval. Takes about 5 minutes.", "", "investor"),
          INV_SIDE)

CAREERS_SIDE = f'''
          <p class="eyebrow r">Join the EPL network</p>
          <h2 class="display r" style="--d:1">Operators first. <strong>Always.</strong></h2>
          <p class="lead r" style="--d:2">Venture partners source and lead in their region, operators run what we build and buy, and industry experts help us with diligence inside the industries they know. Every role starts with a conversation with a partner.</p>
          <div class="r" style="--d:3">{btn("Meet the team", "team.html", "ghost")}</div>
'''
CAREERS_MAIN = f'''<div class="ev-formcard ev-formcard--page join-card r">
            <p class="ev-kicker">Applications</p>
            <h3>Open roles and network applications are on JOIN.</h3>
            <p>See what is open, tell us where you have built, run or advised, and which platform you would strengthen. A partner reads every application.</p>
            <div>{ext_btn("See open roles on JOIN", JOIN, "black")}</div>
            <p class="ev-embed__fine">Opens in a new tab.</p>
          </div>'''
form_page("careers.html", "Careers | EPL Group", "Join the EPL network as a venture partner, operator or industry expert.",
          "Careers", "Join the EPL network. <strong>Operators first.</strong>",
          "For operators and prospective venture partners. Tell us where you have built, run or advised, and which platform you would strengthen.",
          CAREERS_MAIN, CAREERS_SIDE)

# ---------------------------------------------------------------- THANKS / 404
page("404.html", "Page not found | EPL Group", "The page you were looking for could not be found.", "", f'''    <section class="page-hero error-page">
      <div class="wrap">
        <p class="eyebrow r">404</p>
        <h1 class="display r" style="--d:1">That page is not here. <strong>The partners are.</strong></h1>
        <p class="lead r" style="--d:2">The link may be old or mistyped. Head back to the homepage or start a conversation.</p>
        <div class="page-hero__actions r" style="--d:3">{btn("Back to home", "index.html", "ghost")}{btn("Pitch us", "pitch.html")}</div>
      </div>
    </section>
''', closing=False)


# ---------------------------------------------------------------- EVENTS (December in Miami)
# Registration for both events runs only through the EPL investor onboarding form (Pipefy).
PIPEFY_FORM = "https://app.pipefy.com/public/form/qyeXlWs4"

RING = '<svg class="ev-cal__ring" viewBox="0 0 124 86" aria-hidden="true"><path pathLength="1" d="M70 7C102 3 120 22 118 44C116 70 88 82 58 80C26 78 5 64 8 40C11 14 44 3 80 9"/></svg>'

def calendar():
    dows = [("Mon", 0), ("Tue", 1), ("Wed", 0), ("Thu", 1), ("Fri", 0), ("Sat", 0), ("Sun", 0)]
    out = "".join(f'<span class="ev-cal__dow{" hot" if h else ""}">{d}</span>' for d, h in dows)
    days = [(30, "out")] + [(d, "") for d in range(1, 32)] + [(1, "out"), (2, "out"), (3, "out")]
    for i, (d, kind) in enumerate(days):
        cls = "ev-cal__day" + (" wk1" if i < 7 and kind != "out" else "") + (" out" if kind else "") + (" last" if i >= 28 else "")
        if kind == "" and d in (1, 3):
            key = "dec1" if d == 1 else "dec3"
            label = "Tuesday 1 December: private dinner, Key Biscayne" if d == 1 else "Thursday 3 December: breakfast debate, Downtown Miami"
            out += (f'<a class="{cls}" href="#{key}" data-ev="{key}" aria-label="{label}" style="--dl:{1.1 if d == 1 else 1.5}s">'
                    f'{d}{RING.replace("<path", "<path style=\"animation-delay:var(--dl)\"")}<i class="ev-cal__dot"></i></a>')
        else:
            out += f'<span class="{cls}" aria-hidden="true">{d}</span>'
    return out

EVENTS = f"""    <section class="ev-hero" aria-labelledby="ev-title">
      <picture class="ev-hero__bg" aria-hidden="true"><source srcset="assets/miami-skyline.webp" type="image/webp"><img src="assets/miami-skyline.jpg" alt="" width="2048" height="2048"></picture>
      <div class="ev-hero__shade" aria-hidden="true"></div>
      <div class="wrap">
        <div class="ev-hero__grid">
          <div class="ev-hero__copy">
            <p class="ev-eyebrow ev-rise" style="--i:0">Mark your calendar &nbsp;·&nbsp; Miami</p>
            <h1 id="ev-title" class="ev-rise" style="--i:1">December in Miami.</h1>
            <p class="ev-hero__sub ev-rise" style="--i:2">Two conversations for family offices and dealmakers</p>
            <p class="ev-hero__lead ev-rise" style="--i:3">Two small, invite-only gatherings EPL is hosting in Miami during Art Basel: a private dinner in Key Biscayne and a closed-room debate in Downtown Miami. Seats are reserved through the investor onboarding form.</p>
            <div class="ev-hero__actions ev-rise" style="--i:4">
              {btn("Reserve your seat", "investors.html", "coral")}
              {btn("About the events", "#dec1", "glass")}
            </div>
          </div>
          <div class="ev-cal ev-glass ev-rise" style="--i:3" role="group" aria-label="December 2026 calendar with two events">
            <div class="ev-cal__head"><span class="ev-cal__month">December 2026</span><span class="ev-cal__count">2 events &nbsp;·&nbsp; Miami</span></div>
            <div class="ev-cal__grid">{calendar()}</div>
          </div>
        </div>
        <div class="ev-cards">
          <article class="ev-card ev-glass ev-rise" style="--i:5" data-ev="dec1">
            <p class="ev-card__when">Tue 1 Dec &nbsp;·&nbsp; From 5 PM</p>
            <h2>After the Midterms: AI, Cyber Risk &amp; the Next Investment Cycle</h2>
            <p>Private dinner for SFO principals, Key Biscayne</p>
            <div class="ev-card__actions">
              <a class="btn btn--coral" href="investors.html"><span>Reserve your seat</span><span class="btn__icon">{ARROW}</span></a>
            </div>
            <a class="ev-card__more" href="#dec1">About the dinner</a>
          </article>
          <article class="ev-card ev-glass ev-rise" style="--i:6" data-ev="dec3">
            <p class="ev-card__when">Thu 3 Dec &nbsp;·&nbsp; 9:30 AM ET</p>
            <h2>The Sunbelt Acquisition Playbook: Creating Value Through Strategic Acquisitions</h2>
            <p>Breakfast conference and closed-room debate at Miami DDA, Downtown Miami</p>
            <div class="ev-card__actions">
              <a class="btn btn--coral" href="investors.html"><span>Reserve your seat</span><span class="btn__icon">{ARROW}</span></a>
            </div>
            <a class="ev-card__more" href="#dec3">About the breakfast</a>
          </article>
        </div>
      </div>
    </section>

    <!-- EVENT 01 -->
    <section class="section" id="dec1">
      <div class="wrap ev-event">
        <div class="ev-date r">
          <div class="ev-date__big">{blk("coral", 62, "navy", "navy", 40, "coral", 0)}<p class="ev-date__num">01<small>Tuesday<br>December 2026</small></p></div>
          <dl class="ev-facts">
            <div><dt>Time</dt><dd>5:00 PM, open evening after 9:00 PM</dd></div>
            <div><dt>Place</dt><dd>Key Biscayne</dd></div>
            <div><dt>Format</dt><dd>Private dinner for SFO principals</dd></div>
            <div><dt>Seats</dt><dd>Limited to 20 principals</dd></div>
          </dl>
        </div>
        <div class="ev-body">
          <p class="ev-kicker r">Event 01 &nbsp;·&nbsp; Private dinner</p>
          <h2 class="r" style="--d:1">After the Midterms: <strong>AI, Cyber Risk &amp; the Next Investment Cycle</strong></h2>
          <p class="r" style="--d:2">A private dinner for single-family office principals in Key Biscayne. Market intelligence, peer exchange and curated networking, hosted by EPL Group on the eve of the Art Basel Miami Beach VIP Days. Seating is limited to 20 principals.</p>
          <ul class="ev-tags r" style="--d:2"><li>The midterms</li><li>AI</li><li>Cyber risk</li><li>The next investment cycle</li></ul>
          <div class="ev-actions r" style="--d:3">
            <a class="btn btn--black" href="investors.html"><span>Reserve your seat</span><span class="btn__icon">{ARROW}</span></a>
            <p class="ev-fine">Invite-only. Reserve through the investor onboarding form.</p>
          </div>

          <p class="ev-sub r">Your evening</p>
          <ol class="ev-timeline r">
            <li><span class="t">5:00 p.m.</span><b>Cocktails</b><span>5:00 to 6:00 PM.</span></li>
            <li><span class="t">6:00 p.m.</span><b>Seated dinner</b><span>6:00 to 9:00 PM.</span></li>
            <li><span class="t">9:00 p.m.</span><b>Open evening</b><span>9:00 PM onwards.</span></li>
          </ol>

          <p class="ev-sub r">The conversation is led by</p>
          <div class="ev-lead r">
            <b>Professor David Andolfatto</b>
            <span>Chair of the Department of Economics, Miami Herbert Business School</span>
            <p>Professor Andolfatto has written and spoken extensively on monetary and fiscal policy, national debt and inflation. His experience includes Senior Vice President and advisor to the president at the Federal Reserve Bank of St. Louis.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- EVENT 02 -->
    <section class="section section--line" id="dec3">
      <div class="wrap ev-event">
        <div class="ev-date r">
          <div class="ev-date__big">{blk("navy", 50, "coral", "coral", 55, "slate", 0)}<p class="ev-date__num">03<small>Thursday<br>December 2026</small></p></div>
          <dl class="ev-facts">
            <div><dt>Time</dt><dd>9:30 AM ET</dd></div>
            <div><dt>Place</dt><dd>Miami DDA, 201 S. Biscayne Blvd, Suite 2600, Miami, FL 33131 (Citigroup Building)</dd></div>
            <div><dt>Format</dt><dd>Breakfast conference and closed-room debate</dd></div>
            <div><dt>For</dt><dd>SFOs, PE principals and dealmakers</dd></div>
          </dl>
        </div>
        <div class="ev-body">
          <p class="ev-kicker r">Event 02 &nbsp;·&nbsp; Breakfast conference</p>
          <h2 class="r" style="--d:1">The Sunbelt Acquisition Playbook: <strong>Creating Value Through Strategic Acquisitions</strong></h2>
          <p class="r" style="--d:2">A candid discussion on lower-middle-market private equity deals in Florida, bringing together SFOs, PE principals and dealmakers to debate how to source, price, finance and close acquisitions.</p>
          <div class="ev-actions r" style="--d:3">
            <a class="btn btn--black" href="investors.html"><span>Reserve your seat</span><span class="btn__icon">{ARROW}</span></a>
            <p class="ev-fine">Invite-only. Reserve through the investor onboarding form.</p>
          </div>

          <p class="ev-sub r">Your morning</p>
          <ol class="ev-timeline r">
            <li><span class="t">9:30 a.m.</span><b>Breakfast and introductions</b><span>Meet family offices and PE investors.</span></li>
            <li><span class="t">10:00 a.m.</span><b>The debate</b><span>Four dealmakers, one topic, your questions.</span></li>
            <li><span class="t">11:00 a.m.</span><b>Networking coffee</b><span>Meet co-investors and capital partners.</span></li>
          </ol>

          <p class="ev-sub r">What we will debate</p>
          <ol class="ev-debate">
            <li class="r" style="--d:0"><span class="n">01</span><span class="k">Finding the deal</span><p>Is the best Florida opportunity found in a sale process, or before one starts?</p></li>
            <li class="r" style="--d:1"><span class="n">02</span><span class="k">Structuring it</span><p>Should a family office buy directly, back a sponsor, or build a platform with a partner?</p></li>
            <li class="r" style="--d:2"><span class="n">03</span><span class="k">Pricing and closing</span><p>What turns an attractive company into an attractive acquisition at the right price?</p></li>
          </ol>

          <p class="ev-sub r">On stage</p>
          <p class="ev-fine r" style="margin-top:-14px">Four dealmakers. Real transactions. No sales pitches.</p>
          <ul class="ev-stage r">
            <li><b>Single-family office principal</b><span>Owning, governing and co-investing in private companies.</span></li>
            <li><b>Lower-middle-market PE principal</b><span>Underwriting, deploying capital and building platforms.</span></li>
            <li><b>Ponderis Partners</b><span>Proprietary deal flow and disciplined buy-side execution.</span></li>
            <li><b>Acquisition-finance expert</b><span>Debt capacity and financing structures that hold up.</span></li>
          </ul>
          <p class="ev-fine r">Led by an experienced dealmaker who keeps every answer concrete and invites the room in.</p>

          <p class="ev-sub r">Why attend</p>
          <ul class="ev-why r">
            <li>{blk("coral", 62, "navy", "navy", 40, "coral", 0)}<div><b>Family office principals</b><span>See when to own companies directly, back a sponsor or partner on a platform, and whether to build an acquisition team in-house.</span></div></li>
            <li>{blk("navy", 50, "coral", "coral", 55, "slate", 1)}<div><b>Private equity principals</b><span>Sharpen proprietary sourcing, platform and add-on selection, debt capacity and underwriting for a Florida-focused strategy.</span></div></li>
            <li>{blk("slate", 58, "coral", "coral", 35, "navy", 2)}<div><b>A different kind of panel</b><span>No slides and no pitches. Speakers take positions, challenge each other and answer your questions first.</span></div></li>
          </ul>

          <div class="ev-partners r">
            <div><small>Hosted by</small><img src="assets/logo-miami-dda.png" alt="Miami DDA, Downtown Development Authority" width="1200" height="300" loading="lazy"></div>
            <div><small>Organized by</small><span class="logo-epl" role="img" aria-label="EPL Group">{logo_svg()}</span></div>
            <div><small>Featuring</small><img src="assets/logo-ponderis.png" alt="Ponderis" width="552" height="80" loading="lazy" style="height:22px;margin-bottom:6px"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- REGISTRATION -->
    <section class="ev-register" id="register">
      <picture class="ev-register__bg" aria-hidden="true"><source srcset="assets/miami-skyline.webp" type="image/webp"><img src="assets/miami-skyline.jpg" alt="" width="2048" height="2048" loading="lazy"></picture>
      <div class="ev-register__shade" aria-hidden="true"></div>
      <div class="wrap">
        <div class="ev-register__head">
          <p class="ev-eyebrow r">Reserve your seat</p>
          <h2 class="r" style="--d:1">One form for both events. <strong>A partner confirms each seat.</strong></h2>
          <p class="r" style="--d:2">Registration runs only through EPL's investor onboarding form. Tick one or both December events at the top, then complete your investor profile.</p>
        </div>
        <div class="ev-register__grid">
          <div class="ev-formcard r">
            <div class="ev-formcard__head">
              <div>
                <h3>Investor onboarding</h3>
                <p>For qualified investors only, by approval. Takes about 5 minutes.</p>
              </div>
              <a class="ev-formcard__open" href="{PIPEFY_FORM}" target="_blank" rel="noopener">Open in a new tab<span class="arr">→</span></a>
            </div>
            <div class="ev-embed" data-embed data-src="{PIPEFY_FORM}?embedded=true" data-shot="assets/form-investor.webp">
              <div class="ev-embed__fallback">
                <p class="ev-kicker">Secure registration form</p>
                <h4>Choose your events in the investor onboarding form</h4>
                <ul class="ev-picks">
                  <li><span class="ev-picks__box" aria-hidden="true"></span><div><b>Tue 1 Dec &nbsp;·&nbsp; Private dinner for SFO principals</b><span>Key Biscayne, from 5 PM. Limited to 20 seats.</span></div></li>
                  <li><span class="ev-picks__box" aria-hidden="true"></span><div><b>Thu 3 Dec &nbsp;·&nbsp; Closed-room debate</b><span>Miami DDA, Downtown Miami, 9:30 AM ET.</span></div></li>
                </ul>
                <p class="ev-embed__hint">Tick one or both under "December Events" at the top of the form, then complete your investor profile.</p>
                {ext_btn("Open the registration form", PIPEFY_FORM, "coral")}
                <p class="ev-embed__fine">Opens in a new tab. Takes about 5 minutes.</p>
              </div>
              <p class="ev-embed__loading" aria-hidden="true">Loading the form…</p>
              <iframe title="EPL investor onboarding form, including registration for the December 1 and December 3 events" referrerpolicy="strict-origin-when-cross-origin"></iframe>
            </div>
            <p class="ev-formcard__foot">Trouble seeing the form? <a href="{PIPEFY_FORM}" target="_blank" rel="noopener">Open the investor onboarding form</a>.</p>
          </div>
          <aside class="ev-side">
            <div class="ev-glass r" style="--d:1">
              <h3>How to register</h3>
              <ol class="ev-steps">
                <li><b>Tick your events</b><span>Under "December Events" at the top of the form, select the dinner, the debate, or both.</span></li>
                <li><b>Complete your profile</b><span>Contact details, investor type, and the strategies, sectors and check sizes you focus on.</span></li>
                <li><b>We confirm your seat</b><span>Every request is reviewed, and a partner follows up personally.</span></li>
              </ol>
            </div>
            <div class="ev-glass r" style="--d:2">
              <h3>At a glance</h3>
              <dl>
                <div><dt>Tue 1 Dec</dt><dd>Private dinner, Key Biscayne<br>From 5 PM, 20 seats</dd></div>
                <div><dt>Thu 3 Dec</dt><dd>Closed-room debate, Miami DDA<br>9:30 AM ET</dd></div>
              </dl>
              <p>Both events are invite-only. Registration is through the <a class="mail" href="investors.html">investor form</a>.</p>
            </div>
          </aside>
        </div>
        <p class="ev-legal">For information and networking only; not an offer or solicitation of any security.</p>
      </div>
    </section>
"""

page("events.html", "December in Miami: two events for family offices and dealmakers | EPL Group",
     "Two EPL Group events in Miami: a private dinner for selected families on December 1 and the Sunbelt Acquisition Playbook breakfast debate at Miami DDA on December 3, 2026.",
     "events.html", EVENTS, closing=False)

# ---------------------------------------------------------------- EPL CIRCLE (private investor dinners)
import math
CIR_STEPS = [
    ("Investor targeting and curation", "We identify and invite investors whose investment focus, stage preferences, sector expertise and capital profile align with your financing objectives."),
    ("Private investor dinner", "We organize an invitation-only dinner with approximately 8 to 12 qualified investors, selected for relevance and potential fit."),
    ("Company positioning and preparation", "We work with your leadership team to prepare the company briefing, so invited investors understand the opportunity ahead of the dinner."),
    ("Introductions and follow-up", "We facilitate introductions, coordinate post-dinner follow-up and help track investor engagement and potential next steps."),
]
CIR_FOR = [
    ("Seed", "Companies preparing for their first institutional financing."),
    ("Series A", "Companies looking to expand their investor base and accelerate growth."),
    ("Series B and later", "Companies seeking growth capital, strategic investors or new financing relationships."),
]
CIR_NETWORK = ["Venture capital firms", "Family offices", "High-net-worth investors", "Private investment groups", "Strategic investors"]
CIR_WHY = [
    ("Curated, not crowded.", "A deliberately selected group of relevant investors."),
    ("Private and relationship-driven.", "A discreet environment for substantive conversations."),
    ("Relevant investor access.", "Targeting based on your sector, stage and financing objectives."),
    ("Senior-level engagement.", "Direct interaction with founders, executives and investment decision-makers."),
    ("Focused execution.", "A structured process before, during and after each dinner."),
]
CIR_FAQ = [
    ("What is EPL Circle?", "EPL Circle is EPL Group's private investor dinner program. It connects Seed, Series A and Series B companies with qualified investors through invitation-only dinners."),
    ("How many investors attend each dinner?", "Approximately 8 to 12 qualified investors, selected for relevance and potential fit."),
    ("Which companies can take part?", "Ambitious companies seeking institutional and private investment, from Seed-stage companies preparing a first institutional financing to Series B and later-stage companies seeking growth capital."),
    ("Which types of investors are invited?", "The network may include venture capital firms, family offices, high-net-worth investors, private investment groups and strategic investors, chosen to match your sector, stage and financing objectives."),
    ("How does my company prepare?", "We work with your leadership team to prepare the company briefing, so invited investors understand the opportunity before the dinner."),
    ("What happens after the dinner?", "We facilitate introductions, coordinate follow-up and help track investor engagement and potential next steps."),
    ("How is EPL Circle structured commercially?", "The engagement structure depends on the company's stage, fundraising objectives, investor profile and scope. Contact EPL Group to discuss your situation."),
]
CIR_ALT = "Private dinner table set for an EPL Circle investor evening"
SEATS = 10
def circle_table():
    """A dinner table seen from above: chairs, place settings, the EPL logo at the centre."""
    C = 300
    def pol(r, deg):
        a = math.radians(deg)
        return C + r * math.cos(a), C + r * math.sin(a)
    chairs = settings = ""
    for i in range(SEATS):
        deg = -90 + i * 360 / SEATS
        you = " cir-you" if i == 0 else ""
        (x1, y1), (x2, y2) = pol(226, deg - 10.5), pol(226, deg + 10.5)
        chairs += (f'<path class="cir-pop cir-chair{you}" style="--i:{i}" d="M{x1:.1f} {y1:.1f}A226 226 0 0 1 {x2:.1f} {y2:.1f}"/>')
        x, y = pol(140, deg)
        settings += (f'<g transform="translate({x:.1f} {y:.1f}) rotate({deg + 90:.0f})"><g class="cir-pop cir-set{you}" style="--i:{i}">'
                     + ('<circle class="cir-pulse" r="25"/>' if i == 0 else "") +
                     f'<circle class="cir-plate" r="25"/><circle class="cir-plate__in" r="16"/>'
                     # cutlery and glass are turned about the table centre (0,140 in this frame), so they sit like spokes
                     f'<path class="cir-cut" transform="rotate(-14.5 0 140)" d="M0 -13V13M-2.6 -13v7M2.6 -13v7"/>'
                     f'<path class="cir-cut" transform="rotate(14.5 0 140)" d="M0 -13V13"/>'
                     f'<circle class="cir-glass" cx="0" cy="37" r="5.5" transform="rotate(10 0 140)"/></g></g>')
    chips = ""
    for label, deg, cls in [("Your company", -90, " cir-chip--you"), ("Venture capital", -18, ""), ("Family office", 90, ""), ("Strategic investor", 198, "")]:
        x, y = pol(262, deg)
        chips += f'<span class="cir-chip{cls}" style="left:{x / 6:.2f}%;top:{y / 6:.2f}%">{label}</span>'
    return f'''<div class="cir-table" role="img" aria-label="{CIR_ALT}">
            <svg viewBox="0 0 600 600" aria-hidden="true" focusable="false">
              <defs>
                <radialGradient id="cirTop" cx="42%" cy="36%" r="75%"><stop offset="0" stop-color="#ffffff"/><stop offset=".62" stop-color="#f6efeb"/><stop offset="1" stop-color="#e6d8d1"/></radialGradient>
                <radialGradient id="cirBlush" cx="72%" cy="74%" r="52%"><stop offset="0" stop-color="#eb5a5d" stop-opacity=".34"/><stop offset="1" stop-color="#eb5a5d" stop-opacity="0"/></radialGradient>
                <radialGradient id="cirHalo" cx="50%" cy="50%" r="50%"><stop offset=".6" stop-color="#eb5a5d" stop-opacity=".0"/><stop offset=".8" stop-color="#eb5a5d" stop-opacity=".2"/><stop offset="1" stop-color="#eb5a5d" stop-opacity="0"/></radialGradient>
                <filter id="cirShadow" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="22" stdDeviation="20" flood-color="#050d1a" flood-opacity=".6"/></filter>
              </defs>
              <circle cx="300" cy="300" r="300" fill="url(#cirHalo)"/>
              <circle class="cir-orbit" cx="300" cy="300" r="262"/>
              <circle class="cir-orbit2" cx="300" cy="300" r="296"/>
              {chairs}
              <g class="cir-top">
                <circle cx="300" cy="300" r="190" fill="url(#cirTop)" filter="url(#cirShadow)"/>
                <circle cx="300" cy="300" r="190" fill="url(#cirBlush)"/>
                <circle cx="300" cy="300" r="182" fill="none" stroke="#2c3a4b" stroke-opacity=".1"/>
              </g>
              {settings}
              <circle class="cir-ring" cx="300" cy="300" r="86" pathLength="1"/>
              <g class="cir-logo">
                <svg x="232" y="250" width="138" height="64.7" viewBox="0 0 1200 563" color="#2c3a4b">{LOGO_INNER}</svg>
                <text x="304" y="342" text-anchor="middle">CIRCLE</text>
              </g>
            </svg>
            <span aria-hidden="true">{chips}</span>
          </div>'''

def circle_map():
    """Where we host: the United States drawn in horizontal lines, with the three cities.
    data/us-lines.json holds the line segments (made once from US Census outlines)."""
    m = json.loads((HERE / "data" / "us-lines.json").read_text())
    w, h = m["width"], m["height"]
    d = "".join(f"M{x1} {y}H{x2}" for x1, y, x2 in m["segments"])
    side = {"San Francisco": "r"}                       # label to the right of the dot; the others sit to the left
    pins = "".join(
        f'''<button type="button" class="cir-pin cir-pin--{side.get(c["name"], "l")}" data-pin="{i}" style="left:{c["x"] / w * 100:.2f}%;top:{c["y"] / h * 100:.2f}%"><i></i><span>{c["name"]}</span></button>'''
        for i, c in enumerate(m["cities"]))
    items = "".join(f'''<li><button type="button" data-pin="{i}"><span>0{i + 1}</span><b>{c["name"]}</b></button></li>''' for i, c in enumerate(m["cities"]))
    return f'''        <div class="cir-map r r--fade" data-linemap>
          <div class="cir-map__stage">
            <svg class="cir-map__base" viewBox="0 0 {w} {h}" role="img" aria-label="Map of the United States with Miami, New York and San Francisco marked"><defs><path id="usLines" d="{d}"/></defs><use href="#usLines"/></svg>
            <div class="cir-map__glow" aria-hidden="true"><svg viewBox="0 0 {w} {h}"><use href="#usLines"/></svg></div>
            <div class="cir-map__pins">{pins}</div>
          </div>
          <ol class="cir-map__list">{items}</ol>
          <p class="cir-map__note">With other selected markets.</p>
        </div>
'''

CIRCLE = f'''    <section class="cir-hero" aria-labelledby="cir-title">
      <div class="wrap cir-hero__grid">
        <div class="cir-hero__text">
          <p class="cir-lockup r" aria-hidden="true">{logo_svg()}<i></i><span>Circle</span></p>
          <p class="eyebrow r">Private Investor Dinners</p>
          <h1 class="display r" id="cir-title" style="--d:1">EPL Circle: <strong>Curated Access to Private Capital</strong></h1>
          <p class="lead r" style="--d:2">Invitation-only dinners that put your company in front of the right investors, in Miami, New York and San Francisco.</p>
          <div class="page-hero__actions r" style="--d:3">{btn("Request an introduction", "pitch.html", "coral")}</div>
        </div>
        <div class="cir-hero__art r r--fade" style="--d:2" data-reveal-group>
          {circle_table()}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="cir-what">
          <div>
            <p class="eyebrow r">The program</p>
            <h2 class="display r" style="--d:1">What is <strong>EPL Circle?</strong></h2>
          </div>
          <div>
            <p class="definition r">EPL Circle is EPL Group's private investor dinner program for Seed, Series A and Series B companies. Each dinner brings together approximately 8 to 12 qualified investors, selected for relevance and potential fit with your financing objectives.</p>
            <p class="lead r" style="--d:1">It is a focused investor engagement, not a traditional networking event or a large-scale pitch session.</p>
          </div>
        </div>
        <div class="ab-stats cir-stats r" style="--d:1">
          <div><b>8 to 12</b><span>Qualified investors at each dinner</span></div>
          <div><b>Seed to B</b><span>Seed, Series A and Series B companies</span></div>
          <div><b>3 cities</b><span>Miami, New York and San Francisco</span></div>
        </div>
      </div>
    </section>

    <section class="section cir-dark">
      <div class="wrap">
        <div class="section__head section__head--gap56">
          <div class="title">
            <p class="eyebrow r">The process</p>
            <h2 class="display r" style="--d:1">How an EPL Circle <strong>dinner works</strong></h2>
          </div>
        </div>
        <ol class="cir-steps r r--fade" data-reveal-group>
''' + "".join(f'''          <li style="--i:{i}"><span class="cir-steps__n">0{i + 1}</span><h3>{t}</h3><p>{d}</p></li>
''' for i, (t, d) in enumerate(CIR_STEPS)) + f'''        </ol>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
{section_head("", "Stages", "Who EPL Circle <strong>is for</strong>", gap56=True)}
        <div class="cards cir-for">
''' + "".join(f'''          <div class="card r" style="--d:{i}">{FIG_BLK[i]}<h3>{t}</h3><p>{d}</p></div>
''' for i, (t, d) in enumerate(CIR_FOR)) + f'''        </div>
        <div class="cir-network r">
          <p>Our investor network and targeting approach may include venture capital firms, family offices, high-net-worth investors, private investment groups and strategic investors.</p>
          <ul aria-hidden="true">{"".join(f"<li>{n}</li>" for n in CIR_NETWORK)}</ul>
        </div>
      </div>
    </section>

    <section class="section section--line">
      <div class="wrap two-col">
        <div class="sticky-aside">
          <p class="eyebrow r">The difference</p>
          <h2 class="display r" style="--d:1">Why <strong>EPL Circle</strong></h2>
        </div>
        <ul class="cir-why">
''' + "".join(f'''          <li class="r" style="--d:{i % 3}"><span>0{i + 1}</span><div><h3>{t}</h3><p>{d}</p></div></li>
''' for i, (t, d) in enumerate(CIR_WHY)) + f'''        </ul>
      </div>
    </section>

    <section class="section section--line">
      <div class="wrap">
{section_head("", "Locations", "Where <strong>we host</strong>", '<p class="lead">Miami, New York and San Francisco, with other selected markets.</p>', gap56=True)}
{circle_map()}      </div>
    </section>

    <section class="section section--line">
      <div class="wrap">
{section_head("", "FAQ", "Frequently asked <strong>questions</strong>", gap56=True)}
{faq_block(CIR_FAQ, note="About EPL Circle", more=False)}        <p class="cir-links r">EPL Circle is a program of <a href="index.html">EPL Group</a>. To talk to us, use the <a href="pitch.html">contact form</a>.</p>
      </div>
    </section>

    <section class="closing" id="contact-band">
      <img class="closing__bg" src="assets/closing-band.jpg" alt="" data-parallax="0.08" width="1440" height="640" loading="lazy">
      <div class="closing__veil" aria-hidden="true"></div>
      <div class="wrap">
        <p class="closing__kicker r">EPL Circle</p>
        <h2 class="r" style="--d:1">Let's bring the right investors<br><span class="dim">to the table.</span></h2>
        <p class="r" style="--d:2">Whether you are preparing a Seed round, raising a Series A or pursuing a larger growth financing, EPL Circle helps create the investor relationships that can move your financing objectives forward.</p>
        <div class="closing__actions r" style="--d:3">
          {btn("Contact EPL Group", "pitch.html")}
        </div>
      </div>
    </section>
'''
CIR_TITLE = "EPL Circle | Private Investor Dinners for Seed to Series B"
CIR_DESC = "EPL Circle hosts invitation-only dinners with 8 to 12 qualified investors for Seed to Series B companies in Miami, New York and San Francisco."
OG_TITLES["circle.html"] = "EPL Circle: Private Investor Dinners"
page("circle.html", CIR_TITLE, CIR_DESC, "circle.html", CIRCLE, closing=False,
     jsonld=ld(webpage("circle.html", CIR_TITLE, CIR_DESC),
               {"@type": "Service", "@id": clean_url("circle.html") + "#service", "name": "EPL Circle", "alternateName": "EPL Circle Private Investor Dinners",
                "description": "EPL Circle is EPL Group's private investor dinner program for Seed, Series A and Series B companies, bringing approximately 8 to 12 qualified investors together at an invitation-only dinner.",
                "url": clean_url("circle.html"), "provider": {"@type": "Organization", "@id": SITE + "/#org", "name": "EPL Group", "url": SITE},
                "areaServed": [{"@type": "City", "name": c} for c in ("Miami", "New York", "San Francisco")],
                "audience": {"@type": "BusinessAudience", "audienceType": "Seed, Series A and Series B companies"}},
               {"@type": "FAQPage", "@id": clean_url("circle.html") + "#faq", "mainEntity": [
                   {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in CIR_FAQ[:6]]}))

# ---------------------------------------------------------------- SITEMAP / ROBOTS
TODAY = datetime.date.today().isoformat()
order = {"index.html": 0}
urls = "".join(f"  <url><loc>{clean_url(p)}</loc><lastmod>{TODAY}</lastmod></url>\n"
               for p in sorted(PAGES, key=lambda p: (order.get(p, 1), p.count("/"), p)))
(OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
# articles removed from ./insights/ leave no page behind
keep = {f'{a["slug"]}.html' for a in ARTICLES}
if (OUT / "insights").is_dir():
    for old in (OUT / "insights").glob("*.html"):
        if old.name not in keep:
            old.unlink()
print("wrote sitemap.xml, robots.txt,", len(ARTICLES), "article(s)")
