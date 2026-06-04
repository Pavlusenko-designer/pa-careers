# Block spacing strategy

This document describes how vertical spacing works on the composed Careers homepage (`index.html`) and sibling agency pages. The system is implemented in `css/site-overrides.css` (copied to `assets/` on compose) and wired in `scripts/compose_site.py`.

---

## Core idea: Visual Distance (VD)

**Visual Distance (VD)** is the space between the **last visible element** of block A and the **first visible element** of block B.

Visible elements include, but are not limited to:

- Text (headings, paragraphs)
- Buttons and links styled as buttons
- Icons
- Cards and card rows
- Visible backgrounds (tinted bands, callout cards)

VD is **not** measured between anonymous wrapper boxes or invisible padding unless that padding is part of a visible surface (e.g. inside a callout card).

### Target value

| Token       | Desktop (≥768px) | Mobile (<768px) |
|-------------|------------------|-----------------|
| `--pa-vd`   | `7.5rem` (120px) | `5rem` (80px)   |
| `--pa-band-y` | `2.75rem`      | `2rem`          |

Inter-block spacing uses **`margin-top: var(--pa-vd)`** between adjacent widgets in a stack. We do **not** use flex `gap`, because gap measures box edges and is harder to reconcile with AEM’s default component padding.

---

## Architecture

### 1. Widget stacks

Each vertical column of blocks is a **VD stack**:

```html
<div class="pa-vd-stack">
  <!-- widgets as direct or general siblings -->
</div>
```

Stacks use `display: flex; flex-direction: column`. Only **widgets** participate in VD; other children (e.g. breadcrumb) do not receive inter-block margin.

### 2. Widgets (`pa-vd-widget`)

A **widget** is one logical block on the page. Each widget is tagged at compose time with `pa-vd-widget`.

Widget wrappers have **no outer padding** (`padding: 0`) and **no bottom/left/right margin**. Top margin between widgets is applied by the stack, not by the widget itself.

### 3. Surface types

Each widget also gets a surface class that controls **internal** spacing:

| Class | Meaning | VD behavior |
|-------|---------|-------------|
| `pa-vd-surface-content` | Plain content (teasers, hero, card group, resume, jobs) | Widget box hugs content. AEM vertical padding on `.cmp-teaser`, `.cmp-hero`, `.cmp-card-group` is zeroed so the stack margin ≈ true VD. |
| `pa-vd-surface-bg` | Visible background fills the widget (tinted bands, callout cards, social banner) | Background extends to the widget edges. Inset padding lives **inside** the visible background. VD to the next block is measured to the bottom edge of that background. |

Background detection at compose time: any block whose opening tag contains `__bgColor--` or `surface-container-lowest`.

---

## Homepage layout (two stacks)

The Careers homepage has **two VD stacks**:

### Main column stack

Attached to the top AEM grid (`breadcrumb` + hero):

```
pa-vd-stack (main)
├── breadcrumb          ← not a widget; no VD margin
├── hero                ← pa-vd-widget, pa-vd-surface-content
└── (stack ends)

section.agencypage-content   ← 120px below hero (sibling, not inside main stack)
```

### Agency content stack

Inside `section.agencypage-content`, all sections are flattened into one stack:

```
pa-vd-stack (agency)
 1. Get matched by resume      ← content surface (injected above “Your Experience Matters”)
 2. Your Experience Matters    ← content surface
 3. Internships band           ← background surface (full-width tint via ::before)
 4. Explore Popular Job Categories (card group)
 5. Why Work With Us           ← content surface
 6. Diversity & Inclusion      ← background surface (callout card)
 7. Celebrating Excellence     ← content surface
 8. Featured job openings      ← content surface
 9. Contact Us                 ← background surface (callout card)
10. Connect / social banner     ← background surface
```

Legacy AEM separators and empty page alerts are stripped before flattening.

---

## How inter-block spacing is applied

### CSS selectors

```css
/* Main column: any widget after another widget, or agency section after a widget */
.pa-vd-stack > .pa-vd-widget ~ .pa-vd-widget,
.pa-vd-stack > .pa-vd-widget ~ section.agencypage-content,

/* Agency column: adjacent widgets */
.agencypage-content .pa-vd-stack > .pa-vd-widget + .pa-vd-widget {
  margin-top: var(--pa-vd) !important;
}
```

**Important:** `.pa-vd-widget { margin: 0 !important }` must **not** set `margin-top`, or it overrides the rules above. Only bottom/left/right margins are reset on widgets.

The main stack uses the **general sibling combinator (`~`)** where needed so spacing still works when AEM inserts extra wrapper `div`s between siblings.

### Content-surface normalization

For `pa-vd-surface-content` widgets, `site-overrides.css` removes AEM defaults that would inflate or deflate VD:

- `.cmp-teaser` / `.cmp-hero` / `.cmp-card-group` → `padding-block: 0`
- Trailing padding on action buttons → `0`
- Trailing margin/padding on last text, images, card rows → `0`
- First heading/eyebrow in a widget → `margin-top: 0`

Internal spacing **between** title, body, and buttons inside a widget (e.g. `margin-bottom` on titles) is kept — that is layout inside the block, not VD.

