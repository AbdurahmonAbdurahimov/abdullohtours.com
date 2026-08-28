# Fonts

This project self-hosts two typefaces (CLAUDE.md §3) — never hotlink Google
Fonts, and both families must support Cyrillic for the Russian version of
the site.

Place these real WOFF2 binaries here (not included in this scaffold pass —
do not fabricate placeholder binary files):

```
playfair-display-400.woff2
playfair-display-700.woff2
inter-400.woff2
inter-500.woff2
inter-600.woff2
```

Both Playfair Display and Inter have Cyrillic subsets available via Google
Fonts (fonts.google.com) — download the desired weights, convert to WOFF2
if needed (e.g. via `fonttools varLib.instancer` + `woff2_compress`, or
google-webfonts-helper), and drop the files here. `static_src/input.css`
already declares the matching `@font-face` rules with `font-display: swap`.
