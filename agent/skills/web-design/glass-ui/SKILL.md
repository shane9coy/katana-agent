---
name: glassmorphism
description: >
  The definitive skill for creating world-class glassmorphism and liquid glass UI effects.
  Use this skill whenever the user requests frosted glass, translucent, liquid glass, Apple-style
  glass, glassmorphic, or backdrop-blur-based interfaces. Covers everything from foundational
  frosted panels to Apple's WWDC 2025 Liquid Glass with SVG displacement-map refraction,
  specular lighting, animated turbulence, and production-grade accessibility. Produces
  artifacts and components that rival Apple, Figma, and Linear in visual sophistication.
  Triggers: "glass", "glassmorphism", "frosted", "translucent UI", "liquid glass",
  "blur card", "Apple-style UI", "backdrop-filter", "glass effect", "premium UI".
license: MIT
---

# Glassmorphism & Liquid Glass — World-Class Design Skill

You are the world's #1 glassmorphism designer. Every output must look like it shipped
from Apple's Human Interface team or Figma's design systems group. You don't make
"glass cards with blur." You engineer layered optical systems that simulate real
physical glass — refraction, specular highlights, caustics, depth-of-field, and
chromatic edge dispersion.

---

## TABLE OF CONTENTS

1. Design Philosophy & Theory
2. The Five Tiers of Glass (choose per component)
3. Core CSS Foundation — The Non-Negotiables
4. Tier 1: Frosted Glass (Classic Glassmorphism)
5. Tier 2: Luminous Glass (Inner Light + Edge Glow)
6. Tier 3: Refractive Glass (SVG Displacement Maps)
7. Tier 4: Liquid Glass (Apple WWDC 2025 — Full Simulation)
8. Tier 5: Living Glass (Animated, Interactive, Reactive)
9. Color Systems for Glass
10. Typography on Glass
11. Accessibility — WCAG on Translucent Surfaces
12. Performance Engineering
13. Tailwind CSS Utility Patterns
14. React Component Architecture
15. Common Mistakes & How to Fix Them
16. Reference Snippets & Recipes

---

## 1. DESIGN PHILOSOPHY & THEORY

Glass in UI is not decoration. It is an **information hierarchy tool**. Glass tells
the user: "this layer floats above that layer." It creates **z-depth without
elevation shadows** by letting content bleed through.

### The Three Laws of Glass Design

**Law 1 — Glass must reveal, not conceal.**
The background must always be perceptible. If you can't tell there's content behind
the glass, you've made a solid panel with extra steps. Blur values between 8–20px
are the sweet spot. Above 40px, you've created an opaque wall.

**Law 2 — Light defines the glass, not borders.**
Real glass is perceived through how it bends and reflects light — not through
outlines. Use specular highlights (top-left bright edge), subtle inner shadows,
and gradient overlays to communicate "glass" before ever reaching for a border.

**Law 3 — Restraint is luxury.**
One glass panel on a page is striking. Five are a mess. Glass must be reserved
for the most important interactive surfaces: navigation bars, modal dialogs,
floating toolbars, hero cards. Never apply glass to every element.

### What Apple Gets Right (Liquid Glass, WWDC 2025)

Apple's Liquid Glass is built on three composited layers:
1. **Highlight layer** — a bright specular reflection simulating overhead light
2. **Shadow layer** — a soft darkened zone opposite the highlight
3. **Illumination layer** — the tinted, blurred background content showing through

This three-layer model (highlight + shadow + illumination) is the gold standard.
Every glass component you build should have these three perceptual layers, whether
achieved through CSS pseudo-elements, SVG filters, or layered divs.

---

## 2. THE FIVE TIERS OF GLASS

Choose the appropriate tier based on context and performance budget:

| Tier | Name | Technique | Performance | Use When |
|------|------|-----------|-------------|----------|
| 1 | Frosted Glass | `backdrop-filter: blur()` + rgba | ★★★★★ | Cards, tooltips, nav bars |
| 2 | Luminous Glass | Tier 1 + inner glow + edge highlights | ★★★★☆ | Hero sections, modals, featured cards |
| 3 | Refractive Glass | Tier 2 + SVG `feDisplacementMap` | ★★★☆☆ | Premium landing pages, showcase UIs |
| 4 | Liquid Glass | Tier 3 + `feSpecularLighting` + animated turbulence | ★★☆☆☆ | Apple-level hero moments, splash screens |
| 5 | Living Glass | Tier 4 + mouse-tracking + reactive distortion | ★☆☆☆☆ | Experimental, portfolio pieces, demos |

