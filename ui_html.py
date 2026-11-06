"""The editor page, embedded as a Python string.

Vercel does not ship the public/ folder inside the Python function, so the page lives here
where it is always bundled with app.py. Edit the HTML between the quotes."""

HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PDF Editor Pro</title>
<meta name="description" content="Edit PDF text in your browser: click a line and type. Add text, images, highlights, watermarks and page numbers, and reorder pages.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231a73e8'/%3E%3Cpath d='M9 7h10l5 5v13H9z' fill='%23fff'/%3E%3Cpath d='M19 7v5h5' fill='%23cfe0fb'/%3E%3C/svg%3E">
<style>
  :root { --bg:#e9ecf0; --panel:#ffffff; --line:#d3d8df; --ink:#1f2328; --mute:#6b7280; --acc:#1a73e8;
          --acc-d:#1666cf; --hover:#f3f5f8; --side:#f6f7f9; --danger:#d93025; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#1b1d21; --panel:#25282d; --line:#3a3f46; --ink:#e8eaed; --mute:#9aa0a6; --hover:#2f3338; --side:#202327; }
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body { margin:0; font:14px/1.4 system-ui,"Segoe UI",Roboto,sans-serif; color:var(--ink); background:var(--bg);
         display:flex; flex-direction:column; overflow:hidden; }
  .bar { background:var(--panel); border-bottom:1px solid var(--line); padding:6px 10px; display:flex; flex-wrap:wrap;
         gap:6px; align-items:center; }
  .bar.second { padding-top:4px; padding-bottom:6px; }
  .brand { font-weight:700; margin-right:6px; }
  .sep { width:1px; align-self:stretch; background:var(--line); margin:0 4px; }
  button, .btn { font:inherit; border:1px solid var(--line); background:var(--panel); color:var(--ink); padding:5px 10px;
                 border-radius:6px; cursor:pointer; white-space:nowrap; }
  button:hover, .btn:hover { background:var(--hover); }
  button:disabled { opacity:.45; cursor:default; }
  .tool.active { background:var(--acc); border-color:var(--acc); color:#fff; }
  .primary { background:var(--acc); border-color:var(--acc); color:#fff; }
  .primary:hover { background:var(--acc-d); }
  .iconbtn { min-width:34px; padding:5px 8px; }
  .fmt label.l { color:var(--mute); margin-right:4px; }
  input[type=number], input[type=text], select { font:inherit; color:var(--ink); background:var(--panel); border:1px solid var(--line);
         border-radius:6px; padding:4px 6px; }
  .fmt input[type=number] { width:64px; }
  .fmt input[type=color] { width:36px; height:28px; padding:0; border:1px solid var(--line); border-radius:6px; background:var(--panel); vertical-align:middle; }
  .toggle { display:inline-flex; }
  .toggle input { display:none; }
  .toggle span { display:inline-block; min-width:30px; text-align:center; padding:5px 8px; border:1px solid var(--line);
         border-radius:6px; background:var(--panel); cursor:pointer; user-select:none; }
  .toggle input:checked + span { background:var(--acc); border-color:var(--acc); color:#fff; }
  #pageinfo, #zoomv { min-width:60px; text-align:center; color:var(--mute); }
  .app { flex:1; display:flex; min-height:0; position:relative; }
  #side { width:150px; flex:none; background:var(--side); border-right:1px solid var(--line); overflow:auto; padding:10px 8px; }
  body.side-hidden #side { display:none; }
  .th { margin:0 auto 12px; width:112px; text-align:center; cursor:pointer; border-radius:8px; padding:5px 5px 3px; border:2px solid transparent; }
  .th:hover { background:var(--hover); }
  .th.active { border-color:var(--acc); background:var(--hover); }
  .th.over { border-color:var(--danger); }
  .th .pic { width:100%; aspect-ratio:3/4; background:#fff; border:1px solid var(--line); display:flex; align-items:center; justify-content:center; overflow:hidden; }
  .th img { max-width:100%; max-height:100%; display:block; }
  .th small { color:var(--mute); }
  main { flex:1; overflow:auto; padding:20px; position:relative; }
  #empty { max-width:560px; margin:10vh auto 0; text-align:center; color:var(--mute); border:2px dashed var(--line);
           border-radius:14px; padding:40px 24px; background:var(--panel); }
  #empty h2 { color:var(--ink); margin:0 0 8px; }
  #empty ul { text-align:left; display:inline-block; margin:8px 0 0; padding-left:18px; }
  #stage { position:relative; margin:0 auto; background:#fff; box-shadow:0 2px 14px rgba(0,0,0,.28); user-select:none; }
  #stage img { display:block; }
  #stage.cross { cursor:crosshair; }
  #stage.text { cursor:text; }
  #ov { position:absolute; inset:0; pointer-events:none; }
  #ov .ln { position:absolute; pointer-events:none; }
  #ov.edit .ln { pointer-events:auto; cursor:text; }
  #ov.edit .ln:hover { outline:2px solid var(--acc); background:rgba(26,115,232,.08); }
  .inl { position:absolute; z-index:5; border:2px solid var(--acc); background:#fff; padding:0 2px; outline:none; margin:0; border-radius:0; }
  .rubber { position:absolute; border:2px dashed var(--danger); background:rgba(217,48,37,.08); z-index:4; pointer-events:none; }
  footer { background:var(--panel); border-top:1px solid var(--line); padding:4px 12px; color:var(--mute); font-size:13px; min-height:26px; }
  #busy { position:fixed; top:10px; right:14px; background:#222; color:#fff; padding:4px 12px; border-radius:99px; font-size:13px; display:none; z-index:30; }
  dialog { border:1px solid var(--line); border-radius:12px; padding:18px; min-width:340px; background:var(--panel); color:var(--ink); }
  dialog::backdrop { background:rgba(0,0,0,.35); }
  dialog h3 { margin:0 0 6px; }
  dialog label.f { display:block; margin:10px 0 3px; color:var(--mute); }
  dialog input[type=text], dialog input[type=number], dialog select { width:100%; }
  dialog input[type=color] { width:48px; height:30px; padding:0; border:1px solid var(--line); border-radius:6px; background:var(--panel); }
  dialog .row { display:flex; gap:8px; justify-content:flex-end; margin-top:16px; }
  dialog .two { display:flex; gap:10px; } dialog .two > div { flex:1; }
  dialog p.hint { color:var(--mute); margin:4px 0 0; font-size:12px; }
  @media (max-width: 760px) {
    main { padding:8px; }
    #side { position:absolute; left:0; top:0; bottom:0; z-index:12; box-shadow:2px 0 12px rgba(0,0,0,.25); }
  }
</style>
</head>
<body>
<div id="busy">Working…</div>

<div class="bar">
  <span class="brand">PDF Editor Pro</span>
  <label class="btn primary" for="file" title="Open a PDF">Open PDF</label>
  <input id="file" type="file" accept="application/pdf,.pdf" hidden>
  <button id="download" class="primary" disabled title="Download the edited PDF (Ctrl+S)">Download</button>
  <span class="sep"></span>
  <button id="undo" disabled title="Undo (Ctrl+Z)">Undo</button>
  <button id="redo" disabled title="Redo (Ctrl+Y)">Redo</button>
  <span class="sep"></span>
  <button class="tool active" data-mode="edit" title="Click a line of text and type">Edit text</button>
  <button class="tool" data-mode="addtext" title="Click anywhere and type new text">Add text</button>
  <button class="tool" data-mode="highlight" title="Drag over text to highlight">Highlight</button>
  <button class="tool" data-mode="underline" title="Drag over text to underline">Underline</button>
  <button class="tool" data-mode="strike" title="Drag over text to strike out">Strike</button>
  <button class="tool" data-mode="erase" title="Drag a rectangle to remove content">Erase</button>
  <button class="tool" data-mode="image" title="Drag a rectangle, then choose an image">Image</button>
  <span class="sep"></span>
  <button id="findbtn" disabled>Find &amp; replace</button>
  <button id="wmbtn" disabled>Watermark</button>
  <button id="pnbtn" disabled>Page numbers</button>
</div>

<div class="bar second">
  <button id="sidebtn" class="iconbtn" title="Show or hide page thumbnails">&#9776; Pages</button>
  <span class="sep"></span>
  <span class="fmt">
    <label class="l" for="size">Size</label><input id="size" type="number" min="4" max="200" step="1" value="12">
    <label class="toggle" title="Bold"><input id="bold" type="checkbox"><span><b>B</b></span></label>
    <label class="toggle" title="Italic"><input id="italic" type="checkbox"><span><i>I</i></span></label>
    <input id="color" type="color" value="#000000" title="Text colour">
  </span>
  <span class="sep"></span>
  <button id="prev" class="iconbtn" disabled title="Previous page (PgUp)">&#9664;</button><span id="pageinfo">– / –</span><button id="next" class="iconbtn" disabled title="Next page (PgDn)">&#9654;</button>
  <span class="sep"></span>
  <button id="zout" class="iconbtn" disabled title="Zoom out">–</button><span id="zoomv">150%</span><button id="zin" class="iconbtn" disabled title="Zoom in">+</button>
  <button id="zfit" disabled title="Fit page to window width">Fit</button>
  <span class="sep"></span>
  <button id="rotl" class="iconbtn" disabled title="Rotate page left">&#8634;</button>
  <button id="rotr" class="iconbtn" disabled title="Rotate page right">&#8635;</button>
  <button id="dup" disabled title="Duplicate this page">Duplicate</button>
  <button id="blank" disabled title="Insert a blank page after this one">+ Blank</button>
  <button id="up" class="iconbtn" disabled title="Move page earlier">&#8593;</button>
  <button id="down" class="iconbtn" disabled title="Move page later">&#8595;</button>
  <button id="delpg" disabled title="Delete this page">Delete page</button>
  <button id="merge" disabled title="Append another PDF at the end">Merge PDF…</button>
  <input id="mergefile" type="file" accept="application/pdf,.pdf" hidden>
</div>

<div class="app">
  <aside id="side"><div id="thumbs"></div></aside>
  <main id="scroll">
    <div id="empty">
      <h2>Open a PDF to start editing</h2>
      <p>Click <b>Open PDF</b> or drop a file anywhere on this page.</p>
      <ul>
        <li>Click a line of text and type right on the page</li>
        <li>Add text, images, highlights, underlines and strike-through</li>
        <li>Find &amp; replace, watermark and page numbers for the whole file</li>
        <li>Rotate, duplicate, delete, reorder (drag thumbnails) and merge pages</li>
      </ul>
      <p style="font-size:12px;margin-top:14px">Your PDF is processed one page at a time and is never stored on the server.</p>
    </div>
    <div id="stage" hidden><img id="pg" alt="PDF page"><div id="ov"></div></div>
  </main>
</div>
<footer id="status">Ready</footer>
<input id="imgfile" type="file" accept="image/*" hidden>

<dialog id="frdlg">
  <form method="dialog" id="frform">
    <h3>Find &amp; replace</h3>
    <label class="f" for="fr_old">Find</label><input id="fr_old" type="text" autocomplete="off">
    <label class="f" for="fr_new">Replace with</label><input id="fr_new" type="text" autocomplete="off">
    <label class="f" for="fr_scope">Where</label>
    <select id="fr_scope"><option value="all">All pages</option><option value="page">This page only</option></select>
    <div class="row"><button type="button" data-close>Cancel</button><button class="primary" value="go">Replace all</button></div>
  </form>
</dialog>

<dialog id="wmdlg">
  <form method="dialog" id="wmform">
    <h3>Watermark</h3>
    <label class="f" for="wm_text">Text</label><input id="wm_text" type="text" value="CONFIDENTIAL" autocomplete="off">
    <div class="two">
      <div><label class="f" for="wm_size">Size</label><input id="wm_size" type="number" min="12" max="200" value="64"></div>
      <div><label class="f" for="wm_op">Opacity %</label><input id="wm_op" type="number" min="5" max="100" value="25"></div>
      <div><label class="f" for="wm_col">Colour</label><input id="wm_col" type="color" value="#999999"></div>
    </div>
    <label class="f" for="wm_scope">Where</label>
    <select id="wm_scope"><option value="all">All pages</option><option value="page">This page only</option></select>
    <div class="row"><button type="button" data-close>Cancel</button><button class="primary" value="go">Add watermark</button></div>
  </form>
</dialog>

<dialog id="pndlg">
  <form method="dialog" id="pnform">
    <h3>Page numbers</h3>
    <label class="f" for="pn_text">Text</label><input id="pn_text" type="text" value="Page {n} of {total}" autocomplete="off">
    <p class="hint">{n} = page number, {total} = number of pages</p>
    <div class="two">
      <div><label class="f" for="pn_pos">Position</label>
        <select id="pn_pos"><option value="bc">Bottom centre</option><option value="br">Bottom right</option><option value="bl">Bottom left</option>
          <option value="tc">Top centre</option><option value="tr">Top right</option><option value="tl">Top left</option></select></div>
      <div><label class="f" for="pn_size">Size</label><input id="pn_size" type="number" min="6" max="40" value="10"></div>
      <div><label class="f" for="pn_start">Start at</label><input id="pn_start" type="number" min="1" value="1"></div>
    </div>
    <div class="row"><button type="button" data-close>Cancel</button><button class="primary" value="go">Add numbers</button></div>
  </form>
</dialog>

<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js" crossorigin="anonymous"></script>
<script>window.PDFLib || document.write('<script src="https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/dist/pdf-lib.min.js"><\/script>')</script>
<script>
"use strict";
const $ = id => document.getElementById(id);
const L = window.PDFLib;
const S = {
  bytes: null, orig: null, base: 0, name: "document.pdf", page: 0, pages: 0, zoom: 1.5, lines: [],
  undo: [], redo: [], mode: "edit", ed: null, busyN: 0, commitP: null, gen: 0, loadTok: 0,
  thumbs: new Map(), visible: new Set(), _src: null, pendingRect: null,
};
const MAX_UNDO = 15, MIN_Z = 0.5, MAX_Z = 3;
const HINTS = {
  edit: "Edit text: click a line and type. Enter or click elsewhere applies, Esc cancels.",
  addtext: "Add text: click where the text should start, then type.",
  highlight: "Highlight: drag a rectangle over the text.",
  underline: "Underline: drag a rectangle over the text.",
  strike: "Strike out: drag a rectangle over the text.",
  erase: "Erase: drag a rectangle; the content underneath is removed.",
  image: "Image: drag a rectangle, then choose a picture.",
};
const DRAG_MODES = ["highlight", "underline", "strike", "erase", "image"];

const toHex = c => "#" + c.map(v => Math.round(v * 255).toString(16).padStart(2, "0")).join("");
function status(t, err) { const s = $("status"); s.textContent = t; s.style.color = err ? "var(--danger)" : ""; }
function setBusy(on) { S.busyN = Math.max(0, S.busyN + (on ? 1 : -1)); $("busy").style.display = S.busyN > 0 ? "block" : "none"; }
const busy = () => S.busyN > 0;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

/* ================= talking to the server (one page per request) ================= */
async function call(op, fields, pdfBytes, files) {
  const fd = new FormData();
  fd.append("file", new Blob([pdfBytes], { type: "application/pdf" }), "page.pdf");
  for (const [k, v] of Object.entries(fields || {})) fd.append(k, v);
  for (const [k, f] of Object.entries(files || {})) fd.append(k, f, f.name || k);
  let r;
  try { r = await fetch("/api/" + op, { method: "POST", body: fd }); }
  catch (e) { throw new Error("Cannot reach the server. Check your connection."); }
  if (!r.ok) {
    let m = "Server error " + r.status;
    if (r.status === 413) m = "This page is too large for the server (limit about 4.5 MB per page).";
    else if (r.status === 504) m = "The server took too long. Try again.";
    else { try { m = (await r.json()).error || m; } catch (_) {} }
    throw new Error(m);
  }
  return r;
}

/* ================= document helpers (pdf-lib, in the browser) ================= */
const LOAD = { ignoreEncryption: true, updateMetadata: false };
function src() {
  if (!S._src) S._src = L.PDFDocument.load(S.bytes, LOAD);
  return S._src;
}
function setBytes(b) { S.bytes = b; S._src = null; S.gen++; }
async function extractPage(i) {
  const s = await src();
  const out = await L.PDFDocument.create({ updateMetadata: false });
  const [p] = await out.copyPages(s, [i]);
  out.addPage(p);
  return out.save();
}
async function swapPages(map) {          // map: pageIndex -> single-page PDF bytes
  const doc = await L.PDFDocument.load(S.bytes, LOAD);
  for (const [i, b] of map) {
    const ed = await L.PDFDocument.load(b, { updateMetadata: false });
    const [p] = await doc.copyPages(ed, [0]);
    doc.insertPage(i, p);
    doc.removePage(i + 1);
  }
  return doc.save();
}
async function compact(bytes) {          // drop orphaned objects left behind by page swaps
  const a = await L.PDFDocument.load(bytes, LOAD);
  const out = await L.PDFDocument.create({ updateMetadata: false });
  const pages = await out.copyPages(a, a.getPageIndices());
  pages.forEach(p => out.addPage(p));
  try {
    const t = a.getTitle(), au = a.getAuthor();
    if (t) out.setTitle(t, { updateMetadata: false });
    if (au) out.setAuthor(au, { updateMetadata: false });
  } catch (_) {}
  return out.save();
}
async function commitDoc(nb, changed) {
  if (nb.length > S.base * 2 + 1e6) {
    try { nb = await compact(nb); S.base = nb.length; } catch (_) {}
  }
  S.undo.push(S.bytes);
  if (S.undo.length > MAX_UNDO) S.undo.shift();
  S.redo = [];
  setBytes(nb);
  if (changed) { changed.forEach(i => { S.thumbs.delete(i); showThumb(i); }); kickThumbs(); }
  refreshButtons();
}
async function syncCount() {
  S.pages = (await src()).getPageCount();
  S.page = clamp(S.page, 0, S.pages - 1);
}

/* ================= buttons / labels ================= */
function refreshButtons() {
  const has = !!S.bytes;
  for (const id of ["download", "findbtn", "wmbtn", "pnbtn", "zin", "zout", "zfit", "rotl", "rotr", "dup", "blank", "delpg", "merge"]) $(id).disabled = !has;
  $("prev").disabled = !has || S.page <= 0;
  $("next").disabled = !has || S.page >= S.pages - 1;
  $("up").disabled = !has || S.page <= 0;
  $("down").disabled = !has || S.page >= S.pages - 1;
  $("undo").disabled = !S.undo.length;
  $("redo").disabled = !S.redo.length;
  $("pageinfo").textContent = has ? `${S.page + 1} / ${S.pages}` : "– / –";
  $("zoomv").textContent = Math.round(S.zoom * 100) + "%";
}

/* ================= page view ================= */
async function loadPage() {
  if (!S.bytes) return;
  const tok = ++S.loadTok;
  setBusy(true);
  try {
    const pb = await extractPage(S.page);
    const j = await (await call("page", { zoom: S.zoom }, pb)).json();
    if (tok !== S.loadTok) return;
    S.lines = j.lines;
    const img = $("pg"), st = $("stage");
    img.width = j.width; img.height = j.height;
    await new Promise(res => { img.onload = img.onerror = res; img.src = j.image; });
    st.style.width = j.width + "px"; st.style.height = j.height + "px";
    $("empty").hidden = true; st.hidden = false;
    drawOverlays();
    markActive();
    status(j.lines.length ? HINTS[S.mode] : "No editable text on this page (scanned image?). The other tools still work.");
  } catch (e) { if (tok === S.loadTok) status(e.message, true); }
  finally { setBusy(false); refreshButtons(); }
}

function drawOverlays() {
  const ov = $("ov");
  ov.innerHTML = "";
  ov.className = S.mode === "edit" ? "edit" : "";
  S.lines.forEach(l => {
    const d = document.createElement("div");
    d.className = "ln";
    const [x0, y0, x1, y1] = l.vb;
    Object.assign(d.style, { left: x0 + "px", top: y0 + "px", width: (x1 - x0) + "px", height: (y1 - y0) + "px" });
    d.addEventListener("click", ev => { if (S.mode === "edit") { ev.stopPropagation(); startEdit(l); } });
    ov.appendChild(d);
  });
  $("stage").className = (S.mode === "edit" || S.mode === "addtext") ? "text" : "cross";
}

async function fitZoom() {
  const s = (await src()).getPage(S.page);
  const sz = s.getSize(), rot = s.getRotation().angle;
  const w = (rot % 180) ? sz.height : sz.width;
  const avail = $("scroll").clientWidth - 48;
  return clamp(Math.round((avail / w) * 100) / 100, 0.6, 2.5);
}

async function openFile(file) {
  if (!file) return;
  await commit();
  if (S.bytes && S.undo.length && !confirm("Open a new file and discard your unsaved changes?")) return;
  if (!L) { status("The pdf-lib library did not load (blocked network?). Reload the page.", true); return; }
  setBusy(true);
  try {
    const buf = new Uint8Array(await file.arrayBuffer());
    let doc;
    try { doc = await L.PDFDocument.load(buf, { updateMetadata: false }); }
    catch (e) {
      if (/encrypt/i.test(e.message || "")) throw new Error("This PDF is password-protected. Remove the password first.");
      throw new Error("Could not read this file as a PDF.");
    }
    S.name = file.name; S.orig = buf; S.base = buf.length;
    S.undo = []; S.redo = []; S.page = 0; S.pages = doc.getPageCount();
    S.thumbs.clear();
    setBytes(buf);
    S._src = Promise.resolve(doc);
    S.zoom = await fitZoom();
    buildSidebar();
    await loadPage();
  } catch (e) { status(e.message, true); }
  finally { setBusy(false); refreshButtons(); }
}

/* ================= thumbnails sidebar ================= */
let thumbObs = null, thumbRun = 0;
const thumbQ = [];
function buildSidebar() {
  const box = $("thumbs");
  box.innerHTML = "";
  S.visible.clear(); thumbQ.length = 0;
  if (thumbObs) thumbObs.disconnect();
  thumbObs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      const i = +e.target.dataset.i;
      if (e.isIntersecting) { S.visible.add(i); queueThumb(i); } else S.visible.delete(i);
    });
  }, { root: $("side"), rootMargin: "200px" });
  for (let i = 0; i < S.pages; i++) {
    const d = document.createElement("div");
    d.className = "th"; d.dataset.i = i; d.draggable = true;
    d.innerHTML = '<div class="pic"><img alt="" hidden></div><small>' + (i + 1) + "</small>";
    d.addEventListener("click", () => goto(i));
    d.addEventListener("dragstart", e => { e.dataTransfer.setData("text/x-page", String(i)); e.dataTransfer.effectAllowed = "move"; });
    d.addEventListener("dragover", e => { if (e.dataTransfer.types.includes("text/x-page")) { e.preventDefault(); d.classList.add("over"); } });
    d.addEventListener("dragleave", () => d.classList.remove("over"));
    d.addEventListener("drop", e => {
      d.classList.remove("over");
      const from = parseInt(e.dataTransfer.getData("text/x-page"), 10);
      if (!isNaN(from) && from !== i) { e.preventDefault(); e.stopPropagation(); movePage(from, i); }
    });
    box.appendChild(d);
    thumbObs.observe(d);
  }
  markActive();
}
function showThumb(i) {
  const d = $("thumbs").children[i];
  if (!d) return;
  const img = d.querySelector("img"), data = S.thumbs.get(i);
  if (data) { img.src = data; img.hidden = false; } else { img.removeAttribute("src"); img.hidden = true; }
}
function queueThumb(i) { if (!S.thumbs.has(i) && !thumbQ.includes(i)) { thumbQ.push(i); pumpThumbs(); } }
function kickThumbs() { S.visible.forEach(queueThumb); }
function pumpThumbs() {
  while (thumbRun < 2 && thumbQ.length) {
    const i = thumbQ.shift(), gen = S.gen;
    thumbRun++;
    (async () => {
      try {
        const pb = await extractPage(i);
        const j = await (await call("thumb", { zoom: 0.28 }, pb)).json();
        if (gen === S.gen) { S.thumbs.set(i, j.image); showThumb(i); }
      } catch (_) { /* thumbnails are optional */ }
      finally { thumbRun--; pumpThumbs(); }
    })();
  }
}
function markActive() {
  [...$("thumbs").children].forEach((d, i) => d.classList.toggle("active", i === S.page));
  const a = $("thumbs").children[S.page];
  if (a) a.scrollIntoView({ block: "nearest" });
}

async function goto(n) {
  await commit();
  if (!S.bytes || n < 0 || n >= S.pages || n === S.page && !$("stage").hidden && false) return;
  S.page = n;
  $("scroll").scrollTop = 0;
  markActive(); refreshButtons();
  await loadPage();
}

/* ================= formatting bar ================= */
function fmt() {
  return { size: Math.max(4, parseFloat($("size").value) || 12), bold: $("bold").checked,
           italic: $("italic").checked, color: $("color").value.toLowerCase() };
}
function setFmt(size, bold, italic, color) {
  $("size").value = +size.toFixed(2); $("bold").checked = !!bold; $("italic").checked = !!italic; $("color").value = color;
}
function familyOf(l) {
  const n = (l.font || "").toLowerCase();
  if ((l.flags & 8) || /courier|mono|consolas/.test(n)) return '"Courier New", Courier, monospace';
  if (/sans|arial|helvetica|calibri|verdana/.test(n)) return "Helvetica, Arial, sans-serif";
  if ((l.flags & 4) || /times|serif|georgia|garamond|cambria|minion/.test(n)) return '"Times New Roman", Times, serif';
  return "Helvetica, Arial, sans-serif";
}
function styleInput() {
  if (!S.ed) return;
  const f = fmt(), s = S.ed.input.style;
  s.fontSize = (f.size * S.zoom) + "px";
  s.fontWeight = f.bold ? "700" : "400";
  s.fontStyle = f.italic ? "italic" : "normal";
  s.color = f.color;
  s.fontFamily = S.ed.family;
}
for (const id of ["size", "bold", "italic"]) $(id).addEventListener("input", () => { if (S.ed) { styleInput(); S.ed.input.focus(); } });
$("color").addEventListener("change", () => { if (S.ed) { styleInput(); S.ed.input.focus(); } });
// keep focus in the text box while the formatting buttons are clicked
document.querySelector(".fmt").addEventListener("mousedown", e => {
  if (S.ed && !e.target.matches("input[type=number], input[type=color]")) e.preventDefault();
});

/* ================= in-place text editing ================= */
function makeInput(x, y, w, h) {
  const inp = document.createElement("input");
  inp.type = "text"; inp.className = "inl"; inp.spellcheck = false; inp.autocomplete = "off";
  Object.assign(inp.style, { left: (x - 2) + "px", top: (y - 2) + "px", width: w + "px", height: (h + 4) + "px" });
  $("stage").appendChild(inp);
  inp.addEventListener("keydown", ev => {
    if (ev.key === "Enter") { ev.preventDefault(); commit(); }
    else if (ev.key === "Escape") { ev.preventDefault(); cancelEdit(); }
  });
  inp.addEventListener("blur", () => setTimeout(() => {
    const a = document.activeElement;
    if (S.ed && S.ed.input === inp && !(a && a.closest && a.closest(".fmt"))) commit();
  }, 0));
  return inp;
}
function startEdit(l) {
  if (busy()) return;
  cancelEdit();
  setFmt(l.size, l.bold, l.italic, toHex(l.color));
  const [x0, y0, x1, y1] = l.vb;
  const w = Math.max(120, Math.min(x1 - x0 + 60, $("stage").clientWidth - x0 - 4));
  const inp = makeInput(x0, y0, w, y1 - y0);
  S.ed = { kind: "edit", line: l, input: inp, family: familyOf(l), orig: { text: l.text, ...fmt() } };
  inp.value = l.text;
  styleInput();
  inp.focus(); inp.select();
}
function startAdd(x, y) {
  cancelEdit();
  const f = fmt();
  const inp = makeInput(x, y, 260, f.size * S.zoom * 1.35);
  S.ed = { kind: "add", x, y, input: inp, family: "Helvetica, Arial, sans-serif" };
  styleInput();
  inp.focus();
}
function cancelEdit() { if (S.ed) { const e = S.ed; S.ed = null; e.input.remove(); } }
function commit() {
  const e = S.ed;
  if (!e) return S.commitP || Promise.resolve();
  S.ed = null;
  S.commitP = doCommit(e);
  return S.commitP;
}
async function doCommit(e) {
  const text = e.input.value, f = fmt();
  e.input.remove();
  if (e.kind === "edit") {
    const o = e.orig;
    if (text === o.text && f.size === o.size && f.bold === o.bold && f.italic === o.italic && f.color === o.color) return;
    await pageOp("edit", { span: JSON.stringify(e.line), text, size: f.size, color: f.color, bold: +f.bold, italic: +f.italic });
  } else if (text.trim()) {
    await pageOp("addtext", { x: e.x, y: e.y, text, size: f.size, color: f.color, bold: +f.bold, italic: +f.italic });
  }
}

/* ================= running edits ================= */
async function pageOp(op, fields, files) {
  if (!S.bytes || busy()) return;
  setBusy(true);
  try {
    const pb = await extractPage(S.page);
    const r = await call(op, { ...fields, zoom: S.zoom }, pb, files);
    const out = new Uint8Array(await r.arrayBuffer());
    const nb = await swapPages(new Map([[S.page, out]]));
    await commitDoc(nb, [S.page]);
    await loadPage();
  } catch (e) { status(e.message, true); }
  finally { setBusy(false); refreshButtons(); }
}

async function batchOp(op, indexes, fieldsFor, label) {
  if (!S.bytes || busy()) return null;
  setBusy(true);
  try {
    const results = new Map();
    let count = 0, done = 0, next = 0;
    const worker = async () => {
      while (next < indexes.length) {
        const i = indexes[next++];
        const pb = await extractPage(i);
        const r = await call(op, fieldsFor(i), pb);
        if (r.status !== 204) {
          results.set(i, new Uint8Array(await r.arrayBuffer()));
          count += parseInt(r.headers.get("X-Count") || "1", 10) || 0;
        }
        done++;
        status(`${label} ${done}/${indexes.length}…`);
      }
    };
    await Promise.all([worker(), worker(), worker()]);
    if (results.size) {
      const nb = await swapPages(results);
      await commitDoc(nb, [...results.keys()]);
      await loadPage();
    }
    return { count, changed: results.size };
  } catch (e) { status(e.message, true); return null; }
  finally { setBusy(false); refreshButtons(); }
}
const allPages = () => Array.from({ length: S.pages }, (_, i) => i);

async function docOp(mutator) {          // structural page changes done locally with pdf-lib
  await commit();
  if (!S.bytes || busy()) return;
  setBusy(true);
  try {
    const doc = await L.PDFDocument.load(S.bytes, LOAD);
    const show = await mutator(doc);
    await commitDoc(await doc.save(), null);
    S.thumbs.clear();
    await syncCount();
    if (typeof show === "number") S.page = clamp(show, 0, S.pages - 1);
    buildSidebar();
    await loadPage();
  } catch (e) { status(e.message, true); }
  finally { setBusy(false); refreshButtons(); }
}
const rotateBy = d => docOp(doc => {
  const p = doc.getPage(S.page);
  p.setRotation(L.degrees((((p.getRotation().angle + d) % 360) + 360) % 360));
  return S.page;
});
const duplicatePage = () => docOp(async doc => {
  const [c] = await doc.copyPages(doc, [S.page]);
  doc.insertPage(S.page + 1, c);
  return S.page + 1;
});
const insertBlank = () => docOp(doc => {
  const { width, height } = doc.getPage(S.page).getSize();
  doc.insertPage(S.page + 1, [width, height]);
  return S.page + 1;
});
const deletePage = () => {
  if (S.pages <= 1) { status("A PDF needs at least one page.", true); return; }
  if (!confirm(`Delete page ${S.page + 1}?`)) return;
  docOp(doc => { doc.removePage(S.page); return Math.min(S.page, doc.getPageCount() - 1); });
};
const movePage = (from, to) => docOp(doc => {
  const pg = doc.getPage(from);
  doc.removePage(from);
  doc.insertPage(to, pg);
  return to;
});
async function mergeFile(file) {
  if (!file) return;
  let other;
  try { other = await L.PDFDocument.load(new Uint8Array(await file.arrayBuffer()), { updateMetadata: false }); }
  catch (e) { status(/encrypt/i.test(e.message || "") ? "That PDF is password-protected." : "Could not read that file as a PDF.", true); return; }
  await docOp(async doc => {
    const pages = await doc.copyPages(other, other.getPageIndices());
    pages.forEach(p => doc.addPage(p));
    return S.page;
  });
  status(`Merged ${file.name}`);
}

async function doUndo() {
  await commit();
  if (!S.bytes || busy() || !S.undo.length) return;
  S.redo.push(S.bytes); setBytes(S.undo.pop());
  await afterHistory();
}
async function doRedo() {
  await commit();
  if (!S.bytes || busy() || !S.redo.length) return;
  S.undo.push(S.bytes); setBytes(S.redo.pop());
  await afterHistory();
}
async function afterHistory() {
  setBusy(true);
  try { S.thumbs.clear(); await syncCount(); buildSidebar(); await loadPage(); }
  catch (e) { status(e.message, true); }
  finally { setBusy(false); refreshButtons(); }
}

/* ================= images ================= */
async function shrinkImage(file) {
  try {
    const bmp = await createImageBitmap(file);
    const sc = Math.min(1, 1600 / Math.max(bmp.width, bmp.height));
    const supported = file.type === "image/png" || file.type === "image/jpeg";
    if (sc === 1 && file.size < 700000 && supported) return file;
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(bmp.width * sc)); c.height = Math.max(1, Math.round(bmp.height * sc));
    c.getContext("2d").drawImage(bmp, 0, 0, c.width, c.height);
    const jpeg = file.type === "image/jpeg";
    const blob = await new Promise(res => c.toBlob(res, jpeg ? "image/jpeg" : "image/png", 0.9));
    return blob ? new File([blob], jpeg ? "image.jpg" : "image.png", { type: blob.type }) : file;
  } catch (_) { return file; }
}
$("imgfile").addEventListener("change", async e => {
  const f = e.target.files[0], rect = S.pendingRect;
  e.target.value = ""; S.pendingRect = null;
  if (!f || !rect) return;
  const img = await shrinkImage(f);
  pageOp("image", rect, { image: img });
});

