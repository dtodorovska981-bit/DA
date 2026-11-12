# EPL Group website

Static site, no build step. Built from the Figma file "EPL Group | Website Design"
(page "Homepage v5, editorial layers").

## Pages
index.html (home), platforms.html, team.html, track-record.html, partners.html,
insights.html, events.html, pitch.html, investors.html, careers.html, 404.html

## Files
css/styles.css, js/main.js, assets/ (photos, logo and monogram SVGs), favicon.svg, favicon.ico, favicon-32x32.png, apple-touch-icon.png

## Notes
- The Pitch and Investors pages embed Pipefy forms (pitch: czfdp_CJ, investor onboarding: qyeXlWs4). The Events page embeds the investor onboarding form too.
- The Careers form opens a pre-filled email; the site has no form backend.
- Deploy as plain static files, for example on Cloudflare Workers static assets.
- Figures and transactions are placeholders taken from the current EPL site; confirm them before launch.
- Photos were exported from the Figma file at 1x; swap in higher-resolution originals before launch.