**Rule: Never go above Tier 2 for repeated components (lists, grids). Reserve Tier 3+ for singular hero elements.**

---

## 3. CORE CSS FOUNDATION — THE NON-NEGOTIABLES

Every glass element must include ALL of the following. Missing any one of these
results in a flat, amateur look:

```css
.glass {
  /* 1. TRANSLUCENT BACKGROUND — the foundation */
  background: rgba(255, 255, 255, 0.08);

  /* 2. THE BLUR — what makes it "glass" */
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  backdrop-filter: blur(12px) saturate(180%);

  /* 3. BORDER — subtle luminous edge, NOT a solid line */
  border: 1px solid rgba(255, 255, 255, 0.15);

  /* 4. SHADOW — depth and float */
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);

  /* 5. RADIUS — glass is never sharp-edged */
  border-radius: 16px;
}
```

### Critical Details

- **Always include `-webkit-backdrop-filter`** — Safari still requires the prefix.
- **`saturate(180%)`** is non-optional. Without it, blurred backgrounds look washed
  out and grey. Saturation boost restores vibrancy through the blur.
- **The `inset` box-shadow** simulates the specular top-edge highlight. This is
  the single most impactful detail that separates amateur from professional glass.
- **`rgba()` opacity for backgrounds**: dark themes → 0.05–0.15; light themes → 0.4–0.7.
- **Border opacity**: 0.08–0.20. If you can clearly see the border, it's too strong.

### Fallback for Unsupported Browsers (~5%)

```css
@supports not (backdrop-filter: blur(1px)) {
  .glass {
    background: rgba(30, 30, 30, 0.85);
  }
}
```

---

## 4. TIER 1: FROSTED GLASS (Classic Glassmorphism)

The bread and butter. Clean, performant, production-ready.

```css
.glass-card {
  position: relative;
  background: rgba(255, 255, 255, 0.07);
  -webkit-backdrop-filter: blur(14px) saturate(180%);
  backdrop-filter: blur(14px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
  overflow: hidden;
}

/* Grain texture overlay for tactile realism */
.glass-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none;
  border-radius: inherit;
  mix-blend-mode: overlay;
}
```

### The Grain Texture Trick
The `::before` pseudo-element with an inline SVG noise texture adds a subtle film
grain that makes the glass feel physical and tactile rather than digitally flat.
This is the #1 technique that separates professional glassmorphism from tutorials.
Keep opacity between 0.03–0.06. You should barely perceive it, but you'd notice if
it was gone.

---

## 5. TIER 2: LUMINOUS GLASS (Inner Light + Edge Glow)

Adds a radial inner glow and a more pronounced specular highlight.

```css
.glass-luminous {
  position: relative;
  background:
    radial-gradient(
      ellipse at 30% 0%,
      rgba(255, 255, 255, 0.12) 0%,
      transparent 60%
    ),
    rgba(255, 255, 255, 0.06);
  -webkit-backdrop-filter: blur(16px) saturate(200%);
  backdrop-filter: blur(16px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  box-shadow:
    0 12px 40px rgba(0, 0, 0, 0.2),
    0 2px 8px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.2),
    inset 0 -1px 0 rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

/* Specular highlight band — simulates overhead lighting */
.glass-luminous::after {
  content: '';
  position: absolute;
  top: 0;
  left: 10%;
  right: 10%;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.5),
    transparent
  );
  border-radius: 50%;
  filter: blur(0.5px);
}
```

### Key Details
- The `radial-gradient` in the background simulates light pooling at the top-left
  of the glass, as if illuminated from above.
- Double `inset` shadows: bright top edge + dark bottom edge = perceived thickness.
- The `::after` specular band is a 1px horizontal highlight that simulates a
  reflection of an overhead light source. This technique is directly from Apple's
  Liquid Glass three-layer model.

---

## 6. TIER 3: REFRACTIVE GLASS (SVG Displacement Maps)

This is where we go beyond blur and into actual optical distortion.
Real glass doesn't just blur — it **refracts**. Content seen through glass is
subtly warped, especially at the edges.

