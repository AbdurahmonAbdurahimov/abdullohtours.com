---
name: Modern Silk Road
colors:
  surface: '#faf8ff'
  surface-dim: '#dad9e0'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f9'
  surface-container: '#efedf3'
  surface-container-high: '#e9e7ee'
  surface-container-highest: '#e3e2e8'
  on-surface: '#1a1b20'
  on-surface-variant: '#444650'
  inverse-surface: '#2f3035'
  inverse-on-surface: '#f1f0f6'
  outline: '#757682'
  outline-variant: '#c5c6d2'
  surface-tint: '#435b9f'
  primary: '#00113a'
  on-primary: '#ffffff'
  primary-container: '#002366'
  on-primary-container: '#758dd5'
  inverse-primary: '#b3c5ff'
  secondary: '#5f5e58'
  on-secondary: '#ffffff'
  secondary-container: '#e5e2da'
  on-secondary-container: '#65645e'
  tertiary: '#001720'
  on-tertiary: '#ffffff'
  tertiary-container: '#002d3b'
  on-tertiary-container: '#2a9bc1'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b3c5ff'
  on-primary-fixed: '#00174a'
  on-primary-fixed-variant: '#2a4386'
  secondary-fixed: '#e5e2da'
  secondary-fixed-dim: '#c9c6bf'
  on-secondary-fixed: '#1c1c17'
  on-secondary-fixed-variant: '#474741'
  tertiary-fixed: '#bce9ff'
  tertiary-fixed-dim: '#6fd3fa'
  on-tertiary-fixed: '#001f29'
  on-tertiary-fixed-variant: '#004d63'
  background: '#faf8ff'
  on-background: '#1a1b20'
  surface-variant: '#e3e2e8'
typography:
  display-lg:
    fontFamily: Libre Caslon Text
    fontSize: 48px
    fontWeight: '400'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  display-md:
    fontFamily: Libre Caslon Text
    fontSize: 36px
    fontWeight: '400'
    lineHeight: '1.2'
  headline-lg:
    fontFamily: Libre Caslon Text
    fontSize: 32px
    fontWeight: '400'
    lineHeight: '1.3'
  headline-lg-mobile:
    fontFamily: Libre Caslon Text
    fontSize: 28px
    fontWeight: '400'
    lineHeight: '1.3'
  headline-md:
    fontFamily: Libre Caslon Text
    fontSize: 24px
    fontWeight: '400'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  container-max: 1280px
  gutter: 24px
---

## Brand & Style
The design system for this private travel service evokes the quiet confidence of heritage and the precision of high-end logistics. The brand personality is **distinguished, scholarly, and hospitable**, catering to global travelers seeking authentic, high-quality experiences in Uzbekistan.

The aesthetic follows a **Contemporary Corporate** style infused with **Minimalist Editorial** principles. It leverages significant whitespace to signal luxury and focuses on the interplay between rigid structural grids and classical typography. Visual interest is generated through subtle geometric motifs inspired by Islamic architecture—specifically the rhythmic patterns of tilework—used as faint watermarks or divider accents rather than overt decoration. 

The emotional response should be one of "effortless discovery": the UI remains unobtrusive to let high-end photography of Samarkand and Bukhara speak, while the functional elements feel solid and reliable.

