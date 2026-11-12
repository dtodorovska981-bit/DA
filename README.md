# DNA Pro Plans website

Static site for dnaproplans.com. No build step: open `index.html`, or serve the folder with any static server.

## Pages
- `index.html` – home (services, approach, founder, engagements, process)
- `services.html` – what each service includes, pricing, sample business plan
- `case-studies.html`, `case-study-haraz.html`, `case-study-custel.html` – work
- `contact.html` – Pipefy brief form, then the Calendly booking step
- `privacy.html`, `404.html`

## Assets
- `styles.css`, `main.js` – all styling, scroll motion and form logic
- `images/`, `icons/` – exported from the Figma file (Home v3 and the case study frames)

## Form and booking
`contact.html` embeds the Pipefy brief form (`app.pipefy.com/public/form/WjXLnOMX`) as step 1 and the
Calendly calendar (`calendly.com/draganatodorovskajaneva/30min`) as step 2. Submissions arrive in Pipefy.

## Still to fill in
- Review the payments and refunds wording in `privacy.html`