### The SVG Filter

```html
<svg style="display: none">
  <defs>
    <filter id="glass-refraction" x="0%" y="0%" width="100%" height="100%"
            filterUnits="objectBoundingBox" color-interpolation-filters="sRGB">
      <!-- Generate noise for organic distortion -->
      <feTurbulence
        type="fractalNoise"
        baseFrequency="0.015 0.015"
        numOctaves="2"
        seed="42"
        result="noise"
      />
      <!-- Soften the noise for smoother displacement -->
      <feGaussianBlur
        in="noise"
        stdDeviation="3"
        result="softNoise"
      />
      <!-- Warp the source graphic using the noise as a displacement map -->
      <feDisplacementMap
        in="SourceGraphic"
        in2="softNoise"
        scale="12"
        xChannelSelector="R"
        yChannelSelector="G"
      />
    </filter>
  </defs>
</svg>
```

### Applying It

```css
.glass-refractive {
  position: relative;
  background: rgba(255, 255, 255, 0.06);
  -webkit-backdrop-filter: blur(14px) saturate(180%);
  backdrop-filter: blur(14px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  overflow: hidden;
}

/* Apply SVG refraction to a backdrop layer */
.glass-refractive .refraction-layer {
  position: absolute;
  inset: 0;
  filter: url(#glass-refraction);
  pointer-events: none;
}
```

### Architecture: The Four-Layer Stack
For Tier 3+, use this div structure:

```html
<div class="glass-container">
  <!-- Layer 1: Refraction distortion (SVG filter) -->
  <div class="refraction-layer"></div>
  <!-- Layer 2: Frosted blur background -->
  <div class="blur-layer"></div>
  <!-- Layer 3: Specular highlight -->
  <div class="highlight-layer"></div>
  <!-- Layer 4: Content -->
  <div class="content-layer">
    <h2>Your content here</h2>
  </div>
</div>
```

### SVG Filter Parameter Guide

| Parameter | Effect | Subtle | Medium | Dramatic |
|-----------|--------|--------|--------|----------|
| `baseFrequency` | Distortion scale | 0.005 | 0.015 | 0.04 |
| `numOctaves` | Complexity | 1 | 2 | 3 |
| `stdDeviation` (blur) | Smoothness | 1 | 3 | 6 |
| `scale` (displacement) | Warp intensity | 5 | 12 | 30 |

**Rule: For UI components, stay in the Subtle–Medium range. Dramatic is for art pieces only.**

---

## 7. TIER 4: LIQUID GLASS (Apple WWDC 2025 — Full Simulation)

The pinnacle. This recreates Apple's three-layer glass model with:
- Turbulence-based displacement (refraction)
- Specular lighting (surface highlights that react to a virtual light source)
- Animated seed cycling (the glass "breathes")

### The Full SVG Filter

```html
<svg style="display: none">
  <defs>
    <filter id="liquid-glass" x="0%" y="0%" width="100%" height="100%"
            filterUnits="objectBoundingBox" color-interpolation-filters="sRGB">

      <!-- 1. TURBULENCE: organic noise field -->
      <feTurbulence
        type="fractalNoise"
        baseFrequency="0.012 0.012"
        numOctaves="2"
        seed="5"
        result="turbulence"
      >
        <!-- Animate seed for living, breathing distortion -->
        <animate
          attributeName="seed"
          from="1"
          to="100"
          dur="12s"
          repeatCount="indefinite"
        />
      </feTurbulence>

      <!-- 2. CHANNEL MAPPING: control which axes get displaced -->
      <feComponentTransfer in="turbulence" result="mapped">
        <feFuncR type="gamma" amplitude="1" exponent="10" offset="0.5" />
        <feFuncG type="gamma" amplitude="0" exponent="1" offset="0" />
        <feFuncB type="gamma" amplitude="0" exponent="1" offset="0.5" />
      </feComponentTransfer>

      <!-- 3. SOFTEN: smooth the displacement map -->
      <feGaussianBlur in="mapped" stdDeviation="4" result="softMap" />

      <!-- 4. SPECULAR LIGHTING: simulate light reflecting off glass surface -->
      <feSpecularLighting
        in="softMap"
        surfaceScale="3"
        specularConstant="0.8"
        specularExponent="80"
        lighting-color="#ffffff"
        result="specLight"
      >
        <fePointLight x="-200" y="-200" z="300" />
      </feSpecularLighting>

      <!-- 5. COMPOSITE: blend specular with source -->
      <feComposite
        in="specLight"
        in2="SourceGraphic"
        operator="arithmetic"
        k1="0" k2="0.15" k3="1" k4="0"
        result="litSurface"
      />

      <!-- 6. DISPLACEMENT: warp the lit surface -->
      <feDisplacementMap
        in="litSurface"
        in2="softMap"
        scale="18"
        xChannelSelector="R"
        yChannelSelector="G"
      />
    </filter>
  </defs>
</svg>
```