## Colors
The palette is rooted in the "Deep Navy" (#002366), representing trust and the vastness of the night sky over the desert. This is contrasted by "Warm Sand" (#F5F2EA) which serves as a softer, sophisticated alternative to pure white for surfaces and containers.

- **Primary (Deep Navy):** Used for navigation, primary actions, and authoritative headers.
- **Secondary (Warm Sand):** Used for large section backgrounds and container fills to provide a premium, tactile feel.
- **Accent (Samarkand Blue):** A muted turquoise used for interactive elements, highlights, and status indicators related to "Active" or "Confirmed" states.
- **Supporting Accent (Terracotta):** Used sparingly for notifications, specific "Special Offer" calls to action, or to highlight architectural details in iconography.
- **Neutral (Warm Off-White):** The base canvas color to ensure the UI feels airy and clean.

## Typography
This design system employs a **Safe** typographic pairing that balances historical weight with modern utility. 

**Libre Caslon Text** is utilized for all display and headline levels. Its classical proportions and sharp serifs provide a literary quality that echoes travel journals and prestigious editorial features. 

**Inter** handles all functional UI, body copy, and data-heavy tables. It is chosen for its exceptional legibility at small sizes and its neutral character, which prevents the UI from feeling "over-designed." 

Use uppercase styling for **Label-MD** with slight letter spacing to create a professional, architectural feel in navigation and small headings.

## Layout & Spacing
The layout follows a **12-column fixed grid** for desktop, centering the content at a maximum width of 1280px. This creates a focused, high-end gallery feel.

- **Rhythm:** An 8px base grid drives all internal component spacing. 
- **Margins:** Generous outer margins (48px+) are used on desktop to ensure the content never feels cramped.
- **Vertical Spacing:** High-level sections should be separated by `xl` (80px) spacing to maintain the "Editorial" breathing room.
- **Mobile:** Transition to a fluid 4-column grid with 16px gutters and 16px side margins. Large display headings should scale down to `headline-lg-mobile`.

## Elevation & Depth
To maintain a premium feel, the design system avoids heavy shadows, instead using **Tonal Layering** and **Low-Contrast Outlines**.

1.  **Surfaces:** The primary background is `FAF9F6`. Elevated elements (like cards) use a `FFFFFF` background or a very subtle `F5F2EA` fill.
2.  **Depth:** Depth is indicated by a 1px border using a 10% opacity version of the Deep Navy primary color.
3.  **Active State Elevation:** Only "floating" elements like dropdowns or modal dialogs use an **Ambient Shadow**: a soft, highly diffused 20px blur with only 5% opacity, tinted with the primary navy color to keep the shadow "cool" and integrated.

## Shapes
The shape language is **Soft and Precise**. A `roundedness` level of 1 (0.25rem / 4px) is applied to buttons, input fields, and small UI elements. 

For larger elements like **Cards** and **Featured Imagery**, a `rounded-lg` (8px) corner is used. This subtle rounding provides a modern touch without sacrificing the professional, slightly formal tone of the brand. Geometric decorative patterns should always utilize sharp 90-degree or 45-degree angles to maintain their architectural authenticity.

## Components

### Buttons
- **Primary:** Solid Deep Navy fill with white Inter (Bold) text. No gradient. 4px corner radius.
- **Secondary:** Transparent fill with a 1.5px Deep Navy border.
- **Tertiary (Action):** Samarkand Blue text with a subtle underline, used for "View Details" or "Explore More."

### Cards
- **Destination Cards:** Use 8px rounded corners. The image should be the primary focus with a 24px padding area below for the Libre Caslon title. A subtle 1px border (#002366 at 10% opacity) defines the card boundary.
- **Pricing Cards:** Use the Warm Sand (#F5F2EA) as a background fill to distinguish them from content cards.

### Form Elements (Tour Builder)
- **Inputs:** 1px border in a mid-grey, moving to Deep Navy on focus. Labels sit above the field in Inter (Label-MD) style.
- **Checkboxes/Radios:** Use the Samarkand Blue for checked states to provide a clear but soft visual confirmation.

### Data Tables (Admin)
- **Header:** Light sand background with uppercase Inter labels.
- **Rows:** White background with a single-pixel horizontal divider. No vertical lines.
- **Typography:** Shift to `body-md` for row data to maximize information density while maintaining legibility.

### Status Badges
- **Confirmed:** Soft Samarkand Blue background with white text.
- **Pending:** Light Grey background with Deep Navy text.
- **Special/Priority:** Terracotta background with white text.
- **Style:** Pill-shaped (rounded-xl) with small-caps typography.