#!/usr/bin/env python3
"""Lead finder: early-stage US startups (AI, fintech, energy/climate) showing
signs of an upcoming or open pre-seed / seed / Series A raise.

Sources (public, free):
  1. Y Combinator directory - batch timing is the signal; founders publish
     their own names and LinkedIn profiles on their YC company page.
  2. SEC EDGAR Form D - a filed Form D with money still unsold is a confirmed
     open round. Needs SEC_USER_AGENT (SEC requires a declared contact).

Usage:
  python3 lead-finder/find_leads.py                 # YC only
  SEC_USER_AGENT="Your Company you@example.com" python3 lead-finder/find_leads.py --sec-days 30
  HUNTER_API_KEY=... python3 lead-finder/find_leads.py   # look up emails via Hunter

Writes lead-finder/out/leads.csv, leads.json and dashboard.html.
Standard library only.
"""
import argparse
import csv
import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
CACHE = os.path.join(OUT, "cache")
UA = "lead-finder/1.0"
TODAY = dt.date.today()

FIELDS = ["company", "sector", "signal", "likely_round", "score", "signal_date",
          "company_linkedin", "founder_linkedin", "email", "email_status",
          "full_name", "first_name", "last_name", "title", "website",
          "location", "team_size", "description", "source", "source_url"]


def fetch(url, ua=UA, tries=3, timeout=40):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001 - retry any network error
            if i == tries - 1:
                print(f"  ! failed {url}: {e}", file=sys.stderr)
                return None
            time.sleep(2 * (i + 1))


def cached(key, url, ua=UA, max_age_days=7):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, re.sub(r"[^\w.-]", "_", key))
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age_days * 86400:
        return open(path, encoding="utf-8").read()
    body = fetch(url, ua)
    if body:
        open(path, "w", encoding="utf-8").write(body)
    return body


# ---------- shared helpers ----------

def split_name(full):
    parts = [p for p in re.sub(r"\(.*?\)", "", full or "").split() if p]
    suffixes = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv", "phd", "ph.d.", "md"}
    while len(parts) > 1 and parts[-1].lower().strip(",") in suffixes:
        parts.pop()
    if not parts:
        return "", ""
    return parts[0], (" ".join(parts[1:]) if len(parts) > 1 else "")


def domain_of(website):
    if not website:
        return ""
    host = urllib.parse.urlparse(website if "//" in website else "//" + website).netloc.lower()
    host = host.split(":")[0]
    return host[4:] if host.startswith("www.") else host


SHARED_HOSTS = ("github.io", "notion.site", "vercel.app", "webflow.io", "linktr.ee",
                "carrd.co", "framer.website", "framer.app", "wixsite.com", "substack.com",
                "google.com", "apple.com", "linkedin.com", "ycombinator.com")


def guess_email(first, website):
    """first@domain is the most common pattern at <10-person startups. Unverified."""
    dom = domain_of(website)
    f = re.sub(r"[^a-z]", "", (first or "").lower())
    if not dom or not f or dom.endswith(SHARED_HOSTS):
        return ""
    return f"{f}@{dom}"


def hunter_email(first, last, website, key):
    dom = domain_of(website)
    if not (dom and first and last):
        return None
    q = urllib.parse.urlencode({"domain": dom, "first_name": first, "last_name": last, "api_key": key})
    body = fetch("https://api.hunter.io/v2/email-finder?" + q, tries=1)
    try:
        d = json.loads(body)["data"]
        return (d["email"], f"hunter ({d.get('score', '?')}% confidence)") if d.get("email") else None
    except Exception:  # noqa: BLE001
        return None


def li_search(kind, query):
    return f"https://www.linkedin.com/search/results/{kind}/?keywords=" + urllib.parse.quote(query)


# ---------- sector classification ----------

FINTECH_TAGS = {"fintech", "finance", "payments", "banking", "insurance", "consumer finance",
                "investing", "trading", "lending", "credit", "neobank", "crypto / web3",
                "accounting", "tax", "insurtech", "wealth management", "banking as a service"}
CLIMATE_TAGS = {"energy", "climate", "climatetech", "clean energy", "cleantech", "carbon capture and removal",
                "solar power", "renewable energy", "energy storage", "sustainability", "electric vehicles",
                "nuclear", "fusion energy", "battery", "batteries", "grid", "environmental tech"}
