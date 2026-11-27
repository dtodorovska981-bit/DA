# Lead finder

Finds US startups (1 to 50 people; AI, fintech, energy/climate) that show a sign
of an upcoming or open pre-seed, seed or Series A raise, with the founder/CEO's
name, LinkedIn, and a best-guess email.

```bash
SEC_USER_AGENT="DNA Pro Plans office@dnaproplans.com" python3 lead-finder/find_leads.py
```

The first run takes about 10 minutes (it downloads two years of filings); later runs reuse the cache.
Output goes to `lead-finder/out/` (not committed, not served by Netlify):
`leads.csv` (opens in Excel/Sheets), `leads.json`, and `dashboard.html` (open in a browser).

## Sources and signals (US companies only)

| Source | Signal | Contact data |
| --- | --- | --- |
| SEC Form D | Round open now (money still unsold), or a pre-seed/seed round closed in the past 24 months, which puts the next round in reach | Executive officer name; LinkedIn is a search link; no website or email |
| SEC Form C | Crowdfunding round open now, with deadline and target | CEO/founder name and title, website, employee count, guessed email |
| Funding news (VC News Daily) | Announced pre-seed or seed round in the past 24 months | Company and city; founder name only when the article quotes one |
| Y Combinator directory | In the current batch (seed raise at Demo Day) or 12 to 24 months post-batch (Series A window) | Founder name, title, founder and company LinkedIn, guessed email |

A company found in several sources becomes one row with all its signals and a higher score.
Without `SEC_USER_AGENT` both SEC sources are skipped: the SEC rejects requests that do not declare a contact.

## Options

- `--all-founders`: one row per YC founder instead of the CEO only.
- `--sec-months 24`: how far back to read Form D filings.
- `HUNTER_API_KEY=...`: replaces guessed emails with Hunter.io lookups for YC rows (untested).

## Emails

Without a Hunter key, emails are a `first@domain` guess and are marked unverified.
Verify them before sending, and follow CAN-SPAM (real sender identity, physical
address, working unsubscribe).
