#!/usr/bin/env python3
"""Generates the static pages for dnaproplans.com into the repo root.

Usage: python3 tools/build.py .
Pages are written as <name>.html. Links between pages are written here as "<name>.html" and are
rewritten to clean root-relative URLs ("/name"), which is how the Cloudflare Worker serves them.
"""
import re, sys, pathlib, json

OUT = pathlib.Path(sys.argv[1])
SITE = "https://dnaproplans.com"
BUILD = "2026-11-22.1"  # shown in <meta name="dna-build"> and /version.txt; change on every release
CAL = "https://calendly.com/draganatodorovskajaneva/30min"
FORM = "https://app.pipefy.com/public/form/WjXLnOMX"
GA_ID = "G-HCBH87S9EE"  # Google tag in the shared head; analytics cookies only after the visitor accepts
LINKEDIN = "https://www.linkedin.com/company/106128983/"
LINKEDIN_FOUNDER = "https://www.linkedin.com/in/dragana-todorovska-j-054314176/"
SITEMAP = []  # canonical URLs of indexable pages, filled by page()


def clean(name):
    """index.html -> "", services.html -> "services"."""
    return "" if name == "index.html" else name[:-5]


GTAG = f"""
  <script>
    // Consent defaults must be set before the Google tag: no analytics cookies until the visitor accepts.
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('consent', 'default', {{
      ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
      analytics_storage: (function () {{ try {{ return localStorage.getItem('dna-analytics-consent') === 'granted' ? 'granted' : 'denied'; }} catch (e) {{ return 'denied'; }} }})()
    }});
  </script>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtm.js?id={GA_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
  </script>"""


def head(title, desc, path, extra="", index=True, tag=True):
    robots = "" if index else '\n  <meta name="robots" content="noindex">'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>{GTAG if tag else ""}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">{robots}
  <link rel="canonical" href="{SITE}/{path}">
  <meta property="og:site_name" content="DNA Pro Plans">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{SITE}/{path}">
  <meta property="og:image" content="{SITE}/images/og.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="DNA Pro Plans: investor pitch decks, business plans and financial models built on research">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{SITE}/images/og.png">
  <meta name="theme-color" content="#0e1229">
  <meta name="dna-build" content="{BUILD}">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
  <link rel="preload" href="fonts/jost-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="styles.css">
  <script src="consent.js"></script>
  <script>document.documentElement.classList.add('js')</script>{extra}
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
"""


def nav(current=""):
    def cur(k):
        return ' aria-current="page"' if k == current else ""
    return f"""  <header class="nav">
    <div class="wrap nav__in">
      <a href="index.html" class="logo" aria-label="DNA Pro Plans home"><img src="icons/mark.svg" alt="" width="20" height="20">DNA PRO PLANS</a>
      <nav class="nav__links" id="menu" aria-label="Main">
        <a href="services.html"{cur('services')}>Services</a>
        <a href="case-studies.html"{cur('cases')}>Work</a>
        <a href="index.html#approach">Approach</a>
        <a href="index.html#founder">Founder</a>
        <a href="index.html#faq">FAQ</a>
        <a class="nav__only-menu" href="contact.html#book" data-cta="book_call" data-loc="menu">Book a call</a>
      </nav>
      <a class="nav__alt" href="contact.html#book" data-cta="book_call" data-loc="nav">Book a call</a>
      <a href="contact.html" class="btn btn--dark nav__cta" data-cta="request_quote" data-loc="nav">Request a quote</a>
      <button class="nav__toggle" aria-label="Open menu" aria-expanded="false" aria-controls="menu"><span></span><span></span></button>
    </div>
  </header>
"""


def footer(note=""):
    note_html = f'\n      <p class="footer__note">{note}</p>' if note else ""
    return f"""  <div class="wordmark" aria-hidden="true">
    <p class="wordmark__text">DNA PRO PLANS</p>
    <p class="wordmark__tag">Business strategy, plans and design</p>
  </div>
  <footer class="footer">
    <div class="wrap footer__in">
      <a href="index.html" class="logo" aria-label="DNA Pro Plans home"><img src="icons/mark.svg" alt="" width="17" height="17">DNA PRO PLANS</a>
      <nav class="footer__links" aria-label="Footer">
        <a href="services.html">Services</a>
        <a href="case-studies.html">Work</a>
        <a href="contact.html" data-cta="request_quote" data-loc="footer">Request a quote</a>
        <a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>
        <a href="privacy.html">Privacy</a>
        <button type="button" class="footer__cookie" data-consent-open>Cookie settings</button>
      </nav>{note_html}
      <p>© <span id="year">2026</span> DNA Pro Plans</p>
    </div>
  </footer>
  <script src="main.js" defer></script>
