# Deploying dnaproplans.com

Build: see `public/version.txt`. This package updates the existing Cloudflare Worker `throbbing-king-d6ed`,
which serves dnaproplans.com as static files.

## What is in this package

- `public/` – everything Cloudflare serves (pages, styles, scripts, fonts, images, sitemap, robots).
- `wrangler.jsonc` – Worker configuration: name, the `public` folder, clean URLs, and `404.html` for unknown pages.
- `DEPLOY.md` – this file.

## Before you deploy

1. In the Cloudflare dashboard open **Workers & Pages** and confirm the Worker that has `dnaproplans.com`
   under its domains is named `throbbing-king-d6ed`. If the name differs, change `"name"` in `wrangler.jsonc`
   to match. A wrong name creates a second Worker instead of updating the live one.
2. Do not upload files downloaded from the claude.ai preview. They contain preview-only notes.

## Deploy with Wrangler (the configuration in this package was validated this way)

Needs Node.js on your computer. In a terminal, inside the unzipped `dnaproplans-production` folder:

```bash
npx wrangler login
```

```bash
npx wrangler deploy
```

`wrangler login` opens the browser to sign in to the Cloudflare account that owns the Worker.
`wrangler deploy` uploads `public/` to the Worker named in `wrangler.jsonc`. If Wrangler warns that the
Worker's dashboard settings differ from the local configuration, read the warning before confirming, and
check afterwards that `dnaproplans.com` is still listed under the Worker's domains.

If you prefer the dashboard, upload the **contents of `public/`** the same way you uploaded the site before.

## Confirm the new version is live

- `https://dnaproplans.com/version.txt` shows `dnaproplans.com build 2026-11-21.4`.
- Page source of any page contains `<meta name="dna-build" content="2026-11-21.4">`.
- `https://dnaproplans.com/contact` shows the inquiry form inside the page, with no "Preview note".

## After deploying: check on the live site

- [ ] Homepage headline reads "Investor pitch decks, business plans and financial models built on research."
- [ ] `/contact`: the Pipefy form is embedded; submit one real test inquiry and confirm it arrives in Pipefy.
- [ ] `/contact`: "Show available times" loads Calendly; book and cancel one test call.
- [ ] `/sitemap.xml` opens as XML; `/robots.txt` lists the sitemap; a made-up URL shows the 404 page.
- [ ] Click "Accept analytics", then in Google Analytics > Realtime confirm `page_view` and `cta_click` arrive.
- [ ] Submit the sitemap in Google Search Console.

## Changes to make in your accounts (not done by the website code)

### Pipefy public form
The website embeds the form as it is. To match the short inquiry, edit the start form in Pipefy:

- Keep and require: Full name, Email, What do you need?
- Make **Deadline** required.
- Add a required long-text field: **Short project description**.
- Make **Company** optional, add an optional **Website** field, keep **Budget range** optional.
- Remove from the first form, and collect later: What is it for?, Materials you already have, file upload,
  How did you find us?, Referred by.
- Set the message shown after submission (Public form settings > after-submit message), for example:
  "Thank you. Your inquiry is in. We read it and reply by email with any questions, then your quote."

### Counting completed inquiries (pending)
The site only counts an inquiry (`inquiry_submitted` and `generate_lead`) when the page `/thank-you` is reached
from the Pipefy form. The form's configuration exposes an after-submit message but no redirect setting that we
could find, so today nothing sends visitors to `/thank-you` and **completed inquiries are not counted in GA4**.
Options, each needing access to your accounts:

1. If your Pipefy plan allows a redirect or a link after submission, point it to `https://dnaproplans.com/thank-you`.
2. Use a Pipefy automation ("when a card is created") to call the GA4 Measurement Protocol. This needs a GA4 API
   secret and cannot be tied to the visitor's session.
3. Replace the embedded form with a site form that creates the Pipefy card through the Pipefy API. This needs a
   Pipefy API token stored as a Worker secret.

Confirmed Calendly bookings are counted (`call_booked`) through Calendly's own "event scheduled" message.

### Google Analytics
- Admin > Events: mark `generate_lead` as a key event.
- Admin > Custom definitions: add event-scoped dimensions `cta_name`, `cta_location` and `lead_source`.
- Google's "Test your website" check will report the tag as not detected, because the tag is only loaded after a
  visitor accepts analytics. Verify with Realtime after accepting instead.