AI_TAGS = {"ai", "artificial intelligence", "generative ai", "ai assistant", "machine learning",
           "conversational ai", "aiops", "computer vision", "deep learning", "nlp", "ai-enhanced learning",
           "reinforcement learning", "llm"}


def yc_sector(c):
    tags = {t.lower() for t in c.get("tags", [])}
    sub = (c.get("subindustry") or "").lower()
    out = []
    if tags & CLIMATE_TAGS or "energy" in sub or "climate" in sub:
        out.append("Energy & Climate")
    if c.get("industry") == "Fintech" or tags & FINTECH_TAGS or "finance and accounting" in sub:
        out.append("Fintech")
    if tags & AI_TAGS:
        out.append("AI")
    return out


# ---------- source 1: Y Combinator ----------

SEASON_MONTH = {"Winter": 1, "Spring": 4, "Summer": 6, "Fall": 9}


def batch_start(batch):
    try:
        season, year = batch.split()
        return dt.date(int(year), SEASON_MONTH[season], 1)
    except Exception:  # noqa: BLE001
        return None


def yc_signal(c):
    """Turn batch timing into (signal, likely_round, score, date)."""
    start = batch_start(c.get("batch", ""))
    if not start:
        return None
    months = (TODAY - start).days / 30.4
    demo = start + dt.timedelta(days=95)
    hiring = c.get("isHiring")
    team = c.get("team_size") or 0
    b = c["batch"]
    if months < 3.5:
        when = "is coming up" if demo >= TODAY else "just happened"
        sig = f"In YC {b} right now. Demo Day (~{demo:%b %Y}) {when}: this is when batch companies pitch investors for their seed round."
        rnd, score = "Seed", 92
    elif months < 9:
        sig = f"Graduated YC {b} about {months - 3:.0f} months ago. Typically still closing the post-Demo Day seed round or raising a seed extension."
        rnd, score = "Seed", 62
    elif months < 12:
        sig = f"YC {b}, about {months:.0f} months in. Seed money is usually half spent by now, so founders start preparing a seed extension or Series A story."
        rnd, score = "Seed extension / Series A", 66
    elif months <= 26:
        sig = f"YC {b}, {months:.0f} months since the batch. This is the usual Series A window (12 to 24 months after seed)."
        rnd, score = "Series A", 74
    else:
        return None
    if hiring:
        sig += " Actively hiring."
        score += 6
    if rnd != "Seed" and team >= 8:
        sig += f" Team has grown to {team}."
        score += 4
    return sig, rnd, min(score, 99), start.isoformat()


def yc_detail(c):
    page = cached(f"yc_{c['slug']}.html", c["url"])
    if not page:
        return None
    m = re.search(r'data-page="([^"]*)"', page)
    try:
        return json.loads(html.unescape(m.group(1)))["props"]["company"]
    except Exception:  # noqa: BLE001
        return None


def pick_founder(founders):
    active = [f for f in founders if f.get("is_active", True)] or founders
    for f in active:
        if re.search(r"\bceo\b|chief executive", f.get("title") or "", re.I):
            return f
    return active[0] if active else None


def yc_leads(args):
    print("Y Combinator: loading directory...")
    allc = json.loads(fetch("https://yc-oss.github.io/api/companies/all.json"))
    picked = []
    for c in allc:
        if c.get("status") != "Active" or "United States of America" not in c.get("regions", []):
            continue
        if not 1 <= (c.get("team_size") or 0) <= 50:
            continue
        sectors = yc_sector(c)
        sig = yc_signal(c)
        if sectors and sig:
            picked.append((c, sectors, sig))
    print(f"  {len(picked)} companies match (US, 1-50 staff, AI/fintech/climate, raise window). Reading founder pages...")

    with ThreadPoolExecutor(max_workers=6) as ex:
        details = list(ex.map(lambda p: yc_detail(p[0]), picked))

    leads = []
    for (c, sectors, (sig, rnd, score, date)), d in zip(picked, details):
        d = d or {}
        founders = d.get("founders") or []
        people = founders if args.all_founders else [pick_founder(founders)]
        for f in people or [None]:
            f = f or {}
            first, last = split_name(f.get("full_name", ""))
            website = c.get("website") or d.get("website") or ""
            email, status = guess_email(first, website), ""
            if email:
                status = "guess (first@domain), unverified"
            if args.hunter_key and first:
                found = hunter_email(first, last, website, args.hunter_key)
                if found:
                    email, status = found
            leads.append({
                "company": c["name"], "sector": " + ".join(sectors), "signal": sig,
                "likely_round": rnd, "score": score, "signal_date": date,
                "company_linkedin": d.get("linkedin_url") or li_search("companies", c["name"]),
                "founder_linkedin": f.get("linkedin_url") or (li_search("people", f"{f.get('full_name', '')} {c['name']}") if f else ""),
                "email": email, "email_status": status,
                "full_name": " ".join(x for x in (first, last) if x), "first_name": first, "last_name": last,
                "title": f.get("title") or "", "website": website,
                "location": c.get("all_locations") or "", "team_size": c.get("team_size") or "",
                "description": c.get("one_liner") or "", "source": "Y Combinator", "source_url": c["url"],
            })
    return leads


