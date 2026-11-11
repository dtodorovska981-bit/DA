# DNA Pro Plans website

Static site for dnaproplans.com. No build step: open `index.html`, or serve the folder with any static server.

## Pages
- `index.html` – home (services, approach, founder, engagements, process)
- `services.html` – what each service includes, pricing, sample business plan
- `case-studies.html`, `case-study-haraz.html`, `case-study-custel.html` – work
- `contact.html` – brief form, then the Calendly booking step
- `thanks.html` – fallback confirmation page (also offers the booking calendar)
- `privacy.html`, `404.html`

## Assets
- `styles.css`, `main.js` – all styling, scroll motion and form logic
- `images/`, `icons/` – exported from the Figma file (Home v3 and the case study frames)

## Form and booking
The brief form on `contact.html` is a Netlify form named `project-brief`; submissions appear under
Forms in the Netlify dashboard. After a successful submit the page shows the Calendly calendar
(`calendly.com/draganatodorovskajaneva/30min`), prefilled with the visitor's name and email.

## Still to fill in
- Review the payments and refunds wording in `privacy.html`
