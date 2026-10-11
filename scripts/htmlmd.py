"""Minimal, faithful HTML -> Markdown conversion for LEGI article contents."""
import re

import lxml.html
from lxml import etree

WS = re.compile(r"[ \t\r\n ]+")
INLINE_TAGS = {"b", "strong", "i", "em", "u", "sup", "sub", "a", "span", "font", "small", "big", "img", "abbr", "s", "strike", "code", "tt"}
BLOCK_TAGS = {"p", "div", "center", "blockquote", "table", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "dl", "dt", "dd", "hr"}


def esc(s):
    s = s.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").replace("`", "\\`")
    s = re.sub(r"<(?=[A-Za-z/!?])", "&lt;", s)
    return s


def inline(el, html_mode=False):
    """Render the inline content of el (its text and children) as one string; <br> -> hard break."""
    out = [esc(el.text or "") if not html_mode else _h(el.text or "")]
    for c in el:
        tag = c.tag if isinstance(c.tag, str) else ""
        tag = tag.lower()
        if tag == "br":
            out.append("\x00BR\x00")
        elif tag in ("b", "strong"):
            s = inline(c, html_mode).strip()
            out.append((f"<b>{s}</b>" if html_mode else f"**{s}**") if s else "")
        elif tag in ("i", "em"):
            s = inline(c, html_mode).strip()
            out.append((f"<i>{s}</i>" if html_mode else f"*{s}*") if s else "")
        elif tag in ("sup", "sub"):
            out.append(f"<{tag}>{inline(c, html_mode)}</{tag}>")
        elif tag == "img":
            alt = c.get("alt") or ""
            out.append(esc(alt) if alt else "")
        elif tag in BLOCK_TAGS:
            out.append("\x00BR\x00" + inline(c, html_mode) + "\x00BR\x00")
        elif tag:
            out.append(inline(c, html_mode))
        out.append(esc(c.tail or "") if not html_mode else _h(c.tail or ""))
    return "".join(out)


def _h(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def finish_inline(s, br):
    s = WS.sub(" ", s)
    parts = [p.strip() for p in s.split("\x00BR\x00")]
    # drop leading/trailing empty segments, collapse runs of empties
    res = []
    for p in parts:
        if p == "" and (not res or res[-1] == ""):
            continue
        res.append(p)
    while res and res[-1] == "":
        res.pop()
    return br.join(p for p in res if p != "")


def has_block(el):
    return any(isinstance(c.tag, str) and c.tag.lower() in BLOCK_TAGS for c in el.iter() if c is not el)


def table_md(tbl):
    rows = [r for r in tbl.iter("tr")]
    if not rows:
        return ""
    complex_ = False
    grid = []
    for r in rows:
        cells = [c for c in r if isinstance(c.tag, str) and c.tag.lower() in ("td", "th")]
        for c in cells:
            if int(c.get("rowspan", "1") or 1) > 1 or int(c.get("colspan", "1") or 1) > 1:
                complex_ = True
            if any(isinstance(x.tag, str) and x.tag.lower() == "table" for x in c.iter() if x is not c):
                complex_ = True
        grid.append(cells)
    widths = {len(g) for g in grid if g}
    if len(widths) > 1:
        complex_ = True
    if not complex_ and grid and grid[0]:
        lines = []
        for i, cells in enumerate(grid):
            vals = [finish_inline(inline(c), "<br>").replace("|", "\\|") for c in cells]
            lines.append("| " + " | ".join(vals) + " |")
            if i == 0:
                lines.append("|" + "|".join(["---"] * len(cells)) + "|")
        return "\n".join(lines)
    # complex: cleaned HTML table
    out = ["<table>"]
    for cells in grid:
        out.append("<tr>")
        for c in cells:
            tag = c.tag.lower()
            attrs = ""
            for a in ("rowspan", "colspan"):
                v = c.get(a)
                if v and v != "1":
                    attrs += f' {a}="{v}"'
            out.append(f"<{tag}{attrs}>{finish_inline(inline(c, html_mode=True), '<br>')}</{tag}>")
        out.append("</tr>")
    out.append("</table>")
    return "\n".join(out)


def blocks(el, out, prefix=""):
    """Append markdown blocks for el's content to out."""
    buf = [el.text or ""]
    pending = []  # inline pieces accumulated

    def flush():
        if not pending:
            return
        tmp = etree.Element("x")
        # rebuild a temporary element from pending (text and inline elements)
        last = None
        for p in pending:
            if isinstance(p, str):
                if last is None:
                    tmp.text = (tmp.text or "") + p
                else:
                    last.tail = (last.tail or "") + p
            else:
                tmp.append(p)
                last = p
        s = finish_inline(inline(tmp), "\\\n")
        if s:
            out.append(s)
        pending.clear()

    if el.text:
        pending.append(el.text)
    for c in list(el):
        tail = c.tail
        tag = c.tag.lower() if isinstance(c.tag, str) else ""
        if tag in BLOCK_TAGS:
            flush()
            if tag == "table":
                t = table_md(c)
                if t:
                    out.append(t)
            elif tag in ("ul", "ol"):
                n = 0
                for li in c:
                    if not isinstance(li.tag, str):
                        continue
                    n += 1
                    sub = []
                    blocks(li, sub)
                    if sub:
                        mark = f"{n}. " if tag == "ol" else "- "
                        txt = "\n\n".join(sub).replace("\n", "\n   ")
                        out.append(mark + txt)
            elif tag == "hr":
                out.append("---")
            elif tag in ("h1", "h2", "h3", "h4", "h5", "h6", "dt"):
                s = finish_inline(inline(c), " ")
                if s:
                    out.append(f"**{s}**")
            elif tag == "blockquote":
                sub = []
                blocks(c, sub)
                if sub:
                    out.append("\n".join("> " + l if l else ">" for l in "\n\n".join(sub).split("\n")))
            else:
                if has_block(c):
                    blocks(c, out)
                else:
                    s = finish_inline(inline(c), "\\\n")
                    if s:
                        out.append(s)
            c.tail = None
            if tail:
                pending.append(tail)
        else:
            c.tail = None
            pending.append(c)
            if tail:
                pending.append(tail)
    flush()


def html_to_md(html):
    if not html or not html.strip():
        return ""
    try:
        frag = lxml.html.fragment_fromstring(html, create_parent="div")
    except (etree.ParserError, ValueError):
        return esc(WS.sub(" ", re.sub(r"<[^>]+>", " ", html))).strip()
    out = []
    blocks(frag, out)
    text = "\n\n".join(o for o in out if o.strip())
    return text.strip()
