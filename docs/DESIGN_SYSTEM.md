# Signal Graph design system

## Direction

A flat, graphic research identity built from six colours. Paper is the ground,
Ink carries text and structure, and four accents appear as flat shapes: the
nodes, discs and signals of a graph. Content is English-first.
The concept map is explicitly illustrative, not a measured scientific result.

Every page has the same order of surfaces:
Paper header → Ink masthead with a dot grid → Paper body → Sky contact band → Ink footer.

- One Coral key phrase per masthead headline; section headlines end in a "hot" dot.
- Blocks are square. Buttons, chips, tags and status labels are pills.
  Nodes, icon buttons and the brand mark are circles.
- Structural rules are 2px in the text colour; row rules are 1px hairlines.
- No shadows and no colour gradients. (The dot grid and the +/− marks are drawn
  with CSS gradients of a single solid colour.)

## Colour tokens

| Token | Value | Role |
|---|---|---|
| Paper | `#F1F3F4` | Page ground; text and fills on Ink |
| Ink | `#3A3D44` | Text, rules, mastheads, footer, primary button |
| Sky | `#9CC6E0` | Highlight surfaces; primary button and small labels on Ink |
| Azure | `#0297DE` | Direction 01 (graph learning), discs, link underline on Paper |
| Coral | `#FC734D` | "Hot" on Ink: key phrase, brand dot; Direction 02 (biomedical AI) |
| Red | `#E4002B` | "Hot" on Paper and Sky: headline dot, current page, Active dot |

No other colour is used, including pure white or black. Secondary text and
hairlines are alpha mixes of Ink or Paper (84%, 60%, 50%, 40%, 28%, 22%).
Tokens live at the top of `design/styles.css`.

### Contrast

Ratios are calculated from the values above with the WCAG 2.x formula.

| Pair | Ratio | Used for |
|---|---|---|
| Ink / Paper, Paper / Ink | 9.8 | Body text, headings |
| Paper 84% / Ink | 7.5 | Secondary text on Ink |
| Ink 84% / Paper | 6.2 | Secondary text on Paper |
| Ink / Sky, Sky / Ink | 6.0 | Text on Sky surfaces; Sky labels on Ink |
| Red / Paper | 4.4 | Shapes and large headline dots only |
| Coral / Ink, Ink / Coral | 4.0 | Large text only (headline key phrase, panel numbers) |
| Ink / Azure | 3.4 | Large text only (panel numbers) and graphics |
| Ink 60% / Paper, Paper 50% / Ink | 3.3 / 3.8 | Outlines of secondary controls |
| Azure / Paper | 2.9 | Shapes and the 2px link underline; never text |
| Coral / Paper, Red / Sky, Red / Ink | 2.5 / 2.7 / 2.2 | Dots and markers; never text |
| Sky / Paper | 1.6 | Never adjacent as text and ground |

Rules that follow from the table:

- Text on Paper is Ink (or Ink 84%). Text on Sky is always full Ink, because
  Ink 84% on Sky drops to 4.3.
- Azure and Coral sit behind large text only; small text never sits on them.
- Linked text is Ink at weight 600 with a 2px underline (Azure on Paper, Sky on
  Ink, Ink on Sky). The underline colour is an accent, not the only cue.

### Surfaces and themes

Components do not name colours. They read role variables (`--bg`, `--fg`,
`--fg-2`, `--hair`, `--soft`, `--hot`, `--link-line`, `--focus`, `--btn-*`,
`--pill-*`) that are defined for three contexts:

| Context | Selector | Ground | Text | Hot | Primary button |
|---|---|---|---|---|---|
| Paper | `:root` | Paper | Ink | Red | Ink / Paper |
| Ink | `.on-ink`, `:root[data-theme=dark]` | Ink | Paper | Coral | Sky / Ink |
| Sky | `.on-sky` | Sky | Ink | Red | Ink / Paper |

The dark theme is therefore the same six colours with Ink as the ground. Sky
blocks and the accent panels are unchanged. Mastheads, which are also Ink, are
closed by a 2px Paper rule, and the highlighted project card gains a Paper outline.

## Research directions

The three directions are always named by shape and colour together, never by
colour alone, with an outline in the surrounding text colour.

| Direction | Marker | Panel |
|---|---|---|
| Graph learning | ● Azure circle | Azure |
| Biomedical AI | ■ Coral square | Coral |
| Domain adaptation | ◆ Sky diamond | Sky |
| Other | ○ outline circle | — |

## Type

| Role | Family | Size / line height / tracking |
|---|---|---|
| Display (home) | Space Grotesk 600 | clamp(46px, 7vw, 100px) / 0.96 / −0.045em |
| H1 (mastheads) | Space Grotesk 600 | clamp(40px, 5.4vw, 78px) / 1.0 / −0.04em |
| H2 | Space Grotesk 600 | clamp(34px, 4vw, 56px) / 1.02 / −0.035em |
| H3 | Space Grotesk 600 | 26px / 1.15 / −0.02em |
| Lead | Inter 400 | 19px / 1.55 |
| Body | Inter 400–600 | 16px / 1.6 |
| Labels | JetBrains Mono 500 | 12–13px capitals, +0.08em; never below 12px |

The three families are variable fonts (Latin subset) stored in `design/fonts/`
and copied to `site/assets/fonts/` by the build. They are licensed under the
SIL Open Font License 1.1; the licence texts are stored beside them.
No font service is contacted. Korean text uses the system fonts named in the
stacks. If `design/fonts/` is removed, the site falls back to system fonts.

## Layout

Maximum content width 1200px; gutters clamp(16px, 5vw, 48px).
Breakpoints: 1000px (contact pill hidden, research and CV become one column),
899px (hero becomes one column), 820px (brand name hidden), 700px (mobile
navigation and mobile type sizes), then 560, 480, 420 and 350px for small phones.
The research-map labels are SVG text, so their size is stepped at 1239, 1099,
899, 560, 420 and 350px to stay near 12px on screen.

Publications and archive records are ruled rows. Projects are status blocks:
the active grant is a Sky block, the completed one an outlined block.

## Interaction and accessibility

Focus-visible outlines (3px, Ink on Paper and Sky, Sky on Ink), a skip link,
semantic main/nav/article/section structures, native dialogs/details, explicit
input labels, live result counts, and keyboard Escape behaviour. Theme buttons
expose state through aria-pressed. Controls (buttons, chips, icon buttons,
navigation links, form fields and disclosure rows) are at least 44px tall;
linked titles are full text lines of 26px or more.
Hover styles apply only where a pointer can hover, so a tap never leaves a
control in its hover state. No continuously moving decorative animation.
Reduced-motion preference disables smooth scrolling and transitions.
Main content and navigation remain available without JavaScript.

These are implemented accessibility features, not a claim of a formal WCAG audit.

## Assets

The research map, direction motifs, year plot, funding timeline and 404 mark are
emitted by `scripts/build.py` and coloured by `design/styles.css`.
The favicon is the brand mark as outlines (Space Grotesk Bold "sp" on an Ink
node with a Coral dot), written by the build, so it needs no font.
`design/og-card.html` is the editable source for the 1200×630 share image.
The checked-in PNG is a Chromium screenshot of that HTML at the intended size.
If changing identity/role, update and recapture the share image as well.
No external stock images, generated portraits, icon font libraries, or trackers.