---

## Exceptions and special blocks

### Hero

- **Top:** flush (no extra top padding on `.cmp-hero`).
- **Bottom:** explicit inset below CTAs (restores AEM rhythm):
  - `3rem` default
  - `4rem` at ≥1200px
- **Below hero:** `120px` VD to `section.agencypage-content` via main-stack rule.

### Callout cards (Diversity, Contact Us)

- Container IDs: `#container-ca6042f10d`, `#container-9e3377deac`
- Symmetric **internal** padding on the callout container (not on `.cmp-teaser`):
  - `1.5rem` mobile → `3rem` ≥641px → `4rem` ≥1200px
- Rounded corners, shared background token `--pa-callout-bg`
- Contact Us also has a border

VD to the next block is measured to the **bottom of the visible card background**, including internal bottom padding.

### Internships band

- Full-width background via `::before` on the widget; content aligned to the page grid
- Vertical inset inside the band: `--pa-band-y` on `#container-6f978e9e08`
- No outer vertical padding on the widget wrapper (background touches widget top/bottom edges)

### Featured job openings

- Custom section (`pa-recommended-jobs-wrap`) injected before Contact Us at compose time
- Treated as a content-surface widget in the agency stack
- Internal header/footer margins are for layout only; outer vertical padding is zeroed in VD context

### Get matched by resume

- Injected **inside** the agency grid, immediately **above** “Your Experience Matters”
- Not placed below the hero (avoids layout/spacing conflicts with AEM grid wrappers)
- Modal and scripts are unchanged; only placement in the VD stack differs

### Connect / social banner

- Background-surface widget; outer AEM `__top-bottom` padding zeroed
- Inner padding on `#container-9e17cd2f68`: `--pa-band-y` vertically, `2.25rem` horizontally

---

## Horizontal spacing (related, not VD)

VD is vertical only. Horizontal alignment uses separate rules:

- **Page grid inset:** `1.5rem` on breadcrumbs, nav, and main content at most breakpoints
- **≥1200px:** main/agency containers drop horizontal padding so content aligns with the grid
- **Callouts / bands:** full width within the agency column; internships band breaks out to viewport width for background only

---

## Compose pipeline

Run `python scripts/compose_site.py` to regenerate HTML and copy CSS.

| Step | What it does for spacing |
|------|---------------------------|
| Strip legacy resume placements | Removes old in-grid / after-hero resume blocks |
| Inject resume before Experience Matters | Inserts widget in agency grid |
| Inject recommended jobs before Contact Us | Adds jobs widget to agency flow |
| `prepare_agency_content()` | Strips separators/alerts; **flattens** agency blocks into `pa-vd-stack` |
| `apply_main_vd_stack()` | Adds `pa-vd-stack` to main grid; tags hero (+ resume if present) as widgets |
| `_add_vd_widget_class()` | Adds `pa-vd-widget` + surface class to each flattened block |

Do **not** hand-edit composed `index.html` for spacing — changes belong in `css/site-overrides.css` and/or `scripts/compose_site.py`.

---

## Adding or moving a block

1. **Identify the surface type** — content vs visible background.
2. **Ensure the block is a `pa-vd-widget`** in a `pa-vd-stack` (compose or flatten logic).
3. **Zero external vertical padding** on content-surface wrappers; put intentional inset inside the visible background for bg-surface widgets.
4. **Do not** add `margin-top` on the widget — the stack applies `--pa-vd`.
5. **Verify visible edges** — last button/text/card/bottom of background in block A to first visible in block B should read as ~120px (or 80px mobile).
6. Re-run compose and check the pair in the browser.

---

## Files

| File | Role |
|------|------|
| `css/site-overrides.css` | VD tokens, stack rules, surface normalization, block-specific overrides |
| `css/jobs-search.css`, `css/resume-search.css`, `css/recommended-jobs.css` | Section-specific layout sources |
| `assets/site-overrides.css` | Copy served to the browser |
| `assets/recommended-jobs.css` | Featured jobs internal layout |
| `assets/resume-search.css` | Resume widget + modal |
| `scripts/compose_site.py` | Stack flattening, widget classes, block injection order |
| `scripts/site_pages.py` | Page registry and local link maps |
| `scripts/nav.py` | Shared header navigation and breadcrumbs |

---

## Quick reference diagram

```
┌─────────────────────────────────────┐
│ Breadcrumb                          │  ← no VD
├─────────────────────────────────────┤
│ Hero (content surface)              │
│   … CTAs …                          │
│   [3–4rem bottom padding]           │
├─────────────────────────────────────┤  ← 120px VD
│ Agency section                      │
│ ┌─────────────────────────────────┐ │
│ │ Resume match                    │ │
├─┼─────────────────────────────────┤ │  ← 120px VD
│ │ Your Experience Matters         │ │
├─┼─────────────────────────────────┤ │
│ │ Internships band (bg surface)   │ │
├─┼─────────────────────────────────┤ │
│ │ … remaining widgets …           │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

Each `← 120px VD` line is implemented as `margin-top: var(--pa-vd)` on the lower widget, after normalizing the visible bottom/top edges of the pair above and below.