</body>
</html>
"""


def clean_links(html):
    """Rewrite page links to clean root-relative URLs and assets to root-relative paths."""
    html = re.sub(r'href="index\.html(#[^"]*)?"', lambda m: 'href="/' + (m.group(1) or "") + '"', html)
    html = re.sub(r'href="([a-z0-9-]+)\.html(#[^"]*)?"', lambda m: 'href="/' + m.group(1) + (m.group(2) or "") + '"', html)
    html = re.sub(r'(src|href)="(images|icons|fonts)/', r'\1="/\2/', html)
    html = html.replace('href="styles.css"', f'href="/styles.css?v={BUILD}"')
    html = re.sub(r'src="(main|consent)\.js"', lambda m: f'src="/{m.group(1)}.js?v={BUILD}"', html)
    html = html.replace('href="favicon.svg"', 'href="/favicon.svg"').replace('href="apple-touch-icon.png"', 'href="/apple-touch-icon.png"')
    return html


def page(name, title, desc, body, current="", note="", extra="", index=True, tag=True):
    path = clean(name)
    html = head(title, desc, path, extra, index, tag) + nav(current) + body + footer(note)
    (OUT / name).write_text(clean_links(html))
    if index:
        SITEMAP.append(f"{SITE}/{path}")
    print("wrote", name)


def quote_cta(loc, primary="Request a project quote", dark=False, book=True):
    """The primary action, with booking as the alternative."""
    cls = "btn btn--on-dark" if dark else "btn"
    alt = f'<a class="ulink" href="contact.html#book" data-cta="book_call" data-loc="{loc}">Or book a 30-minute call</a>' if book else ""
    return f'<div class="cta-row"><a href="contact.html" class="{cls}" data-cta="request_quote" data-loc="{loc}">{primary}</a>{alt}</div>'


FAQS = [
    ("Can you develop the content, or do I need finished copy?",
     "We develop it. Research, financial modeling, copy and presentation design are done together, so you do not need finished text. You bring what you know about the business and we write and structure the material."),
    ("Can you improve an existing plan, model or deck?",
     "Yes. We refine existing plans, models and decks. Send what you have with your inquiry and we will tell you what can be kept and what needs rebuilding."),
    ("What information do you need from me?",
     "To start: the decision you need, your deadline and the data you already have. After your inquiry we send a short list of the business inputs and documents needed for your specific project."),
    ("What files will I receive?",
     "Editable files, not only PDFs. Financial models are delivered as Excel workbooks with live formulas, and decks are delivered with a PowerPoint export. The exact file formats for your project are listed in your quote."),
    ("How does confidentiality work?",
     "Everything you share about your finances and internal planning stays confidential, and an NDA is available on request. Work is shown publicly only with the client’s permission, with confidential figures masked."),
    ("How are delivery times and revisions agreed?",
     "Most decks, plans and models are delivered in 7 days, counted from the day we have your complete inputs. Graphic design and websites follow an agreed timeline. The scope, fee, delivery date and revisions are confirmed in your quote before work starts."),
    ("Do you guarantee funding?",
     "No. We make your case clear and check that the numbers hold. Investors and lenders decide."),
]


def faq_html(items, heading="Questions before you start", anchor="faq", band=True):
    rows = "".join(f'<details class="faq__item"><summary>{q}</summary><div><p>{a}</p></div></details>' for q, a in items)
    return f"""
    <section class="faq{' band' if band else ''}" id="{anchor}">
      <div class="wrap faq__grid">
        <h2 class="h2" data-reveal>{heading}</h2>
        <div class="faq__list" data-reveal style="--d:2">{rows}</div>
      </div>
    </section>"""


def faq_ld(items):
    data = {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}
    return '\n  <script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


# ------------------------------------------------------------------ HOME
SECTORS = [("fintech", "Fintech"), ("agribusiness", "Agribusiness"), ("energy", "Energy technology"), ("biotech", "Biotech"),
           ("franchising", "Franchising"), ("textile", "Textile manufacturing"), ("luxury", "Luxury retail"), ("wellness", "Wellness"),
           ("lending", "Private lending"), ("hardware", "Consumer hardware")]
sector_group = "".join(f'<li class="sector"><img src="icons/ind-{k}.svg" alt="" width="30" height="30">{v}</li>' for k, v in SECTORS)

SERVICES = [
    ("pitch", "Pitch decks and sales decks", "Decks for investors, partners and large clients.", "Why this company, and why now?"),
    ("plan", "Business and financial plans", "Plans and five-year projections in four scenarios.", "Do the numbers still hold if the market turns?"),
    ("research", "Market research papers", "Market sizing, demand and competitor intelligence.", "How big is this market, and who says so?"),
    ("website", "Graphic design", "Brand identity, guidelines and designed materials.", "Does this company look as serious as its plan?"),
]
svc_html = ""
for i, (icon, t, d, q) in enumerate(SERVICES):
    act = " is-active" if i == 0 else ""
    svc_html += f"""
            <li class="svc{act}">
              <button class="svc__head" type="button" aria-expanded="{'true' if i == 0 else 'false'}" aria-controls="show-{icon}">
                <img src="icons/icon-{icon}.svg" alt="" width="30" height="30">
                <span><span class="svc__title">{t}</span><span class="svc__desc">{d}</span></span>
              </button>
              <div class="svc__more"><div><div class="svc__more-in">
                <p class="svc__k">The reader asks</p>
                <p class="svc__q">{q}</p>
              </div></div></div>
            </li>"""


def thumbs(items):
    return '<div class="show__thumbs">' + "".join(
        f'<img src="images/{s}.webp" alt="{a}" style="--i:{i}" loading="lazy" width="432" height="243">' for i, (s, a) in enumerate(items)) + "</div>"


showcase = f"""
          <div class="showcase" data-reveal="scale">
            <div class="show is-active show--boards" id="show-pitch">
              <div class="show__boards">
                <img src="images/board-custel.webp" alt="Overview of the Custel fintech seed deck" style="--i:0" width="1600" height="962">
                <img src="images/board-aro.webp" alt="Overview of the ARO Social Club investment memorandum" style="--i:1" width="1600" height="962">
                <img src="images/board-ants.webp" alt="Overview of the ANTS Platform seed deck" style="--i:2" width="1600" height="962">
                <img src="images/board-haraz.webp" alt="Overview of the Haraz Coffee House franchise deck" style="--i:3" width="1600" height="962">
              </div>
              <p class="show__cap"><strong>Investor pitch decks</strong><a href="services.html#deck-examples">Fintech, hospitality, software and franchise decks. See the examples →</a></p>
            </div>
            <div class="show" id="show-plan">
              <div class="show__pages">
                <img src="images/sample-1-cover.webp" alt="Cover of a sample business plan for Fieldhouse Workspace" style="--i:0" loading="lazy" width="900" height="1273">
                <img src="images/sample-3-summary.webp" alt="Executive summary page of the sample business plan" style="--i:1" loading="lazy" width="900" height="1273">
                <img src="images/sample-6-financials.webp" alt="Financial statements page of the sample business plan" style="--i:2" loading="lazy" width="900" height="1273">
              </div>
              <p class="show__cap"><strong>Sample business plan</strong><a href="services.html#sample">Fieldhouse Workspace, a fictional company. See more pages →</a></p>
            </div>
            <div class="show" id="show-research">
              <div class="show__pages">
                <img src="images/research-1-cover.webp" alt="Cover of a sample market research report: Charging where America lives" style="--i:0" loading="lazy" width="900" height="1273">
                <img src="images/research-3-market.webp" alt="Market size and growth page of the sample report" style="--i:1" loading="lazy" width="900" height="1273">
                <img src="images/research-5-competition.webp" alt="Competitive landscape page of the sample report" style="--i:2" loading="lazy" width="900" height="1273">
              </div>
              <p class="show__cap"><strong>Sample market research report</strong><a href="services.html#research-sample">EV charging for apartment buildings. Illustrative figures. See more pages →</a></p>
            </div>
            <div class="show show--brand" id="show-website">
              <div class="show__main"><img src="images/brand-01-cover.webp" alt="Cover of the DNA Pro Plans brand guidelines: One identity for every deck, plan and page" loading="lazy" width="1200" height="717"></div>
              {thumbs([("brand-02-logo", "Logo and icon page"), ("brand-05-pattern", "Pattern page"), ("brand-07-treatment", "Photo treatment page"), ("brand-08-color", "Colour and font page"), ("brand-09-icons", "Icons page")])}
              <p class="show__cap"><strong>Brand identity and guidelines</strong><a href="services.html#brand-sample">The DNA Pro Plans brand guidelines. See more pages →</a></p>
            </div>
          </div>"""

TIERS = [
    ("Start", "For founders launching a company and getting ready to sell.",
     ["Brand identity and guidelines", "Website design and build", "Business plan", "Financial plan with four scenarios"], "Discuss your launch", "Start"),
    ("Raise", "For founders and owners raising equity or bank debt.",
     ["Market research paper", "Investor pitch deck", "Scenario-based financial model", "Lender-ready business plan"], "Discuss your raise", "Raise"),
    ("Partner and sell", "For companies approaching partners, distributors and large clients.",
     ["Sales deck", "Partnership proposal", "Market and competitor research", "One-pagers for partners"], "Discuss a partnership", "Partner and sell"),
]
tiers_html = ""
for i, (t, f, items, cta, need) in enumerate(TIERS):
    lis = "".join(f"<li>{x}</li>" for x in items)
    tiers_html += f"""
          <article class="tier{' is-active' if i == 1 else ''}">
            <h3>{t}</h3>
            <p class="tier__for">{f}</p>
            <ul class="squares">{lis}</ul>
            <a class="ulink" href="contact.html" data-cta="request_quote" data-loc="engagements">{cta}</a>
          </article>"""

STEPS = [("Brief", "A short intake: the decision you need, the deadline, the data you have."),
         ("Call", "Thirty minutes to agree the reader, the scope and the delivery date."),
         ("Build", "Research, numbers, story and design, developed together."),
         ("Review", "Preview, revisions, then editable files, or your site live.")]
def deck_gallery(anchor="deck-examples", heading="Pitch deck examples"):
    """Overview boards only. Individual slides and confidential figures are never published."""
    figs = "".join(
        f'<figure class="deckboard" data-reveal style="--d:{n % 2}"><img src="images/{img}.webp" alt="{name}: {kind.lower()}, overview of the deck" width="1600" height="962" loading="lazy">'
        f'<figcaption><strong>{name}</strong>{kind}</figcaption></figure>' for n, (img, name, kind, _) in enumerate(BOARDS))
    return f"""
    <section class="sample decks" id="{anchor}">
      <div class="wrap">
        <p class="eyebrow" data-reveal="fade">Pitch decks</p>
        <h2 class="lines"><span class="line"><span>{heading}</span></span></h2>
        <p class="lead" data-reveal style="--d:2">Overviews of four client decks. Full slides and confidential figures are not shown.</p>
        <div class="deckboards">{figs}</div>
      </div>
    </section>"""


BOARDS = [
    ("board-custel", "Custel", "Fintech seed deck", "case-study-custel.html"),
    ("board-aro", "ARO Social Club", "Investment memorandum", "services.html#deck-examples"),
    ("board-ants", "ANTS Platform", "Software seed deck", "services.html#deck-examples"),
    ("board-haraz", "Haraz Coffee House", "Franchise deck", "case-study-haraz.html"),
]


def board_items(hidden=False):
    extra = ' aria-hidden="true" tabindex="-1"' if hidden else ""
    return "".join(
        f'<li><a class="board" href="{href}" data-cta="open_work" data-loc="work_strip"{extra}>'
        f'<img src="images/{img}.webp" alt="{"" if hidden else name + ": " + kind.lower() + ", slide overview"}" width="1600" height="962" loading="lazy">'
        f'<span><strong>{name}</strong>{kind}</span></a></li>' for img, name, kind, href in BOARDS)


work_html = f"""    <section class="work" id="work">
      <div class="wrap work__head">
        <h2 class="h2" data-reveal>Relevant work</h2>
        <a class="ulink" href="services.html#deck-examples" data-cta="view_examples" data-loc="work" data-reveal style="--d:2">See all deck examples</a>
      </div>
      <div class="strip" data-reveal="fade" style="--d:2">
        <div class="strip__track">
          <ul class="strip__group">{board_items()}</ul>
          <ul class="strip__group" aria-hidden="true">{board_items(hidden=True)}</ul>
        </div>
      </div>
      <div class="wrap">
        <div class="work__cta" data-reveal>
          <p>Have a deck, plan or model to prepare?</p>
          {quote_cta("after_work")}
        </div>
      </div>
    </section>"""

LAYERS = [
    ("Research", "Market sizing, competitors and demand evidence from sources the reader can verify. Estimates are labelled as estimates.",
     ["Market size from public sources", "Competitor revenue, clients and funding", "Customer segments and demand", "Every source cited"]),
    ("Projections", "A five-year model with Base, Upside, Downside and Stress cases. One source of truth for every number you present.",
     ["Four scenarios, switched with one input", "P&amp;L, cash flow and balance sheet", "Revenue, payroll and cost assumptions", "NPV, IRR, DSCR and cash runway"]),
    ("Presentation", "Decks, plans, brand and website that say it clearly, so each page points to the decision you need.",
     ["Pitch decks and sales decks", "Designed plans and reports", "Brand identity and guidelines", "Websites that match the documents"]),
]
layers_html = ""
for i, (t, lead, items) in enumerate(LAYERS):
    lis = "".join(f'<li style="--i:{k + 1}">{x}</li>' for k, x in enumerate(items))
    layers_html += f"""
          <article class="layer layer--{i + 1}">
            <button class="layer__head" type="button" aria-expanded="false" aria-controls="layer-{i + 1}">
              <h3>{t}<span class="layer__plus" aria-hidden="true"></span></h3>
              <span class="layer__lead">{lead}</span>
            </button>
            <div class="layer__more" id="layer-{i + 1}"><p class="layer__k">What is inside</p><ul>{lis}</ul></div>
          </article>"""

steps_html = "".join(f'<li class="step"><span class="step__n">0{i + 1}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(STEPS))

home = f"""  <main id="main">
    <section class="hero">
      <div class="wrap">
        <div class="hero__grid">
          <div>
            <h1 class="h1 hero__h1" data-reveal style="--d:4">Investor pitch decks, business plans and financial models built on research.</h1>
            <p class="hero__sub" data-reveal style="--d:6">I help founders turn their business, market and numbers into clear materials for investors, lenders and partners. Research, financial modeling, copy and presentation design are developed together.</p>
            <div class="hero__actions" data-reveal style="--d:8">
              <a href="contact.html" class="btn" data-cta="request_quote" data-loc="hero">Request a project quote</a>
              <a href="#work" class="btn btn--ghost" data-cta="view_work" data-loc="hero">View relevant work</a>
            </div>
            <p class="hero__alt" data-reveal style="--d:9">Prefer to talk first? <a href="contact.html#book" data-cta="book_call" data-loc="hero">Book a 30-minute call</a>.</p>
          </div>
          <aside class="hero__aside" data-reveal="fade" style="--d:10">
            <p class="hero__label">Led by</p>
            <div class="led">
              <img src="images/dragana.webp" alt="Dragana Todorovska Janeva" width="64" height="64">
              <div><p class="led__name">Dragana Todorovska Janeva</p><p class="led__role">Founder &amp; Principal Business Consultant</p></div>
            </div>
            <hr>
            <p class="hero__label">What we build</p>
            <ul class="squares">
              <li>Investor pitch decks and sales decks</li>
              <li>Business plans and financial models</li>
              <li>Market research papers</li>
              <li>Graphic design</li>
            </ul>
          </aside>
        </div>
        <div class="hero__media"><div class="hero__zoom"><img src="images/hero.jpg" alt="Glass tower rising into a blue sky" width="1024" height="683" fetchpriority="high" data-parallax="-0.12"></div></div>
      </div>
    </section>

    <section class="sectors" aria-label="Sectors we have worked in">
      <div class="sectors__track">
        <ul class="sectors__group">{sector_group}</ul>
        <ul class="sectors__group" aria-hidden="true">{sector_group}</ul>
      </div>
    </section>

