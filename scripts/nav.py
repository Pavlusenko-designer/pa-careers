"""Shared site header navigation, search, locale selector, and breadcrumbs."""

from __future__ import annotations

from site_pages import (
    BENEFITS_BY_ACTIVE,
    BENEFITS_CHILD_PAGES,
    WHO_BY_ACTIVE,
    WHO_CHILD_PAGES,
)


def _nav_item(key: str, href: str, label: str, active: str) -> str:
    current = ' aria-current="page"' if key == active else ""
    return f"""
                <li class="cmp-nav__primary-item">
                    <a href="{href}" class="cmp-button cmp-button__nav"{current}>
                        <span class="cmp-button__text">{label}</span>
                    </a>
                </li>"""


def _nav_dropdown_item(
    *,
    active: str,
    parent_key: str,
    parent_href: str,
    parent_label: str,
    branch_prefix: str,
    menu_id: str,
    children: list[dict],
) -> str:
    branch_active = active == parent_key or active.startswith(f"{branch_prefix}-")
    parent_current = ' aria-current="page"' if active == parent_key else ""
    branch_class = " pa-nav-dropdown--branch-active" if branch_active else ""
    items = []
    for child in children:
        child_current = ' aria-current="page"' if active == child["active"] else ""
        items.append(
            f"""
                            <li role="none">
                                <a href="{child['output'].name}" class="pa-nav-dropdown__item" role="menuitem"{child_current}>{child['title']}</a>
                            </li>"""
        )
    return f"""
                <li class="cmp-nav__primary-item pa-nav-dropdown{branch_class}" data-nav-dropdown>
                    <div class="pa-nav-dropdown__control">
                        <a href="{parent_href}" class="cmp-button cmp-button__nav pa-nav-dropdown__link"{parent_current}>
                            <span class="cmp-button__text">{parent_label}</span>
                        </a>
                        <button type="button" class="pa-nav-dropdown__toggle" aria-expanded="false" aria-controls="{menu_id}" aria-label="Show {parent_label} pages">
                            <i class="ri-arrow-down-s-line" aria-hidden="true"></i>
                        </button>
                    </div>
                    <div class="pa-nav-dropdown__menu" id="{menu_id}" role="menu" aria-label="{parent_label} pages" hidden>
                        <ul class="pa-nav-dropdown__list" role="none">
{"".join(items)}
                        </ul>
                    </div>
                </li>"""


def nav_html(active: str) -> str:
    lis = [
        _nav_item("careers", "index.html", "Careers", active),
        _nav_item("jobs", "all-jobs.html", "All Jobs", active),
        _nav_dropdown_item(
            active=active,
            parent_key="benefits",
            parent_href="our-benefits.html",
            parent_label="Our Benefits",
            branch_prefix="benefits",
            menu_id="pa-nav-benefits-menu",
            children=BENEFITS_CHILD_PAGES,
        ),
        _nav_dropdown_item(
            active=active,
            parent_key="who",
            parent_href="who-we-are.html",
            parent_label="Who We Are",
            branch_prefix="who",
            menu_id="pa-nav-who-menu",
            children=WHO_CHILD_PAGES,
        ),
    ]
    return (
        '<ul id="nav-site" class="cmp-nav__primary" data-placeholder-text="false">'
        + "".join(lis)
        + "\n        </ul>"
    )


def search_html() -> str:
    return """<div class="cmp-header__search site-header-search">
\t\t\t\t\t\t<form class="site-search-form" role="search" action="all-jobs.html" method="get">
\t\t\t\t\t\t\t<label class="cmp-link__screen-reader-only" for="site-search-input">Search</label>
\t\t\t\t\t\t\t<span class="site-search-form__icon" aria-hidden="true"><i class="ri-search-line"></i></span>
\t\t\t\t\t\t\t<input type="search" id="site-search-input" name="keyWord" placeholder="Search jobs" autocomplete="off">
\t\t\t\t\t\t\t<button type="submit" class="site-search-submit" aria-label="Search">
\t\t\t\t\t\t\t\t<i class="ri-arrow-right-line" aria-hidden="true"></i>
\t\t\t\t\t\t\t</button>
\t\t\t\t\t\t</form>
\t\t\t\t\t</div>"""


