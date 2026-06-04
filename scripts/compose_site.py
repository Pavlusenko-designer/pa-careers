#!/usr/bin/env python3
"""Compose the PA Careers site into pages with shared assets and site nav."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from nav import breadcrumb_html, nav_html, toolbar_html
from site_pages import (
    ASSETS,
    BENEFITS_BY_ACTIVE,
    BENEFITS_LOCAL_LINKS,
    CSS_DIR,
    JS_DIR,
    PAGES,
    ROOT,
    VENDOR_DIR,
    WHO_BY_ACTIVE,
    WHO_LOCAL_LINKS,
)

ASSET_PREFIX_PATTERN = re.compile(r"\./(?:[^\"<>]+?)_files/")

SIDE_NAV_PATTERN = re.compile(
    r"\s*<div class=\"experiencefragment xf-side-navigation\">.*?"
    r"(?=<div class=\"container responsivegrid cmp-bootstrap-container)",
    re.DOTALL,
)

AGENCYPAGE_SECTION_OPEN = (
    '<section class="container responsivegrid cmp-bootstrap-container agencypage-content">'
)
AGENCY_SEPARATOR_BLOCK_PATTERN = re.compile(
    r'\s*<div class="separator aem-GridColumn aem-GridColumn--default--12">[\s\S]*?</div>\s*'
)
AGENCY_EMPTY_ALERT_PATTERN = re.compile(
    r'\s*<div class="pagealert aem-GridColumn aem-GridColumn--default--12">\s*'
    r'<div class="cmp-content-fragment__in-page-alert"[^>]*>\s*</div></div>\s*'
)

NAV_CONTAINER_PATTERN = re.compile(
    r'(<div class="cmp-bootstrap-container cmp-nav__container"[^>]*>).*?(</div>\s*\n\t\t</nav>)',
    re.DOTALL,
)

BREADCRUMB_PATTERN = re.compile(
    r"<nav id=\"breadcrumb-[^\"]+\" class=\"cmp-breadcrumb\".*?</nav>",
    re.DOTALL,
)

SKIP_AGENCY_NAV_PATTERN = re.compile(
    r"\s*<!--\s*Skip to side navigation[^>]*-->\s*"
    r"<div class=\"cmp-bootstrap-container cmp-header__skip-main\">\s*"
    r"<div class=\"cmp-button__primary\"[^>]*>.*?</div>\s*"
    r"</div>\s*",
    re.DOTALL,
)

BANNER_PATTERN = re.compile(
    r"\s*<!--\s*Banner[^>]*-->\s*<section class=\"cmp-header__banner\">.*?</section>\s*",
    re.DOTALL,
)

HEADER_BANNER_MODAL_PATTERN = re.compile(
    r'<div class="modal aem-GridColumn aem-GridColumn--default--12">\s*'
    r'.*?<dialog id="header_banner".*?</dialog>\s*</div>\s*',
    re.DOTALL,
)

NAVBAR_SECTION_PATTERN = re.compile(
    r"<!--\s*NavBar[^>]*-->\s*<section class=\"cmp-header__navbar\">.*?</section>\s*"
    r"(?=<!--\s*Navigation Menu)",
    re.DOTALL,
)

TRANSLATE_DROPDOWN_PATTERN = re.compile(
    r"<div class=\"dropdown\">\s*<button[^>]*btn-translate[^>]*>.*?</ul>\s*</div>",
    re.DOTALL,
)

SITE_CSS_LINK = (
    '<link id="site-overrides-css" rel="stylesheet" '
    'href="./assets/site-overrides.css" type="text/css">\n'
)
LOCALE_JS_SCRIPT = (
    '<script id="locale-selector-js" src="./assets/locale-selector.js" defer></script>\n'
)
NAV_BENEFITS_JS_SCRIPT = (
    '<script id="pa-nav-dropdown-js" src="./assets/pa-nav-dropdown.js" defer></script>\n'
)
REMIXICON_CSS_LINK = (
    '<link id="remixicon-css" rel="stylesheet" '
    'href="./assets/remixicon/remixicon.css" type="text/css">\n'
)
ROBOTO_SLAB_FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link id="roboto-slab-font" rel="stylesheet" '
    'href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;600;700&display=swap">\n'
)
SITE_OVERRIDES_SOURCE = CSS_DIR / "site-overrides.css"
REMIXICON_VENDOR = VENDOR_DIR / 'remixicon'
ROBOTO_SLAB_CSS_VENDOR = VENDOR_DIR / "css2-roboto-slab.css"

DIVERSITY_TEASER_COL_PATTERN = re.compile(
    r'(<div class="cmp-teaser " data-cmp-data-layer="\{&quot;teaser-d930effaa4[^"]*"[^>]*>'
    r"[\s\S]*?<div class=\"cmp-teaser__content)\s+col-md\s*(\">)",
)

CONNECT_TEASER_COL_PATTERN = re.compile(
    r'(<div class="cmp-teaser " data-cmp-data-layer="\{&quot;teaser-b4c3b71094[^"]*"[^>]*>'
    r"[\s\S]*?<div class=\"cmp-teaser__content)\s+col-md\s*(\">)",
)

MAIN_BODY_AFTER_BREADCRUMB_PATTERN = re.compile(
    r'(<div class="breadcrumb aem-GridColumn[^>]*>\s*<nav.*?</nav>\s*</div>\s*)'
    r".*?"
    r'(?=<div class="container responsivegrid bottom_section">)',
    re.DOTALL,
)

JOBS_CSS_LINK = (
    '<link id="jobs-search-css" rel="stylesheet" '
    'href="./assets/jobs-search.css" type="text/css">\n'
)
JOBS_JS_SCRIPT = (
    '<script id="jobs-search-js" src="./assets/jobs-search.js" defer></script>\n'
)

RESUME_CSS_LINK = (
    '<link id="resume-search-css" rel="stylesheet" '
    'href="./assets/resume-search.css" type="text/css">\n'
)
RESUME_JS_SCRIPT = (
    '<script id="resume-search-js" src="./assets/resume-search.js" defer></script>\n'
)

RECOMMENDED_JOBS_CSS_LINK = (
    '<link id="recommended-jobs-css" rel="stylesheet" '
    'href="./assets/recommended-jobs.css" type="text/css">\n'
)
RECOMMENDED_JOBS_JS_SCRIPT = (
    '<script id="recommended-jobs-js" src="./assets/recommended-jobs.js" defer></script>\n'
)

IN_GRID_RESUME_WIDGET_PATTERN = re.compile(
    r'<div class="aem-GridColumn aem-GridColumn--default--12 pa-resume-match">[\s\S]*?</div>\s*',
)

OUT_RESUME_WIDGET_PATTERN = re.compile(
    r'<section class="container responsivegrid cmp-bootstrap-container pa-resume-match-wrap[^"]*"[^>]*>[\s\S]*?</section>\s*',
)

BEFORE_EXPERIENCE_MATTERS_PATTERN = re.compile(
    r'(?=<div class="teaser aem-GridColumn aem-GridColumn--default--12">[\s\S]*?teaser-46db38f6d6)',
)

RECOMMENDED_JOBS_PATTERN = re.compile(
    r'<section class="container responsivegrid cmp-bootstrap-container pa-recommended-jobs-wrap"[^>]*>[\s\S]*?</section>\s*',
)

BEFORE_CONTACT_US_PATTERN = re.compile(
    r'(<div class="container responsivegrid cmp-bootstrap-container cmp-bootstrap-container__bgColor--surface-container-lowest cmp-bootstrap-container__borderRadius aem-GridColumn aem-GridColumn--default--12">\s*'
    r'\n\s*\n\s*\n\s*'
    r'<div id="container-9e3377deac" class="cmp-container">)',
)

RESUME_MODAL_BLOCK_PATTERN = re.compile(
    r'<div id="pa-resume-modal-backdrop"[^>]*>[\s\S]*?'
    r'<div id="pa-resume-modal"[^>]*>[\s\S]*?</div>\s*</div>\s*',
)

# Qualtrics "Was this page helpful?" embed (footer-only separator id)
FOOTER_SURVEY_PATTERN = re.compile(
    r'<div class="separator aem-GridColumn aem-GridColumn--default--12">\s*'
    r'<div id="separator-0599c4c4cc"[^>]*>[\s\S]*?'
    r"<!--END WEBSITE FEEDBACK SNIPPET-->\s*"
    r"</div>\s*",
    re.IGNORECASE,
)

FOOTER_BLOCK_PATTERN = re.compile(
    r'<footer class="experiencefragment cmp-experiencefragment--footer[\s\S]*?</footer>\s*',
    re.IGNORECASE,
)

ROOT_END_BEFORE_SCRIPTS_PATTERN = re.compile(
    r'(</div>\s*</div>\s*</div>\s*\n)(\s*\n\s*<script src="\./assets/clientlib-dependencies)',
    re.IGNORECASE,
)


def all_jobs_main_html() -> str:
    return """