{work_html}

    <section class="services band" id="services">
      <div class="wrap">
        <div class="sec-head">
          <h2 class="h2 lines"><span class="line"><span>Everything you need to</span></span><span class="line"><span>start, raise and partner.</span></span></h2>
          <p class="lead" data-reveal style="--d:2">One team for the research, the numbers, the story and the brand. Choose a service to see what the reader gets.</p>
        </div>
        <div class="services__grid">
          <ul class="svc-list" data-reveal>{svc_html}
          </ul>{showcase}
        </div>
        <p class="svc-more" data-reveal><a class="ulink" href="services.html" data-cta="view_services" data-loc="services">See what each service includes, and pricing</a></p>
      </div>
    </section>

    <section class="statement">
      <div class="wrap">
        <p>Investors, lenders and partners say yes to what they can believe. We build every deck, plan and page on real market research and realistic projections, so your story holds up when someone checks the numbers.</p>
      </div>
    </section>

    <section class="approach" id="approach">
      <div class="wrap approach__grid">
        <div class="approach__copy">
          <h2 class="h2 lines"><span class="line"><span>One team.</span></span><span class="line"><span>Three layers that</span></span><span class="line"><span>always agree.</span></span></h2>
          <p class="lead" data-reveal style="--d:3">Most founders hire a researcher, a modeler, a designer and a web agency, then spend weeks making their work match. We build it as one piece, so the research, the numbers and the story never contradict each other.</p>
        </div>
        <div class="layers">{layers_html}
        </div>
      </div>
    </section>

    <section class="founder" id="founder">
      <div class="wrap founder__grid">
        <figure class="portrait" data-reveal="clip">
          <img class="portrait__mark" src="icons/mark-outline.svg" alt="" width="520" height="520" data-parallax="0.1">
          <img class="portrait__photo" src="images/dragana.webp" alt="Portrait of Dragana Todorovska Janeva" width="960" height="1032" loading="lazy">
          <figcaption class="portrait__cap"><strong>Dragana Todorovska Janeva</strong><span>Founder &amp; Principal Business Consultant</span></figcaption>
        </figure>
        <div class="founder__copy">
          <h2 class="lines"><span class="line"><span>Led by a business consultant</span></span><span class="line"><span>with 7+ years in strategy.</span></span></h2>
          <p class="founder__bio" data-reveal style="--d:2">Dragana is a business consultant with more than seven years of experience developing business strategies, business and financial plans, market research and investor-ready design. She holds a BA in Economics with a major in Corporate Management, and works as an embedded consultant with advisory firms alongside her own clients. Every engagement is led and checked by her.</p>
          <dl class="stats" data-reveal style="--d:3">
            <div class="stat"><dt data-count="7" data-suffix="+">7+</dt><dd>years developing business strategies and plans</dd></div>
            <div class="stat"><dt data-count="4">4</dt><dd>market scenarios in every financial plan</dd></div>
          </dl>
          <div class="founder__cta" data-reveal style="--d:4"><a href="contact.html" class="btn btn--lg btn--on-dark" data-cta="request_quote" data-loc="founder">Request a project quote</a><a class="ulink" href="contact.html#book" data-cta="book_call" data-loc="founder">Book a call with Dragana</a><a class="ulink" href="{LINKEDIN_FOUNDER}" target="_blank" rel="noopener">Dragana on LinkedIn</a></div>
        </div>
      </div>
    </section>

    <section class="engagements" id="engagements">
      <div class="wrap">
        <h2 class="h2 lines"><span class="line"><span>Wherever you are, we build what comes next.</span></span></h2>
        <div class="tiers" data-reveal style="--d:2">{tiers_html}
        </div>
      </div>
    </section>

    <section class="process band" id="process">
      <div class="wrap">
        <div class="sec-head">
          <h2 class="h2 lines"><span class="line"><span>Clear steps, fast delivery.</span></span></h2>
          <p class="lead" data-reveal style="--d:2">Most decks, plans and models are delivered in 7 days from complete inputs. Graphic design and websites follow an agreed timeline.</p>
        </div>
        <div class="rail" aria-hidden="true"><i></i></div>
        <ol class="steps">{steps_html}</ol>
      </div>
    </section>

{faq_html(FAQS)}

    <section class="cta">
      <div class="cta__bg"><img src="images/cta.jpg" alt="" width="1024" height="683" loading="lazy" data-parallax="-0.1"></div>
      <div class="wrap">
        <span class="cta__accent" data-reveal="rule"></span>
        <h2 class="lines" style="--d:1"><span class="line"><span>Bring the decision</span></span><span class="line"><span>you need to win.</span></span></h2>
        <p data-reveal style="--d:4">Tell us who has to say yes and by when. We will tell you what they need to see.</p>
        <div data-reveal style="--d:5">{quote_cta("bottom", dark=True)}</div>
      </div>
    </section>
  </main>
