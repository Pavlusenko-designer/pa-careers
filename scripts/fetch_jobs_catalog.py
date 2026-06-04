#!/usr/bin/env python3
"""Fetch job classification rows from careers.employment.pa.gov into jobs-catalog.json."""

from __future__ import annotations

import json
import re
import urllib.request
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "jobs-catalog.json"
BASE = "https://careers.employment.pa.gov/Home/NoDegreeRequired"
PAGES = 5
PER_PAGE = 100


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_row(row: str) -> dict | None:
    cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL | re.IGNORECASE)
    if len(cells) < 8:
        return None
    title_html = cells[3]
    title_m = re.search(
        r'title="([^"]*)"[^>]*href="([^"]*)"', title_html, re.IGNORECASE
    )
    title = title_m.group(1) if title_m else strip_html(title_html)
    spec_url = (
        f"https://careers.employment.pa.gov{title_m.group(2)}"
        if title_m
        else None
    )
    pay_type_html = cells[5]
    pay_m = re.search(r">([^<]+)<", pay_type_html)
    pay_type = pay_m.group(1).strip() if pay_m else strip_html(pay_type_html)
    info_m = re.search(r'href="([^"]+)"', cells[8] if len(cells) > 8 else "")
    public_m = re.search(r'href="([^"]+)"', cells[10] if len(cells) > 10 else "")
    internal_m = re.search(r'href="([^"]+)"', cells[9] if len(cells) > 9 else "")

    def abs_url(path: str | None) -> str | None:
        if not path or path.strip() in ("", "&nbsp;"):
            return None
        if path.startswith("http"):
            return path
        return f"https://careers.employment.pa.gov{path}"

    return {
        "occupationalGroup": strip_html(cells[0]),
        "jobFamily": strip_html(cells[1]),
        "jobCode": strip_html(cells[2]),
        "title": title,
        "specUrl": spec_url,
        "payScaleGroup": strip_html(cells[4]),
        "payScaleType": pay_type,
        "bargainingUnit": strip_html(cells[6]),
        "salaryRange": strip_html(cells[7]),
        "payExpUrl": abs_url(info_m.group(1) if info_m else None),
        "internalPostingsUrl": abs_url(internal_m.group(1) if internal_m else None),
        "publicPostingsUrl": abs_url(public_m.group(1) if public_m else None),
    }


def fetch_page(page: int) -> list[dict]:
    url = (
        f"{BASE}?page={page}&education=50620180"
        "&entirePlanSearch=jobcode&entirePlanSort=ASC"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "pa-gov-static-site/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    tbody = re.search(r"<tbody>(.*?)</tbody>", html, re.DOTALL | re.IGNORECASE)
    if not tbody:
        return []
    rows = re.findall(r"<tr>\s*(.*?)\s*</tr>", tbody.group(1), re.DOTALL | re.IGNORECASE)
    jobs = []
    for row in rows:
        job = parse_row(row)
        if job:
            jobs.append(job)
    return jobs


def main() -> None:
    all_jobs: list[dict] = []
    for page in range(1, PAGES + 1):
        batch = fetch_page(page)
        print(f"Page {page}: {len(batch)} jobs")
        all_jobs.extend(batch)
    catalog = {
        "source": BASE,
        "fetchedPages": PAGES,
        "total": len(all_jobs),
        "jobs": all_jobs,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(all_jobs)} jobs)")


if __name__ == "__main__":
    main()