<div class="aem-GridColumn aem-GridColumn--default--12 pa-jobs-page" id="pa-jobs-app">
  <header class="pa-jobs-hero" aria-labelledby="pa-jobs-hero-title">
    <div class="pa-jobs-hero__inner">
      <div class="pa-jobs-hero__copy">
        <h1 id="pa-jobs-hero-title" class="pa-jobs-hero__title">Search job openings</h1>
        <p class="pa-jobs-hero__sub">Browse current roles across Pennsylvania state agencies by title, keyword, or location.</p>
      </div>
      <div class="pa-jobs-global-search">
      <form id="pa-jobs-search-form" class="pa-jobs-global-search__form" role="search" aria-label="Search job openings">
        <div class="pa-jobs-global-search__field">
          <label class="sr-only" for="pa-jobs-keyword">Search by keyword</label>
          <i class="ri-search-line" aria-hidden="true"></i>
          <input type="search" id="pa-jobs-keyword" name="keyword" placeholder="Search by job title, location, or keyword" maxlength="255" autocomplete="off">
          <button type="button" class="pa-jobs-global-search__clear" id="pa-jobs-keyword-clear" hidden aria-label="Clear search">
            <i class="ri-close-line" aria-hidden="true"></i>
          </button>
        </div>
        <button type="submit" class="pa-jobs-global-search__submit">Search</button>
      </form>
      </div>
    </div>
  </header>

  <div class="pa-jobs-refine-backdrop" id="pa-jobs-refine-backdrop" aria-hidden="true"></div>

  <div class="pa-jobs-layout">
    <div class="pa-jobs-sidebar">
