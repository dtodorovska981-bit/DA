# Insights articles

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
