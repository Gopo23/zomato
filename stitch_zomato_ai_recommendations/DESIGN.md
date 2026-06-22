---
name: Culinary Intelligence
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1b1b1b'
  on-surface-variant: '#5b403f'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#7b5800'
  on-secondary: '#ffffff'
  secondary-container: '#fcb802'
  on-secondary-container: '#6a4b00'
  tertiary: '#5c5c5c'
  on-tertiary: '#ffffff'
  tertiary-container: '#757474'
  on-tertiary-container: '#fffcfb'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#ffdea6'
  secondary-fixed-dim: '#ffbb12'
  on-secondary-fixed: '#271900'
  on-secondary-fixed-variant: '#5d4200'
  tertiary-fixed: '#e4e2e1'
  tertiary-fixed-dim: '#c8c6c6'
  on-tertiary-fixed: '#1b1c1c'
  on-tertiary-fixed-variant: '#474747'
  background: '#fcf9f8'
  on-background: '#1b1b1b'
  surface-variant: '#e5e2e1'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 48px
  xl: 80px
  container-max: 1280px
  gutter: 20px
---

## Brand & Style
The design system is engineered for an AI-driven restaurant discovery experience that balances technological precision with the warmth of hospitality. The brand personality is authoritative yet inviting, functioning as a "digital concierge" that understands personal taste.

The visual style follows a **Modern Corporate** aesthetic with **Tactile** accents. It prioritizes high-quality food photography and clear information hierarchy. To evoke a premium feel, the interface utilizes generous whitespace, subtle depth through layering, and purposeful motion. The emotional response is one of reliability and appetite—users should feel confident in the AI's recommendations while feeling immersed in the culinary world.

## Colors
The palette is led by a signature "Warm Red" (#E23744), designed to stimulate appetite and signify the energy of the dining industry. This is supported by a clean, paper-white background to ensure food photography remains the focal point.

- **Primary:** Warm Red is used for key actions, branding, and active states.
- **Secondary (Accents):** A gold/yellow spectrum is reserved for ranking badges and star ratings.
- **Neutrals:** A range of grays from #1C1C1C (Primary Text) to #F8F8F8 (Panel backgrounds) provides structural contrast without visual noise.
- **Compliance:** All text-to-background combinations must maintain a minimum 4.5:1 contrast ratio (WCAG AA). Decorative elements and disabled states may use softer grays.

## Typography
Inter is used across the entire system to provide a systematic, clean, and highly legible experience. The hierarchy relies on significant weight shifts (from 400 to 800) to distinguish between editorial content and functional data.

Large headlines use a tight negative letter-spacing to appear more modern and impactful. Labels and secondary metadata use a slightly increased letter-spacing to maintain legibility at smaller sizes. For mobile views, large display type should scale down to prevent excessive line-breaking, prioritizing "headline-lg-mobile" for page titles.

## Layout & Spacing
The layout uses a **Fluid Grid** system based on an 8px rhythm. For desktop, a 12-column grid with 20px gutters is standard. On mobile, the system transitions to a single-column layout with 16px side margins.

- **Margins:** Use `lg` (48px) for vertical section spacing on desktop, scaling to `md` (24px) on mobile.
- **Component Padding:** Internal card padding should consistently be `sm` (16px) or `md` (24px) depending on the density of information.
- **Reflow:** AI suggestion carousels should allow partial visibility of the next item on mobile to signal horizontal scrollability.

## Elevation & Depth
Depth is used to signify interactivity and priority. The system employs **Ambient Shadows** and **Tonal Layers**.

- **Level 0 (Flat):** Main background surface (#FFFFFF).
- **Level 1 (Subsurface):** Used for input fields and layout containers (#F8F8F8). Uses a subtle 1px inner border (#E8E8E8) instead of a shadow.
- **Level 2 (Cards):** Standard restaurant cards use a soft, diffused shadow: `0px 4px 12px rgba(0, 0, 0, 0.08)`.
- **Level 3 (Hover/Active):** When a user hovers over a card, the elevation increases (`0px 12px 24px rgba(0, 0, 0, 0.12)`) and the element lifts slightly (-4px Y-axis) to provide tactile feedback.
- **Level 4 (Modals/Overlays):** Heavy diffusion to focus attention, paired with a 40% opacity neutral-dark backdrop.

## Shapes
The shape language is "Rounded," reflecting a friendly and approachable personality. 

- **Standard (8px):** Applied to restaurant cards, primary buttons, and input fields.
- **Large (16px):** Applied to promotional banners and AI chat containers.
- **Extra Large (24px/Pill):** Used exclusively for filter chips and status badges (e.g., "Open Now").
- **Image Treatment:** Photos within cards should always inherit the parent container's 8px radius for a cohesive, professional look.

## Components

### Buttons & Chips
- **Primary Button:** Solid Warm Red background, white text. 8px radius. Subtle scale-down effect on click (0.98x).
- **Secondary Button:** White background with a 1px border (#E8E8E8).
- **Filter Chips:** Pill-shaped. Inactive: #F8F8F8 background with dark text. Active: Warm Red background or a thick Warm Red border.

### Restaurant Cards
- **Structure:** Top-aligned image (16:9 ratio), followed by title, rating badge, and AI "Match Score." 
- **Interaction:** Hover triggers a lift effect and a slight darkening of the image to make white text overlays more legible.

### Rank Badges
- **Gold/Silver/Bronze:** Circular or shield-shaped icons with a gradient finish to imply metallic quality. They should appear in the top-left corner of the restaurant card, slightly overlapping the image.

### Form Controls
- **Search Bar:** Large, centered, with a Level 2 shadow. Includes an "AI Magic" icon to differentiate the smart search from standard filters.
- **Checkboxes/Radios:** Use the Primary Warm Red for active states.

### AI Insights Panel
- A distinct component using the #F8F8F8 background and a unique "Sparkle" icon. It uses `body-md` italicized text to separate AI-generated rationale from hard data.