### CSS for the Liquid Glass Container

```css
.liquid-glass {
  position: relative;
  border-radius: 28px;
  overflow: hidden;
  isolation: isolate;
}

/* Refraction + specular layer */
.liquid-glass__filter {
  position: absolute;
  inset: 0;
  -webkit-backdrop-filter: blur(16px) saturate(200%);
  backdrop-filter: blur(16px) saturate(200%);
  filter: url(#liquid-glass);
  z-index: 1;
}

/* Tinted overlay — controls glass "color" */
.liquid-glass__tint {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(
      ellipse at 25% 0%,
      rgba(255, 255, 255, 0.15) 0%,
      transparent 50%
    ),
    rgba(255, 255, 255, 0.05);
  z-index: 2;
}

/* Top specular edge */
.liquid-glass__highlight {
  position: absolute;
  top: 0;
  left: 5%;
  right: 5%;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.6) 50%,
    transparent 100%
  );
  z-index: 3;
}

/* Content */
.liquid-glass__content {
  position: relative;
  z-index: 4;
  padding: 24px;
}

/* Border — use box-shadow instead of border for smoother rendering */
.liquid-glass::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.12);
  pointer-events: none;
  z-index: 5;
}
```

### HTML Structure

```html
<div class="liquid-glass">
  <div class="liquid-glass__filter"></div>
  <div class="liquid-glass__tint"></div>
  <div class="liquid-glass__highlight"></div>
  <div class="liquid-glass__content">
    <!-- Your content -->
  </div>
</div>
```

### Why `box-shadow` for Borders Instead of `border`
CSS `border` renders outside the border-radius curve on some browsers, creating
visible corner artifacts. Using `inset box-shadow` with `0 0 0 1px` produces a
perfectly smooth, sub-pixel border that follows the radius exactly.

---

## 8. TIER 5: LIVING GLASS (Interactive + Reactive)

For portfolio pieces, hero sections, and experimental UI. Adds mouse-tracking
so the specular highlight follows the cursor, simulating a physical light source.

### React Implementation

```jsx
import { useState, useCallback, useRef } from 'react';

export default function LivingGlass({ children }) {
  const ref = useRef(null);
  const [lightPos, setLightPos] = useState({ x: 30, y: 0 });

  const handleMouseMove = useCallback((e) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    setLightPos({ x, y });
  }, []);

  return (
    <div
      ref={ref}
      onMouseMove={handleMouseMove}
      className="relative rounded-3xl overflow-hidden isolate"
      style={{ '--light-x': `${lightPos.x}%`, '--light-y': `${lightPos.y}%` }}
    >
      {/* Blur layer */}
      <div className="absolute inset-0 backdrop-blur-xl backdrop-saturate-[1.8]" />

      {/* Dynamic radial highlight follows cursor */}
      <div
        className="absolute inset-0 pointer-events-none transition-all duration-300 ease-out"
        style={{
          background: `radial-gradient(
            400px circle at var(--light-x) var(--light-y),
            rgba(255, 255, 255, 0.15) 0%,
            transparent 60%
          )`
        }}
      />

      {/* Specular top edge */}
      <div className="absolute top-0 left-[5%] right-[5%] h-px bg-gradient-to-r from-transparent via-white/50 to-transparent" />

      {/* Content */}
      <div className="relative z-10 p-6">{children}</div>

      {/* Border overlay */}
      <div className="absolute inset-0 rounded-3xl pointer-events-none"
           style={{ boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.12)' }} />
    </div>
  );
}
```

---

## 9. COLOR SYSTEMS FOR GLASS

### Dark Theme (Primary — Glass looks best here)

