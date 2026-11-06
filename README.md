# PDF Editor Pro (Vercel edition)

A PDF editor that runs in the browser. Click a line of text and type over it, add text and
images, highlight / underline / strike out, erase areas, find & replace, add watermarks and
page numbers, and rotate / duplicate / delete / reorder / merge pages.

One small Flask function (`app.py`) serves the page (embedded in `ui_html.py`) and does the
PDF work with PyMuPDF. The browser splits your file into pages and sends the server **one
page per request**, so big PDFs work despite Vercel's 4.5 MB request limit. Nothing is stored
on the server.

## Deploy on Vercel

1. Create a new GitHub repository.
2. Upload the **contents** of this folder so that `app.py` sits at the top level of the
   repository (not inside a sub-folder):

   ```
   app.py
   pdf_core.py
   ui_html.py
   requirements.txt
   ```

   `.python-version`, `.gitignore`, `.vercelignore`, `tests/` and this README are optional.
   Do not add a `public/` folder: Vercel keeps it out of the Python function.
   If you reuse an old repository, delete the old files first.
3. In Vercel: **Add New > Project**, import the repository, and click **Deploy**.
   Leave Build Command and Output Directory empty. No environment variables are needed.

If the build says `No python entrypoint found`, `app.py` is not at the top of the repository.
Either move the files up, or set **Settings > General > Root Directory** to the folder that
contains `app.py`.

## Run locally

```bash
pip install -r requirements.txt
python app.py            # http://localhost:5000  (the page is in ui_html.py)
pytest                   # optional
```

## Using it

| Tool | How |
|------|-----|
| Edit text | Click a line of text and type on the page. Enter or clicking elsewhere applies, Esc cancels. Size / B / I / colour apply to that line. |
| Add text | Click where the text should start, then type. |
| Highlight, Underline, Strike | Drag a rectangle over the text. |
| Erase | Drag a rectangle; the content underneath is really removed. |
| Image | Drag a rectangle, then pick a PNG or JPG (large images are shrunk first). |
| Find & replace, Watermark, Page numbers | Buttons in the top bar, for all pages or just this one. |
| Page tools | Rotate, Duplicate, + Blank, move up/down, Delete, Merge PDF. Thumbnails can be dragged to reorder. |

Shortcuts: `Ctrl+Z` undo, `Ctrl+Y` redo, `Ctrl+S` download, `PgUp` / `PgDn` change page.

## Limits

- **One line at a time.** Editing rewrites a line in place; it does not re-wrap paragraphs.
- **Fonts.** The original font is swapped for the nearest built-in one (Helvetica, Times or
  Courier, with bold/italic). Urdu, Pashto, Arabic and other non-Latin scripts are not
  supported in this version, because Vercel functions cannot bundle and shape custom fonts
  reliably here.
- **Scanned PDFs** are just pictures; there is no text to edit (the other tools still work).
- **Rotated pages:** rotate back to 0 degrees before editing text.
- **Password-protected PDFs** are rejected; remove the password first.
- **Per-page size:** one page (with its images and fonts) must stay under about 4.5 MB.
- **Bookmarks and form fields** may be lost on files that were edited heavily, because the
  editor rebuilds the file to keep its size down.
- The editor loads `pdf-lib` from a public CDN, so the browser needs internet access.

## Licence

PyMuPDF is licensed under **AGPL-3.0** (Artifex also sells a commercial licence). If you
publish this source or run it as a public service, release it under AGPL-3.0 and add a
`LICENSE` file, or check Artifex's terms first.