""" + resume_match_sidebar_html() + """
      <aside class="pa-jobs-refine" id="pa-jobs-refine" role="region" aria-label="Refine your search">
      <button type="button" class="pa-jobs-refine__close" id="pa-jobs-refine-close">
        <i class="ri-close-line" aria-hidden="true"></i> Close filter
      </button>
      <h2 class="pa-jobs-refine__heading">Refine your search</h2>

      <div class="pa-jobs-profile-facet">
        <label class="pa-jobs-profile-facet__control">
          <input type="checkbox" id="pa-jobs-profile-match" name="profile-match">
          <span class="pa-jobs-profile-facet__label">Based on your profile</span>
        </label>
        <p class="pa-jobs-profile-facet__help">See results based on your personal information preferences, experience and skills.</p>
      </div>

      <div class="pa-jobs-facet is-open">
        <button type="button" class="pa-jobs-facet__toggle" aria-expanded="true">
          Department <i class="ri-arrow-down-s-line" aria-hidden="true"></i>
        </button>
        <div class="pa-jobs-facet__body">
          <div class="pa-jobs-facet__search">
            <input type="search" data-facet-filter="facet-occupational-group" placeholder="Search" aria-label="Filter departments">
          </div>
          <ul class="pa-jobs-facet__list" id="facet-occupational-group"></ul>
        </div>
      </div>

      <div class="pa-jobs-facet">
        <button type="button" class="pa-jobs-facet__toggle" aria-expanded="false">
          Category <i class="ri-arrow-down-s-line" aria-hidden="true"></i>
        </button>
        <div class="pa-jobs-facet__body">
          <div class="pa-jobs-facet__search">
            <input type="search" data-facet-filter="facet-job-family" placeholder="Search" aria-label="Filter categories">
          </div>
          <ul class="pa-jobs-facet__list" id="facet-job-family"></ul>
        </div>
      </div>

      <div class="pa-jobs-facet">
        <button type="button" class="pa-jobs-facet__toggle" aria-expanded="false">
          Pay scale <i class="ri-arrow-down-s-line" aria-hidden="true"></i>
        </button>
        <div class="pa-jobs-facet__body">
          <ul class="pa-jobs-facet__list" id="facet-pay-scale"></ul>
        </div>
      </div>

      <div class="pa-jobs-facet">
        <button type="button" class="pa-jobs-facet__toggle" aria-expanded="false">
          Bargaining Unit <i class="ri-arrow-down-s-line" aria-hidden="true"></i>
        </button>
        <div class="pa-jobs-facet__body">
          <ul class="pa-jobs-facet__list" id="facet-bargaining"></ul>
        </div>
      </div>
    </aside>
    </div>

    <section class="pa-jobs-results" aria-labelledby="pa-jobs-results-label">
      <h2 id="pa-jobs-results-label" class="sr-only">Search results</h2>
      <div class="pa-jobs-results__header">
        <div class="pa-jobs-results__count-row">
          <p class="pa-jobs-results__count" id="pa-jobs-count">Loading jobs…</p>
          <div class="pa-jobs-results__controls">
            <button type="button" class="pa-jobs-filter-btn" id="pa-jobs-filter-open">
              <i class="ri-filter-3-line" aria-hidden="true"></i> Filter
            </button>
            <div class="pa-jobs-results__sort">
              <label for="pa-jobs-sort">Sort by</label>
              <select id="pa-jobs-sort" name="sort">
                <option value="relevance" selected>Relevance</option>
                <option value="posted-desc">Date posted (newest)</option>
                <option value="title-asc">Job title (A–Z)</option>
                <option value="title-desc">Job title (Z–A)</option>
                <option value="salary-desc">Salary (high to low)</option>
              </select>
            </div>
          </div>
        </div>
        <ul class="pa-jobs-tags" id="pa-jobs-tags" aria-label="Active filters"></ul>
      </div>

      <ul class="pa-jobs-list" id="pa-jobs-list" role="list" aria-live="polite"></ul>
      <p class="pa-jobs-empty" id="pa-jobs-empty" hidden>No jobs match your search. Try clearing filters or using a different keyword.</p>
      <ul class="pa-jobs-pagination" id="pa-jobs-pagination" aria-label="Results pages"></ul>
    </section>
  </div>
