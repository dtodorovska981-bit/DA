#!/usr/bin/env python3
"""Generates the static pages for dnaproplans.com into the repo root."""
import sys, pathlib

OUT = pathlib.Path(sys.argv[1])
SITE = "https://dnaproplans.com"
CAL = "https://calendly.com/draganatodorovskajaneva/30min"
FORM = "https://app.pipefy.com/public/form/WjXLnOMX"
GA_ID = "G-HCBH87S9EE"  # Google Analytics measurement ID, loaded once in the shared head
LINKEDIN = "https://www.linkedin.com/company/106128983/"
LINKEDIN_FOUNDER = "https://www.linkedin.com/in/dragana-todorovska-j-054314176/"


def head(title, desc, path, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtm.js?id={GA_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
  </script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{SITE}/{path}">
  <meta property="og:image" content="{SITE}/images/og.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{SITE}/{path}">
  <meta name="theme-color" content="#0e1229">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
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
        <a href="index.html#approach">Approach</a>
        <a href="case-studies.html"{cur('cases')}>Case studies</a>
        <a href="index.html#founder">Founder</a>
        <a href="index.html#engagements">Engagements</a>
      </nav>
      <a href="contact.html" class="btn btn--dark nav__cta">Book a call</a>
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
        <a href="index.html#engagements">Engagements</a>
        <a href="case-studies.html">Case studies</a>
        <a href="contact.html">Contact</a>
        <a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>
        <a href="privacy.html">Privacy</a>
      </nav>{note_html}
      <p>© <span id="year">2026</span> DNA Pro Plans</p>
    </div>
  </footer>
  <script src="main.js" defer></script>
</body>
</html>
"""


def page(name, title, desc, body, current="", note="", extra=""):
    (OUT / name).write_text(head(title, desc, "" if name == "index.html" else name, extra) + nav(current) + body + footer(note))
    print("wrote", name)


# ------------------------------------------------------------------ HOME
SECTORS = [("fintech", "Fintech"), ("agribusiness", "Agribusiness"), ("energy", "Energy technology"), ("biotech", "Biotech"),
           ("franchising", "Franchising"), ("textile", "Textile manufacturing"), ("luxury", "Luxury retail"), ("wellness", "Wellness"),
           ("lending", "Private lending"), ("hardware", "Consumer hardware")]
sector_group = "".join(f'<li class="sector"><img src="icons/ind-{k}.svg" alt="" width="30" height="30">{v}</li>' for k, v in SECTORS)

SERVICES = [
    ("pitch", "Pitch decks and sales decks", "Decks for investors, partners and large clients.", "Why this company, and why now?"),
    ("plan", "Business and financial plans", "Plans and five-year projections in four scenarios.", "Do the numbers still hold if the market turns?"),
    ("research", "Market research papers", "Market sizing, demand and competitor intelligence.", "How big is this market, and who says so?"),
    ("website", "Branding and websites", "Identity, guidelines and a website that sells.", "Does this company look as serious as its plan?"),
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
            <div class="show is-active" id="show-pitch">
              <div class="show__main"><img src="images/custel-cover.webp" alt="Cover slide of the Custel investor deck: Spend today. Pay on the statement." width="1520" height="855"></div>
              {thumbs([("custel-market", "Market slide"), ("custel-unit", "Unit economics slide"), ("custel-competition", "Competition slide"), ("custel-scenarios", "Scenarios slide"), ("custel-ask", "The ask slide")])}
              <p class="show__cap"><strong>Investor pitch deck</strong><a href="case-study-custel.html">From the Custel deck. Figures masked. →</a></p>
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
            <a class="ulink" href="contact.html">{cta}</a>
          </article>"""

STEPS = [("Brief", "A short intake: the decision you need, the deadline, the data you have."),
         ("Call", "Thirty minutes to agree the reader, the scope and the delivery date."),
         ("Build", "Research, numbers, story and design, developed together."),
         ("Review", "Preview, revisions, then editable files, or your site live.")]
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
        <div class="hero__media"><div class="hero__zoom"><img src="images/hero.jpg" alt="Glass tower rising into a blue sky" width="1024" height="683" fetchpriority="high" data-parallax="-0.12"></div></div>
        <div class="hero__grid">
          <div>
            <h1 class="h1 lines" style="--d:4"><span class="line"><span>Built on research.</span></span><span class="line"><span>Presented to win the yes.</span></span></h1>
            <p class="hero__sub" data-reveal style="--d:7">Pitch decks, business plans, financial plans, market research, sales decks, branding and websites for founders who are starting, raising or partnering.</p>
            <div class="hero__actions" data-reveal style="--d:9">
              <a href="contact.html" class="btn">Book a 30-minute call</a>
              <a href="#approach" class="btn btn--ghost">See how we work</a>
            </div>
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
              <li>Pitch decks and sales decks</li>
              <li>Business and financial plans</li>
              <li>Market research papers</li>
              <li>Branding and websites</li>
            </ul>
          </aside>
        </div>
      </div>
    </section>

    <section class="sectors" aria-label="Sectors we have worked in">
      <div class="sectors__track">
        <ul class="sectors__group">{sector_group}</ul>
        <ul class="sectors__group" aria-hidden="true">{sector_group}</ul>
      </div>
    </section>

    <section class="statement">
      <div class="wrap">
        <p>Investors, lenders and partners say yes to what they can believe. We build every deck, plan and page on real market research and realistic projections, so your story holds up when someone checks the numbers.</p>
      </div>
    </section>

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
        <p class="svc-more" data-reveal><a class="ulink" href="services.html">See what each service includes, and pricing</a></p>
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
          <div class="founder__cta" data-reveal style="--d:4"><a href="contact.html" class="btn btn--lg btn--on-dark">Book a call with Dragana</a><a class="ulink" href="{LINKEDIN_FOUNDER}" target="_blank" rel="noopener">Dragana on LinkedIn</a></div>
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
          <p class="lead" data-reveal style="--d:2">Most decks, plans and models are delivered in 7 days from complete inputs. Branding and websites follow an agreed timeline.</p>
        </div>
        <div class="rail" aria-hidden="true"><i></i></div>
        <ol class="steps">{steps_html}</ol>
      </div>
    </section>

    <section class="cta">
      <div class="cta__bg"><img src="images/cta.jpg" alt="" width="1024" height="683" loading="lazy" data-parallax="-0.1"></div>
      <div class="wrap">
        <span class="cta__accent" data-reveal="rule"></span>
        <h2 class="lines" style="--d:1"><span class="line"><span>Bring the decision</span></span><span class="line"><span>you need to win.</span></span></h2>
        <p data-reveal style="--d:4">Tell us who has to say yes and by when. We will tell you what they need to see.</p>
        <div data-reveal style="--d:5"><a href="contact.html" class="btn btn--on-dark">Book a 30-minute call</a></div>
      </div>
    </section>
  </main>
"""
ld = """
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"ProfessionalService","name":"DNA Pro Plans","url":"https://dnaproplans.com/","description":"Pitch decks, business plans, financial plans, market research, branding and websites for founders who are starting, raising or partnering.","founder":{"@type":"Person","name":"Dragana Todorovska Janeva","jobTitle":"Founder & Principal Business Consultant","sameAs":"https://www.linkedin.com/in/dragana-todorovska-j-054314176/"},"sameAs":["https://www.linkedin.com/company/106128983/"],"areaServed":"Worldwide"}
  </script>"""
page("index.html", "DNA Pro Plans | Built on research. Presented to win the yes.",
     "Pitch decks, business plans, financial plans, market research, sales decks, branding and websites for founders who are starting, raising or partnering.",
     home, extra=ld)


# ------------------------------------------------------------------ CASE STUDIES
def case_page(c):
    facts = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in c["facts"])
    stack = "".join(f'<img src="images/{s}.webp" alt="{a}" width="1260" height="709" loading="lazy" data-reveal style="--d:{i}">' for i, (s, a) in enumerate(c["stack"]))
    light = "".join(f'<img src="images/{s}.webp" alt="{a}" width="1500" height="844" loading="lazy" data-reveal style="--d:{i + 1}">' for i, (s, a) in enumerate(c["light"]))
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

    <section class="wall" aria-label="Slides from the {c['short']} deck">
      <img src="images/{c['key']}-wall.webp" alt="A wall of slides from the {c['short']} deck" width="2160" height="990" data-drift="-0.06">
    </section>

    <section class="panels">
      <div class="wrap panels__grid">
        <div class="panel">{stack}</div>
        <div class="panel panel--light"><p class="eyebrow" data-reveal="fade">{c['light_label']}</p>{light}</div>
      </div>
    </section>

    <section class="key">
      <div class="wrap">
        <div class="feature">
          <div class="feature__slide" data-reveal="left"><img src="images/{c['key']}-{c['feature'][0]}.webp" alt="{c['feature'][1]}" width="1520" height="855" loading="lazy"></div>
          <div>
            <p class="proof__label" data-reveal="fade">What the deck had to prove</p>
            <ul class="proof">{proof}</ul>
          </div>
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
        <p data-reveal style="--d:2">Book a call with Dragana. Tell us who has to say yes and by when.</p>
        <div data-reveal style="--d:3"><a href="contact.html" class="btn btn--on-dark">Book a 30-minute call</a></div>
      </div>
    </section>

    <section class="next-case">
      <div class="wrap"><a href="{c['next'][0]}"><small>Next case study</small><strong>{c['next'][1]} <span class="arrow" aria-hidden="true">→</span></strong></a></div>
    </section>
  </main>
"""
    page(c["file"], f"{c['short']} case study | DNA Pro Plans", c["desc"], body, current="cases", note="Confidential figures are masked with X.")


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
          <a class="case-card__media" href="{c['file']}" data-reveal="clip" tabindex="-1" aria-hidden="true"><img src="images/{c['key']}-wall.webp" alt="" width="2160" height="990"></a>
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
        <p class="lead" data-reveal style="--d:4">Two engagements, shown with the client’s permission. Confidential figures are masked with X.</p>
      </div>
    </section>
    <section class="wrap cases">{cards}
    </section>
    <section class="cta-plain">
      <div class="wrap">
        <h2 class="lines"><span class="line"><span>Want your materials built this way?</span></span></h2>
        <p data-reveal style="--d:2">Book a call with Dragana. Tell us who has to say yes and by when.</p>
        <div data-reveal style="--d:3"><a href="contact.html" class="btn btn--on-dark">Book a 30-minute call</a></div>
      </div>
    </section>
  </main>
""", current="cases", note="Confidential figures are masked with X.")

# ------------------------------------------------------------------ SERVICES
def offer(anchor, eyebrow, title, lead, price_html, need, right):
    return f"""
    <section class="offer" id="{anchor}">
      <div class="wrap offer__grid">
        <div class="offer__side" data-reveal>
          <p class="eyebrow">{eyebrow}</p>
          <h2>{title}</h2>
          <p class="lead">{lead}</p>
          {price_html}
          <a href="contact.html" class="btn">Book a 30-minute call</a>
        </div>
        <div data-reveal style="--d:2">{right}</div>
      </div>
    </section>"""


def contents(label, items):
    return f'<p class="offer__k">{label}</p><ol class="contents">' + "".join(f"<li><div><strong>{t}</strong><span>{d}</span></div></li>" for t, d in items) + "</ol>"


def price(amount, note):
    return f'<p class="price"><small>from</small><strong>{amount}</strong></p><p class="price__note">{note}</p>'


QUOTE = '<p class="price price--quote"><strong>Quoted after the call</strong></p><p class="price__note">Scope, fee and delivery date are agreed before work starts.</p>'
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


services_body = f"""  <main id="main">
    <section class="page-head">
      <div class="wrap">
        <p class="eyebrow" data-reveal="fade">Services</p>
        <h1 class="h1 lines" style="--d:1"><span class="line"><span>What we build,</span></span><span class="line"><span>and what the reader gets.</span></span></h1>
        <p class="lead" data-reveal style="--d:4">One team for the research, the numbers, the story and the brand. Most decks, plans and models are delivered in 7 days from complete inputs.</p>
      </div>
    </section>
{offer("business-plan", "Business plan", "A written plan built for investors, banks and visa officers.",
       "Built on the financial plan, so every number in the text matches the model behind it.",
       price("$900", "Written plan. Final price depends on scope."), "Business plan", contents("What you get", BP))}

{sample_sec("sample", "Sample business plan", "See what a finished plan looks like.", "Six pages from a 24-page plan for Fieldhouse Workspace, a fictional coworking company asking for an SBA loan. Swipe or drag to look through it.", reel, "Sample plan for a fictional company, prepared by DNA Pro Plans. All figures are illustrative.")}
{offer("financial-plan", "Financial plan", "An Excel model in four scenarios based on market factors.",
       "Live formulas and analysis based on real market data, built to account for the future: Base, Upside, Downside and Stress.",
       price("$360", "Excel model. Final price depends on scope."), "Financial plan", contents("What you get", FP))}
{offer("pitch-decks", "Pitch decks and sales decks", "Decks for investors, partners and large clients.",
       "The reader asks: why this company, and why now? The deck answers it with a clear story and the numbers behind it.",
       QUOTE, "Pitch deck or sales deck",
       contents("What you get", [("Investor pitch deck", "Problem, solution, market, model, traction and the ask."),
                                 ("Sales and partnership decks", "For partners, distributors and large clients."),
                                 ("Appendix for due diligence", "Scenarios, assumptions and supporting data."),
                                 ("Editable files", "Figma and PowerPoint, in light and dark where needed.")])
       + '<p style="margin-top:26px"><a class="ulink" href="case-studies.html">See the Custel and Haraz decks</a></p>')}
{offer("market-research", "Market research papers", "Market sizing, demand and competitor intelligence.",
       "Evidence from sources the reader can verify. Estimates are labelled as estimates.",
       QUOTE, "Market research paper",
       contents("What you get", [("Market size", "Sized from public sources, with the method shown."),
                                 ("Customer segments and demand", "Who buys, how many there are and what they pay."),
                                 ("Competitor intelligence", "Revenue, clients, funding and the strategies they use."),
                                 ("Sources", "Every figure cited, every estimate labelled.")]))}
{sample_sec("research-sample", "Sample market research report", "See what a research report looks like.", "Six pages from a 32-page report on EV charging for apartment and multifamily buildings in the United States: market size, demand, competition and where to enter first.", research_reel, "Sample report with illustrative figures, prepared by DNA Pro Plans for a fictional client.")}
{offer("branding-websites", "Branding and websites", "Identity, guidelines and a website that sells.",
       "The same story your documents tell, carried into how the company looks and what its website says.",
       QUOTE, "Branding and website",
       contents("What you get", [("Brand identity", "Logo, icon, colour, type and pattern."),
                                 ("Brand guidelines", "Usage rules your team and suppliers can follow."),
                                 ("Website design and build", "Pages that point to the decision you need."),
                                 ("Matching materials", "Reports, one-pagers and ads on one identity.")]))}
{sample_sec("brand-sample", "Brand guidelines", "One identity for every deck, plan and page.", "Our own brand guidelines: logo, colour, type, pattern, photography and icons. This is the kind of system we build for clients.", brand_reel, "DNA Pro Plans brand guidelines.", wide=True)}

    <section class="cta-plain">
      <div class="wrap">
        <h2 class="lines"><span class="line"><span>Not sure which one you need?</span></span></h2>
        <p data-reveal style="--d:2">Tell us who has to say yes and by when. We will tell you what they need to see.</p>
        <div data-reveal style="--d:3"><a href="contact.html" class="btn btn--on-dark">Book a 30-minute call</a></div>
      </div>
    </section>
  </main>
"""
page("services.html", "Services and pricing | DNA Pro Plans",
     "Business plans from $900, financial plans from $360, pitch decks, market research, branding and websites. See what each includes and a sample business plan.",
     services_body, current="services")

# ------------------------------------------------------------------ CONTACT
NEEDS = ["Pitch deck or sales deck", "Business plan", "Financial plan", "Market research paper", "Branding and website",
         "Start", "Raise", "Partner and sell", "Not sure yet"]
LABELS = {"Start": "Start: launching a company", "Raise": "Raise: equity or bank debt", "Partner and sell": "Partner and sell: partners and large clients"}
opts = "".join(f'<option value="{n}">{LABELS.get(n, n)}</option>' for n in NEEDS)
page("contact.html", "Book a call | DNA Pro Plans",
     "Tell us who has to say yes and by when, then pick a 30-minute slot with Dragana.",
     f"""  <main id="main">
    <section class="contact">
      <div class="wrap contact__grid">
        <div class="contact__copy">
          <p class="eyebrow" data-reveal="fade">Book a call</p>
          <h1 class="h1 lines" style="--d:1"><span class="line"><span>Tell us who has</span></span><span class="line"><span>to say yes.</span></span></h1>
          <p class="lead" data-reveal style="--d:4">A two-minute brief, then thirty minutes with Dragana. You leave the call knowing what your reader needs to see, the scope and the delivery date.</p>
          <ol class="flow" data-reveal style="--d:5">
            <li class="is-on"><span>01</span><div><strong>Send a short brief</strong><small>The decision you need, the deadline, the data you have.</small></div></li>
            <li class="is-on"><span>02</span><div><strong>Pick a time</strong><small>Choose a 30-minute slot that suits you.</small></div></li>
          </ol>
          <div class="led" data-reveal style="--d:6">
            <img src="images/dragana.webp" alt="Dragana Todorovska Janeva" width="64" height="64">
            <div><p class="led__name">Dragana Todorovska Janeva</p><p class="led__role">Founder &amp; Principal Business Consultant</p></div>
          </div>
          <p class="contact__direct" data-reveal style="--d:7">In a hurry? <a href="#book">Skip the brief and book directly</a>.</p>
        </div>

        <div class="contact__steps">
          <div class="card" id="brief" data-reveal style="--d:3">
            <p class="card__step">Step 1</p>
            <h2>Your brief</h2>
            <p class="card__sub">Everything you share stays confidential. An NDA is available on request.</p>
            <div class="booking">
              <iframe class="brief__frame" src="{FORM}?embedded=true" title="Project brief form" loading="lazy"></iframe>
              <p class="booking__alt">Form not loading? <a href="{FORM}" target="_blank" rel="noopener">Open the brief form in a new tab</a>.</p>
            </div>
          </div>
          <div class="card" id="book" data-reveal>
            <p class="card__step">Step 2</p>
            <h2>Pick a time</h2>
            <p class="card__sub">Once your brief is sent, choose a 30-minute slot and Dragana will come prepared.</p>
            <div class="booking">
              <iframe class="booking__frame" src="{CAL}?hide_gdpr_banner=1&amp;primary_color=5271ff" title="Book a 30-minute call with Dragana" loading="lazy"></iframe>
              <p class="booking__alt">Calendar not loading? <a href="{CAL}" target="_blank" rel="noopener">Open the booking page in a new tab</a>.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
""")

# ------------------------------------------------------------------ PRIVACY / 404
page("privacy.html", "Privacy policy | DNA Pro Plans", "How DNA Pro Plans collects, uses and stores your information, and how payments and refunds work.",
     f"""  <main id="main">
    <div class="wrap">
      <div class="prose">
        <p class="eyebrow">Legal</p>
        <h1 class="h1">Privacy, payments and refunds</h1>
        <p>Last updated: November 2026</p>
        <h2>Who we are</h2>
        <p>DNA Pro Plans ("we", "us") provides business planning, financial modeling, research, presentation, branding and website services. Contact: <a href="mailto:office@dnaproplans.com">office@dnaproplans.com</a>.</p>
        <h2>What we collect</h2>
        <p>When you submit the brief form, we collect your name, email address, company, the service you are interested in, what it is for, your deadline, budget range, any files you upload and how you found us. When you book a call, the booking is handled by Calendly, which collects the details you enter there.</p>
        <h2>How we use it</h2>
        <ul><li>To reply to your inquiry, hold the call and prepare a proposal.</li><li>To deliver agreed work and communicate about your project.</li></ul>
        <p>We do not sell your information or use it for unrelated marketing.</p>
        <h2>Analytics</h2>
        <p>This website uses Google Analytics to count visits and see which pages are read. Google Analytics sets cookies and collects usage data such as pages viewed, approximate location and device type. We use it only in aggregate and do not use it to identify you.</p>
        <h2>Where it is stored</h2>
        <p>Brief form submissions are processed by Pipefy and delivered to us. Bookings are processed by Calendly. Project materials are stored only as long as needed for the engagement and any agreed support period.</p>
        <h2>Confidentiality</h2>
        <p>An NDA is available on request. Any public use of your name, project materials or results requires your permission.</p>
        <h2>Payments</h2>
        <p>The fee, what it covers and the payment schedule are agreed in writing before work starts. This website does not take payments and we do not collect or store card details. You pay by invoice using the method named in your proposal, and any bank or payment provider involved handles your details under its own privacy policy. We keep invoices and payment records for as long as accounting and tax rules require.</p>
        <h2>Cancellations and refunds</h2>
        <p>Every plan, deck, model and website is made for one client, so refunds depend on how much of the work has been done.</p>
        <ul><li>If you cancel before work starts, we refund what you have paid in full.</li><li>If you cancel after work has started, we refund the part of the fee for work not yet done and send you what has been completed.</li><li>Once the final files are delivered, the fee is not refundable. The revisions included in your proposal still apply, and we will correct any error on our side.</li></ul>
        <p>To cancel or ask for a refund, email <a href="mailto:office@dnaproplans.com">office@dnaproplans.com</a>. We reply within two working days.</p>
        <h2>Your rights</h2>
        <p>You can ask us to access, correct or delete your personal information at any time by emailing <a href="mailto:office@dnaproplans.com">office@dnaproplans.com</a>.</p>
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
      <div class="hero__actions"><a href="index.html" class="btn">Back to home</a><a href="contact.html" class="btn btn--ghost">Book a call</a></div>
    </section>
  </main>
""", extra='\n  <meta name="robots" content="noindex">')
