"""PDF engine for the web app (PyMuPDF).

Works on one in-memory PDF (in this app: a single page sent by the browser).
Page numbers are 0-based. Coordinates passed to editing methods are PDF points
in unrotated page space, the same space PyMuPDF uses for text extraction.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import List, Optional, Tuple

try:  # PyMuPDF >= 1.24.3 prefers "import pymupdf"
    import pymupdf as fitz
except ImportError:  # older installs only expose "fitz"
    import fitz  # type: ignore

Color = Tuple[float, float, float]


class PasswordRequired(Exception):
    """The PDF is encrypted."""


# --------------------------------------------------------------------------- #
# colours and fonts
# --------------------------------------------------------------------------- #
def int_to_rgb(value: int) -> Color:
    return (((value >> 16) & 255) / 255, ((value >> 8) & 255) / 255, (value & 255) / 255)


def hex_to_rgb(value: str) -> Color:
    value = (value or "#000000").lstrip("#")
    if len(value) != 6:
        return (0.0, 0.0, 0.0)
    return (int(value[0:2], 16) / 255, int(value[2:4], 16) / 255, int(value[4:6], 16) / 255)


# (regular, bold, italic, bold-italic) per built-in PDF font family
_FONT_TABLE = {
    "sans": ("helv", "hebo", "heit", "hebi"),
    "serif": ("tiro", "tibo", "tiit", "tibi"),
    "mono": ("cour", "cobo", "coit", "cobi"),
}


def pick_base14(font_name: str, flags: int = 0,
                bold: Optional[bool] = None, italic: Optional[bool] = None) -> str:
    """Closest built-in font for an arbitrary PDF font."""
    name = (font_name or "").lower()
    if bold is None:
        bold = bool(flags & 16) or any(k in name for k in ("bold", "black", "heavy"))
    if italic is None:
        italic = bool(flags & 2) or any(k in name for k in ("italic", "oblique"))
    if bool(flags & 8) or any(k in name for k in ("courier", "mono", "consolas")):
        family = "mono"
    elif any(k in name for k in ("sans", "arial", "helvetica", "calibri", "verdana")):
        family = "sans"
    elif bool(flags & 4) or any(
        k in name for k in ("times", "serif", "georgia", "garamond", "cambria", "minion")
    ):
        family = "serif"
    else:
        family = "sans"
    return _FONT_TABLE[family][int(bool(bold)) + 2 * int(bool(italic))]


@dataclass
class TextSpan:
    """One line of text with its styling."""
    page: int
    bbox: Tuple[float, float, float, float]
    text: str
    font: str
    size: float
    color: Color
    flags: int
    origin: Tuple[float, float]

    @property
    def bold(self) -> bool:
        return bool(self.flags & 16) or any(k in self.font.lower() for k in ("bold", "black", "heavy"))

    @property
    def italic(self) -> bool:
        return bool(self.flags & 2) or any(k in self.font.lower() for k in ("italic", "oblique"))


def _apply_redactions(page) -> None:
    """Apply redactions without touching images or vector graphics."""
    images = getattr(fitz, "PDF_REDACT_IMAGE_NONE", 0)
    try:
        page.apply_redactions(images=images, graphics=getattr(fitz, "PDF_REDACT_LINE_ART_NONE", 0))
    except TypeError:  # older PyMuPDF without the "graphics" argument
        page.apply_redactions(images=images)


MARKUP_COLORS = {
    "highlight": (1.0, 0.92, 0.2),
    "underline": (0.85, 0.1, 0.1),
    "strike": (0.85, 0.1, 0.1),
}


# --------------------------------------------------------------------------- #
# document
# --------------------------------------------------------------------------- #
class PDFDoc:
    def __init__(self, data: bytes):
        if not data:
            raise ValueError("Empty file")
        try:
            self.doc = fitz.open(stream=data, filetype="pdf")
        except Exception as exc:  # noqa: BLE001
            raise ValueError("This file is not a readable PDF") from exc
        if self.doc.needs_pass:
            self.doc.close()
            raise PasswordRequired("password-protected PDF")
        if self.doc.page_count < 1:
            self.doc.close()
            raise ValueError("The PDF has no pages")

    # ---- basics ---------------------------------------------------------- #
    @property
    def page_count(self) -> int:
        return self.doc.page_count

    def _n(self, n: int) -> int:
        return max(0, min(int(n), self.page_count - 1))

    def to_bytes(self) -> bytes:
        return self.doc.tobytes(garbage=3, deflate=True)

    def page_size(self, n: int = 0) -> Tuple[float, float]:
        r = self.doc[self._n(n)].rect
        return (r.width, r.height)

    # ---- rendering and coordinates ----------------------------------------- #
    def render(self, n: int, zoom: float, max_png: int = 2_400_000):
        """Render a page. Returns (bytes, mime, (width, height)).

        Vercel limits responses to 4.5 MB, so very large PNGs fall back to JPEG.
        """
        pix = self.doc[self._n(n)].get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        data, mime = pix.tobytes("png"), "image/png"
        if len(data) > max_png:
            try:
                data, mime = pix.tobytes("jpeg", jpg_quality=82), "image/jpeg"
            except TypeError:
                data, mime = pix.tobytes("jpeg"), "image/jpeg"
        return data, mime, (pix.width, pix.height)

    def view_to_pdf(self, n: int, x: float, y: float, zoom: float) -> Tuple[float, float]:
        p = fitz.Point(x / zoom, y / zoom) * self.doc[self._n(n)].derotation_matrix
        return (p.x, p.y)

    def view_rect_to_pdf(self, n: int, rect, zoom: float) -> Tuple[float, float, float, float]:
        r = fitz.Rect(rect) * fitz.Matrix(1 / zoom, 1 / zoom) * self.doc[self._n(n)].derotation_matrix
        r.normalize()
        return (r.x0, r.y0, r.x1, r.y1)

    def pdf_rect_to_view(self, n: int, rect, zoom: float) -> Tuple[float, float, float, float]:
        r = fitz.Rect(rect) * self.doc[self._n(n)].rotation_matrix * fitz.Matrix(zoom, zoom)
        r.normalize()
        return (r.x0, r.y0, r.x1, r.y1)

    # ---- reading text --------------------------------------------------------- #
    def text_lines(self, n: int = 0) -> List[TextSpan]:
        """One item per visual line of text (the unit for click-to-edit)."""
        n = self._n(n)
        out: List[TextSpan] = []
        for block in self.doc[n].get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                spans = [s for s in line["spans"] if s["text"]]
                text = "".join(s["text"] for s in spans)
                if not text.strip():
                    continue
                main = max(spans, key=lambda s: len(s["text"].strip()))
                out.append(TextSpan(
                    page=n, bbox=tuple(line["bbox"]), text=text, font=main["font"],
                    size=main["size"], color=int_to_rgb(main["color"]),
                    flags=main["flags"], origin=tuple(spans[0]["origin"]),
                ))
        return out

    def extract_text(self, n: Optional[int] = None) -> str:
        pages = range(self.page_count) if n is None else [self._n(n)]
        return "\n".join(self.doc[i].get_text() for i in pages)

    # ---- editing text ------------------------------------------------------------ #
    @staticmethod
    def _background(page, rect) -> Color:
        """Guess the page background colour around ``rect``."""
        try:
            pix = page.get_pixmap(clip=fitz.Rect(rect), dpi=72, alpha=False)
            w, h = pix.width, pix.height
            corners = [tuple(pix.pixel(x, y))[:3] for x in (0, w - 1) for y in (0, h - 1)]
            r, g, b = Counter(corners).most_common(1)[0][0]
            return (r / 255, g / 255, b / 255)
        except Exception:  # noqa: BLE001
            return (1, 1, 1)

    @staticmethod
    def _font(span: Optional[TextSpan], bold, italic) -> str:
        if span is not None:
            return pick_base14(span.font, span.flags, bold, italic)
        return pick_base14("", 0, bold, italic)

    def replace_line(self, span: TextSpan, new_text: str, size: Optional[float] = None,
                     color: Optional[Color] = None, bold: Optional[bool] = None,
                     italic: Optional[bool] = None) -> None:
        """Replace the text of a line in place, keeping its position."""
        page = self.doc[self._n(span.page)]
        rect = fitz.Rect(span.bbox)
        fill = self._background(page, rect)
        size = size or span.size
        color = color or span.color
        # Shrink slightly so neighbouring text is not caught by the redaction.
        page.add_redact_annot(rect + (0.5, 0.5, -0.5, -0.5), fill=fill)
        _apply_redactions(page)
        font = self._font(span, bold, italic)
        ox, oy = span.origin
        for i, line in enumerate(new_text.split("\n")):
            if line:
                page.insert_text((ox, oy + i * size * 1.2), line, fontsize=size,
                                 color=color, fontname=font)

    def add_text(self, n: int, point, text: str, size: float = 12, color: Color = (0, 0, 0),
                 bold: bool = False, italic: bool = False) -> None:
        """Add new text with its top-left corner at ``point``."""
        page = self.doc[self._n(n)]
        font = self._font(None, bold, italic)
        x, y = point
        for i, line in enumerate(text.split("\n")):
            if line:
                page.insert_text((x, y + size + i * size * 1.2), line,
                                 fontsize=size, color=color, fontname=font)

    def find_replace(self, old: str, new: str) -> int:
        """Replace every occurrence of ``old`` on every page of this PDF."""
        if not old:
            return 0
        plans = {}
        for n in range(self.page_count):
            page = self.doc[n]
            spans = self.text_lines(n)
            found = []
            for rect in page.search_for(old):
                cx, cy = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
                owner = next((s for s in spans
                              if s.bbox[0] <= cx <= s.bbox[2] and s.bbox[1] <= cy <= s.bbox[3]), None)
                found.append((rect, owner))
            if found:
                plans[n] = found
        total = sum(len(v) for v in plans.values())
        for n, found in plans.items():
            page = self.doc[n]
            fills = [self._background(page, r) for r, _ in found]
            for (rect, _), fill in zip(found, fills):
                page.add_redact_annot(rect + (0.3, 0.3, -0.3, -0.3), fill=fill)
            _apply_redactions(page)
            for rect, span in found:
                size = span.size if span else 11
                color = span.color if span else (0, 0, 0)
                baseline = span.origin[1] if span else rect.y1 - size * 0.2
                page.insert_text((rect.x0, baseline), new, fontsize=size, color=color,
                                 fontname=self._font(span, None, None))
        return total

    # ---- annotations and content --------------------------------------------------- #
    def markup(self, n: int, rect, kind: str = "highlight") -> None:
        page = self.doc[self._n(n)]
        make = {"highlight": page.add_highlight_annot, "underline": page.add_underline_annot,
                "strike": page.add_strikeout_annot}.get(kind)
        if make is None:
            raise ValueError(f"Unknown markup type: {kind}")
        annot = make(fitz.Rect(rect))
        annot.set_colors(stroke=MARKUP_COLORS[kind])
        annot.update()

    def erase_region(self, n: int, rect) -> None:
        """Remove (not just cover) whatever is inside ``rect``."""
        page = self.doc[self._n(n)]
        page.add_redact_annot(fitz.Rect(rect), fill=self._background(page, rect))
        _apply_redactions(page)

    def add_image(self, n: int, rect, data: bytes) -> None:
        try:
            self.doc[self._n(n)].insert_image(fitz.Rect(rect), stream=data, keep_proportion=True)
        except Exception as exc:  # noqa: BLE001
            raise ValueError("That image format is not supported (use PNG or JPG)") from exc

    def rotate(self, n: int, degrees: int = 90) -> None:
        page = self.doc[self._n(n)]
        page.set_rotation((page.rotation + degrees) % 360)

    def watermark(self, n: int, text: str, size: float = 64, color: Color = (0.6, 0.6, 0.6),
                  opacity: float = 0.25, angle: float = 45) -> None:
        """Diagonal text across the middle of the page."""
        page = self.doc[self._n(n)]
        r = page.rect
        width = fitz.get_text_length(text, fontname="helv", fontsize=size)
        center = fitz.Point(r.width / 2, r.height / 2)
        origin = fitz.Point(center.x - width / 2, center.y + size / 3)
        page.insert_text(origin, text, fontsize=size, fontname="helv", color=color,
                         fill_opacity=opacity, morph=(center, fitz.Matrix(-angle)))

    def page_number(self, n: int, text: str, size: float = 10, pos: str = "bc",
                    color: Color = (0, 0, 0)) -> None:
        """Stamp ``text`` in a corner / edge (pos = [b|t][l|c|r])."""
        page = self.doc[self._n(n)]
        r = page.rect
        width = fitz.get_text_length(text, fontname="helv", fontsize=size)
        margin = 28
        horiz = (pos[1:2] or "c")
        x = {"l": margin, "c": (r.width - width) / 2, "r": r.width - margin - width}.get(horiz, (r.width - width) / 2)
        y = r.height - margin if pos[:1] != "t" else margin + size
        page.insert_text((x, y), text, fontsize=size, fontname="helv", color=color)
