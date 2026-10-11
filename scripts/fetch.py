#!/usr/bin/env python3
"""Download the DILA LEGI open-data dump (latest global + all later daily increments).

Usage: python fetch.py [RAW_DIR]
Default RAW_DIR: ../../_raw/fr/dl (relative to this script).
Files already present with the expected size are skipped (cache).
"""
import os
import re
import sys
import time

import requests

BASE = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "_raw", "fr", "dl")

S = requests.Session()
S.headers["User-Agent"] = UA


def get(url, **kw):
    for attempt in range(6):
        try:
            r = S.get(url, timeout=120, **kw)
            if r.status_code == 200:
                return r
            print(f"HTTP {r.status_code} for {url}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"error {e} for {url}", file=sys.stderr)
        time.sleep(2 ** attempt)
    raise RuntimeError(f"failed: {url}")


def listing():
    html = get(BASE).text
    names = re.findall(r'href="((?:Freemium_legi_global|LEGI)_\d{8}-\d{6}\.tar\.gz)"', html)
    glob = sorted(n for n in names if n.startswith("Freemium"))
    if not glob:
        raise RuntimeError("no global dump found")
    g = glob[-1]
    gstamp = re.search(r"(\d{8}-\d{6})", g).group(1)
    incs = sorted(n for n in set(names) if n.startswith("LEGI_") and re.search(r"(\d{8}-\d{6})", n).group(1) > gstamp)
    return g, incs


def head_size(name):
    for attempt in range(8):
        try:
            r = S.head(BASE + name, timeout=60)
            if r.status_code == 200:
                return int(r.headers.get("Content-Length", -1))
        except requests.RequestException as e:
            print(f"HEAD retry {name}: {e}", file=sys.stderr)
        time.sleep(2 ** attempt)
    raise RuntimeError(f"HEAD failed: {name}")


def download(name):
    dest = os.path.join(RAW, name)
    size = head_size(name)
    if os.path.exists(dest) and os.path.getsize(dest) == size:
        return dest
    tmp = dest + ".part"
    have = os.path.getsize(tmp) if os.path.exists(tmp) else 0
    headers = {"Range": f"bytes={have}-"} if have else {}
    for attempt in range(8):
        try:
            with S.get(BASE + name, headers=headers, stream=True, timeout=120) as r:
                if r.status_code not in (200, 206):
                    raise requests.RequestException(f"HTTP {r.status_code}")
                mode = "ab" if r.status_code == 206 else "wb"
                with open(tmp, mode) as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
            break
        except requests.RequestException as e:
            print(f"retry {name}: {e}", file=sys.stderr)
            time.sleep(2 ** attempt)
            have = os.path.getsize(tmp) if os.path.exists(tmp) else 0
            headers = {"Range": f"bytes={have}-"} if have else {}
    os.replace(tmp, dest)
    print("downloaded", name, flush=True)
    time.sleep(0.5)
    return dest


CHUNK = 64 << 20  # ranged pieces for the large global archive


def fetch_range(name, idx, start, end):
    """Download bytes [start, end] of `name` into a piece file (resumable)."""
    piece = os.path.join(RAW, f"{name}.p{idx:04d}")
    want = end - start + 1
    for attempt in range(10):
        have = os.path.getsize(piece) if os.path.exists(piece) else 0
        if have >= want:
            return piece
        try:
            with S.get(BASE + name, headers={"Range": f"bytes={start + have}-{end}"}, stream=True, timeout=120) as r:
                if r.status_code != 206:
                    raise requests.RequestException(f"HTTP {r.status_code}")
                with open(piece, "ab") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
        except requests.RequestException as e:
            print(f"retry {name} piece {idx}: {e}", file=sys.stderr)
            time.sleep(2 ** min(attempt, 6))
    if os.path.getsize(piece) < want:
        raise RuntimeError(f"piece {idx} of {name} incomplete")
    return piece


def main():
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(RAW, exist_ok=True)
    g, incs = listing()
    print(f"global: {g}; {len(incs)} increments", flush=True)
    gdest = os.path.join(RAW, g)
    size = head_size(g)
    with ThreadPoolExecutor(max_workers=4) as ex:  # politeness: <= 4 connections
        futs = []
        if not (os.path.exists(gdest) and os.path.getsize(gdest) == size):
            ranges = [(i, a, min(a + CHUNK, size) - 1) for i, a in enumerate(range(0, size, CHUNK))]
            futs_g = [ex.submit(fetch_range, g, *r) for r in ranges]
        else:
            futs_g = []
        futs = [ex.submit(download, n) for n in incs]
        pieces = [f.result() for f in futs_g]
        if pieces:
            with open(gdest + ".part", "wb") as out:
                for p in pieces:
                    with open(p, "rb") as f:
                        while True:
                            b = f.read(1 << 24)
                            if not b:
                                break
                            out.write(b)
            os.replace(gdest + ".part", gdest)
            for p in pieces:
                os.remove(p)
            print("assembled", g, flush=True)
        failed = []
        for n, f in zip(incs, futs):
            try:
                f.result()
            except Exception as e:  # keep going; a re-run fetches what is missing
                failed.append(n)
                print(f"FAILED {n}: {e}", file=sys.stderr)
        if failed:
            raise SystemExit(f"{len(failed)} downloads failed; re-run fetch.py")
    with open(os.path.join(RAW, "manifest.txt"), "w") as f:
        f.write("\n".join([g] + incs) + "\n")


if __name__ == "__main__":
    main()