</div>
"""


def recommended_jobs_html() -> str:
    return """
<section class="container responsivegrid cmp-bootstrap-container pa-recommended-jobs-wrap" aria-labelledby="pa-recommended-jobs-title">
  <header class="pa-recommended-jobs__header">
    <div class="cmp-teaser__title pa-recommended-jobs__title-wrap">
      <h2 id="pa-recommended-jobs-title">Featured job openings</h2>
    </div>
    <p class="pa-recommended-jobs__sub">Explore current opportunities across Pennsylvania state agencies.</p>
  </header>
  <ul class="pa-recommended-jobs__list" id="pa-recommended-jobs" role="list" aria-live="polite"></ul>
  <div class="pa-recommended-jobs__footer">
    <div class="button cmp-button__secondary">
      <a class="cmp-button" href="all-jobs.html">
        <span class="cmp-button__text">View all job openings</span>
      </a>
    </div>
  </div>
</section>
"""


def resume_match_sidebar_html() -> str:
    return """
      <div class="pa-jobs-resume-match">
        <p class="pa-jobs-resume-match__title">Get matched by resume</p>
        <p class="pa-jobs-resume-match__text">Upload your resume to see jobs that match your skills and experience.</p>
        <button type="button" class="pa-jobs-resume-match__cta" id="pa-resume-open" aria-haspopup="dialog" aria-controls="pa-resume-modal">
          Search with resume
        </button>
      </div>
"""


def resume_match_widget_html() -> str:
    return """
<section class="container responsivegrid cmp-bootstrap-container pa-resume-match-wrap pa-vd-widget pa-vd-surface-content">
  <div class="pa-resume-match">
    <section class="pa-resume-match__card" aria-labelledby="pa-resume-match-title">
      <p class="pa-resume-match__label">Recommended</p>
      <div class="cmp-teaser__title">
        <h2 id="pa-resume-match-title">Get matched by resume.</h2>
      </div>
      <p class="pa-resume-match__text">Upload your resume and see jobs that match your skills, experience, and next step.</p>
      <div class="button cmp-button__primary">
        <button type="button" class="cmp-button pa-resume-match__cta" id="pa-resume-open" aria-haspopup="dialog" aria-controls="pa-resume-modal">
          <span class="cmp-button__text">Search with resume</span>
        </button>
      </div>
    </section>
  </div>
</section>
"""


def resume_match_modal_html() -> str:
    return """
<div id="pa-resume-modal-backdrop" class="pa-resume-modal-backdrop" aria-hidden="true"></div>
<div id="pa-resume-modal" class="pa-resume-modal" role="dialog" aria-modal="true" aria-labelledby="pa-resume-modal-title" aria-hidden="true">
  <div class="pa-resume-modal__dialog">
    <header class="pa-resume-modal__header">
      <h2 id="pa-resume-modal-title" class="pa-resume-modal__title">Find better job matches with your resume</h2>
      <button type="button" class="pa-resume-modal__close" id="pa-resume-modal-close" aria-label="Close dialog">
        <i class="ri-close-line" aria-hidden="true"></i>
      </button>
    </header>
    <div class="pa-resume-modal__body">
      <p class="pa-resume-modal__intro">Upload your resume (PDF or Word). We will use it to surface roles that align with your background.</p>
      <form id="pa-resume-form" novalidate>
        <div class="pa-resume-upload">
          <span class="pa-resume-upload__label" id="pa-resume-file-label-text">Resume</span>
          <label class="pa-resume-upload__drop" for="pa-resume-file">
            <i class="ri-upload-cloud-2-line" aria-hidden="true"></i>
            <span class="pa-resume-upload__filename" id="pa-resume-file-label">Choose a file or drag it here</span>
            <span class="pa-resume-upload__hint">PDF, DOC, or DOCX — 5 MB max</span>
            <input type="file" id="pa-resume-file" name="resume" accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" aria-labelledby="pa-resume-file-label-text pa-resume-file-label">
          </label>
        </div>
        <label class="pa-resume-consent">
          <input type="checkbox" id="pa-resume-consent" name="consent" value="1">
          <span>I agree to the <a href="https://www.pa.gov/privacy-policy" target="_blank" rel="noopener noreferrer">privacy policy</a> and <a href="https://www.governmentjobs.com/careers/pabureau/termsofuse" target="_blank" rel="noopener noreferrer">terms of use</a>.</span>
        </label>
        <p class="pa-resume-modal__error" id="pa-resume-error" role="alert" hidden></p>
        <button type="submit" class="pa-resume-modal__submit" id="pa-resume-submit" disabled>Search with resume</button>
      </form>
    </div>
  </div>
