#!/usr/bin/env python3
"""Stream the LEGI tarballs (global dump + daily increments, in order) into a SQLite DB.

Nothing is extracted to disk: each tar member is parsed on the fly.
Only the `code_et_TNC_en_vigueur` part of the dump is kept (texts currently in force).
Articles/sections of excluded natures (ARRETE, ...) are not stored, to keep the DB small.

Usage: python ingest.py RAW_DL_DIR DB_PATH [ARCHIVE_NAME ...]
(default: all archives listed in RAW_DL_DIR/manifest.txt, written by fetch.py)
"""
import os
import re
import sqlite3
import sys
import tarfile

from lxml import etree

# natures whose sections/articles we store (text metadata is stored for every nature)
SKIP_BODY_NATURES = {"ARRETE", "CIRCULAIRE", "DECISION", "DELIBERATION", "AVIS", "INSTRUCTION", "NOTE", "INSTRUCTIONINTERMINISTERIELLE"}
KEEP_ART_ETATS = {"VIGUEUR", "VIGUEUR_DIFF", "ABROGE_DIFF"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS done(archive TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS textv(id TEXT PRIMARY KEY, cid TEXT, nature TEXT, num TEXT, nor TEXT, titre TEXT, titrefull TEXT,
  etat TEXT, date_debut TEXT, date_fin TEXT, date_texte TEXT, date_publi TEXT, dern_modif TEXT, cat TEXT,
  visas TEXT, signataires TEXT, nota TEXT, tp TEXT);
CREATE TABLE IF NOT EXISTS texts(id TEXT PRIMARY KEY, struct TEXT);
CREATE TABLE IF NOT EXISTS section(id TEXT PRIMARY KEY, titre TEXT, struct TEXT);
CREATE TABLE IF NOT EXISTS article(id TEXT PRIMARY KEY, num TEXT, etat TEXT, debut TEXT, fin TEXT, nature TEXT, cid TEXT,
  contenu TEXT, nota TEXT);
"""

ID_RE = re.compile(r"(LEGI(?:TEXT|SCTA|ARTI)\d{12})")


def inner(el):
    """Serialized inner XML/HTML of an element (text + children)."""
    if el is None:
        return ""
    parts = [el.text or ""]
    for c in el:
        parts.append(etree.tostring(c, encoding="unicode", with_tail=True))
    return "".join(parts).strip()


def t(root, path):
    el = root.find(path)
    return (el.text or "").strip() if el is not None and el.text else ""


def handle(db, name, data):
    if "/code_et_TNC_non_vigueur/" in name:
        m = ID_RE.search(os.path.basename(name))
        if m and "/texte/version/" in name:
            # text left the in-force set
            db.execute("DELETE FROM textv WHERE id=?", (m.group(1),))
            db.execute("DELETE FROM texts WHERE id=?", (m.group(1),))
        return
    if "/code_et_TNC_en_vigueur/" not in name or not name.endswith(".xml"):
        return
    try:
        root = etree.fromstring(data)
    except etree.XMLSyntaxError as e:
        print("XML error", name, e, file=sys.stderr)
        return
    tag = root.tag
    if tag == "ARTICLE":
        aid = t(root, "META/META_COMMUN/ID")
        etat = t(root, "META/META_SPEC/META_ARTICLE/ETAT")
        txt = root.find("CONTEXTE/TEXTE")
        nature = txt.get("nature", "") if txt is not None else ""
        if etat not in KEEP_ART_ETATS or nature.upper() in SKIP_BODY_NATURES:
            db.execute("DELETE FROM article WHERE id=?", (aid,))
            return
        db.execute("INSERT OR REPLACE INTO article VALUES(?,?,?,?,?,?,?,?,?)", (
            aid, t(root, "META/META_SPEC/META_ARTICLE/NUM"), etat,
            t(root, "META/META_SPEC/META_ARTICLE/DATE_DEBUT"), t(root, "META/META_SPEC/META_ARTICLE/DATE_FIN"),
            nature, txt.get("cid", "") if txt is not None else "",
            inner(root.find("BLOC_TEXTUEL/CONTENU")), inner(root.find("NOTA/CONTENU"))))
    elif tag == "SECTION_TA":
        txt = root.find("CONTEXTE/TEXTE")
        nature = txt.get("nature", "") if txt is not None else ""
        if nature.upper() in SKIP_BODY_NATURES:
            return
        st = root.find("STRUCTURE_TA")
        db.execute("INSERT OR REPLACE INTO section VALUES(?,?,?)", (
            t(root, "ID"), t(root, "TITRE_TA"), etree.tostring(st, encoding="unicode") if st is not None else ""))
    elif tag == "TEXTELR":
        st = root.find("STRUCT")
        db.execute("INSERT OR REPLACE INTO texts VALUES(?,?)", (
            t(root, "META/META_COMMUN/ID"), etree.tostring(st, encoding="unicode") if st is not None else ""))
    elif tag == "TEXTE_VERSION":
        c = "META/META_SPEC/META_TEXTE_CHRONICLE/"
        v = "META/META_SPEC/META_TEXTE_VERSION/"
        cat = "code" if "/code_en_vigueur/" in name else "tnc"
        db.execute("INSERT OR REPLACE INTO textv VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            t(root, "META/META_COMMUN/ID"), t(root, c + "CID"), t(root, "META/META_COMMUN/NATURE"), t(root, c + "NUM"),
            t(root, c + "NOR"), t(root, v + "TITRE"), t(root, v + "TITREFULL"), t(root, v + "ETAT"),
            t(root, v + "DATE_DEBUT"), t(root, v + "DATE_FIN"), t(root, c + "DATE_TEXTE"), t(root, c + "DATE_PUBLI"),
            t(root, c + "DERNIERE_MODIFICATION"), cat,
            inner(root.find("VISAS/CONTENU")), inner(root.find("SIGNATAIRES/CONTENU")),
            inner(root.find("NOTA/CONTENU")), inner(root.find("TP/CONTENU"))))


def suppress(db, data):
    for line in data.decode("utf-8", "replace").splitlines():
        line = line.strip().rstrip("/")
        if "/code_et_TNC_en_vigueur/" not in "/" + line:
            continue  # we never store non-in-force paths
        last = line.rsplit("/", 1)[-1]
        if re.fullmatch(r"(JORF|LEGI)TEXT\d{12}", last) and not ID_RE.fullmatch(last.replace(".xml", "")):
            # a whole JORFTEXT directory removed
            db.execute("DELETE FROM texts WHERE id IN (SELECT id FROM textv WHERE cid=?)", (last,))
            db.execute("DELETE FROM textv WHERE cid=?", (last,))
            continue
        m = ID_RE.search(last)
        if not m:
            continue
        i = m.group(1)
        if "TEXT" in i:
            db.execute("DELETE FROM textv WHERE id=?", (i,))
            db.execute("DELETE FROM texts WHERE id=?", (i,))
        elif "SCTA" in i:
            db.execute("DELETE FROM section WHERE id=?", (i,))
        else:
            db.execute("DELETE FROM article WHERE id=?", (i,))


class PieceReader:
    """Read a file being downloaded as ranged pieces (NAME.pNNNN, see fetch.py) in order, waiting for each."""

    def __init__(self, path, total, chunk=64 << 20):
        self.path, self.total, self.chunk = path, total, chunk
        self.npieces = (total + chunk - 1) // chunk
        self.i = 0
        self.f = None

    def _open_next(self):
        import time
        want = min(self.chunk, self.total - self.i * self.chunk)
        p = f"{self.path}.p{self.i:04d}"
        while True:
            if os.path.exists(self.path) and os.path.getsize(self.path) == self.total:
                f = open(self.path, "rb")
                f.seek(self.i * self.chunk)
                return f
            try:
                if os.path.getsize(p) >= want:
                    return open(p, "rb")
            except OSError:
                pass
            time.sleep(10)

    def read(self, n=-1):
        out = b""
        while n < 0 or len(out) < n:
            if self.f is None:
                if self.i >= self.npieces:
                    break
                self.f = self._open_next()
                self.left = min(self.chunk, self.total - self.i * self.chunk)
            b = self.f.read(min(self.left, (n - len(out)) if n >= 0 else self.left))
            self.left -= len(b)
            out += b
            if self.left == 0 or not b:
                self.f.close()
                self.f = None
                self.i += 1
        return out


def open_archive(path):
    if os.path.exists(path):
        return tarfile.open(path, "r|gz")
    total = int(os.environ.get("LEGI_GLOBAL_SIZE", "0"))
    if os.path.exists(path + ".p0000") and total:
        return tarfile.open(fileobj=PieceReader(path, total), mode="r|gz")
    raise FileNotFoundError(path)


def ingest(db, path):
    n = 0
    with open_archive(path) as tf:
        for m in tf:
            if not m.isfile():
                continue
            f = tf.extractfile(m)
            data = f.read()
            if m.name.endswith("liste_suppression_legi.dat"):
                suppress(db, data)
            else:
                handle(db, m.name, data)
            n += 1
            if n % 200000 == 0:
                print(f"  {n} members", flush=True)
                db.commit()
    return n


def main():
    raw, dbp = sys.argv[1], sys.argv[2]
    db = sqlite3.connect(dbp)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=OFF")
    db.executescript(SCHEMA)
    if len(sys.argv) > 3:
        names = sys.argv[3:]
    else:
        names = [l.strip() for l in open(os.path.join(raw, "manifest.txt")) if l.strip()]
    for name in names:  # manifest order: global first, then increments chronologically
        if db.execute("SELECT 1 FROM done WHERE archive=?", (name,)).fetchone():
            continue
        print("ingest", name, flush=True)
        n = ingest(db, os.path.join(raw, name))
        db.execute("INSERT INTO done VALUES(?)", (name,))
        db.commit()
        print(f"  done {n} members", flush=True)


if __name__ == "__main__":
    main()