"""
ld = faq_ld(FAQS) + """
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"ProfessionalService","name":"DNA Pro Plans","url":"https://dnaproplans.com/","description":"Research-led business plans, investor pitch decks and financial models for founders and business owners.","email":"office@dnaproplans.com","founder":{"@type":"Person","name":"Dragana Todorovska Janeva","jobTitle":"Founder & Principal Business Consultant","sameAs":"https://www.linkedin.com/in/dragana-todorovska-j-054314176/"},"sameAs":["https://www.linkedin.com/company/106128983/"],"areaServed":"Worldwide"}
  </script>"""
page("index.html", "Pitch Decks, Business Plans and Financial Models | DNA Pro Plans",
     "Research-led business plans, investor pitch decks and financial models for founders and business owners. Explore work samples and request a project quote.",
     home, extra=ld)


# ------------------------------------------------------------------ CASE STUDIES
def case_page(c):
    facts = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in c["facts"])
    proof = "".join(f'<li data-reveal style="--d:{i + 1}"><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(c["proof"]))
    deliver = "".join(f'<div class="deliver__item"><h3>{t}</h3><p>{d}</p></div>' for t, d in c["deliver"])
    body = f"""  <main id="main">
    <section class="case-intro">
      <div class="wrap">
        <p class="eyebrow" data-reveal="fade"><a href="case-studies.html">Case study</a></p>
        <h1 data-reveal style="--d:1">{c['title']}</h1>
        <div class="case-intro__grid">
          <dl class="facts" data-reveal style="--d:2">{facts}</dl>
          <div data-reveal style="--d:3">
            <h2>The challenge</h2>
            <p>{c['challenge']}</p>
            <h2>Our approach</h2>
            <p>{c['approach']}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="wall wall--board" aria-label="Overview of the {c['short']} deck">
      <img src="images/board-{c['key']}.webp" alt="Overview of the {c['short']} deck" width="1600" height="962" data-drift="-0.04">
    </section>

    <section class="key">
      <div class="wrap">
        <div class="feature feature--text">
          <p class="proof__label" data-reveal="fade">What the deck had to prove</p>
          <ul class="proof">{proof}</ul>
        </div>
      </div>
    </section>

    <section class="deliver band">
      <div class="wrap">
        <h2 data-reveal>What we delivered</h2>
        <div class="deliver__grid" data-stagger>{deliver}</div>
      </div>
    </section>

    <section class="cta-plain">
      <div class="wrap">
        <h2 class="lines"><span class="line"><span>Want your materials built this way?</span></span></h2>
        <p data-reveal style="--d:2">Tell us who has to say yes and by when. We reply with what they need to see and a quote.</p>
        <div data-reveal style="--d:3">{quote_cta("page_bottom", dark=True)}</div>
      </div>
    </section>

    <section class="next-case">
      <div class="wrap"><a href="{c['next'][0]}"><small>Next case study</small><strong>{c['next'][1]} <span class="arrow" aria-hidden="true">→</span></strong></a></div>
    </section>
  </main>
"""
    page(c["file"], f"{c['short']} case study | DNA Pro Plans", c["desc"], body, current="cases", note="Confidential details are not shown.")


HARAZ = dict(
    file="case-study-haraz.html", key="haraz", short="Haraz Coffee House",
    title="Haraz Coffee House: a franchise deck that turns a café brand into an investment case.",
    desc="How DNA Pro Plans built a 23-slide franchise opportunity deck for Haraz Coffee House, in light and dark versions.",
    facts=[("Client", "Haraz Coffee House"), ("Industry", "Specialty coffee, franchising"), ("Deliverable", "Franchise opportunity deck, 23 slides"),
           ("Audience", "Prospective franchisees and investors"), ("Versions", "Light and dark")],
    challenge="Haraz needed to present a fast-growing café brand to prospective franchisees. The deck had to carry the heritage story, prove the network’s growth and unit performance, and lay out the investment clearly enough for a serious buyer to evaluate in one sitting.",
    approach="We structured the deck in three chapters, Overview, Opportunity and Franchise, so each section answers one question a franchisee asks. Growth, unit sales and location performance became a single data story, and the design uses the brand’s warm gold palette with editorial photography. Delivered in light and dark versions.",
    stack=[("haraz-chapter", "Chapter slide: Opportunity"), ("haraz-location", "Slide: Location makes the difference"), ("haraz-median", "Slide: median franchised café sales")],
    light_label="From growth to opening day",
    light=[("haraz-growth", "Slide: Growth that stays open"), ("haraz-timeline", "Slide: From signing to opening day")],
    feature=("key", "Slide: cafés open and more on the way"),
    proof=[("The brand is proven", "Heritage, products and the café experience, told in a few slides."),
           ("The network is growing", "Openings, pipeline and growth that stays open, in one data story."),
           ("The investment is clear", "Terms, support and the path from signing to opening day.")],
    deliver=[("Franchise deck", "23 slides in Figma, structured in three chapters"), ("Light and dark versions", "For print, screen and in-person meetings"),
             ("PowerPoint export", "Editable for the franchise sales team"), ("Data story", "Growth, unit sales and location insights")],
    next=("case-study-custel.html", "Custel"),
)
CUSTEL = dict(
    file="case-study-custel.html", key="custel", short="Custel",
    title="Custel: an investment case for corporate cards in Türkiye, built from the research up.",
    desc="How DNA Pro Plans built a market research report, a four-scenario financial plan and a 14-slide investor deck for Custel.",
    facts=[("Client", "Custel"), ("Industry", "Fintech, corporate cards and spend control"), ("Deliverables", "Market research report, financial plan, pitch deck"),
           ("Audience", "Seed investors"), ("Deck", "14 slides and a 6-slide appendix")],
    challenge="Custel is building corporate cards and spend control for Türkiye’s field teams. To raise, they had to size a market no one had published numbers for, prove the unit economics, and explain why neither banks nor expense software already solve the problem.",
    approach="We started with a market research report on Türkiye’s corporate card market, then built a financial plan with four market scenarios. Both became a 14-slide pitch deck with an appendix for due diligence, so every figure in the deck traces back to the research and the model.",
    stack=[("custel-problem", "Slide: the problem"), ("custel-solution", "Slide: the solution"), ("custel-how", "Slide: how it works")],
    light_label="Scenarios and competition",
    light=[("custel-scenarios", "Slide: four market scenarios"), ("custel-competition", "Slide: competition")],
    feature=("market", "Slide: market sizing"),
    proof=[("The market is real", "Field employees, employers and active cards, sized from published sources."),
           ("The model holds", "Four market scenarios, with cash positive in each."),
           ("The gap is open", "Banks hold the card, software holds the ledger. No one holds both.")],
    deliver=[("Market research report", "Türkiye corporate card market, designed in Figma"), ("Financial plan", "Five-year model with four scenarios"),
             ("Pitch deck", "14 slides plus a 6-slide appendix"), ("Figures that reconcile", "Every deck number traced to research or model")],
    next=("case-study-haraz.html", "Haraz Coffee House"),
)
case_page(HARAZ)
case_page(CUSTEL)

cards = ""
for c, blurb, tags in [
    (HARAZ, "A 23-slide franchise opportunity deck that carries the heritage story, proves the network’s growth and lays out the investment for a serious buyer.", ["Franchising", "Pitch deck", "Light and dark"]),
    (CUSTEL, "A market research report and a four-scenario financial plan, turned into a 14-slide seed deck where every figure traces back to the research and the model.", ["Fintech", "Market research", "Financial plan", "Pitch deck"]),
]:
    tg = "".join(f"<li>{t}</li>" for t in tags)
    cards += f"""
        <article class="case-card">
          <a class="case-card__media" href="{c['file']}" data-reveal="clip" tabindex="-1" aria-hidden="true"><img src="images/board-{c['key']}.webp" alt="" width="1600" height="962"></a>
          <div data-reveal style="--d:2">
            <p class="eyebrow">{c['facts'][1][1]}</p>
            <h2><a href="{c['file']}">{c['short']}</a></h2>
            <p>{blurb}</p>
            <ul class="tags">{tg}</ul>
            <a class="ulink" href="{c['file']}">Read the case study</a>
          </div>
        </article>"""
page("case-studies.html", "Case studies | DNA Pro Plans",
     "Selected work from DNA Pro Plans: investor and franchise decks, market research and financial plans. Confidential figures are masked.",
     f"""  <main id="main">
    <section class="page-head">
      <div class="wrap">
        <p class="eyebrow" data-reveal="fade">Case studies</p>
        <h1 class="h1 lines" style="--d:1"><span class="line"><span>Work that had to</span></span><span class="line"><span>hold up to scrutiny.</span></span></h1>
        <p class="lead" data-reveal style="--d:4">Two engagements, shown with the client’s permission. Confidential details are not shown.</p>
      </div>
    </section>
    <section class="wrap cases">{cards}
    </section>
    <section class="cta-plain">
      <div class="wrap">
        <h2 class="lines"><span class="line"><span>Want your materials built this way?</span></span></h2>
        <p data-reveal style="--d:2">Tell us who has to say yes and by when. We reply with what they need to see and a quote.</p>
        <div data-reveal style="--d:3">{quote_cta("page_bottom", dark=True)}</div>
      </div>
    </section>
  </main>
