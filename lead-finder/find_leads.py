#!/usr/bin/env python3
"""Lead finder: early-stage US startups (AI, fintech, energy/climate) showing
signs of an upcoming or open pre-seed / seed / Series A raise.

Sources (public, free):
  1. Y Combinator directory - batch timing is the signal; founders publish
     their own names and LinkedIn profiles on their YC company page.
  2. SEC EDGAR Form D - the public record of a private raise. Finds startups
     with a round open now or a first round closed in the past two years.
     Needs SEC_USER_AGENT (SEC requires a declared contact).

Usage:
  python3 lead-finder/find_leads.py                 # YC only
  SEC_USER_AGENT="Your Company you@example.com" python3 lead-finder/find_leads.py
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
# A Form D is filed when a company sells securities privately, so it is the public
# record of a raise. Two years of history come from the SEC's quarterly Form D data
# sets; the weeks since the last data set come from EDGAR search plus each filing's XML.

SEC_INDUSTRY = {
    "Other Technology": "Software / tech", "Computers": "Software / tech",
    "Commercial Banking": "Fintech", "Insurance": "Fintech", "Investing": "Fintech",
    "Investment Banking": "Fintech", "Other Banking and Financial Services": "Fintech",
    "Electric Utilities": "Energy & Climate", "Energy Conservation": "Energy & Climate",
    "Environmental Services": "Energy & Climate", "Other Energy": "Energy & Climate",
}
AI_NAME = re.compile(r"\bAI\b|\.ai\b|AI$|\bartificial intelligence\b|intelligen|\bML\b|robot|autonom|\bGPT\b|neural|cognit|\bagent", re.I)
NOT_A_STARTUP = re.compile(r"\b(fund|spv|l\.?p\.?|trust|reit|holdings?|capital|partners|ventures|investors?|"
                           r"co-?invest|a series of|series [a-z0-9]+|feeder|opportunit(y|ies)|acquisition|"
                           r"real estate|realty|propert(y|ies)|bancorp|bancshares|bank|oil|gas|mining|minerals)\b", re.I)
US_STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())
SEC_DATASETS = "https://www.sec.gov/data-research/sec-markets-data/form-d-data-sets"
LEGAL_SUFFIX = re.compile(r"[,.]?\s+(inc|incorporated|corp|corporation|co|company|llc|ltd|pbc|p\.b\.c|plc)\.?$", re.I)


def _money(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _date(s):
    for fmt in ("%Y-%m-%d", "%d-%b-%Y"):
        try:
            return dt.datetime.strptime((s or "").strip().title(), fmt).date()
        except ValueError:
            pass
    return None


def usd(v):
    return f"${v / 1e6:.1f}M" if v >= 1e6 else f"${v / 1e3:.0f}K"


def nice(s):
    """De-shout ALL-CAPS filings: ACME ROBOTICS, INC. -> Acme Robotics, Inc."""
    s = (s or "").strip()
    if s.isupper() and len(s) > 4:
        s = re.sub(r"\bAi\b", "AI", s.title())
        s = re.sub(r"\b(Llc|Pbc)\b", lambda m: m.group(1).upper(), s)
    return s


def name_key(name):
    n = name.lower().strip()
    for _ in range(2):
        n = LEGAL_SUFFIX.sub("", n)
    return re.sub(r"[^a-z0-9]", "", n)


def fetch_bytes(key, url, ua):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, key)
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=180) as r:
            open(path, "wb").write(r.read())
        time.sleep(0.2)
    return path


def sec_dataset_records(ua, since):
    """Filings from the quarterly data sets. Returns (records, first day not covered)."""
    import io
    import zipfile
    page = fetch(SEC_DATASETS, ua) or ""
    links = sorted(set(re.findall(r'href="(/files/[^"]*?/(\d{4})q(\d)_d\.zip)"', page)), key=lambda x: (x[1], x[2]))
    recs, covered_to = [], since
    for href, y, q in links:
        q_end = dt.date(int(y) + (q == "4"), (int(q) * 3) % 12 + 1, 1)  # first day after the quarter
        if q_end <= since:
            continue
        try:
            zf = zipfile.ZipFile(fetch_bytes(f"formd_{y}q{q}.zip", "https://www.sec.gov" + href, ua))
        except Exception as e:  # noqa: BLE001
            print(f"  ! could not read {y}q{q}: {e}", file=sys.stderr)
            continue
        tables = {}
        for n in zf.namelist():
            base = os.path.basename(n).upper()
            if base.endswith(".TSV"):
                text = io.TextIOWrapper(zf.open(n), encoding="utf-8", errors="replace", newline="")
                tables[base[:-4]] = list(csv.DictReader(text, delimiter="\t", quoting=csv.QUOTE_NONE))
        subs = {r["ACCESSIONNUMBER"]: r for r in tables.get("FORMDSUBMISSION", [])}
        issuers = {r["ACCESSIONNUMBER"]: r for r in tables.get("ISSUERS", []) if r.get("IS_PRIMARYISSUER_FLAG") == "YES"}
        people = {}
        for r in tables.get("RELATEDPERSONS", []):
            rels = [r.get(f"RELATIONSHIP_{i}") for i in (1, 2, 3) if r.get(f"RELATIONSHIP_{i}")]
            people.setdefault(r["ACCESSIONNUMBER"], []).append(
                (r.get("FIRSTNAME", ""), r.get("LASTNAME", ""), rels, r.get("RELATIONSHIPCLARIFICATION", "")))
        for o in tables.get("OFFERING", []):
            a = o["ACCESSIONNUMBER"]
            i, s = issuers.get(a), subs.get(a)
            if not i or not s or o.get("INDUSTRYGROUPTYPE") not in SEC_INDUSTRY:
                continue
            recs.append({
                "adsh": a, "cik": i["CIK"].lstrip("0"), "name": i["ENTITYNAME"], "city": i.get("CITY", ""),
                "state": i.get("STATEORCOUNTRY", ""), "year": i.get("YEAROFINC_VALUE_ENTERED", ""),
                "entity": i.get("ENTITYTYPE", ""), "group": o["INDUSTRYGROUPTYPE"],
                "amend": o.get("ISAMENDMENT") == "true", "filed": _date(s.get("FILING_DATE")),
                "total": _money(o.get("TOTALOFFERINGAMOUNT")), "sold": _money(o.get("TOTALAMOUNTSOLD")) or 0,
                "revenue": o.get("REVENUERANGE", ""), "people": people.get(a, []),
            })
        covered_to = max(covered_to, q_end)
    return recs, covered_to


def _t(node, path):
    el = node.find(path) if node is not None else None
    return (el.text or "").strip() if el is not None else ""


def parse_form_d(xml_text, adsh, cik, filed):
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None
    issuer, off = root.find("primaryIssuer"), root.find("offeringData")
    if issuer is None or off is None:
        return None
    people = []
    for p in root.findall("relatedPersonsList/relatedPersonInfo"):
        people.append((_t(p, "relatedPersonName/firstName"), _t(p, "relatedPersonName/lastName"),
                       [r.text or "" for r in p.findall("relatedPersonRelationshipList/relationship")],
                       _t(p, "relationshipClarification")))
    return {
        "adsh": adsh, "cik": cik, "name": _t(issuer, "entityName"), "city": _t(issuer, "issuerAddress/city"),
        "state": _t(issuer, "issuerAddress/stateOrCountry"), "year": _t(issuer, "yearOfInc/value"),
        "entity": _t(issuer, "entityType"), "group": _t(off, "industryGroup/industryGroupType"),
        "amend": _t(off, "typeOfFiling/newOrAmendment/isAmendment") == "true", "filed": filed,
        "total": _money(_t(off, "offeringSalesAmounts/totalOfferingAmount")),
        "sold": _money(_t(off, "offeringSalesAmounts/totalAmountSold")) or 0,
        "revenue": _t(off, "issuerSize/revenueRange"), "people": people,
    }


def sec_recent_records(ua, start):
    """Filings newer than the last data set: EDGAR search per industry group, then each XML."""
    hits = {}
    for group in SEC_INDUSTRY:
        frm = 0
        while frm < 9900:
            q = urllib.parse.urlencode({"q": f'"{group}"', "forms": "D", "dateRange": "custom",
                                        "startdt": start.isoformat(), "enddt": TODAY.isoformat(), "from": frm})
            body = fetch("https://efts.sec.gov/LATEST/search-index?" + q, ua)
            page = json.loads(body)["hits"]["hits"] if body else []
            for h in page:
                s = h["_source"]
                name = (s.get("display_names") or [""])[0]
                if set(s.get("biz_states") or []) & US_STATES and not NOT_A_STARTUP.search(name):
                    hits[s["adsh"]] = s
            frm += len(page)
            time.sleep(0.15)
            if len(page) < 100:
                break
    print(f"  {len(hits)} recent filings since {start} to read (SEC limit: 10 requests/second)...")
    recs = []
    for adsh, s in hits.items():
        cik = str(int(s["ciks"][0]))
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/primary_doc.xml"
        fresh = not os.path.exists(os.path.join(CACHE, f"sec_{adsh}.xml"))
        xml_text = cached(f"sec_{adsh}.xml", url, ua, max_age_days=3650)
        if fresh:
            time.sleep(0.12)
        rec = parse_form_d(xml_text, adsh, cik, _date(s["file_date"])) if xml_text else None
        if rec and rec["group"] in SEC_INDUSTRY:
            recs.append(rec)
    return recs


def sec_contact(people):
    best = None
    for first, last, rels, clar in people:
        if not first or not last or first in ("-", "N/A", "n/a"):
            continue
        rank = 0 if re.search(r"\bceo\b|chief executive", clar, re.I) else \
            1 if re.search(r"founder|president", clar, re.I) else \
            2 if "Executive Officer" in rels else 3
        if best is None or rank < best[0]:
            title = clar if rank < 2 and clar else ", ".join(rels)
            best = (rank, nice(first), nice(last), title)
    return best[1:] if best else ("", "", "")


def sec_lead(recs):
    """One company's Form D filings in the window -> a lead, or None if it is not a fit."""
    recs = sorted(recs, key=lambda r: r["filed"])
    latest = recs[-1]
    name = latest["name"]
    year = latest["year"]
    if latest["entity"] != "Corporation" or latest["state"] not in US_STATES or NOT_A_STARTUP.search(name):
        return None
    if not year.isdigit() or TODAY.year - int(year) > 5:
        return None
    new = [r for r in recs if not r["amend"]]
    if not new:
        return None  # only amendments: the first raise was before the window
    sold = max(r["sold"] for r in recs)
    size = max([sold] + [r["total"] for r in recs if r["total"]])
    if sold > 20e6 or size > 30e6 or size < 100e3:
        return None

    last_new = new[-1]
    months = (TODAY - last_new["filed"]).days / 30.4
    remaining = (latest["total"] - latest["sold"]) if latest["total"] is not None else None
    open_now = (TODAY - latest["filed"]).days <= 180 and (remaining is None or remaining > 0.02 * (latest["total"] or 1))
    stage = "Pre-seed" if size < 1.5e6 else "Seed" if size < 6e6 else "Series A"
    if open_now:
        target = usd(latest["total"]) if latest["total"] is not None else "an uncapped amount"
        sig = (f"Round open now. Form D filed {latest['filed']}: {usd(latest['sold'])} raised of {target}"
               + (f", {usd(remaining)} still to raise." if remaining else "."))
        rnd, score = stage, 95 if (TODAY - latest["filed"]).days <= 90 else 86
    else:
        if stage == "Series A":
            return None  # next round would be a Series B, outside the target
        nxt = "Seed" if stage == "Pre-seed" else "Series A"
        sig = f"Raised a {usd(sold or size)} {stage.lower()} round {months:.0f} months ago (Form D filed {last_new['filed']}). "
        if months < 6:
            sig += f"Early for the next raise; worth warming up for their {nxt}."
            score = 50
        elif months < 12:
            sig += f"Founders usually start preparing the {nxt} around now."
            score = 70
        else:
            sig += f"In the usual 12 to 24 month window to raise a {nxt}."
            score = 82
        rnd = nxt
    if len(new) > 1:
        sig += f" {len(new)} separate raises filed in two years."
    sector = SEC_INDUSTRY[latest["group"]]
    if sector == "Software / tech" and AI_NAME.search(name):
        sector = "AI"
    first, last, title = sec_contact(latest["people"])
    full = f"{first} {last}".strip()
    display = nice(name)
    rev = latest["revenue"] if latest["revenue"] not in ("", "Decline to Disclose", "Not Applicable") else "undisclosed"
    return {
        "company": display, "sector": sector, "signal": sig, "likely_round": rnd, "score": score,
        "signal_date": latest["filed"].isoformat(), "company_linkedin": li_search("companies", LEGAL_SUFFIX.sub("", display)),
        "founder_linkedin": li_search("people", f"{full} {LEGAL_SUFFIX.sub('', display)}") if full else "",
        "email": "", "email_status": "", "full_name": full, "first_name": first, "last_name": last,
        "title": title, "website": "", "location": f"{nice(latest['city']).title()}, {latest['state']}",
        "team_size": "", "description": f"SEC industry: {latest['group']}. Incorporated {year}. Revenue: {rev}.",
        "source": "SEC Form D",
        "source_url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={latest['cik']}&type=D",
    }


