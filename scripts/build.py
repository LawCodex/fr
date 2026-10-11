#!/usr/bin/env python3
"""Generate the Markdown corpus from the SQLite DB built by ingest.py.

Usage: python build.py DB_PATH OUT_DIR [--date YYYY-MM-DD] [--only constitution,codes,lois,ordonnances,decrets]

The consolidation date (default: today) selects, for every structure link (section or article),
the version whose [debut, fin) interval contains that date.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict

from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from htmlmd import html_to_md  # noqa: E402

MAX_FILE = 4 * 1024 * 1024        # a code larger than this is split into one file per top-level part
MAX_PART = 12 * 1024 * 1024       # a part larger than this is split again, one level down
IN_FORCE_TEXT_ETATS = ("VIGUEUR", "ABROGE_DIFF")

# official texts of constitutional value, all LEGI nature CONSTITUTION
CATEGORIES = {
    "CONSTITUTION": "constitution",
    "CODE": "codes",
    "LOI": "lois",
    "LOI_ORGANIQUE": "lois",
    "LOI_CONSTIT": "constitution",
    "DECLARATION": "constitution",
    "LOI_PROGRAMME": "lois",
    "ORDONNANCE": "ordonnances",
    "DECRET": "decrets",
    "DECRET_LOI": "decrets-lois",
}
TYPES = {"CONSTITUTION": "constitution", "CODE": "code", "LOI": "act", "LOI_ORGANIQUE": "organic-act",
         "LOI_CONSTIT": "constitutional-act", "DECLARATION": "constitution", "LOI_PROGRAMME": "act", "ORDONNANCE": "ordinance",
         "DECRET": "decree", "DECRET_LOI": "decree-law"}


def slugify(s, maxlen=90):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if len(s) > maxlen:
        s = s[:maxlen].rsplit("-", 1)[0]
    return s or "sans-titre"


def yq(s):
    return json.dumps(s or "", ensure_ascii=False)


def valid_date(d):
    return d if d and re.match(r"^\d{4}-\d{2}-\d{2}$", d) and not d.startswith("2999") else ""


class Builder:
    def __init__(self, db, today):
        self.db = db
        self.today = today
        self.sec_cache = {}
        self.stats = Counter()

    def in_window(self, debut, fin):
        debut = debut or "0000"
        fin = fin or "2999-01-01"
        return debut <= self.today < fin

    def article(self, aid):
        r = self.db.execute("SELECT num, etat, debut, fin, contenu, nota FROM article WHERE id=?", (aid,)).fetchone()
        if not r:
            return None
        num, etat, debut, fin, contenu, nota = r
        if not self.in_window(debut, fin):
            return None
        return num, contenu, nota

    def section(self, sid):
        r = self.db.execute("SELECT titre, struct FROM section WHERE id=?", (sid,)).fetchone()
        return r

    def tree(self, struct_xml, seen=None):
        """Build a tree of in-force nodes: list of ('sec', title, id, children) / ('art', num, id, md)."""
        if not struct_xml:
            return []
        seen = seen or set()
        root = etree.fromstring(struct_xml)
        nodes = []
        for el in root:
            if not isinstance(el.tag, str):
                continue
            if not self.in_window(el.get("debut"), el.get("fin")):
                continue
            i = el.get("id")
            if el.tag == "LIEN_SECTION_TA":
                if i in seen:
                    continue
                s = self.section(i)
                if not s:
                    self.stats["missing_section"] += 1
                    continue
                kids = self.tree(s[1], seen | {i})
                if kids:
                    nodes.append(("sec", s[0] or (el.text or "").strip(), i, kids))
            elif el.tag == "LIEN_ART":
                a = self.article(i)
                if not a:
                    self.stats["missing_article"] += 1
                    continue
                num, contenu, nota = a
                body = html_to_md(contenu)
                nota_md = html_to_md(nota)
                nodes.append(("art", num or el.get("num") or "", i, (body, nota_md)))
        return nodes

    @staticmethod
    def count_articles(nodes):
        n = 0
        for nd in nodes:
            n += 1 if nd[0] == "art" else Builder.count_articles(nd[3])
        return n


def art_label(num):
    num = (num or "").strip()
    if not num:
        return "Article"
    low = num.lower()
    if re.match(r"^(annexe|tableau|etat|état|article|préambule|preambule|titre|chapitre|section|liste|appendice)", low):
        return num
    return f"Article {num}"


def render(nodes, level, out):
    for nd in nodes:
        if nd[0] == "sec":
            title = re.sub(r"\s+", " ", nd[1]).strip()
            out.append(("#" * level + " " + title) if level <= 6 else f"**{title}**")
            out.append("")
            render(nd[3], level + 1, out)
        else:
            label = art_label(nd[1])
            out.append(("#" * level + " " + label) if level <= 6 else f"**{label}**")
            out.append("")
            body, nota = nd[3]
            if body:
                out.append(body)
                out.append("")
            if nota:
                q = "\n".join("> " + l if l else ">" for l in ("**Nota :** " + nota).split("\n"))
                out.append(q)
                out.append("")


def front_matter(meta):
    lines = ["---"]
    for k, v in meta.items():
        if v is None or v == "":
            continue
        lines.append(f"{k}: {v if k in ('date', 'last_amended', 'retrieved', 'consolidated') or re.match(r'^[a-z_-]+$', str(v)) else yq(v)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.rstrip("\n") + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("out")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--retrieved", default=dt.date.today().isoformat())
    ap.add_argument("--only", default="constitution,codes,lois,ordonnances,decrets,decrets-lois")
    args = ap.parse_args()
    only = set(args.only.split(","))
    db = sqlite3.connect(args.db)
    b = Builder(db, args.date)

    # pick one in-force LEGITEXT per CID
    rows = db.execute("SELECT id, cid, nature, num, nor, titre, titrefull, etat, date_debut, date_fin, date_texte, date_publi, "
                      "dern_modif, cat, visas, signataires, nota FROM textv").fetchall()
    by_cid = defaultdict(list)
    nat_all = Counter()
    for r in rows:
        if r[7] in IN_FORCE_TEXT_ETATS:
            by_cid[r[1] or r[0]].append(r)
            nat_all[r[2]] += 1
    chosen = []
    for cid, rs in by_cid.items():
        rs.sort(key=lambda r: (r[8] or "") <= args.date and (r[8] or ""), reverse=True)
        chosen.append(rs[0])

    for cat in only:
        d = os.path.join(args.out, cat)
        if os.path.isdir(d):
            shutil.rmtree(d)

    counts = Counter()
    art_counts = Counter()
    skipped_empty = Counter()
    used = set()
    manifest = []
    os.makedirs(os.path.join(args.out, "scripts"), exist_ok=True)
    # GitHub's web UI lists at most 1,000 entries per directory: years with more texts get month subdirs
    year_load = Counter()
    for r in chosen:
        c = CATEGORIES.get((r[2] or "").upper())
        if c and c not in ("codes", "constitution"):
            year_load[(c, (valid_date(r[10]) or valid_date(r[11]) or "0000")[:4])] += 1
    for r in sorted(chosen, key=lambda r: r[0]):
        (tid, cid, nature, num, nor, titre, titrefull, etat, ddeb, dfin, dtexte, dpubli, dmod, cat, visas, sign, nota) = r
        nature = (nature or "").upper()
        catdir = CATEGORIES.get(nature)
        if not catdir or catdir not in only:
            continue
        srow = db.execute("SELECT struct FROM texts WHERE id=?", (tid,)).fetchone()
        nodes = b.tree(srow[0] if srow else "")
        if not nodes:
            skipped_empty[nature] += 1
            continue
        title = re.sub(r"\s+", " ", (titrefull or titre or tid)).strip()
        # strip trailing "(1)" footnote markers in titles
        title = re.sub(r"\s*\(\d\)\s*$", "", title)
        date = valid_date(dtexte) or valid_date(dpubli)
        src = (f"https://www.legifrance.gouv.fr/codes/texte_lc/{tid}" if nature == "CODE"
               else f"https://www.legifrance.gouv.fr/loda/id/{tid}")
        meta = {
            "title": title, "identifier": tid, "cid": cid, "nature": nature,
            "number": num or "", "nor": nor or "",
            "type": TYPES.get(nature, "other"), "jurisdiction": "fr", "language": "fr",
            "date": date, "last_amended": valid_date(dmod), "consolidated": args.date,
            "status": "in_force", "source": src, "retrieved": args.retrieved,
        }
        nart = Builder.count_articles(nodes)
        counts[catdir if nature != "LOI_ORGANIQUE" else "lois (organiques)"] += 1
        art_counts[catdir] += nart

        head = []
        if visas:
            v = html_to_md(visas)
            if v:
                head += [v, ""]
        tail = []
        if sign:
            s = html_to_md(sign)
            if s:
                tail += ["", "---", "", s]
        if nota:
            n = html_to_md(nota)
            if n:
                tail += ["", "> " + "\n> ".join(("**Nota :** " + n).split("\n"))]

        if catdir == "constitution" and nature == "LOI_CONSTIT":
            rel = os.path.join("constitution", "lois-constitutionnelles", slugify(title, 95))
        elif catdir == "constitution":
            base = slugify(titre or title, 80)
            rel = os.path.join("constitution", base)
        elif catdir == "codes":
            base = slugify(titre or title, 90)
            rel = os.path.join("codes", base)
        else:
            year = (date or "0000")[:4]
            base = slugify(title, 95)
            if year_load[(catdir, year)] > 900:
                rel = os.path.join(catdir, year, (date or "0000-00")[5:7], base)
            else:
                rel = os.path.join(catdir, year, base)
        if rel in used:
            rel = rel + "-" + tid[-8:].lower()
        used.add(rel)

        body = []
        render(nodes, 2, body)
        full = front_matter(meta) + f"# {title}\n\n" + "\n".join(head + body) + "\n".join(tail)
        if catdir == "codes" and len(full.encode()) > MAX_FILE:
            split_code(args.out, rel, meta, title, nodes)
            manifest.append((catdir, rel + "/", tid, nart))
        else:
            write(os.path.join(args.out, rel + ".md"), full)
            manifest.append((catdir, rel + ".md", tid, nart))

    with open(os.path.join(args.out, "scripts", f"manifest-{'-'.join(sorted(only))}.tsv"), "w") as f:
        for m in manifest:
            f.write("\t".join(map(str, m)) + "\n")
    stats = {"date": args.date, "texts": dict(counts), "articles": dict(art_counts),
             "skipped_no_in_force_articles": dict(skipped_empty), "in_force_texts_by_nature": dict(nat_all),
             "missing": dict(b.stats)}
    with open(os.path.join(args.out, "scripts", f"stats-{'-'.join(sorted(only))}.json"), "w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(stats, ensure_ascii=False, indent=1))


def split_code(outdir, rel, meta, title, nodes, level=2, toc_title=None):
    """Write a directory: index.md (front matter + table of contents) + one file per top-level node."""
    d = os.path.join(outdir, rel)
    idx = [front_matter(meta) + f"# {toc_title or title}\n"]
    loose = [n for n in nodes if n[0] == "art"]
    i = 0
    pending_loose = []
    for nd in nodes:
        if nd[0] == "art":
            pending_loose.append(nd)
            continue
        if pending_loose:
            i += 1
            fn = f"{i:02d}-articles"
            write_part(d, fn, meta, title, "Articles", pending_loose, level)
            idx.append(f"- [Articles]({fn}.md)")
            pending_loose = []
        i += 1
        stitle = re.sub(r"\s+", " ", nd[1]).strip()
        fn = f"{i:02d}-" + slugify(stitle, 70)
        part = []
        render([nd], level, part)
        txt = "\n".join(part)
        pmeta = dict(meta, title=f"{title} — {stitle}")
        if len(txt.encode()) > MAX_PART and any(k[0] == "sec" for k in nd[3]):
            split_code(outdir, os.path.join(rel, fn), pmeta, title, nd[3], level, toc_title=f"{title} — {stitle}")
            idx.append(f"- [{stitle}]({fn}/index.md)")
        else:
            write(os.path.join(d, fn + ".md"), front_matter(pmeta) + f"# {title} — {stitle}\n\n" + txt)
            idx.append(f"- [{stitle}]({fn}.md)")
    if pending_loose:
        i += 1
        fn = f"{i:02d}-articles"
        write_part(d, fn, meta, title, "Articles", pending_loose, level)
        idx.append(f"- [Articles]({fn}.md)")
    write(os.path.join(d, "index.md"), "\n".join(idx))


def write_part(d, fn, meta, title, stitle, nodes, level):
    part = []
    render(nodes, level, part)
    pmeta = dict(meta, title=f"{title} — {stitle}")
    write(os.path.join(d, fn + ".md"), front_matter(pmeta) + f"# {title} — {stitle}\n\n" + "\n".join(part))


if __name__ == "__main__":
    main()