/* ================= mouse: add text and drag tools ================= */
let drag = null;
$("stage").addEventListener("mousedown", ev => {
  if (!S.bytes || ev.button !== 0) return;
  if (S.ed) { if (ev.target !== S.ed.input) commit(); return; }
  if (busy() || ev.target.classList.contains("inl")) return;
  const r = $("stage").getBoundingClientRect();
  const x = ev.clientX - r.left, y = ev.clientY - r.top;
  if (S.mode === "addtext") { ev.preventDefault(); startAdd(x, y); }
  else if (DRAG_MODES.includes(S.mode)) {
    ev.preventDefault();
    const el = document.createElement("div");
    el.className = "rubber";
    $("stage").appendChild(el);
    drag = { x, y, el, mx: x, my: y };
  }
});
document.addEventListener("mousemove", ev => {
  if (!drag) return;
  const r = $("stage").getBoundingClientRect();
  drag.mx = clamp(ev.clientX - r.left, 0, r.width);
  drag.my = clamp(ev.clientY - r.top, 0, r.height);
  Object.assign(drag.el.style, { left: Math.min(drag.x, drag.mx) + "px", top: Math.min(drag.y, drag.my) + "px",
                                  width: Math.abs(drag.mx - drag.x) + "px", height: Math.abs(drag.my - drag.y) + "px" });
});
document.addEventListener("mouseup", () => {
  if (!drag) return;
  const d = drag; drag = null; d.el.remove();
  if (Math.abs(d.mx - d.x) < 4 || Math.abs(d.my - d.y) < 4) return;
  const rect = { x0: d.x, y0: d.y, x1: d.mx, y1: d.my };
  if (S.mode === "image") { S.pendingRect = rect; $("imgfile").click(); return; }   // must stay synchronous (user gesture)
  if (S.mode === "erase") pageOp("erase", rect);
  else pageOp("markup", { ...rect, kind: S.mode });
});