def sec_leads(args):
    ua = os.environ.get("SEC_USER_AGENT", "")
    if not ua:
        print("SEC Form D: skipped. Set SEC_USER_AGENT=\"Company Name email@domain\" to enable (SEC requires it).")
        return []
    since = TODAY - dt.timedelta(days=args.sec_months * 30.4)
    print(f"SEC Form D: loading filings since {since}...")
    recs, covered_to = sec_dataset_records(ua, since)
    print(f"  {len(recs)} filings in target industries from quarterly data sets (through {covered_to - dt.timedelta(days=1)}).")
    recs += sec_recent_records(ua, covered_to)
    by_cik = {}
    for r in recs:
        if r["filed"] and r["filed"] >= since:
            by_cik.setdefault(r["cik"], {})[r["adsh"]] = r
    leads = [lead for lead in (sec_lead(list(v.values())) for v in by_cik.values()) if lead]
    print(f"  {len(leads)} startups kept out of {len(by_cik)} filers.")
    return leads


def merge(yc, sec):
    """A YC company that also filed a Form D gets the confirmed raise added to its row."""
    by_name = {}
    for lead in yc:
        by_name.setdefault(name_key(lead["company"]), []).append(lead)
    rest = []
    for s in sec:
        hits = by_name.get(name_key(s["company"]))
        if not hits:
            rest.append(s)
            continue
        for lead in hits:
            lead["signal"] = s["signal"] + " Also: " + lead["signal"]
            lead["score"] = min(99, max(lead["score"], s["score"]) + 3)
            lead["likely_round"] = s["likely_round"]
            lead["signal_date"] = s["signal_date"]
            lead["source"] = "Y Combinator + SEC Form D"
    return yc + rest


# ---------- output ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all-founders", action="store_true", help="one row per founder instead of CEO only")
    ap.add_argument("--sec-months", type=int, default=24, help="how far back to read Form D filings")
    ap.add_argument("--no-yc", action="store_true")
    args = ap.parse_args()
    args.hunter_key = os.environ.get("HUNTER_API_KEY", "")
    os.makedirs(OUT, exist_ok=True)

    leads = merge([] if args.no_yc else yc_leads(args), sec_leads(args))
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