</div>
"""


def relocate_footer_outside_root(html: str) -> str:
    """Move footer outside .root.container so backgrounds span the viewport."""
    match = FOOTER_BLOCK_PATTERN.search(html)
    if not match:
        return html
    footer_html = match.group(0)
    html = html[: match.start()] + html[match.end() :]
    anchor = ROOT_END_BEFORE_SCRIPTS_PATTERN.search(html)
    if anchor:
        html = html[: anchor.end(1)] + footer_html + html[anchor.start(2) :]
    return html


def fix_local_links(html: str, links: list[tuple[str, str]]) -> str:
    for external, local in links:
        html = html.replace(f'href="{external}"', f'href="{local}"')
        html = html.replace(f"href='{external}'", f"href='{local}'")
    return html


def merge_assets() -> None:
    """Merge page asset folders into assets/ without wiping the whole tree (Windows-safe)."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    for css_file in sorted(CSS_DIR.glob("*.css")):
        shutil.copy2(css_file, ASSETS / css_file.name)
    for js_file in sorted(JS_DIR.glob("*.js")):
        shutil.copy2(js_file, ASSETS / js_file.name)
    if REMIXICON_VENDOR.is_dir():
        shutil.copytree(REMIXICON_VENDOR, ASSETS / "remixicon", dirs_exist_ok=True)
    if ROBOTO_SLAB_CSS_VENDOR.is_file():
        shutil.copy2(ROBOTO_SLAB_CSS_VENDOR, ASSETS / "css2")
    for placeholder in (
        "clientlib-dependencies.lc-d41d8cd98f00b204e9800998ecf8427e-lc.min.css",
        "clientlib-dependencies.lc-d41d8cd98f00b204e9800998ecf8427e-lc.min.js.загружено",
    ):
        path = ASSETS / placeholder
        if not path.exists():
            path.touch()
    for page in PAGES:
        src = page["assets_from"]
        if not src.is_dir():
            raise FileNotFoundError(f"Missing assets folder: {src}")
        for item in src.iterdir():
            dest = ASSETS / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)


def _extract_balanced_element(html: str, start: int) -> tuple[str, int]:
    open_end = html.find(">", start) + 1
    depth = 1
    index = open_end
    length = len(html)
    while index < length and depth > 0:
        events: list[tuple[int, str, str]] = []
        for tag in ("div", "section"):
            open_at = html.find(f"<{tag}", index)
            close_at = html.find(f"</{tag}>", index)
            if open_at != -1:
                events.append((open_at, "open", tag))
            if close_at != -1:
                events.append((close_at, "close", tag))
        if not events:
            break
        position, kind, tag = min(events, key=lambda item: item[0])
        if kind == "open":
            depth += 1
            index = html.find(">", position) + 1
            continue
        depth -= 1
        index = position + len(f"</{tag}>")
    return html[start:index], index


def _split_top_level_elements(html: str) -> list[str]:
    blocks: list[str] = []
    index = 0
    length = len(html)
    while index < length:
        while index < length and html[index].isspace():
            index += 1
        if index >= length:
            break
        if not (html.startswith("<div", index) or html.startswith("<section", index)):
            index += 1
            continue
        block, index = _extract_balanced_element(html, index)
        blocks.append(block)
    return blocks


def _is_vd_grid_block(open_tag: str) -> bool:
    if "pagealert" in open_tag or "separator" in open_tag:
        return False
    if "pa-recommended-jobs-wrap" in open_tag or "pa-resume-match-wrap" in open_tag:
        return True
    return "aem-GridColumn" in open_tag


def _has_vd_visible_bg(open_tag: str) -> bool:
    return "__bgColor--" in open_tag or "surface-container-lowest" in open_tag