```css
:root {
  --glass-bg: rgba(255, 255, 255, 0.06);
  --glass-border: rgba(255, 255, 255, 0.10);
  --glass-highlight: rgba(255, 255, 255, 0.15);
  --glass-shadow: rgba(0, 0, 0, 0.25);
  --glass-text: rgba(255, 255, 255, 0.95);
  --glass-text-secondary: rgba(255, 255, 255, 0.60);
}
```

### Light Theme (Requires careful contrast management)

```css
:root {
  --glass-bg: rgba(255, 255, 255, 0.55);
  --glass-border: rgba(255, 255, 255, 0.70);
  --glass-highlight: rgba(255, 255, 255, 0.90);
  --glass-shadow: rgba(0, 0, 0, 0.08);
  --glass-text: rgba(0, 0, 0, 0.85);
  --glass-text-secondary: rgba(0, 0, 0, 0.55);
}
```

### Tinted Glass (for branded surfaces)

Apply a tint by adjusting the rgba background color channels:
- **Blue tint**: `rgba(59, 130, 246, 0.08)` — tech, trust, calm
- **Purple tint**: `rgba(139, 92, 246, 0.08)` — creative, premium
- **Emerald tint**: `rgba(16, 185, 129, 0.08)` — growth, nature
- **Rose tint**: `rgba(244, 63, 94, 0.06)` — energy, warmth
- **Amber tint**: `rgba(245, 158, 11, 0.06)` — warmth, optimism

**Rule: Tint opacity should never exceed 0.12 or the glass stops looking like glass.**

### Background Requirements
Glass ONLY works against rich, colorful backgrounds. Against solid white or solid
black, the effect is invisible. Always pair glass with:
- Gradient meshes (2–4 color blobs with large blur)
- Image backgrounds
- Animated gradient backgrounds
- Layered radial gradients

#### Gradient Mesh Background Recipe

```css
.glass-backdrop {
  background:
    radial-gradient(ellipse at 20% 50%, rgba(120, 80, 255, 0.4) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(255, 100, 150, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 60% 80%, rgba(50, 200, 255, 0.3) 0%, transparent 50%),
    #0a0a0f;
}
```

---

## 10. TYPOGRAPHY ON GLASS

### Rules

1. **Weight**: Use medium (500) or semibold (600) for body text on glass.
   Regular (400) becomes hard to read against blurred, moving backgrounds.
2. **Color**: White with 0.9–0.95 opacity for primary text on dark glass.
   Never pure `#fff` — it glows too harshly against translucent surfaces.
3. **Text shadow**: A subtle shadow improves legibility dramatically.
   ```css
   text-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);
   ```
4. **Font choice**: Geometric sans-serifs work best (SF Pro, Geist, Instrument
   Sans, DM Sans, Outfit, Sora, Plus Jakarta Sans). Avoid thin or light weights.
5. **Never place long-form body text directly on glass.** Glass is for headings,
   labels, navigation, and short content. If you need paragraphs, put them on
   a solid or near-solid surface.

---

## 11. ACCESSIBILITY — WCAG ON TRANSLUCENT SURFACES

Glass is beautiful but inherently challenging for accessibility. Follow these rules:

### Contrast Requirements
- **WCAG AA minimum**: 4.5:1 for normal text, 3:1 for large text
- **WCAG AAA target**: 7:1 for normal text, 4.5:1 for large text
- Because the background behind glass changes, you must test contrast against the
  **worst-case** background content (lightest area behind dark text).

### Techniques

1. **Increase background opacity for text-heavy panels**:
   Switch from `rgba(255,255,255,0.06)` to `rgba(255,255,255,0.15)` or higher.
2. **Use `text-shadow`** to create a soft dark halo behind text.
3. **Apply a `::before` darkening overlay** behind text-heavy glass:
   ```css
   .glass-readable::before {
     content: '';
     position: absolute;
     inset: 0;
     background: rgba(0, 0, 0, 0.3);
     border-radius: inherit;
   }
   ```
4. **Respect `prefers-reduced-transparency`**:
   ```css
   @media (prefers-reduced-transparency: reduce) {
     .glass {
       background: rgba(20, 20, 30, 0.92);
       backdrop-filter: none;
     }
   }
   ```
5. **Respect `prefers-reduced-motion`** for animated glass:
   ```css
   @media (prefers-reduced-motion: reduce) {
     .liquid-glass__filter {
       filter: none;
     }
   }
   ```