/* ================= toolbar wiring ================= */
document.querySelectorAll(".tool").forEach(b => b.addEventListener("click", async () => {
  await commit();
  S.mode = b.dataset.mode;
  document.querySelectorAll(".tool").forEach(x => x.classList.toggle("active", x === b));
  drawOverlays();
  status(HINTS[S.mode]);
}));

const guarded = fn => async () => { await commit(); if (S.bytes) try { await fn(); } catch (e) { status(e.message, true); } };
$("prev").onclick = guarded(() => goto(S.page - 1));
$("next").onclick = guarded(() => goto(S.page + 1));
const setZoom = async z => { S.zoom = clamp(Math.round(z * 100) / 100, MIN_Z, MAX_Z); refreshButtons(); await loadPage(); };
$("zin").onclick = guarded(() => setZoom(S.zoom * 1.25));
$("zout").onclick = guarded(() => setZoom(S.zoom / 1.25));
$("zfit").onclick = guarded(async () => setZoom(await fitZoom()));
$("rotl").onclick = () => rotateBy(-90);
$("rotr").onclick = () => rotateBy(90);
$("dup").onclick = duplicatePage;
$("blank").onclick = insertBlank;
$("delpg").onclick = deletePage;
$("up").onclick = () => movePage(S.page, S.page - 1);
$("down").onclick = () => movePage(S.page, S.page + 1);
$("merge").onclick = () => $("mergefile").click();
$("mergefile").addEventListener("change", e => { const f = e.target.files[0]; e.target.value = ""; mergeFile(f); });
$("undo").onclick = doUndo;
$("redo").onclick = doRedo;
$("sidebtn").onclick = () => document.body.classList.toggle("side-hidden");
if (innerWidth < 760) document.body.classList.add("side-hidden");