# ---------- source 2: SEC Form D ----------

SEC_INDUSTRY = {
    "Other Technology": "AI", "Computers": "AI", "Telecommunications": "AI",
    "Commercial Banking": "Fintech", "Insurance": "Fintech", "Investing": "Fintech",
    "Investment Banking": "Fintech", "Other Banking and Financial Services": "Fintech",
    "Electric Utilities": "Energy & Climate", "Energy Conservation": "Energy & Climate",
    "Environmental Services": "Energy & Climate", "Other Energy": "Energy & Climate",
}
AI_NAME = re.compile(r"\bAI\b|\.ai\b|\bartificial intelligence\b|\bintelligen|\bml\b|\brobot|\bautonom|\bGPT\b|labs?\b", re.I)
US_STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())


def _t(node, path):
    el = node.find(path) if node is not None else None
    return (el.text or "").strip() if el is not None else ""


def _money(s):
    try:
        return float(s)
    except ValueError:
        return None


def parse_form_d(xml_text, filed, url):
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    issuer, off = root.find("primaryIssuer"), root.find("offeringData")
    if issuer is None or off is None:
        return []
    group = _t(off, "industryGroup/industryGroupType")
    name = _t(issuer, "entityName")
    state = _t(issuer, "issuerAddress/stateOrCountry")
    if group not in SEC_INDUSTRY or state not in US_STATES:
        return []
    sector = SEC_INDUSTRY[group]
    if sector == "AI" and not AI_NAME.search(name):
        return []  # Form D has no AI category; keep only tech issuers whose name suggests it
    year = _t(issuer, "yearOfInc/value")
    if year.isdigit() and TODAY.year - int(year) > 6:
        return []
    total = _money(_t(off, "offeringSalesAmounts/totalOfferingAmount"))
    sold = _money(_t(off, "offeringSalesAmounts/totalAmountSold")) or 0
    if total is not None and not 100_000 <= total <= 20_000_000:
        return []
    if total is None and sold > 20_000_000:
        return []
    remaining = (total - sold) if total is not None else None
    amend = _t(off, "typeOfFiling/newOrAmendment/isAmendment") == "true"
    size = total if total is not None else sold
    rnd = "Pre-seed" if size < 1_500_000 else "Seed" if size < 6_000_000 else "Series A"

    def usd(v):
        return f"${v / 1e6:.2f}M" if v >= 1e6 else f"${v / 1e3:.0f}K"

    target = usd(total) if total is not None else "an open-ended amount"
    sig = f"Filed SEC Form D{' amendment' if amend else ''} on {filed}: raising {target}, {usd(sold)} sold so far."
    if remaining and remaining > 0:
        sig += f" {usd(remaining)} still to raise, so the round is open."
        score = 96
    elif total is None:
        sig += " No cap stated, round likely still open."
        score = 88
    else:
        sig += " Round fully subscribed; next raise typically 12 to 18 months out."
        score = 45

    people = []
    for p in root.findall("relatedPersonsList/relatedPersonInfo"):
        rels = [r.text or "" for r in p.findall("relatedPersonRelationshipList/relationship")]
        first, last = _t(p, "relatedPersonName/firstName"), _t(p, "relatedPersonName/lastName")
        if first and last and first not in ("-", "N/A"):
            people.append((0 if "Executive Officer" in rels else 1, first.title(), last.title(), ", ".join(rels)))
    people.sort()
    _, first, last, title = people[0] if people else (0, "", "", "")
    full = f"{first} {last}".strip()
    return [{
        "company": name, "sector": sector, "signal": sig, "likely_round": rnd, "score": score,
        "signal_date": filed, "company_linkedin": li_search("companies", name),
        "founder_linkedin": li_search("people", f"{full} {name}") if full else "",
        "email": "", "email_status": "", "full_name": full, "first_name": first, "last_name": last,
        "title": title, "website": "", "location": f"{_t(issuer, 'issuerAddress/city').title()}, {state}",
        "team_size": "", "description": f"Form D industry group: {group}. Incorporated {year or 'n/a'}.",
        "source": "SEC Form D", "source_url": url,
    }]


