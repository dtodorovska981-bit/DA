# Lead finder

Finds US startups (1 to 50 people; AI, fintech, energy/climate) that show a sign
of an upcoming or open pre-seed, seed or Series A raise, with the founder/CEO's
name, LinkedIn, and a best-guess email.

```bash
python3 lead-finder/find_leads.py
```

Output goes to `lead-finder/out/` (not committed, not served by Netlify):
`leads.csv` (opens in Excel/Sheets), `leads.json`, and `dashboard.html` (open in a browser).

## Signals

| Source | Signal | Contact data |
| --- | --- | --- |
| Y Combinator directory | In the current batch (seed raise at Demo Day), recently graduated, or 12 to 24 months post-batch (Series A window); hiring and team growth raise the score | Founder name, title, founder and company LinkedIn as published on the YC page |
| SEC Form D (optional) | A filed Form D with money still unsold means the round is open | Executive officer name; LinkedIn is a search link; no email |

## Options

- `--all-founders`: one row per founder instead of the CEO only.
- `SEC_USER_AGENT="Company Name you@example.com"`: turns on Form D. The SEC rejects requests that do not declare a contact. `--sec-days 30` sets how far back to look.
- `HUNTER_API_KEY=...`: replaces guessed emails with Hunter.io lookups where it finds one.

## Emails

Without a Hunter key, emails are a `first@domain` guess and are marked unverified.
Verify them before sending, and follow CAN-SPAM (real sender identity, physical
address, working unsubscribe).