$("download").onclick = async () => {
  await commit();
  if (!S.bytes || busy()) return;
  setBusy(true);
  try {
    let out = S.bytes;
    if (out !== S.orig && out.length > S.base * 1.25 + 200000) { status("Optimising file…"); out = await compact(out); }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([out], { type: "application/pdf" }));
    a.download = S.name.replace(/\.pdf$/i, "") + (S.undo.length ? "-edited" : "") + ".pdf";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    status("Downloaded " + a.download);
  } catch (e) { status(e.message, true); }
  finally { setBusy(false); }
};

/* ================= dialogs ================= */
document.querySelectorAll("dialog [data-close]").forEach(b => b.onclick = () => b.closest("dialog").close());
const openDlg = async (id, focusId) => { await commit(); if (!S.bytes) return; $(id).showModal(); $(focusId).focus(); };
$("findbtn").onclick = () => openDlg("frdlg", "fr_old");
$("wmbtn").onclick = () => openDlg("wmdlg", "wm_text");
$("pnbtn").onclick = () => openDlg("pndlg", "pn_text");

$("frform").addEventListener("submit", async () => {
  const old = $("fr_old").value;
  if (!old) return;
  const idx = $("fr_scope").value === "page" ? [S.page] : allPages();
  const res = await batchOp("replace", idx, () => ({ old, new: $("fr_new").value }), "Replacing");
  if (res) status(res.count ? `Replaced ${res.count} occurrence(s)` : `"${old}" was not found`);
});
$("wmform").addEventListener("submit", async () => {
  const text = $("wm_text").value.trim();
  if (!text) return;
  const idx = $("wm_scope").value === "page" ? [S.page] : allPages();
  const fields = { text, size: $("wm_size").value, color: $("wm_col").value, opacity: (parseFloat($("wm_op").value) || 25) / 100 };
  const res = await batchOp("watermark", idx, () => fields, "Watermarking");
  if (res) status(`Watermark added to ${res.changed} page(s)`);
});
$("pnform").addEventListener("submit", async () => {
  const tpl = $("pn_text").value || "{n}", start = parseInt($("pn_start").value, 10) || 1;
  const res = await batchOp("pagenum", allPages(), i => ({
    text: tpl.split("{n}").join(String(start + i)).split("{total}").join(String(S.pages)),
    size: $("pn_size").value, pos: $("pn_pos").value,
  }), "Numbering");
  if (res) status(`Page numbers added to ${res.changed} page(s)`);
});

/* ================= open: button, drag and drop, shortcuts ================= */
$("file").addEventListener("change", e => { const f = e.target.files[0]; e.target.value = ""; openFile(f); });
window.addEventListener("dragover", e => e.preventDefault());
window.addEventListener("drop", e => {
  e.preventDefault();
  const f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
  if (f) openFile(f);
});
window.addEventListener("keydown", e => {
  if (S.ed || document.querySelector("dialog[open]")) return;
  if (e.ctrlKey || e.metaKey) {
    const k = e.key.toLowerCase();
    if (k === "z") { e.preventDefault(); doUndo(); }
    else if (k === "y") { e.preventDefault(); doRedo(); }
    else if (k === "s") { e.preventDefault(); $("download").click(); }
  } else if (e.key === "PageDown") { e.preventDefault(); $("next").click(); }
  else if (e.key === "PageUp") { e.preventDefault(); $("prev").click(); }
});
window.addEventListener("beforeunload", e => { if (S.undo.length) { e.preventDefault(); e.returnValue = ""; } });
if (!L) status("The pdf-lib library did not load (blocked network?). Reload the page.", true);
refreshButtons();
</script>
</body>
</html>
'''