""", current="cases", note="Confidential details are not shown.")

# ------------------------------------------------------------------ SERVICES
def facts(rows):
    return ('<details class="more"><summary>Who it is for, files, timing and inputs</summary><dl class="specs">'
            + "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows) + "</dl></details>")


def offer(anchor, eyebrow, title, lead, price_html, need, right, more=None):
    more_html = f'<p class="offer__more"><a class="ulink" href="{more[0]}">{more[1]}</a></p>' if more else ""
    return f"""
    <section class="offer" id="{anchor}">
      <div class="wrap offer__grid">
        <div class="offer__side" data-reveal>
          <p class="eyebrow">{eyebrow}</p>
          <h2>{title}</h2>
          <p class="lead">{lead}</p>
          {price_html}
          <div class="cta-row cta-row--stack"><a href="contact.html" class="btn" data-cta="request_quote" data-loc="services_{anchor}">Request a quote</a><a class="ulink" href="contact.html#book" data-cta="book_call" data-loc="services_{anchor}">Or book a 30-minute call</a></div>
          {more_html}
        </div>
        <div data-reveal style="--d:2">{right}</div>
      </div>
    </section>"""


TIMING = "Most plans, models and decks are delivered in 7 days. The 7 days start on the day we have your complete inputs, not on the day you inquire."
REVISIONS = "You review a preview before final files are sent. The number of revision rounds is confirmed in your quote."
INPUT_NOTE = " A full input list for your project follows after your inquiry."
HOW = 'Send a short inquiry on the <a href="contact.html">quote page</a>: name, email, service, deadline and a few lines about the project. A call is optional.'


def contents(label, items):
    return f'<p class="offer__k">{label}</p><ol class="contents">' + "".join(f"<li><div><strong>{t}</strong><span>{d}</span></div></li>" for t, d in items) + "</ol>"


def price(amount, note):
    return f'<p class="price"><small>from</small><strong>{amount}</strong></p><p class="price__note">{note}</p>'


QUOTE = '<p class="price price--quote"><strong>Individually quoted</strong></p><p class="price__note">Scope, fee and delivery date are agreed before work starts.</p>'
BP = [("Executive summary", "The whole plan on one page: opportunity, ask and key numbers."),
      ("Market gaps", "The unmet needs your business is built to solve."),
      ("Company description", "Who you are, structure, mission, location and team."),
      ("Products &amp; services", "What you sell, how it works and why it wins."),
      ("Industry analysis", "Market size, trends and growth from public sources."),
      ("Customer analysis", "Target segments, how many potential customers there are, and how many you can acquire with specific marketing strategies."),
      ("Competitor analysis", "Key players analysed from public data and financials: revenue, clients, funding and the strategies they use."),
      ("Marketing plan", "Channels, pricing and customer acquisition cost (CAC) for each channel."),
      ("Financial plan", "Projections and funding need, taken from the model.")]
FP = [("Cover", "Company, scenario selector and key results."),
      ("Scenarios", "Four market driven cases, switched with one input."),
      ("Revenue assumptions", "Marketing spend, CAC, conversion, pricing and churn."),
      ("Payroll assumptions", "Every role costed from its start month."),
      ("Cost assumptions", "Operating costs, cost of sales and inflation."),
      ("Investment assumptions", "Start up costs, capex, funding and use of funds."),
      ("Monthly projections", "All 3 statements: P&amp;L, cash flow and balance sheet."),
      ("Annual projections", "The yearly view of all three statements."),
      ("Investor metrics", "NPV, IRR, payback period, ROI, break-even month, DSCR, gross margin, EBITDA margin, cash runway and peak funding need.")]
SAMPLE = [("sample-1-cover", "Cover"), ("sample-2-contents", "Contents"), ("sample-3-summary", "Executive summary"),
          ("sample-4-company", "Company overview"), ("sample-5-market", "Market analysis"), ("sample-6-financials", "Financial statements")]
reel = "".join(f'<figure><img src="images/{f}.webp" alt="Sample business plan page: {c}" width="900" height="1273" loading="lazy" draggable="false"><figcaption>{c}</figcaption></figure>' for f, c in SAMPLE)

RESEARCH = [("research-1-cover", "Cover"), ("research-2-findings", "Key findings"), ("research-3-market", "Market size and growth"),
            ("research-4-customer", "Customer and demand"), ("research-5-competition", "Competitive landscape"), ("research-6-entry", "Where to enter first")]
BRAND = [("brand-01-cover", "Cover"), ("brand-02-logo", "Logo and icon"), ("brand-03-usage", "Logo and icon usage"), ("brand-04-clearspace", "Clear space and misuse"),
         ("brand-05-pattern", "Pattern"), ("brand-06-photography", "Photography"), ("brand-07-treatment", "Photo treatment"), ("brand-08-color", "Colour and font"),
         ("brand-09-icons", "Icons"), ("brand-10-industry", "Industry icons"), ("brand-11-linkedin", "LinkedIn cover"), ("brand-12-contact", "Contact")]
research_reel = "".join(f'<figure><img src="images/{f}.webp" alt="Sample market research report page: {c}" width="900" height="1273" loading="lazy" draggable="false"><figcaption>{c}</figcaption></figure>' for f, c in RESEARCH)
brand_reel = "".join(f'<figure><img src="images/{f}.webp" alt="DNA Pro Plans brand guidelines page: {c}" width="1200" height="717" loading="lazy" draggable="false"><figcaption>{c}</figcaption></figure>' for f, c in BRAND)


def sample_sec(anchor, eyebrow, title, lead, reel_html, note, wide=False):
    return f"""
    <section class="sample" id="{anchor}">
      <div class="wrap">
        <p class="eyebrow" data-reveal="fade">{eyebrow}</p>
        <h2 class="lines"><span class="line"><span>{title}</span></span></h2>
        <p class="lead" data-reveal style="--d:2">{lead}</p>
      </div>
      <div class="reel{' reel--wide' if wide else ''}" data-reveal="fade" style="--d:3" tabindex="0" aria-label="{eyebrow} pages">{reel_html}</div>
      <div class="wrap"><p class="sample__note">{note}</p></div>
    </section>"""


SPEC = {
    "business-plan": facts([
        ("Who it is for", "Founders and owners who need a written plan for investors, banks or visa programs."),
        ("Editable files", "The written plan as an editable document, plus a designed PDF."),
        ("Financial model", "The plan is built on a financial plan, so every number in the text matches the model. Your quote states whether the editable Excel model is included in your price or quoted with it (financial models start from $360)."),
        ("What we need from you", "The decision you need and your deadline, what the business sells and to whom, and any existing financials, plans or decks." + INPUT_NOTE),
        ("Delivery", TIMING),
        ("Revisions", REVISIONS),
        ("Sample", 'Six pages of a <a href="services.html#sample">sample business plan</a> for a fictional company.'),
        ("How to request a quote", HOW)]),
    "financial-plan": facts([
        ("Who it is for", "Founders and owners who need projections for a raise, a loan application or their own planning."),
        ("Editable files", "An Excel workbook with live formulas. Change an assumption and all three statements update."),
        ("What we need from you", "Prices and sales assumptions, team and salaries, operating costs, start-up costs and the funding you are looking for." + INPUT_NOTE),
        ("Delivery", TIMING),
        ("Revisions", REVISIONS),
        ("Sample", 'An <a href="financial-modeling-services.html#example">illustrative four-scenario example</a> and the <a href="services.html#sample">financial pages of the sample plan</a>.'),
        ("How to request a quote", HOW)]),
    "pitch-decks": facts([
        ("Who it is for", "Founders raising from investors, and companies approaching partners, distributors or large clients."),
        ("Editable files", "Designed in Figma and delivered with a PowerPoint export your team can edit. Light and dark versions where needed."),
        ("What we need from you", "Your current deck or notes, the key numbers, who the deck is for and your brand assets." + INPUT_NOTE),
        ("Delivery", TIMING),
        ("Revisions", REVISIONS),
        ("Sample", 'Overviews of <a href="services.html#deck-examples">four client decks</a>.'),
        ("How to request a quote", HOW)]),
    "market-research": facts([
        ("Who it is for", "Founders who need to size a market or prove demand before they raise, borrow or enter a new market."),
        ("Editable files", "A designed report. The file formats are listed in your quote."),
        ("What we need from you", "The product, the market and geography you want sized, and the competitors you already know." + INPUT_NOTE),
        ("Delivery", "The delivery date depends on the scope of the research and is agreed in your quote. It is counted from the day we have your complete inputs."),
        ("Revisions", REVISIONS),
        ("Sample", 'Six pages of a <a href="services.html#research-sample">sample market research report</a> with illustrative figures.'),
        ("How to request a quote", HOW)]),
    "graphic-design": facts([
        ("Who it is for", "Founders launching a company, or owners whose brand and materials no longer match their plan."),
        ("Editable files", "Logo files, brand guidelines and a live website. The file formats are listed in your quote."),
        ("What we need from you", "What the company does, who it sells to, and any existing logo, colours or website." + INPUT_NOTE),
        ("Delivery", "Graphic design and websites follow a timeline agreed in your quote."),
        ("Revisions", REVISIONS),
        ("Sample", 'Our own <a href="services.html#brand-sample">brand guidelines</a>.'),
        ("How to request a quote", HOW)]),
}

services_body = f"""  <main id="main">
    <section class="page-head">
      <div class="wrap">
        <p class="eyebrow" data-reveal="fade">Services and pricing</p>
        <h1 class="h1" data-reveal style="--d:1">What we build, what you receive and what it costs.</h1>
        <p class="lead" data-reveal style="--d:3">Business plans, financial plans, pitch decks, market research and graphic design. Business plans start from $900 and financial plans from $360; the rest are quoted individually. Every price is confirmed in a written quote before work starts.</p>
        <nav class="jump" aria-label="Services on this page" data-reveal style="--d:4"><a href="#business-plan">Business plans</a><a href="#financial-plan">Financial plans</a><a href="#pitch-decks">Pitch decks</a><a href="#market-research">Market research</a><a href="#graphic-design">Graphic design</a></nav>
      </div>
    </section>
{offer("business-plan", "Business plans", "A written plan built for investors, banks and visa programs.",
       "Built on the financial plan, so every number in the text matches the model behind it.",
       price("$900", "Written plan. Final price depends on scope."), "Business plan", contents("What you get", BP) + SPEC["business-plan"],
       more=("business-plan-services.html", "More about business plans"))}

