"""PDF Editor Pro - web version for Vercel (Flask).

Vercel detects this file and the `app` object automatically.
The page is served from ui_html.py (bundled with the function).

The server is stateless and only ever receives ONE PDF PAGE per request: the
browser splits the document into pages (pdf-lib), sends the page it is working
on, and stitches the results back together. That keeps every request far below
Vercel's 4.5 MB body limit, so even very large PDFs work.

    python app.py            local test at http://localhost:5000
"""
import base64
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, Response, jsonify, request  # noqa: E402
from werkzeug.exceptions import HTTPException  # noqa: E402

from pdf_core import PasswordRequired, PDFDoc, TextSpan, hex_to_rgb  # noqa: E402
from ui_html import HTML  # noqa: E402

MAX_MB = 4.4  # Vercel rejects request/response bodies above ~4.5 MB

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = int(MAX_MB * 1024 * 1024)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _doc() -> PDFDoc:
    upload = request.files.get("file")
    if upload is None:
        raise ValueError("No PDF received")
    return PDFDoc(upload.read())


def _s(name: str, default: str = "") -> str:
    return request.form.get(name, default)


def _f(name: str, default: float = 0.0) -> float:
    return float(_s(name, str(default)))


def _flag(name: str) -> bool:
    return _s(name) in ("1", "true", "True", "on")


def _zoom(default: float = 1.5) -> float:
    return max(0.2, min(_f("zoom", default), 4.0))


def _rect(doc: PDFDoc):
    view = (_f("x0"), _f("y0"), _f("x1"), _f("y1"))
    return doc.view_rect_to_pdf(0, view, _zoom())


def _pdf(doc: PDFDoc, count=None) -> Response:
    resp = Response(doc.to_bytes(), mimetype="application/pdf")
    if count is not None:
        resp.headers["X-Count"] = str(count)
    return resp


# --------------------------------------------------------------------------- #
# routes
# --------------------------------------------------------------------------- #
@app.get("/")
def index():
    resp = Response(HTML, mimetype="text/html")
    resp.headers["Cache-Control"] = "public, max-age=0, must-revalidate"
    return resp


@app.get("/health")
def health():
    return jsonify(ok=True)


@app.post("/api/page")
def api_page():
    """Render the page and list its editable text lines."""
    doc = _doc()
    zoom = _zoom()
    data, mime, (w, h) = doc.render(0, zoom)
    lines = []
    for s in doc.text_lines(0):
        d = asdict(s)
        d["vb"] = doc.pdf_rect_to_view(0, s.bbox, zoom)  # box in image pixels
        d["bold"], d["italic"] = s.bold, s.italic
        lines.append(d)
    pw, ph = doc.page_size(0)
    return jsonify(image=f"data:{mime};base64," + base64.b64encode(data).decode(),
                   width=w, height=h, pt_w=pw, pt_h=ph, lines=lines)


@app.post("/api/thumb")
def api_thumb():
    doc = _doc()
    data, mime, (w, h) = doc.render(0, max(0.15, min(_f("zoom", 0.3), 0.6)))
    return jsonify(image=f"data:{mime};base64," + base64.b64encode(data).decode(), width=w, height=h)


@app.post("/api/edit")
def api_edit():
    doc = _doc()
    d = json.loads(_s("span"))
    span = TextSpan(page=0, bbox=tuple(d["bbox"]), text=d["text"], font=d["font"],
                    size=float(d["size"]), color=tuple(d["color"]), flags=int(d["flags"]),
                    origin=tuple(d["origin"]))
    doc.replace_line(span, _s("text"), _f("size", span.size), hex_to_rgb(_s("color")),
                     _flag("bold"), _flag("italic"))
    return _pdf(doc)


@app.post("/api/addtext")
def api_addtext():
    doc = _doc()
    pt = doc.view_to_pdf(0, _f("x"), _f("y"), _zoom())
    doc.add_text(0, pt, _s("text"), _f("size", 12), hex_to_rgb(_s("color")),
                 _flag("bold"), _flag("italic"))
    return _pdf(doc)


@app.post("/api/markup")
def api_markup():
    doc = _doc()
    doc.markup(0, _rect(doc), _s("kind", "highlight"))
    return _pdf(doc)


@app.post("/api/erase")
def api_erase():
    doc = _doc()
    doc.erase_region(0, _rect(doc))
    return _pdf(doc)


@app.post("/api/image")
def api_image():
    doc = _doc()
    img = request.files.get("image")
    if img is None:
        raise ValueError("No image received")
    doc.add_image(0, _rect(doc), img.read())
    return _pdf(doc)


@app.post("/api/replace")
def api_replace():
    doc = _doc()
    count = doc.find_replace(_s("old"), _s("new"))
    if count == 0:  # nothing changed, so skip sending the page back
        return Response(status=204, headers={"X-Count": "0"})
    return _pdf(doc, count)


@app.post("/api/watermark")
def api_watermark():
    doc = _doc()
    doc.watermark(0, _s("text", "CONFIDENTIAL"), _f("size", 64), hex_to_rgb(_s("color", "#999999")),
                  opacity=max(0.05, min(_f("opacity", 0.25), 1.0)))
    return _pdf(doc)


@app.post("/api/pagenum")
def api_pagenum():
    doc = _doc()
    doc.page_number(0, _s("text"), _f("size", 10), _s("pos", "bc"))
    return _pdf(doc)


@app.errorhandler(Exception)
def on_error(exc):
    if isinstance(exc, HTTPException):
        code, msg = exc.code or 500, exc.description
    elif isinstance(exc, PasswordRequired):
        code, msg = 400, "This PDF is password-protected. Remove the password first."
    else:
        code, msg = 400, str(exc) or exc.__class__.__name__
    if code == 413:
        msg = "This page is too large for the server (limit about 4.5 MB per page)."
    return jsonify(error=msg), code


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
