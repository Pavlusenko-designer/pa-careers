"""Page registry and link maps for the PA Careers composed site."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"
ASSETS = ROOT / "assets"
CSS_DIR = ROOT / "css"
JS_DIR = ROOT / "js"
VENDOR_DIR = ROOT / "vendor"

BENEFITS_SOURCES = SOURCES / "benefits"
WHO_SOURCES = SOURCES / "who"

BENEFITS_CHILD_PAGES = [
    {
        "active": "benefits-our-team",
        "source": BENEFITS_SOURCES / "Our Team, Our Benefits.html",
        "output": ROOT / "benefits-our-team.html",
        "assets_from": BENEFITS_SOURCES / "Our Team, Our Benefits_files",
        "title": "Our Team, Our Benefits",
    },
    {
        "active": "benefits-health",
        "source": BENEFITS_SOURCES / "Health and Wellness.html",
        "output": ROOT / "benefits-health-and-wellness.html",
        "assets_from": BENEFITS_SOURCES / "Health and Wellness_files",
        "title": "Health and Wellness",
    },
    {
        "active": "benefits-work-life",
        "source": BENEFITS_SOURCES / "Work Life Balance.html",
        "output": ROOT / "benefits-work-life-balance.html",
        "assets_from": BENEFITS_SOURCES / "Work Life Balance_files",
        "title": "Work Life Balance",
    },
    {
        "active": "benefits-financial",
        "source": BENEFITS_SOURCES / "Financial Security.html",
        "output": ROOT / "benefits-financial-security.html",
        "assets_from": BENEFITS_SOURCES / "Financial Security_files",
        "title": "Financial Security",
    },
    {
        "active": "benefits-lifestyle",
        "source": BENEFITS_SOURCES / "Lifestyle & Wellness Perks.html",
        "output": ROOT / "benefits-lifestyle-wellness-perks.html",
        "assets_from": BENEFITS_SOURCES / "Lifestyle & Wellness Perks_files",
        "title": "Lifestyle & Wellness Perks",
    },
]

BENEFITS_BY_ACTIVE = {page["active"]: page for page in BENEFITS_CHILD_PAGES}

WHO_CHILD_PAGES = [
    {
        "active": "who-awards",
        "source": WHO_SOURCES / "Awards and Recognitions.html",
        "output": ROOT / "who-awards-and-recognitions.html",
        "assets_from": WHO_SOURCES / "Awards and Recognitions_files",
        "title": "Awards and Recognitions",
    },
]

WHO_BY_ACTIVE = {page["active"]: page for page in WHO_CHILD_PAGES}

PAGES = [
    {
        "source": SOURCES / "Employment.html",
        "output": ROOT / "index.html",
        "assets_from": SOURCES / "Employment_files",
        "active": "careers",
    },
    {
        "source": SOURCES / "Who We Are.html",
        "output": ROOT / "all-jobs.html",
        "assets_from": SOURCES / "Who We Are_files",
        "active": "jobs",
    },
    {
        "source": SOURCES / "Our Benefits.html",
        "output": ROOT / "our-benefits.html",
        "assets_from": SOURCES / "Our Benefits_files",
        "active": "benefits",
    },
    *BENEFITS_CHILD_PAGES,
    {
        "source": SOURCES / "Who We Are.html",
        "output": ROOT / "who-we-are.html",
        "assets_from": SOURCES / "Who We Are_files",
        "active": "who",
    },
    *WHO_CHILD_PAGES,
]

BENEFITS_LOCAL_LINKS = [
    (
        "https://www.pa.gov/agencies/employment/benefits/our-team--our-benefits",
        "benefits-our-team.html",
    ),
    (
        "https://www.pa.gov/agencies/employment/benefits/health-and-wellness",
        "benefits-health-and-wellness.html",
    ),
    (
        "https://www.pa.gov/agencies/employment/benefits/work-life-balance",
        "benefits-work-life-balance.html",
    ),
    (
        "https://www.pa.gov/agencies/employment/benefits/financial-security",
        "benefits-financial-security.html",
    ),
    (
        "https://www.pa.gov/agencies/employment/benefits/lifestyle-perks",
        "benefits-lifestyle-wellness-perks.html",
    ),
    ("https://www.pa.gov/agencies/employment/benefits", "our-benefits.html"),
]

WHO_LOCAL_LINKS = [
    (
        "https://www.pa.gov/agencies/employment/about-pa/awards-and-recognitions",
        "who-awards-and-recognitions.html",
    ),
    ("https://www.pa.gov/agencies/employment/about-pa", "who-we-are.html"),
]