{sample_sec("sample", "Sample business plan", "See what a finished plan looks like.", "Six pages from a 24-page plan for Fieldhouse Workspace, a fictional coworking company asking for an SBA loan. Swipe or drag to look through it.", reel, "Sample plan for a fictional company, prepared by DNA Pro Plans. All figures are illustrative.")}
{offer("financial-plan", "Financial plans", "An Excel financial model in four scenarios based on market factors.",
       "Live formulas and analysis based on real market data, built to account for the future: Base, Upside, Downside and Stress.",
       price("$360", "Excel model. Final price depends on scope."), "Financial plan", contents("What you get", FP) + SPEC["financial-plan"],
       more=("financial-modeling-services.html", "More about financial plans and models"))}
{offer("pitch-decks", "Pitch decks and sales decks", "Decks for investors, partners and large clients.",
       "The reader asks: why this company, and why now? The deck answers it with a clear story and the numbers behind it.",
       QUOTE, "Pitch deck or sales deck",
       contents("What you get", [("Investor pitch deck", "Problem, solution, market, model, traction and the ask."),
                                 ("Sales and partnership decks", "For partners, distributors and large clients."),
                                 ("Appendix for due diligence", "Scenarios, assumptions and supporting data."),
                                 ("Editable files", "Figma and PowerPoint, in light and dark where needed.")]) + SPEC["pitch-decks"],
       more=("pitch-deck-services.html", "More about pitch decks"))}
{deck_gallery()}
{offer("market-research", "Market research papers", "Market sizing, demand and competitor intelligence.",
       "Evidence from sources the reader can verify. Estimates are labelled as estimates.",
       QUOTE, "Market research paper",
       contents("What you get", [("Market size", "Sized from public sources, with the method shown."),
                                 ("Customer segments and demand", "Who buys, how many there are and what they pay."),
                                 ("Competitor intelligence", "Revenue, clients, funding and the strategies they use."),
                                 ("Sources", "Every figure cited, every estimate labelled.")]) + SPEC["market-research"])}
{sample_sec("research-sample", "Sample market research report", "See what a research report looks like.", "Six pages from a 32-page report on EV charging for apartment and multifamily buildings in the United States: market size, demand, competition and where to enter first.", research_reel, "Sample report with illustrative figures, prepared by DNA Pro Plans for a fictional client.")}
{offer("graphic-design", "Graphic design", "Brand identity and designed materials that match your documents.",
       "The same story your plan and deck tell, carried into how the company looks: identity, guidelines, reports, one-pagers and web pages.",
       QUOTE, "Graphic design",
       contents("What you get", [("Brand identity", "Logo, icon, colour, type and pattern."),
                                 ("Brand guidelines", "Usage rules your team and suppliers can follow."),
                                 ("Designed documents", "Reports, one-pagers, proposals and ads on one identity."),
                                 ("Website design and build", "Pages that point to the decision you need.")]) + SPEC["graphic-design"])}
{sample_sec("brand-sample", "Brand guidelines", "One identity for every deck, plan and page.", "Our own brand guidelines: logo, colour, type, pattern, photography and icons. This is the kind of system we build for clients.", brand_reel, "DNA Pro Plans brand guidelines.", wide=True)}
{faq_html(FAQS, band=False)}

    <section class="cta-plain">
      <div class="wrap">
        <h2 class="lines"><span class="line"><span>Not sure which one you need?</span></span></h2>
        <p data-reveal style="--d:2">Tell us who has to say yes and by when. We reply with what they need to see and a quote.</p>
        <div data-reveal style="--d:3">{quote_cta("page_bottom", dark=True)}</div>
      </div>
    </section>
  </main>
"""
page("services.html", "Services and Pricing | DNA Pro Plans",
     "Business plans, financial plans, pitch decks, market research and graphic design. See deliverables, pricing, file formats, timing and samples for each service.",
     services_body, current="services")

# ------------------------------------------------------------------ SERVICE PAGES (phase 2)
def bullets(items):
    return '<ul class="squares">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def service_page(file, eyebrow, h1, lead, price_html, who, get_label, get_items, spec, middle, faqs, title, desc, loc):
    body = f"""  <main id="main">
    <section class="page-head page-head--svc">
      <div class="wrap svc-hero">
        <div>
          <p class="eyebrow" data-reveal="fade"><a href="services.html">Services</a> / {eyebrow}</p>
          <h1 class="h1" data-reveal style="--d:1">{h1}</h1>
          <p class="lead" data-reveal style="--d:3">{lead}</p>
          <div data-reveal style="--d:4">{quote_cta(loc + "_top")}</div>
        </div>
        <aside class="svc-hero__side" data-reveal style="--d:3">
          {price_html}
          <p class="offer__k" style="margin-top:26px">Who it is for</p>
          {bullets(who)}
        </aside>
      </div>
    </section>

    <section class="offer">
      <div class="wrap offer__grid">
        <div class="offer__side" data-reveal>
          <h2>{get_label}</h2>
        </div>
        <div data-reveal style="--d:2">{contents("Included", get_items)}{spec}</div>
      </div>
    </section>
{middle}
{faq_html(faqs)}

    <section class="cta-plain">
      <div class="wrap">
        <h2 class="lines"><span class="line"><span>Tell us who has to say yes.</span></span></h2>
        <p data-reveal style="--d:2">Send a short inquiry and we reply with what your reader needs to see and a quote. A call is optional.</p>
        <div data-reveal style="--d:3">{quote_cta(loc + "_bottom", dark=True)}</div>
      </div>
    </section>
  </main>
