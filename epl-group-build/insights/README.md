# Insights

The Insights page shows two things together, newest first:

1. **Newsletter issues** from beehiiv ("Operating Advantage"). They come from the feed set as
   `FEED_URL` in `build.py`. The page also re-reads the feed in the visitor's browser, so a new
   issue appears on the live site without a new upload. `feed-cache.xml` is the last copy seen at build time.
2. **Articles written for the site**, one Markdown file each, described below.

## Articles

Each `.md` file in this folder becomes an article on the site: its own page at
`/insights/<file-name>` and a card at the top of the Insights page, newest first.
Nothing else needs editing. Run `python3 ../build.py` and upload the `epl-group` folder.

A file looks like this:

    ---
    title: The title shown on the page
    date: 2026-11-17
    tag: Permanent capital
    author: Jerome Davant
    summary: One or two sentences shown on the Insights page and in search results.
    ---

    The article text, in plain paragraphs.

    ## A section heading

    - A bullet point
    - Another one

Only `title` and `date` matter; the rest is optional. Delete the file to remove the article.
