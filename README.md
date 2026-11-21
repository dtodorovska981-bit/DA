# DNA Pro Plans website

Static site for dnaproplans.com, served by the Cloudflare Worker `throbbing-king-d6ed`.

## Working on the site
- Pages are generated: edit `tools/build.py`, then run `python3 tools/build.py .` and commit the result.
  The head, menu, footer, FAQ and calls to action are shared there so every page stays consistent.
- `styles.css`, `main.js` and `consent.js` are edited directly.
- Preview locally with `python3 tools/serve.py . 8080`. It serves clean URLs the way Cloudflare does.
  Opening the `.html` files directly does not work, because links and assets are root-relative.
- Build the production package with `python3 tools/package.py`. It writes `dist/dnaproplans-production.zip`.
  See `DEPLOY.md` for deployment and the post-deploy checklist.
- Change `BUILD` in `tools/build.py` on every release. It appears in `/version.txt` and in each page's
  `<meta name="dna-build">`.

## Pages
- `index.html` – offer, client work, services, approach, founder, engagements, process, FAQ
- `services.html` – scope, pricing and samples for every service
- `pitch-deck-services.html`, `financial-modeling-services.html`, `business-plan-services.html`,
  `sba-business-plan-services.html` – one page per service
- `case-studies.html`, `case-study-haraz.html`, `case-study-custel.html` – client work
- `contact.html` – inquiry form (Pipefy) and optional booking (Calendly)
- `thank-you.html` – inquiry confirmation, not indexed
- `privacy.html`, `404.html`

## Inquiry and booking
`contact.html` embeds the Pipefy public form (`app.pipefy.com/public/form/WjXLnOMX`). The Calendly calendar
(`calendly.com/draganatodorovskajaneva/30min`) loads only when the visitor asks for it.

## Analytics and consent
Google Analytics (`G-HCBH87S9EE`) is opt-in. `consent.js` loads Google's tag only after the visitor clicks
"Accept analytics"; the choice is stored in local storage and can be changed from "Cookie settings" in the footer.
Events: `cta_click`, `inquiry_submitted`, `call_booked` and `generate_lead` (once per visitor in 30 days).
Only fixed labels are sent, never names, emails or free text. Fonts are self-hosted in `fonts/`.