"""
    page(file, title, desc, body, current="services", extra=faq_ld(faqs))


SCENARIO_EXAMPLE = """
    <section class="example band" id="example">
      <div class="wrap">
        <div class="sec-head">
          <h2 class="h2" data-reveal>One business. Four futures.</h2>
          <p class="lead" data-reveal style="--d:2">An illustrative example: a boutique fitness studio opening its first location with a planned $250K investment. Hypothetical figures, not a client project.</p>
        </div>
        <div class="table-wrap" data-reveal style="--d:3">
          <table class="table">
            <caption class="sr">Illustrative four-scenario comparison for a boutique fitness studio</caption>
            <thead><tr><th scope="col">Scenario</th><th scope="col">What changes</th><th scope="col">Year 3 revenue</th><th scope="col">Break-even</th><th scope="col">Funding need</th></tr></thead>
            <tbody>
              <tr><th scope="row">Upside</th><td>Strong demand and pricing power</td><td>$624K</td><td>Month 9</td><td>$230K</td></tr>
              <tr><th scope="row">Base</th><td>Steady local demand</td><td>$461K</td><td>Month 14</td><td>$250K</td></tr>
              <tr class="is-key"><th scope="row">Downside</th><td>Consumer spending slows</td><td>$331K</td><td>Month 22</td><td>$290K</td></tr>
              <tr><th scope="row">Stress</th><td>Competitor opens, rent +15%</td><td>$238K</td><td>Month 34</td><td>$340K</td></tr>
            </tbody>
          </table>
        </div>
        <p class="example__take" data-reveal><strong>Downside is the number to fund.</strong> Ask for $290K, not $250K. The studio still breaks even in the Downside case, and the lender sees you planned for it.</p>
      </div>
    </section>"""

DECK_SLIDES = [("The core deck", "Cover, problem, solution, how it works, market, business model, unit economics, competition, go-to-market, traction and roadmap, financials, the ask, founders and closing."),
               ("Appendix for due diligence", "Vision and exit, team and organisation, scenarios, risks and mitigations, and key assumptions, so follow-up questions have an answer ready."),
               ("Sales and partnership decks", "The same approach for partners, distributors and large clients: what you offer, why it works and what you are asking them to do."),
               ("Light and dark versions", "Where needed, one version for screens and one for print and in-person meetings."),
               ("Editable files", "Designed in Figma and delivered with a PowerPoint export your team can edit.")]

service_page(
    "pitch-deck-services.html", "Pitch decks",
    "Investor pitch decks built on the research and the model.",
    "A deck opens the door. Investors then ask for what is behind it. We build the deck from market research and a financial model, so each slide holds up when someone checks the numbers.",
    QUOTE,
    ["Founders raising a seed or later round", "Owners and brokers presenting an investment or property opportunity", "Companies approaching partners, distributors or large clients"],
    "What a pitch deck engagement includes", DECK_SLIDES, SPEC["pitch-decks"],
    deck_gallery(),
    [("How many slides is an investor deck?", "It depends on the reader. Recent seed decks ran from 13 to 15 slides, some with an appendix for due diligence, and franchise and investment decks ran longer. We agree the structure with you before design starts."),
     ("I have a deck already. Do I still need a business plan?", "If you are raising money or applying for a loan, usually yes. The deck opens the door and the plan gets the approval: due diligence asks for the model behind the deck."),
     ("Can you write the deck, or only design it?", "Both. Research, financial modeling, copy and presentation design are developed together, so you do not need finished text."),
     ("Can you rework the deck I have?", "Yes. Send it with your inquiry and we will tell you what can be kept and what needs rebuilding."),
     ("What files do I get?", "A PowerPoint export your team can edit, and the Figma source. The exact formats are listed in your quote."),
     FAQS[5], FAQS[4]],
    "Investor Pitch Deck Services | DNA Pro Plans",
    "Investor pitch decks and sales decks built on market research and a financial model. See overviews of recent decks and request a project quote.",
    "pitch")

service_page(
    "financial-modeling-services.html", "Financial models",
    "Financial models in four scenarios, built in Excel.",
    "Instead of one fixed five-year forecast, your model shows how the business performs across four futures driven by real market factors: Base, Upside, Downside and Stress.",
    price("$360", "Excel model. Final price depends on scope."),
    ["Founders preparing a raise who need the numbers behind the deck", "Owners applying for a bank or SBA loan", "Teams that need a planning model they can keep updating"],
    "What the Excel model contains", FP, SPEC["financial-plan"],
    SCENARIO_EXAMPLE,
    [("Why four scenarios instead of one forecast?", "Because the reader will ask what happens if things go worse than planned. Four cases, switched with one input, show how revenue, break-even and the funding need move when the market does."),
     ("Is the model editable?", "Yes. It is an Excel workbook with live formulas. Change an assumption and the monthly and annual statements update."),
     ("Which statements and metrics are included?", "All three statements, P&amp;L, cash flow and balance sheet, monthly and annual, plus investor metrics: NPV, IRR, payback period, ROI, break-even month, DSCR, gross margin, EBITDA margin, cash runway and peak funding need."),
     ("What do you need from me to build it?", "Prices and sales assumptions, team and salaries, operating costs, start-up costs and the funding you are looking for. A full input list for your project follows after your inquiry."),
     ("Can you fix or extend a model I already have?", "Yes. Send it with your inquiry and we will tell you what can be kept and what needs rebuilding."),
     FAQS[5], FAQS[6]],
    "Financial Modeling Services in Excel | DNA Pro Plans",
    "Editable Excel financial models from $360: five-year projections in Base, Upside, Downside and Stress scenarios with three statements and investor metrics.",
    "model")

service_page(
    "business-plan-services.html", "Business plans",
    "Business plans written for investors, banks and visa programs.",
    "A written plan built on a financial plan, so every number in the text matches the model behind it. Research, writing, numbers and design are done as one piece of work.",
    price("$900", "Written plan. Final price depends on scope."),
    ["Founders raising money: due diligence asks for the model behind the deck", "Owners applying to banks and the SBA: lenders need projections that prove repayment", "Applicants to visa programs that require a complete, credible business plan"],
    "The nine sections of the plan", BP, SPEC["business-plan"],
    sample_sec("sample", "Sample business plan", "See what a finished plan looks like.", "Six pages from a 24-page plan for Fieldhouse Workspace, a fictional coworking company asking for an SBA loan. Swipe or drag to look through it.", reel, "Sample plan for a fictional company, prepared by DNA Pro Plans. All figures are illustrative."),
    [("Does the $900 starting price include the financial model?", "The plan is always built on a financial plan, so the numbers in the text match a model. Your quote states whether the editable Excel model is included in your price or quoted alongside it. Financial models on their own start from $360."),
     ("I already have a pitch deck. Why would I need a plan?", "The deck opens the door, the plan gets the approval. Investors ask for the model behind the deck, lenders need projections that prove repayment, and visa programs require a complete plan."),
     ("Where does the market data come from?", "From public sources the reader can verify: market size, trends and growth, and competitors analysed from public data and financials. Estimates are labelled as estimates."),
     FAQS[0], FAQS[1], FAQS[5], FAQS[6]],
    "Business Plan Services | DNA Pro Plans",
    "Research-led business plans from $900, built on a four-scenario financial plan. See the nine sections, a sample plan and how to request a quote.",
    "plan")

SBA_GET = [("Funding request and use of funds", "How much you are asking for and what each part pays for. In the sample plan: build-out, furniture and IT, and working capital."),
           ("Company overview and operating history", "Who you are, ownership and management, and what the business has done so far."),
           ("Market and competitor analysis", "Local demand, customers and competitors, from sources the lender can verify."),
           ("Operations and marketing plan", "The site, staffing, opening timeline and how customers will be won."),
           ("Financial plan in four scenarios", "Monthly and annual P&amp;L, cash flow and balance sheet in Base, Upside, Downside and Stress cases."),
           ("Debt service view", "Cash flow after debt service and the debt service coverage ratio (DSCR) for each year, so the lender can see how repayment holds up when sales fall short.")]
service_page(
    "sba-business-plan-services.html", "SBA business plans",
    "Business plans for SBA and bank loan applications.",
    "Lenders need projections that prove repayment. We write the plan and build the financial plan behind it, with a Downside and a Stress case, so the lender can see the loan is still serviced when things go worse than planned.",
    '<p class="price"><small>plan from</small><strong>$900</strong></p><p class="price__note">Financial models start from $360. Your quote states what is included. Final price depends on scope.</p>',
    ["Owners applying for an SBA or bank loan to open, expand or buy a business", "Founders whose lender has asked for a business plan and projections", "Advisors who need a lender-ready plan for a client"],
    "What a lender-ready plan covers", SBA_GET, SPEC["business-plan"],
    sample_sec("sample", "Sample SBA loan plan", "A sample plan for an SBA 7(a) loan request.", "Six pages from a 24-page plan for Fieldhouse Workspace, a fictional coworking company asking for a $420,000 SBA 7(a) loan to open a second location. Swipe or drag to look through it.", reel, "Sample plan for a fictional company, prepared by DNA Pro Plans. All figures are illustrative.") + SCENARIO_EXAMPLE,
    [("Do you guarantee the loan will be approved?", "No. We make your case clear and check that the numbers hold. The lender decides."),
     ("Why does the plan include Downside and Stress cases?", "Because a lender wants to know the loan is repaid even when sales come in below plan. In the illustrative example on this page, the Downside case is the number to fund."),
     ("Which loan programs do you write plans for?", "Bank loans and SBA loans. The sample on this page is written for an SBA 7(a) request. Your lender’s own checklist decides what the plan must contain, so send it with your inquiry if you have one."),
     ("What do you need from me?", "The amount you want to borrow and what it is for, your existing financials if the business is already trading, and your lender’s checklist if you have one. A full input list follows after your inquiry."),
     ("Can you work from my existing plan or projections?", "Yes. Send what you have with your inquiry and we will tell you what can be kept and what needs rebuilding."),
     FAQS[5], FAQS[4]],
    "SBA Business Plan Services | DNA Pro Plans",
    "Lender-ready business plans for SBA and bank loans, with projections in four scenarios and a debt service view. See a sample SBA 7(a) plan and request a quote.",
    "sba")

# ------------------------------------------------------------------ CONTACT
page("contact.html", "Request a Project Quote | DNA Pro Plans",
     "Send a short inquiry for a pitch deck, business plan or financial model and get a written quote. Booking a call is optional.",
     f"""  <main id="main">
    <section class="contact">
      <div class="wrap contact__grid">
        <div class="contact__copy">
          <p class="eyebrow" data-reveal="fade">Request a quote</p>
          <h1 class="h1" data-reveal style="--d:1">Tell us who has to say yes.</h1>
          <p class="lead" data-reveal style="--d:3">Send a short inquiry and get a written quote: scope, fee and delivery date. You do not need to book a call.</p>
          <ol class="flow" data-reveal style="--d:4">
            <li class="is-on"><span>01</span><div><strong>Send a short inquiry</strong><small>The service you need, your deadline and a few lines about the project.</small></div></li>
            <li class="is-on"><span>02</span><div><strong>Get your quote by email</strong><small>We reply with any questions, then the scope, fee and delivery date.</small></div></li>
            <li class="is-on"><span>03</span><div><strong>Send inputs, work starts</strong><small>Detailed business inputs and documents are collected after you accept the quote.</small></div></li>
          </ol>
          <div class="led" data-reveal style="--d:5">
            <img src="images/dragana.webp" alt="Dragana Todorovska Janeva" width="64" height="64">
            <div><p class="led__name">Dragana Todorovska Janeva</p><p class="led__role">Founder &amp; Principal Business Consultant</p></div>
          </div>
          <p class="contact__direct" data-reveal style="--d:6">Prefer to talk first? <a href="#book" data-cta="book_call" data-loc="contact_side">Book an optional 30-minute call</a>, or write to <a href="mailto:office@dnaproplans.com">office@dnaproplans.com</a>.</p>
        </div>

        <div class="contact__steps">
          <div class="card" id="inquiry" data-reveal style="--d:2">
            <h2>Your inquiry</h2>
            <p class="card__sub">Everything you share stays confidential. An NDA is available on request.</p>
            <div class="booking" id="inquiry-form">
              <iframe class="brief__frame" src="{FORM}?embedded=true" title="Project inquiry form"></iframe>
              <p class="booking__alt">The form is provided by Pipefy. When you submit it, the form itself confirms that your inquiry was received. If it does not load, <a href="{FORM}" target="_blank" rel="noopener">open the form in a new tab</a> or email <a href="mailto:office@dnaproplans.com">office@dnaproplans.com</a>.</p>
            </div>
            <div class="confirm" id="inquiry-done" hidden tabindex="-1">
              <span class="tick"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M4 12.5l5.5 5.5L20 6.5"/></svg></span>
              <h2>Your inquiry is in.</h2>
              <p class="card__sub">Thank you. We read it and reply by email with any questions, then your quote. Nothing else is needed from you now.</p>
              <p class="card__sub">If you would like to talk it through, you can book an optional call below.</p>
            </div>
          </div>
          <div class="card" id="book" data-reveal>
            <p class="card__step">Optional</p>
            <h2>Book a 30-minute call</h2>
            <p class="card__sub">Useful if you want to talk the project through first. You can also send the inquiry and skip the call.</p>
            <div class="booking">
              <div id="calendly" class="calendly" data-url="{CAL}?hide_gdpr_banner=1&amp;primary_color=5271ff"></div>
              <button type="button" class="btn" id="calendly-load" data-cta="show_calendar" data-loc="contact">Show available times</button>
              <p class="booking__alt">The calendar is provided by Calendly and loads only when you ask for it. Or <a href="{CAL}" target="_blank" rel="noopener" data-cta="open_calendly" data-loc="contact">open the booking page in a new tab</a>.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