def _add_vd_widget_class(block: str) -> str:
    open_end = block.index(">") + 1
    open_tag = block[:open_end]
    surface = "pa-vd-surface-bg" if _has_vd_visible_bg(open_tag) else "pa-vd-surface-content"
    if "pa-vd-widget" in open_tag:
        if surface in open_tag:
            return block
        new_open = re.sub(
            r'class="([^"]*)"',
            lambda match: f'class="{match.group(1)} {surface}"',
            open_tag,
            count=1,
        )
        return new_open + block[open_end:]
    new_open = re.sub(
        r'class="([^"]*)"',
        lambda match: f'class="{match.group(1)} pa-vd-widget {surface}"',
        open_tag,
        count=1,
    )
    return new_open + block[open_end:]


GRID_OPEN = '<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 ">'


def flatten_agency_vd_stack(section_html: str) -> str:
    cmp_match = re.search(r'<div id="[^"]+" class="cmp-container">', section_html)
    if not cmp_match:
        return section_html

    cmp_start = cmp_match.start()
    cmp_block, cmp_end = _extract_balanced_element(section_html, cmp_start)
    cmp_inner_start = cmp_block.index(">") + 1
    cmp_inner = cmp_block[cmp_inner_start : cmp_block.rfind("</div>")]

    grid_idx = cmp_inner.find(GRID_OPEN)
    if grid_idx == -1:
        return section_html

    grid_block, after_grid_start = _extract_balanced_element(cmp_inner, grid_idx)
    grid_inner = grid_block[grid_block.index(">") + 1 : grid_block.rfind("</div>")]
    after_grid = cmp_inner[after_grid_start:]

    widgets: list[str] = []
    for block in _split_top_level_elements(grid_inner):
        open_tag = block[: block.index(">") + 1]
        if _is_vd_grid_block(open_tag):
            widgets.append(_add_vd_widget_class(block))

    for block in _split_top_level_elements(after_grid):
        if "bottom_section" in block:
            continue
        open_tag = block[: block.index(">") + 1]
        if _is_vd_grid_block(open_tag):
            widgets.append(_add_vd_widget_class(block))

    if not widgets:
        return section_html

    stack_html = '<div class="pa-vd-stack">\n' + "\n".join(widgets) + "\n</div>"
    new_cmp = cmp_block[:cmp_inner_start] + stack_html + cmp_block[cmp_block.rfind("</div>") :]
    return section_html[:cmp_start] + new_cmp + section_html[cmp_end:]


def apply_main_vd_stack(html: str) -> str:
    html = html.replace(
        '<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 "pa-vd-stack >',
        '<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 pa-vd-stack">',
    )
    html = re.sub(
        r'(<div class="aem-Grid aem-Grid--12 aem-Grid--default--12)\s*("\s*>\s*\n\s*<div class="breadcrumb)',
        r'\1 pa-vd-stack\2',
        html,
        count=1,
    )
    html = re.sub(
        r'class="hero cmp-teaser--text-align-center aem-GridColumn aem-GridColumn--default--12( pa-vd-widget)?( pa-vd-surface-content)?"',
        'class="hero cmp-teaser--text-align-center aem-GridColumn aem-GridColumn--default--12 pa-vd-widget pa-vd-surface-content"',
        html,
        count=1,
    )
    html = re.sub(
        r'class="container responsivegrid cmp-bootstrap-container pa-resume-match-wrap( pa-vd-widget)?( pa-vd-surface-content)?"',
        'class="container responsivegrid cmp-bootstrap-container pa-resume-match-wrap pa-vd-widget pa-vd-surface-content"',
        html,
        count=1,
    )
    return html


def prepare_agency_content(html: str) -> str:
    """Remove legacy spacers and flatten agency blocks into a VD stack."""

    index = 0
    while True:
        start = html.find(AGENCYPAGE_SECTION_OPEN, index)
        if start == -1:
            break
        section_block, end = _extract_balanced_element(html, start)
        section = AGENCY_SEPARATOR_BLOCK_PATTERN.sub("\n", section_block)
        section = AGENCY_EMPTY_ALERT_PATTERN.sub("\n", section)
        new_section = flatten_agency_vd_stack(section)
        html = html[:start] + new_section + html[end:]
        index = start + len(new_section)
    return html


