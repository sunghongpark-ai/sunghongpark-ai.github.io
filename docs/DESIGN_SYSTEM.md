# Research × AI Hybrid design system

## Direction

A restrained editorial research website rather than a SaaS landing page.
A light, near-white reading surface is paired with deep navy, muted green,
serif emphasis, and graph-based explanatory motifs. Content is English-first.
The concept map is explicitly illustrative, not a measured scientific result.

## Tokens

| Role | Light | Dark |
|---|---|---|
| Background | #FCFDFB | #101D24 |
| Paper | #FFFFFF | #152730 |
| Wash | #F2F5F2 | #192D35 |
| Main text | #142D34 | #E8F0ED |
| Secondary text | #5C6E72 | #ADBFBD |
| Accent | #156D5C | #8DD4B9 |
| Border | #DBE3DF | #30454C |
| Secondary network group | #727CAF | #B0B8EA |

Design tokens live at the top of `design/styles.css`.

## Type

System sans-serif for navigation, body, and paper titles.
Georgia/Times-style serif italics for expressive headings.
System monospace for dates, labels, identifiers, and bibliographic code.
No font files are distributed and no font service is contacted.

## Layout

Maximum content width 1200px. Desktop gutters 48px; phone gutters 20px.
Breakpoints at 1100, 850, 700, and 360px.
The hero uses two columns on larger screens and a single column on phones.
Research directions use one shared framed row, not multiple floating dashboards.
Publications use editorial rows; projects use clear status cards.

## Interaction and accessibility

Focus-visible outlines, a skip link, semantic main/nav/article/section structures,
native dialogs/details, explicit input labels, live result counts, and keyboard
Escape behavior. Theme buttons expose state through aria-pressed.
No continuously moving decorative animation. Reduced-motion preference disables
smooth scrolling and transitions. Main content remains available without JavaScript.

These are implemented accessibility features, not a claim of a formal WCAG audit.

## Assets

The hero and research motifs are editable SVG emitted by `scripts/build.py`.
`design/og-card.html` is the editable source for the 1200×630 share image.
The checked-in PNG is a Chromium screenshot of that HTML at the intended size.
If changing identity/role, update and recapture the share image as well.
No external stock images, generated portraits, icon font libraries, or trackers.