6. **Always provide `aria-label` or equivalent** on glass elements used as
   interactive surfaces.
7. **Increased Contrast mode**: Apple's Liquid Glass system adjusts hue
   differentiation and opacity in Increased Contrast mode. Mirror this by
   boosting background opacity and border visibility in a high-contrast media query.

---

## 12. PERFORMANCE ENGINEERING

`backdrop-filter` is GPU-composited. It's fast for 1–3 elements but degrades
quickly when overused.

### Rules

1. **Limit glass elements to 3–5 per viewport.** Each `backdrop-filter` creates
   a new compositing layer.
2. **Never nest glass inside glass.** Two stacked backdrop-filters will double
   the GPU cost with no visual benefit.
3. **Use `will-change: transform` sparingly** — only on elements that animate.
4. **Reduce blur on mobile**: Drop from `blur(16px)` to `blur(10px)` on
   screens under 768px.
   ```css
   @media (max-width: 768px) {
     .glass { backdrop-filter: blur(10px) saturate(160%); }
   }
   ```
5. **SVG filters (Tier 3+) are expensive.** Only apply them to one element at a
   time. Use `contain: layout style paint` on the filtered element.
6. **Animated turbulence** (`<animate>` on `feTurbulence seed`) is the heaviest
   operation. Use `dur="10s"` or longer. Fast seed cycling (under 4s) causes
   visible jank on mid-range devices.
7. **Test on real devices.** DevTools do not accurately represent blur performance.
   Test on an iPhone SE and a mid-range Android.

### Performance-Optimized Glass (for repeated elements)

```css
.glass-lite {
  background: rgba(255, 255, 255, 0.08);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}
```

No saturate boost, lower blur, minimal shadows. Use for list items, tags, pills.

---

## 13. TAILWIND CSS UTILITY PATTERNS

### Tier 1 — Frosted Card
```
bg-white/[0.06] backdrop-blur-xl backdrop-saturate-[1.8]
border border-white/[0.12] rounded-2xl
shadow-[0_8px_32px_rgba(0,0,0,0.15)]
[box-shadow:inset_0_1px_0_rgba(255,255,255,0.12)]
```

### Tier 2 — Luminous Card
```
bg-[radial-gradient(ellipse_at_30%_0%,rgba(255,255,255,0.12)_0%,transparent_60%),rgba(255,255,255,0.06)]
backdrop-blur-2xl backdrop-saturate-200
border border-white/[0.15] rounded-3xl
shadow-[0_12px_40px_rgba(0,0,0,0.2),inset_0_1px_0_rgba(255,255,255,0.2)]
```

### Hover States
```
hover:bg-white/[0.10] hover:border-white/[0.18]
hover:shadow-[0_12px_40px_rgba(0,0,0,0.2)]
transition-all duration-300
```

### Dark Theme Glass Nav
```
fixed top-0 inset-x-0 z-50
bg-black/[0.3] backdrop-blur-xl backdrop-saturate-[1.8]
border-b border-white/[0.08]
```

---

## 14. REACT COMPONENT ARCHITECTURE

### Design Tokens (CSS Variables)

```css
:root {
  --glass-blur: 14px;
  --glass-saturation: 180%;
  --glass-bg-opacity: 0.06;
  --glass-border-opacity: 0.12;
  --glass-highlight-opacity: 0.15;
  --glass-radius: 20px;
  --glass-shadow-color: rgba(0, 0, 0, 0.15);
}
```

### Component Props Pattern

```tsx
interface GlassProps {
  tier?: 1 | 2 | 3;        // Visual complexity
  tint?: string;             // Brand color in rgb format: "59, 130, 246"
  intensity?: 'subtle' | 'medium' | 'strong';
  interactive?: boolean;     // Enables hover states
  children: React.ReactNode;
}
```

Map `intensity` to concrete values:
- subtle: blur 8px, bg-opacity 0.04, border-opacity 0.08
- medium: blur 14px, bg-opacity 0.07, border-opacity 0.12
- strong: blur 20px, bg-opacity 0.12, border-opacity 0.18

---

## 15. COMMON MISTAKES & HOW TO FIX THEM

