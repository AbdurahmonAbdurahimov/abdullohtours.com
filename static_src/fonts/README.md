# Fonts

This project self-hosts two typefaces (CLAUDE.md §3) — never hotlink Google
Fonts. Both are real WOFF2 files fetched from Google Fonts' own CDN
(fonts.gstatic.com) and vendored here, split per script subset:

```
playfair-display-latin.woff2
playfair-display-latin-ext.woff2
playfair-display-cyrillic.woff2
inter-latin.woff2
inter-latin-ext.woff2
inter-cyrillic.woff2
inter-cyrillic-ext.woff2
```

Both families are **variable fonts** (confirmed via each file's `fvar`
table — Inter's `wght` axis is 100–900, Playfair Display's is 400–900), so
one file per subset covers every weight the type scale uses (400/500/600
Inter, 400/700 Playfair) via `font-weight: <min> <max>` range declarations
in `static_src/input.css` — not a separate static file per weight. Playfair
Display has no distinct `cyrillic-ext` offering on Google Fonts (only
`latin`/`latin-ext`/`cyrillic`), which is why it has one fewer file than
Inter.

Splitting into subsets (rather than one merged file per family) means a
page only downloads the script it's actually rendering — a Latin-only page
never fetches the Cyrillic glyphs, and vice versa — via each `@font-face`
block's `unicode-range`.

`static_src/input.css` declares the matching `@font-face` rules, each
pointing at `/static/fonts/<file>.woff2` (absolute from `STATIC_URL`, not a
path relative to this directory — Tailwind CLI doesn't rewrite `url()`s it
finds in the source, so a relative path resolves against wherever the
*compiled* `static_src/css/main.css` ends up served from, not against
`static_src/` itself).

To refresh these (e.g. adding a weight/style Google later drops from the
variable axis, or a script this project starts supporting): fetch
`https://fonts.googleapis.com/css2?family=<Family>:wght@<weights>&display=swap`
with a modern browser User-Agent (Google serves legacy TTF/EOT to old/no
UA strings), download each subset's `src: url(...)`, and update the
`unicode-range` values here from that response — don't hand-roll them.
