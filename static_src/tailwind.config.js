/**
 * Tailwind CLI config (NOT the CDN script — CLAUDE.md §2/§3).
 * Color tokens, type scale, spacing and radius below are copied verbatim
 * from CLAUDE.md §3 "Design system". Do not add Material Design tokens or
 * extra colors — the `colors` block is the complete palette.
 *
 * The `semantic` colors underneath it are NOT new brand colours: each one
 * resolves at runtime to one of the palette values above via a CSS custom
 * property (see static_src/input.css), so the same template markup renders
 * correctly in both light and dark mode without doubling every colour class
 * into a `x dark:y` pair. Use these in templates; reach for a raw palette
 * name only when an element is deliberately one fixed colour in both themes
 * (e.g. gold CTAs, or the permanently-navy hero overlay).
 */
/** @type {import('tailwindcss').Config} */
module.exports = {
  // Paths are resolved relative to the process's cwd (project root), since
  // npm scripts (package.json) invoke the Tailwind CLI from there — not
  // relative to this config file's own directory.
  content: [
    "templates/**/*.html",
    "apps/**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        navy: "#071A2A",
        "navy-soft": "#0A1D2D",
        gold: "#C9A66B",
        "gold-bright": "#D9A02E",
        cream: "#FFF8F1",
        "cream-soft": "#FCF2E4",
        ink: "#1F1B13",
        muted: "#43474C",
        line: "#C4C6CC",

        // Theme-aware aliases. `<alpha-value>` keeps Tailwind's opacity
        // modifiers working (e.g. `bg-surface/60`), which plain
        // `var(--x)` colours would silently break.
        surface: "rgb(var(--c-surface) / <alpha-value>)",
        "surface-alt": "rgb(var(--c-surface-alt) / <alpha-value>)",
        "surface-raised": "rgb(var(--c-surface-raised) / <alpha-value>)",
        content: "rgb(var(--c-content) / <alpha-value>)",
        "content-muted": "rgb(var(--c-content-muted) / <alpha-value>)",
        hairline: "rgb(var(--c-hairline) / <alpha-value>)",
      },
      fontFamily: {
        // Playfair Display and Inter have no Arabic coverage, so the Noto
        // Arabic faces sit directly behind them in each stack: the browser
        // falls through per-glyph, meaning Arabic text picks up Noto while
        // Latin/Cyrillic still renders in the brand faces. No conditional
        // font-family per language needed.
        serif: ["Playfair Display", "Noto Naskh Arabic", "Georgia", "serif"],
        sans: ["Inter", "Noto Sans Arabic", "system-ui", "sans-serif"],
      },
      fontSize: {
        display: ["32px", { lineHeight: "1.2" }],
        "display-md": ["52px", { lineHeight: "1.2" }],
        h1: ["28px", { lineHeight: "1.25" }],
        "h1-md": ["44px", { lineHeight: "1.25" }],
        h2: ["24px", { lineHeight: "1.3" }],
        "h2-md": ["32px", { lineHeight: "1.3" }],
        h3: ["20px", { lineHeight: "1.35" }],
        "h3-md": ["24px", { lineHeight: "1.35" }],
        body: ["16px", { lineHeight: "1.6" }],
        small: ["14px", { lineHeight: "1.5" }],
        label: ["13px", { lineHeight: "1.4", letterSpacing: "0.08em" }],
      },
      spacing: {
        xs: "4px",
        sm: "12px",
        base: "8px",
        md: "24px",
        lg: "48px",
        xl: "80px",
      },
      maxWidth: {
        container: "1280px",
      },
      borderRadius: {
        DEFAULT: "4px",
        lg: "8px",
        xl: "12px",
        full: "9999px",
      },
    },
  },
  plugins: [],
};