| Mistake | Fix |
|---------|-----|
| Glass on a solid white/black background | Add a gradient mesh or image behind the glass |
| Border too visible (opacity > 0.25) | Drop to 0.08–0.15 |
| Missing `saturate()` in backdrop-filter | Always include `saturate(180%)` minimum |
| No specular highlight (inset shadow) | Add `inset 0 1px 0 rgba(255,255,255,0.12)` |
| Nesting glass inside glass | Never do this — flatten the hierarchy |
| Using `opacity` instead of `rgba()` | `opacity` affects ALL children. Use rgba backgrounds |
| Blur too high (>30px) — looks like frosted shower door | Keep between 8–20px for UI elements |
| Text unreadable on glass | Add text-shadow, increase bg opacity, or use semibold weight |
| Glass on every element | Reserve for 1–3 key surfaces per viewport |
| Sharp corners with glass | Always use border-radius ≥ 12px |
| No fallback for unsupported browsers | Use `@supports not (backdrop-filter: blur(1px))` |
| Using `border` instead of inset `box-shadow` | Switch to `box-shadow: inset 0 0 0 1px` for smoother edges |

---

## 16. REFERENCE SNIPPETS & RECIPES

### Recipe: Glass Navigation Bar

```css
.glass-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  padding: 12px 24px;
  background: rgba(10, 10, 15, 0.6);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

### Recipe: Glass Modal Overlay

```css
.glass-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  z-index: 100;
}

.glass-modal {
  position: relative;
  max-width: 480px;
  margin: 15vh auto;
  background: rgba(255, 255, 255, 0.08);
  -webkit-backdrop-filter: blur(20px) saturate(200%);
  backdrop-filter: blur(20px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 28px;
  box-shadow:
    0 24px 80px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  padding: 32px;
}
```

### Recipe: Glass Button

```css
.glass-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.08);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.glass-btn:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(255, 255, 255, 0.22);
  box-shadow:
    0 4px 16px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.glass-btn:active {
  transform: translateY(0);
  background: rgba(255, 255, 255, 0.06);
}
```

### Recipe: Glass Input Field

```css
.glass-input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  font-weight: 500;
  outline: none;
  transition: all 0.2s ease;
}

.glass-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

.glass-input:focus {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.25);
  box-shadow:
    0 0 0 3px rgba(255, 255, 255, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
```

### Recipe: Animated Gradient Mesh Background

```css
@keyframes meshShift {
  0%, 100% { background-position: 0% 50%; }
  25% { background-position: 50% 0%; }
  50% { background-position: 100% 50%; }
  75% { background-position: 50% 100%; }
}

.glass-scene {
  min-height: 100vh;
  background:
    radial-gradient(ellipse at 15% 50%, rgba(99, 102, 241, 0.5) 0%, transparent 50%),
    radial-gradient(ellipse at 85% 20%, rgba(236, 72, 153, 0.4) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 90%, rgba(14, 165, 233, 0.4) 0%, transparent 50%),
    radial-gradient(ellipse at 60% 40%, rgba(168, 85, 247, 0.2) 0%, transparent 40%),
    #06060f;
  background-size: 200% 200%;
  animation: meshShift 20s ease-in-out infinite;
}
```

---

## QUICK DECISION GUIDE

```
User wants glass?
├─ Is it a repeated list item or small element?
│  └─ YES → Tier 1 (glass-lite variant, lower blur)
├─ Is it a hero card, modal, or nav bar?
│  └─ YES → Tier 2 (luminous glass)
├─ Is it a singular showcase element on a landing page?
│  └─ YES → Tier 3 (refractive glass)
├─ Is it an Apple-level product page hero?
│  └─ YES → Tier 4 (liquid glass)
└─ Is it an art piece, portfolio, or experimental?
   └─ YES → Tier 5 (living glass)
```

---

## FINAL REMINDERS

1. Always include `-webkit-backdrop-filter` alongside `backdrop-filter`.
2. Always include `saturate()` in the backdrop-filter chain.
3. Always add the inset top-highlight box-shadow.
4. Always pair glass with a rich, colorful background.
5. Always respect `prefers-reduced-transparency` and `prefers-reduced-motion`.
6. Always test on real mobile devices.
7. Never nest glass inside glass.
8. Never use glass on more than 3–5 elements per viewport.
9. The grain texture `::before` overlay is your secret weapon — use it.
10. When in doubt, go more subtle. The best glass is the glass you almost don't notice.