def sec_leads(args):
    ua = os.environ.get("SEC_USER_AGENT", "")
    if not ua:
        print("SEC Form D: skipped. Set SEC_USER_AGENT=\"Company Name email@domain\" to enable (SEC requires it).")
        return []
    start = TODAY - dt.timedelta(days=args.sec_days)
    print(f"SEC Form D: listing filings since {start}...")
    hits, frm = [], 0
    while True:
        q = urllib.parse.urlencode({"q": "", "forms": "D", "dateRange": "custom",
                                    "startdt": start.isoformat(), "enddt": TODAY.isoformat(), "from": frm})
        body = fetch("https://efts.sec.gov/LATEST/search-index?" + q, ua)
        page = json.loads(body)["hits"]["hits"] if body else []
        hits += page
        frm += len(page)
        if len(page) < 100 or frm >= 9900:
            break
        time.sleep(0.15)
    print(f"  {len(hits)} filings. Reading each one (SEC limit: 10 requests/second)...")
    leads = []
    for h in hits:
        s = h["_source"]
        if not set(s.get("biz_states") or []) & US_STATES:
            continue
        adsh = s["adsh"]
        url = f"https://www.sec.gov/Archives/edgar/data/{int(s['ciks'][0])}/{adsh.replace('-', '')}/primary_doc.xml"
        fresh = not os.path.exists(os.path.join(CACHE, f"sec_{adsh}.xml"))
        xml_text = cached(f"sec_{adsh}.xml", url, ua, max_age_days=365)
        if fresh:
            time.sleep(0.12)
        if xml_text:
            leads += parse_form_d(xml_text, s["file_date"], url.replace("primary_doc.xml", ""))
    return leads


# ---------- output ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all-founders", action="store_true", help="one row per founder instead of CEO only")
    ap.add_argument("--sec-days", type=int, default=30, help="how far back to read Form D filings")
    ap.add_argument("--no-yc", action="store_true")
    args = ap.parse_args()
    args.hunter_key = os.environ.get("HUNTER_API_KEY", "")
    os.makedirs(OUT, exist_ok=True)

    leads = ([] if args.no_yc else yc_leads(args)) + sec_leads(args)
    seen, unique = set(), []
    for lead in sorted(leads, key=lambda r: (-r["score"], r["company"].lower())):
        key = (re.sub(r"\W", "", lead["company"].lower()), lead["full_name"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(lead)

    with open(os.path.join(OUT, "leads.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(unique)
    payload = "[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in unique) + "\n]\n"
    open(os.path.join(OUT, "leads.json"), "w", encoding="utf-8").write(payload)
    template = open(os.path.join(HERE, "dashboard.html"), encoding="utf-8").read()
    inline = f"<script>window.LEADS={payload.replace('</', '<\\/')};window.LEADS_UPDATED='{TODAY}'</script>\n"
    open(os.path.join(OUT, "dashboard.html"), "w", encoding="utf-8").write('<meta charset="utf-8">\n' + inline + template)
    # page for hosting next to leads.json (data fetched instead of inlined)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(template.replace("<script>\nconst PAGE", f"<script>window.LEADS_UPDATED='{TODAY}'</script>\n<script>\nconst PAGE", 1))
    print(f"\n{len(unique)} leads -> {OUT}/leads.csv, leads.json, dashboard.html")


if __name__ == "__main__":
    main()
