/**
 * Tailwind CLI config (NOT the CDN script — CLAUDE.md §2/§3).
 * Color tokens, type scale, spacing and radius below are copied verbatim
 * from CLAUDE.md §3 "Design system". Do not add Material Design tokens or
 * extra colors — this is the complete palette.
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
      },
      fontFamily: {
        serif: ["Playfair Display", "Georgia", "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
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