def transform_html(source: Path, output: Path, active: str) -> None:
    html = source.read_text(encoding="utf-8")

    html = ASSET_PREFIX_PATTERN.sub("./assets/", html)
    html = html.replace('href="https://www.pa.gov/"', 'href="index.html"')
    html = html.replace('href="https://www.pa.gov/agencies/employment"', 'href="index.html"')
    html = SKIP_AGENCY_NAV_PATTERN.sub("\n", html)
    html = BANNER_PATTERN.sub("\n", html)

    navbar_section = (
        "\t\t<!--  NavBar.................... */ -->\n"
        '\t\t<section class="cmp-header__navbar">\n'
        '\t\t\t<div class="cmp-bootstrap-container cmp-navbar__container">\n'
        f"{toolbar_html()}"
        "\t\t\t</div>\n"
        "\t\t</section>\n\t\t"
    )
    html = NAVBAR_SECTION_PATTERN.sub(navbar_section, html, count=1)

    html = SIDE_NAV_PATTERN.sub("\n", html)

    html = NAV_CONTAINER_PATTERN.sub(
        lambda m: m.group(1) + nav_html(active) + m.group(2), html, count=1
    )
    html = BREADCRUMB_PATTERN.sub(breadcrumb_html(active), html, count=1)
    if active.startswith("benefits-"):
        title = BENEFITS_BY_ACTIVE[active]["title"]
        html = re.sub(
            r"<title>[^<]+</title>",
            f"<title>{title} | Careers</title>",
            html,
            count=1,
        )
    if active.startswith("who-"):
        title = WHO_BY_ACTIVE[active]["title"]
        html = re.sub(
            r"<title>[^<]+</title>",
            f"<title>{title} | Careers</title>",
            html,
            count=1,
        )
    if active in ("benefits",) or active.startswith("benefits-"):
        html = fix_local_links(html, BENEFITS_LOCAL_LINKS)
    if active in ("who",) or active.startswith("who-"):
        html = fix_local_links(html, WHO_LOCAL_LINKS)
    if active == "jobs":
        html = HEADER_BANNER_MODAL_PATTERN.sub("\n", html, count=1)
        html = MAIN_BODY_AFTER_BREADCRUMB_PATTERN.sub(
            lambda m: m.group(1) + all_jobs_main_html(), html, count=1
        )
    if active == "careers":
        html = IN_GRID_RESUME_WIDGET_PATTERN.sub("", html, count=1)
        html = OUT_RESUME_WIDGET_PATTERN.sub("", html)
        html = BEFORE_EXPERIENCE_MATTERS_PATTERN.sub(
            resume_match_widget_html(), html, count=1
        )
        html = RECOMMENDED_JOBS_PATTERN.sub("", html, count=1)
        html = BEFORE_CONTACT_US_PATTERN.sub(
            lambda m: recommended_jobs_html() + m.group(1), html, count=1
        )
    html = DIVERSITY_TEASER_COL_PATTERN.sub(r"\1 col-12\2", html, count=1)
    html = CONNECT_TEASER_COL_PATTERN.sub(r"\1 col-12\2", html, count=1)
    html = FOOTER_SURVEY_PATTERN.sub("", html, count=1)
    html = relocate_footer_outside_root(html)
    html = html.replace('href="mailto:mailto:%20statejobs@pa.gov"', 'href="mailto:statejobs@pa.gov"')
    html = html.replace(
        "<p>Have questions? We’re here to help. Reach out to our team for any inquiries "
        "about job opportunities, the application process, or working with the Commonwealth "
        "of Pennsylvania.</p>\n<ul></ul>",
        "<p>Have questions? We’re here to help. Reach out to our team for any inquiries "
        "about job opportunities, the application process, or working with the Commonwealth "
        "of Pennsylvania.</p>",
    )
    html = re.sub(
        r'(<a class="cmp-button" id="teaser-b4c3b71094-button-1"[^>]*) target="_blank"',
        r"\1",
        html,
        count=1,
    )
    html = re.sub(
        r'(id="teaser-b4c3b71094-button-1"[^>]*>\s*'
        r'<span class="cmp-button__text">Email Us</span>)\s*'
        r'<span class="cmp-link__screen-reader-only">\(opens in a new tab\)</span>',
        r"\1",
        html,
        count=1,
    )

    html = html.replace("Zilla Slab", "Roboto Slab")
    html = html.replace("Zilla+Slab", "Roboto+Slab")
    html = html.replace('aria-label="Commonwealth of Pennsylvania"', 'aria-label="Careers site"')
    if active == "careers":
        html = html.replace("<title>Employment</title>", "<title>Careers</title>", 1)
        html = html.replace(
            '<meta property="og:title" content="Employment">',
            '<meta property="og:title" content="Careers">',
        )
        html = html.replace(
            '<meta name="twitter:title" content="Employment">',
            '<meta name="twitter:title" content="Careers">',
        )
        html = html.replace(
            '<meta name="copapwp-agency" content="Employment">',
            '<meta name="copapwp-agency" content="Careers">',
        )
        html = html.replace(
            'href="https://www.governmentjobs.com/careers/pabureau" target="_blank" data-cmp-clickable="">\n'
            '                                <span class="cmp-button__text">View all job openings</span>',
            'href="all-jobs.html">\n'
            '                                <span class="cmp-button__text">View all job openings</span>',
            1,
        )
    if active == "jobs":
        html = re.sub(r"<title>[^<]+</title>", "<title>All Jobs | Careers</title>", html, count=1)
        html = html.replace(
            '<meta property="og:title" content="Who We Are">',
            '<meta property="og:title" content="All Jobs">',
        )
        html = html.replace(
            '<meta name="twitter:title" content="Who We Are">',
            '<meta name="twitter:title" content="All Jobs">',
        )
    html = re.sub(
        r'href="https://www\.pa\.gov/agencies/employment[^"]*#content"',
        'href="#content"',
        html,
    )

    stylesheet_anchor = (
        'href="./assets/clientlib-site.lc-e44da7e0780f5ad74766bd9fc82eb564-lc.min.css" '
        'type="text/css">'
    )
    if 'id="roboto-slab-font"' not in html:
        html = html.replace("<head>", f"<head>\n    {ROBOTO_SLAB_FONTS_LINK}", 1)

    extra_styles = ""
    if 'id="site-overrides-css"' not in html:
        extra_styles += f"    {SITE_CSS_LINK}"
    if 'id="remixicon-css"' not in html:
        extra_styles += f"    {REMIXICON_CSS_LINK}"
    if active == "jobs" and 'id="jobs-search-css"' not in html:
        extra_styles += f"    {JOBS_CSS_LINK}"
    if active == "jobs" and 'id="resume-search-css"' not in html:
        extra_styles += f"    {RESUME_CSS_LINK}"
    if active == "careers" and 'id="resume-search-css"' not in html:
        extra_styles += f"    {RESUME_CSS_LINK}"
    if active == "careers" and 'id="jobs-search-css"' not in html:
        extra_styles += f"    {JOBS_CSS_LINK}"
    if active == "careers" and 'id="recommended-jobs-css"' not in html:
        extra_styles += f"    {RECOMMENDED_JOBS_CSS_LINK}"
    if extra_styles:
        html = html.replace(stylesheet_anchor, f"{stylesheet_anchor}\n{extra_styles}", 1)

    if 'id="locale-selector-js"' not in html:
        html = html.replace("</body>", f"{LOCALE_JS_SCRIPT}</body>", 1)
    if 'id="pa-nav-dropdown-js"' not in html:
        html = html.replace("</body>", f"{NAV_BENEFITS_JS_SCRIPT}</body>", 1)

    if active == "jobs" and 'id="jobs-search-js"' not in html:
        html = html.replace("</body>", f"{JOBS_JS_SCRIPT}</body>", 1)
    if active == "jobs":
        if RESUME_MODAL_BLOCK_PATTERN.search(html):
            html = RESUME_MODAL_BLOCK_PATTERN.sub(
                resume_match_modal_html(), html, count=1
            )
        elif 'id="pa-resume-modal"' not in html:
            html = html.replace(
                "</body>", f"{resume_match_modal_html()}{RESUME_JS_SCRIPT}</body>", 1
            )
        if 'id="resume-search-js"' not in html:
            html = html.replace("</body>", f"{RESUME_JS_SCRIPT}</body>", 1)
    if active == "careers":
        if RESUME_MODAL_BLOCK_PATTERN.search(html):
            html = RESUME_MODAL_BLOCK_PATTERN.sub(
                resume_match_modal_html(), html, count=1
            )
        elif 'id="pa-resume-modal"' not in html:
            html = html.replace(
                "</body>", f"{resume_match_modal_html()}{RESUME_JS_SCRIPT}</body>", 1
            )
        if 'id="resume-search-js"' not in html:
            html = html.replace("</body>", f"{RESUME_JS_SCRIPT}</body>", 1)
        if 'id="recommended-jobs-js"' not in html:
            html = html.replace("</body>", f"{RECOMMENDED_JOBS_JS_SCRIPT}</body>", 1)

    html = prepare_agency_content(html)
    if active == "careers":
        html = apply_main_vd_stack(html)

    output.write_text(html, encoding="utf-8")
    print(f"Wrote {output.name}")


def main() -> None:
    merge_assets()
    for page in PAGES:
        if not page["source"].is_file():
            raise FileNotFoundError(f"Missing source page: {page['source']}")
        transform_html(page["source"], page["output"], page["active"])
    print(f"Shared assets: {ASSETS}")


if __name__ == "__main__":
    main()
