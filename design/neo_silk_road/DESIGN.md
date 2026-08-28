---
name: Neo-Silk Road
colors:
  surface: '#fff8f1'
  surface-dim: '#e2d9cb'
  surface-bright: '#fff8f1'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fcf2e4'
  surface-container: '#f6eddf'
  surface-container-high: '#f0e7d9'
  surface-container-highest: '#eae1d4'
  on-surface: '#1f1b13'
  on-surface-variant: '#43474c'
  inverse-surface: '#343027'
  inverse-on-surface: '#f9f0e1'
  outline: '#74777d'
  outline-variant: '#c4c6cc'
  surface-tint: '#4f6073'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#0a1d2d'
  on-primary-container: '#748699'
  inverse-primary: '#b6c8de'
  secondary: '#7d5700'
  on-secondary: '#ffffff'
  secondary-container: '#ffc24f'
  on-secondary-container: '#725000'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#291800'
  on-tertiary-container: '#ae7a25'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d2e4fb'
  primary-fixed-dim: '#b6c8de'
  on-primary-fixed: '#0a1d2d'
  on-primary-fixed-variant: '#37485a'
  secondary-fixed: '#ffdeaa'
  secondary-fixed-dim: '#f9bc49'
  on-secondary-fixed: '#271900'
  on-secondary-fixed-variant: '#5f4100'
  tertiary-fixed: '#ffddb2'
  tertiary-fixed-dim: '#f9bb61'
  on-tertiary-fixed: '#291800'
  on-tertiary-fixed-variant: '#624000'
  background: '#fff8f1'
  on-background: '#1f1b13'
  surface-variant: '#eae1d4'
  white: '#FFFFFF'
  golden-beige: '#C9A66B'
typography:
  display-lg:
    fontFamily: Libre Caslon Text
    fontSize: 48px
    fontWeight: '400'
    lineHeight: '1.1'
    letterSpacing: -0.02em
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
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.08em
  caption:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin-mobile: 16px
  container-max: 1280px
---

## Brand & Style

This design system embodies the **Modern Neo-Silk Road** aesthetic, a visual bridge between the historic grandeur of Central Asian heritage and the technical precision of modern luxury travel. The personality is **authoritative, hospitable, and culturally rich**, avoiding the sterile nature of contemporary SaaS in favor of a "literary-luxe" feel.

The style is characterized by **High-Contrast Layering** and **Architectural Geometry**. It utilizes a sophisticated interplay between "Deep Navy" and "Warm Cream," punctuated by gold accents that mimic the sun-drenched domes of Samarkand. Unlike generic modernism, this system uses intentional decoration—subtle Uzbek geometric motifs and fine gold borders—to create a sense of place and exclusivity. The result is a UI that feels like a premium travel journal: grounded, tactile, and deeply evocative.

## Colors

The palette is anchored by the depth of the night sky and the luster of precious metals.

- **Deep Navy (#071A2A):** The foundation. Used for primary backgrounds, navigation, and administrative interfaces to project stability and luxury.
- **Warm Gold (#D9A02E):** The functional spark. Reserved for primary CTAs, active states, and critical price information.
- **Dark Gold (#A87520):** The refinement layer. Used for hover states, interactive borders, and intricate decorative patterns.
- **Warm Cream / Ivory (#F4EBDD):** The canvas. This provides a soft, organic alternative to white for content areas, ensuring the UI feels warm and approachable rather than clinical.
- **Golden Beige (#C9A66B):** The supporting detail. Used for secondary text and delicate dividers.
- **White (#FFFFFF):** High-contrast utility. Exclusively for text on navy backgrounds or specific high-visibility labels.

## Typography

This system pairs the intellectual weight of a classical serif with the technical precision of a monospaced-influenced sans-serif.

- **Libre Caslon Text** is the voice of the brand. It is used for all headlines and display copy. In "Dark Mode" (Navy backgrounds), headlines should be set in White or Warm Gold. On "Light Mode" (Cream backgrounds), headlines transition to Deep Navy to maintain authority.
- **Geist** provides a clean, technical UI layer. Its monospaced roots ensure that data—such as flight times, prices, and itinerary details—looks structured and reliable. 
- **Label-MD** uses uppercase Geist with generous tracking to create an architectural, "wayfinding" feel for navigation and metadata.

## Layout & Spacing

The layout philosophy is based on a **Fixed Grid** model that emphasizes editorial pacing and focus.

- **Grid:** A 12-column grid is used for desktop (max 1280px), centered within the viewport. Mobile uses a 4-column fluid grid.
- **Rhythm:** An 8px base unit controls all internal padding and alignment.
- **Verticality:** Large `xl` (80px) gaps are used between major content sections to prevent information overload and maintain a premium, airy feel.
- **Reflow:** On mobile, margins reduce to 16px. Display typography scales aggressively to ensure readability without sacrificing the distinctive serif character.

## Elevation & Depth

Hierarchy is established through **Tonal Layering** and **High-Contrast Outlines** rather than physical shadows.

- **Surfaces:** Depth is created by stacking Navy elements on Cream backgrounds (or vice-versa).
- **Outlines:** Instead of ambient shadows, elements use 1px borders. 
    - **Dark Cards:** Navy background with a `Dark Gold (#A87520)` border.
    - **Light Cards:** Cream background with a subtle `Warm Gold (#D9A02E)` border.
- **Focus States:** Active or floating elements (like dropdowns) may use a very subtle tinted shadow: 10px blur, 5% opacity, using the Deep Navy color to maintain a "cool" and integrated depth.

## Shapes

The shape language is **Softly Architectural**. A `roundedness` level of 2 (0.5rem / 8px) is applied to all standard UI components to provide a modern, approachable touch that softens the rigidity of the Deep Navy blocks.

- **Components:** Buttons and input fields use 8px corners.
- **Large Elements:** Hero sections and large image containers use `rounded-xl` (1.5rem / 24px) to create a "framed" feel.
- **Decorative:** Uzbek geometric patterns used in corners or dividers remain sharp and mathematical, providing a structural counterpoint to the rounded UI elements.

## Components

### Buttons
- **Primary:** Solid `Warm Gold (#D9A02E)` background with `Deep Navy (#071A2A)` text. Bold Geist font.
- **Secondary:** Transparent background with a 1.5px `Warm Gold` or `Deep Navy` border depending on the parent surface.
- **Hover:** Transition to `Dark Gold (#A87520)` for primary buttons to indicate depth.

### Cards
- **Dark Theme:** `Deep Navy` fill, `Dark Gold` 1px border. Headlines in `White`.
- **Light Theme:** `Warm Cream` fill, `Warm Gold` 1px border. Headlines in `Deep Navy`.
- **Styling:** Consistent 24px internal padding and 8px corner radius.

### Input Fields
- **Base:** `Warm Cream` background with a `Golden Beige (#C9A66B)` border.
- **Focus:** Border transitions to `Warm Gold (#D9A02E)` with a subtle inner glow. Labels use Geist (Label-MD) in `Deep Navy`.

### Dividers & Patterns
- **Geometric Accents:** Subtle Uzbek tile patterns are used as watermarks in the corners of sections or as 1px "pattern-lines" to separate content.
- **Dividers:** Use `Golden Beige` at 30% opacity for a soft, sophisticated separation.

### Status & Chips
- **Pricing:** Always rendered in `Warm Gold` using the Geist font to emphasize the technical value.
- **Badges:** Pill-shaped with Navy backgrounds and Gold borders for high-importance status indicators.