LOCALES = [
    ("", "English"),
    ("ar", "العربية"),
    ("bn", "বাংলা"),
    ("zh-CN", "简体中文"),
    ("zh-TW", "繁體中文"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("gu", "ગુજરાતી"),
    ("ht", "Kreyòl ayisyen"),
    ("it", "Italiano"),
    ("km", "ភាសាខ្មែរ"),
    ("ko", "한국어"),
    ("ne", "नेपाली"),
    ("pl", "Polski"),
    ("pt", "Português (Brasil)"),
    ("ru", "Русский"),
    ("es", "Español"),
    ("vi", "Tiếng Việt"),
]


def locale_selector_html() -> str:
    options = "\n".join(
        f'\t\t\t\t\t\t\t<option value="{code}">{label}</option>'
        for code, label in LOCALES
    )
    return f"""<div class="cmp-translate g-translate pa-locale-wrap">
\t\t\t\t\t\t<label class="cmp-link__screen-reader-only" for="pa-locale-select">Language</label>
\t\t\t\t\t\t<select id="pa-locale-select" class="pa-locale-select" aria-label="Language">
{options}
\t\t\t\t\t\t</select>
\t\t\t\t\t\t<div class="pa-locale-compat" hidden aria-hidden="true">
\t\t\t\t\t\t\t<div class="dropdown">
\t\t\t\t\t\t\t\t<button type="button" class="btn btn-translate" data-bs-toggle="dropdown" id="defaultDropdown" disabled tabindex="-1"></button>
\t\t\t\t\t\t\t\t<ul class="dropdown-menu skiptranslate" aria-labelledby="defaultDropdown"></ul>
\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t</div>
\t\t\t\t\t\t<div id="google-translate-element" class="google-translate-element"></div>
\t\t\t\t\t</div>"""


def toolbar_html() -> str:
    return f"""<div class="navbar-withsearch site-header-toolbar">
\t\t\t\t<div class="cmp-navbar site-header-row">
\t\t\t\t\t<div class="cmp-navbar__header-logo">
\t\t\t\t\t\t<a href="index.html">
\t\t\t\t\t\t\t<img alt="Commonwealth of Pennsylvania | Home" src="./assets/CoPA Logo - Horizontal Lockup 1.svg">
\t\t\t\t\t\t</a>
\t\t\t\t\t</div>
{search_html()}
\t\t\t\t\t<div class="cmp-header__translate">
{locale_selector_html()}
\t\t\t\t\t</div>
\t\t\t\t</div>
\t\t\t</div>
\t\t\t"""


def _breadcrumb_link(text: str, href: str, position: int) -> str:
    return (
        f'<li class="cmp-breadcrumb__item cmp-breadcrumb__icon" '
        f'itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem">'
        f'<a class="cmp-breadcrumb__item-link" itemprop="item" href="{href}">'
        f'<span itemprop="name">{text}</span></a>'
        f'<meta itemprop="position" content="{position}"></li>'
    )


def _breadcrumb_active(text: str, position: int) -> str:
    return (
        f'<li class="cmp-breadcrumb__item cmp-breadcrumb__icon cmp-breadcrumb__item--active" '
        f'aria-current="page" itemprop="itemListElement" itemscope '
        f'itemtype="http://schema.org/ListItem">'
        f'<span itemprop="name">{text}</span>'
        f'<meta itemprop="position" content="{position}"></li>'
    )


def breadcrumb_html(active: str) -> str:
    if active == "careers":
        items = _breadcrumb_active("Careers", 1)
    elif active == "jobs":
        items = _breadcrumb_link("Careers", "index.html", 1) + _breadcrumb_active(
            "All Jobs", 2
        )
    elif active == "benefits":
        items = _breadcrumb_link("Careers", "index.html", 1) + _breadcrumb_active(
            "Our Benefits", 2
        )
    elif active.startswith("benefits-"):
        title = BENEFITS_BY_ACTIVE[active]["title"]
        items = (
            _breadcrumb_link("Careers", "index.html", 1)
            + _breadcrumb_link("Our Benefits", "our-benefits.html", 2)
            + _breadcrumb_active(title, 3)
        )
    elif active == "who":
        items = _breadcrumb_link("Careers", "index.html", 1) + _breadcrumb_active(
            "Who We Are", 2
        )
    elif active.startswith("who-"):
        title = WHO_BY_ACTIVE[active]["title"]
        items = (
            _breadcrumb_link("Careers", "index.html", 1)
            + _breadcrumb_link("Who We Are", "who-we-are.html", 2)
            + _breadcrumb_active(title, 3)
        )
    else:
        items = _breadcrumb_link("Careers", "index.html", 1) + _breadcrumb_active(
            "Who We Are", 2
        )
    return (
        '<nav class="cmp-breadcrumb" aria-label="Breadcrumb">'
        '<ol class="cmp-breadcrumb__list" itemscope itemtype="http://schema.org/BreadcrumbList">'
        f"{items}</ol></nav>"
    )
