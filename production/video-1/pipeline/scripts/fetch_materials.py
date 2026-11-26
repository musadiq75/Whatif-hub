#!/usr/bin/env python3
"""Fetch ordered stock clips for Video 1 from Pexels and/or Pixabay (both free).

Usage:
  export PEXELS_API_KEY=...        # free key from pexels.com/api
  export PIXABAY_API_KEY=...       # optional fallback
  python3 fetch_materials.py scenes.json --out-dir ../materials

Output:
  ../materials/01_midnight_street.mp4 ... (numbered in storyboard order)
  ../materials/ATTRIBUTION.md  (required by Pexels/Pixabay licenses)

Both providers are free for commercial use. Keys are read from environment
variables and never written to files or logs.
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse

PEXELS_SEARCH = "https://api.pexels.com/videos/search"
PIXABAY_SEARCH = "https://pixabay.com/api/videos/"


def http_get_json(url: str, headers: dict) -> dict:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_download(url: str, dest: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "WhatifHub/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as out:
        while True:
            chunk = resp.read(1024 * 512)
            if not chunk:
                break
            out.write(chunk)


def pick_pexels_video(item: dict, orientation: str) -> str:
    files = item.get("video_files", [])
    # prefer full HD landscape (~1920 wide), else largest available
    landscape = [f for f in files if f.get("width", 0) >= f.get("height", 1)]
    pool = landscape if orientation == "landscape" else files
    pool = pool or files
    best = max(pool, key=lambda f: f.get("width", 0))
    return best["link"]


def fetch_pexels(term: str, count: int, orientation: str, key: str):
    params = urllib.parse.urlencode({"query": term, "per_page": count, "size": "medium"})
    data = http_get_json(f"{PEXELS_SEARCH}?{params}",
                         {"Authorization": key, "User-Agent": "WhatifHub/1.0"})
    out = []
    for item in data.get("videos", [])[:count]:
        link = pick_pexels_video(item, orientation)
        out.append({"url": link, "source": "Pexels", "credit": item.get("user", {}).get("name", "Pexels"),
                    "page": item.get("url", ""), "term": term})
    return out


def fetch_pixabay(term: str, count: int, orientation: str, key: str):
    params = urllib.parse.urlencode({"key": key, "q": term, "per_page": min(count * 3, 200)})
    data = http_get_json(f"{PIXABAY_SEARCH}?{params}", {"User-Agent": "WhatifHub/1.0"})
    out = []
    for item in data.get("hits", []):
        large = item.get("videos", {}).get("large", {})
        tl = large.get("large", {})
        url = tl.get("url") or large.get("url")
        if url:
            out.append({"url": url, "source": "Pixabay", "credit": item.get("user", "Pixabay"),
                        "page": item.get("pageURL", ""), "term": term})
        if len(out) >= count:
            break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes_file")
    ap.add_argument("--out-dir", default="../materials")
    args = ap.parse_args()

    pexels_key = os.environ.get("PEXELS_API_KEY", "").strip()
    pixabay_key = os.environ.get("PIXABAY_API_KEY", "").strip()
    if not pexels_key and not pixabay_key:
        print("ERROR: set PEXELS_API_KEY (and optionally PIXABAY_API_KEY) env vars first.",
              file=sys.stderr)
        return 1

    with open(args.scenes_file, encoding="utf-8") as fh:
        scenes = json.load(fh)

    os.makedirs(args.out_dir, exist_ok=True)
    attribution_lines = ["# Footage attribution (Pexels/Pixabay license requirement)", ""]
    idx = 0
    for env in scenes["environments"]:
        got = []
        for term in env["terms"]:
            try:
                if not got and pexels_key:
                    got = fetch_pexels(term, env["count"], env.get("orientation", "landscape"), pexels_key)
                if not got and pixabay_key:
                    got = fetch_pixabay(term, env["count"], pixabay_key)
                if got:
                    break
            except Exception as exc:  # noqa: BLE001 - keep fetching other terms
                print(f"  warn: '{term}' failed: {exc}", file=sys.stderr)
                time.sleep(2)
        if not got:
            print(f"  ERROR: no clips found for environment '{env['id']}' - add PIXABAY_API_KEY or adjust terms.", file=sys.stderr)
            continue
        for clip in got:
            idx += 1
            dest = os.path.join(args.out_dir, f"{idx:02d}_{env['id']}.mp4")
            try:
                http_download(clip["url"], dest)
                attribution_lines.append(f"- {os.path.basename(dest)}: {clip['term']} by {clip['credit']} via {clip['source']} ({clip['page']})")
                print(f"ok {dest}")
            except Exception as exc:  # noqa: BLE001
                print(f"  warn: download failed for {clip['url']}: {exc}", file=sys.stderr)
                idx -= 1
        # Pexels free tier: 200 req/hour; Pixabay: 100 req/min. Stay well under.
        time.sleep(3)

    with open(os.path.join(args.out_dir, "ATTRIBUTION.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(attribution_lines) + "\n")
    print(f"\nDone. {idx} clips in {args.out_dir}. Attribution saved.")
    return 0 if idx > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