""")

page("thank-you.html", "Inquiry received | DNA Pro Plans", "Your inquiry has been received.",
     f"""  <main id="main">
    <section class="wrap center-page" id="thanks" data-inquiry-complete>
      <span class="tick"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M4 12.5l5.5 5.5L20 6.5"/></svg></span>
      <h1 class="h1">Your inquiry is in.</h1>
      <p class="lead">Thank you. We read it and reply by email with any questions, then your quote: scope, fee and delivery date. Nothing else is needed from you now.</p>
      <p class="lead">If you would like to talk it through, you can book an optional 30-minute call.</p>
      <div class="hero__actions"><a href="contact.html#book" class="btn" data-cta="book_call" data-loc="thank_you">Book an optional call</a><a href="case-studies.html" class="btn btn--ghost">See client work</a></div>
    </section>
  </main>
""", index=False, tag=False)

# ------------------------------------------------------------------ PRIVACY / 404
MAIL = '<a href="mailto:office@dnaproplans.com">office@dnaproplans.com</a>'
page("privacy.html", "Privacy, Cookies, Payments and Refunds | DNA Pro Plans", "How DNA Pro Plans collects, uses and stores your information, how optional analytics works, and how payments and refunds work.",
     f"""  <main id="main">
    <div class="wrap">
      <div class="prose">
        <p class="eyebrow">Legal</p>
        <h1 class="h1">Privacy, cookies, payments and refunds</h1>
        <p>Last updated: November 2026</p>
        <h2>Who we are</h2>
        <p>DNA Pro Plans ("we", "us") provides business planning, financial modeling, research, presentation, branding and website services. Contact: {MAIL}.</p>
        <h2>What we collect</h2>
        <p>When you submit the inquiry form, we collect the details you enter in it, such as your name, email address, the service you need, your deadline, a description of your project and any files you choose to upload. When you book a call, the booking is handled by Calendly, which collects the details you enter there.</p>
        <h2>How we use it</h2>
        <ul><li>To reply to your inquiry, prepare a quote and hold a call if you book one.</li><li>To deliver agreed work and communicate about your project.</li></ul>
        <p>We do not sell your information or use it for unrelated marketing.</p>
        <h2 id="cookies">Analytics and cookies</h2>
        <p>This website uses Google Analytics. Google’s tag is loaded on every page, with analytics cookies switched off by default. Until you choose "Accept", no analytics cookies are set or read, and Google receives only limited, cookieless signals that a page was viewed, which are not tied to you as a visitor.</p>
        <p>If you accept, Google Analytics sets cookies and records usage data such as pages viewed, buttons clicked, approximate location and device type, and whether an inquiry or booking was completed. We do not send your name, email address, project description or files to Google Analytics, and advertising features are not enabled. If you choose "Reject", cookies stay off.</p>
        <p>Your choice is saved in your browser’s local storage so we do not ask on every page. You can change it at any time: <button type="button" class="linklike" data-consent-open>open cookie settings</button>. The same link is in the footer of every page.</p>
        <p>The site’s fonts, styles and scripts are served from our own domain.</p>
        <h2>Embedded services</h2>
        <p>The inquiry form on the quote page is provided by Pipefy and is shown in a frame on that page only. It loads when you open the page, and Pipefy and its spam-protection provider (hCaptcha) may set cookies that are needed for the form to work. The booking calendar is provided by Calendly and is loaded only when you click "Show available times" or follow a "Book a call" link. Each provider processes the details you enter under its own privacy policy.</p>
        <h2>Where it is stored</h2>
        <p>Inquiries are stored in Pipefy and bookings in Calendly. The website is hosted on Cloudflare, which processes technical data such as IP addresses to deliver and protect the site. Project materials are stored only as long as needed for the engagement and any agreed support period.</p>
        <h2>Confidentiality</h2>
        <p>An NDA is available on request. Any public use of your name, project materials or results requires your permission.</p>
        <h2>Payments</h2>
        <p>The fee, what it covers and the payment schedule are agreed in writing before work starts. This website does not take payments and we do not collect or store card details. You pay by invoice using the method named in your quote, and any bank or payment provider involved handles your details under its own privacy policy. We keep invoices and payment records for as long as accounting and tax rules require.</p>
        <h2>Cancellations and refunds</h2>
        <p>Every plan, deck, model and website is made for one client, so refunds depend on how much of the work has been done.</p>
        <ul><li>If you cancel before work starts, we refund what you have paid in full.</li><li>If you cancel after work has started, we refund the part of the fee for work not yet done and send you what has been completed.</li><li>Once the final files are delivered, the fee is not refundable. The revisions included in your quote still apply, and we will correct any error on our side.</li></ul>
        <p>To cancel or ask for a refund, email {MAIL}.</p>
        <h2>Your rights</h2>
        <p>You can ask us to access, correct or delete your personal information at any time by emailing {MAIL}.</p>
      </div>
    </div>
  </main>
""")

page("404.html", "Page not found | DNA Pro Plans", "This page does not exist.",
     """  <main id="main">
    <section class="wrap center-page">
      <p class="big404" aria-hidden="true">404</p>
      <h1 class="h1">This page is not in the plan.</h1>
      <p class="lead">The link may be old or mistyped. The home page has everything we build.</p>
      <div class="hero__actions"><a href="index.html" class="btn">Back to home</a><a href="contact.html" class="btn btn--ghost">Request a quote</a></div>
    </section>
  </main>
""", index=False)

# ------------------------------------------------------------------ SITEMAP / ROBOTS / VERSION
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                 + "".join(f"  <url><loc>{u}</loc></url>\n" for u in SITEMAP) + "</urlset>\n")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /thank-you\n\nSitemap: {SITE}/sitemap.xml\n")
(OUT / "version.txt").write_text(f"dnaproplans.com build {BUILD}\n")
print("wrote sitemap.xml, robots.txt, version.txt:", len(SITEMAP), "indexable pages")
