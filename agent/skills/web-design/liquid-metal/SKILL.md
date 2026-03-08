---
name: liquid-gold-navbar
description: "Create a premium liquid gold floating navigation navbar with animated golden indicator ring, glassmorphism toolbar, and theme toggle. Use when building luxury UI navigation bars with metallic gold effects, bouncy animations, and studio-lighting aesthetics."
---

# Liquid Gold Floating Navbar

This skill creates a stunning floating navigation toolbar with a luxurious liquid gold aesthetic. It features a glassmorphism base, an animated golden active indicator ring with studio-lighting reflections, bouncy overshoot animations, and a theme toggle with sun/moon crossfade effects.

---

## Core Design Elements

### 1. Layout Structure

```html
<div class="gold-nav-container">
  <div class="gold-nav-toolbar">
    <nav class="gold-nav-buttons">
      <!-- Nav buttons here -->
    </nav>
    
    <!-- Theme toggle separate from nav items -->
    <button class="theme-toggle">
      <!-- Sun/Moon icons -->
    </button>
  </div>
  
  <!-- Active indicator ring -->
  <div class="gold-indicator">
    <div class="indicator-glow"></div>
    <div class="indicator-clip">
      <div class="indicator-spin"></div>
    </div>
    <div class="indicator-inner"></div>
  </div>
</div>
```

### 2. The Glassmorphism Toolbar

```css
.gold-nav-toolbar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  
  /* Glassmorphism foundation */
  background: rgba(20, 20, 25, 0.75);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  backdrop-filter: blur(20px) saturate(180%);
  
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 0 80px rgba(232, 175, 72, 0.08);
  
  padding: 12px 20px;
  overflow: hidden;
}

/* Film grain noise overlay */
.gold-nav-toolbar::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
  pointer-events: none;
  border-radius: inherit;
  mix-blend-mode: overlay;
}

/* Radial ambient glow */
.gold-nav-toolbar::after {
  content: '';
  position: absolute;
  inset: -50%;
  background: radial-gradient(
    ellipse at 50% 120%,
    rgba(232, 175, 72, 0.15) 0%,
    transparent 50%
  );
  pointer-events: none;
}
```

---

## The Golden Active Indicator Ring

This is the centerpiece — a 4-layer spinning gold ring that slides between buttons.

### Layer Structure

```css
.gold-indicator {
  position: absolute;
  width: 56px;
  height: 56px;
  pointer-events: none;
  z-index: 10;
  transition: transform 0.6s cubic-bezier(0.34, 1.2, 0.64, 1);
}

/* Layer 1: Glow behind the ring */
.indicator-glow {
  position: absolute;
  inset: -8px;
  background: #e8af48;
  border-radius: 20px;
  filter: blur(12px);
  opacity: 0.15;
}

/* Layer 2: Clip container */
.indicator-clip {
  position: absolute;
  inset: 0;
  border-radius: 18px;
  overflow: hidden;
}

/* Layer 3: Rotating conic gradient */
.indicator-spin {
  position: absolute;
  width: 200%;
  height: 200%;
  top: -50%;
  left: -50%;
  background: conic-gradient(
    from 0deg,
    /* Pattern repeats twice across 360° */
    /* First repetition */
    #533517 0%,
    #533517 33%,
    #c49746 35%,
    #feeaa5 38%,
    #ffffff 39%,
    #ffffff 42%,
    #ffc0cb 43%,
    #89cff0 44.5%,
    #533517 45%,
    #c49746 68%,
    #feeaa5 71%,
    #ffffff 72%,
    #ffffff 75%,
    #ffc0cb 76%,
    #89cff0 77.5%,
    #533517 78%,
    /* Second repetition */
    #533517 78%,
    #533517 111%,
    #c49746 113%,
    #feeaa5 116%,
    #ffffff 117%,
    #ffffff 120%,
    #ffc0cb 121%,
    #89cff0 122.5%,
    #533517 123%,
    #c49746 146%,
    #feeaa5 149%,
    #ffffff 150%,
    #ffffff 153%,
    #ffc0cb 154%,
    #89cff0 155.5%,
    #533517 156%,
    #533517 189%,
    #c49746 191%,
    #feeaa5 194%,
    #ffffff 195%,
    #ffffff 198%,
    #ffc0cb 199%,
    #89cff0 200.5%,
    #533517 201%,
    #c49746 224%,
    #feeaa5 227%,
    #ffffff 228%,
    #ffffff 231%,
    #ffc0cb 232%,
    #89cff0 233.5%,
    #533517 234%,
    #c49746 257%,
    #feeaa5 260%,
    #ffffff 261%,
    #ffffff 264%,
    #ffc0cb 265%,
    #89cff0 266.5%,
    #533517 267%,
    #533517 300%,
    #c49746 302%,
    #feeaa5 305%,
    #ffffff 306%,
    #ffffff 309%,
    #ffc0cb 310%,
    #89cff0 311.5%,
    #533517 312%,
    #533517 345%,
    #c49746 347%,
    #feeaa5 350%,
    #ffffff 351%,
    #ffffff 354%,
    #ffc0cb 355%,
    #89cff0 356.5%,
    #533517 357%,
    #533517 360%
  );
  animation: spinGold 4.5s linear infinite;
}

@keyframes spinGold {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Layer 4: Inner plate - only 2px of ring visible */
.indicator-inner {
  position: absolute;
  inset: 2px;
  background: rgba(20, 20, 25, 0.9);
  border-radius: 16px;
  z-index: 2;
}
```

### Gradient Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Dark Bronze | #533517 | Base gold shadow |
| Warm Gold | #c49746 | Main gold body |
| Light Gold | #feeaa5 | Gold highlights |
| White Hotspot | #ffffff | Studio light reflections (~3%) |
| Pink Hint | #ffc0cb | Chromatic iridescence (~1.5%) |
| Blue Hint | #89cff0 | Chromatic iridescence (~1.5%) |

---

## Navigation Buttons

```css
.gold-nav-buttons {
  display: flex;
  align-items: center;
  gap: 4px;
}

.gold-nav-btn {
  position: relative;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 14px;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.34, 1.2, 0.64, 1);
  z-index: 5;
}

.gold-nav-btn:hover {
  transform: scale(1.05);
}

.gold-nav-btn.active {
  color: #feeaa5;
}

/* SVG stroke icons - thin lines */
.gold-nav-btn svg {
  width: 22px;
  height: 22px;
  stroke-width: 1.5;
  stroke: rgba(255, 255, 255, 0.7);
  fill: none;
  transition: stroke 0.3s ease;
}

.gold-nav-btn.active svg {
  stroke: #feeaa5;
}

/* Subtle dividers between buttons */
.gold-nav-buttons::before,
.gold-nav-buttons::after {
  content: '';
  width: 1px;
  height: 24px;
  background: linear-gradient(
    to bottom,
    transparent,
    rgba(255, 255, 255, 0.1),
    transparent
  );
}
```

### SVG Icons for Nav Buttons

```html
<!-- Home Icon -->
<svg viewBox="0 0 24 24">
  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
  <polyline points="9,22 9,12 15,12 15,22"/>
</svg>

<!-- Search Icon -->
<svg viewBox="0 0 24 24">
  <circle cx="11" cy="11" r="8"/>
  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
</svg>

<!-- User Icon -->
<svg viewBox="0 0 24 24">
  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
  <circle cx="12" cy="7" r="4"/>
</svg>
```

---

## Theme Toggle (Sun/Moon Crossfade)

```css
.theme-toggle {
  position: relative;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.34, 1.2, 0.64, 1);
  margin-left: 8px;
  overflow: hidden;
}

.theme-toggle:hover {
  transform: scale(1.1);
  border-color: rgba(232, 175, 72, 0.3);
}

/* Bounce animation on click */
.theme-toggle.bouncing {
  animation: toggleBounce 0.6s cubic-bezier(0.34, 1.2, 0.64, 1);
}

@keyframes toggleBounce {
  0% { transform: scale(1); }
  30% { transform: scale(1.25); }
  60% { transform: scale(0.95); }
  100% { transform: scale(1); }
}

/* Sun/Moon icons with crossfade */
.theme-toggle .icon-sun,
.theme-toggle .icon-moon {
  position: absolute;
  width: 20px;
  height: 20px;
  transition: all 0.5s cubic-bezier(0.34, 1.2, 0.64, 1);
}

.theme-toggle .icon-sun {
  opacity: 1;
  transform: rotate(0deg) scale(1);
}

.theme-toggle .icon-moon {
  opacity: 0;
  transform: rotate(-90deg) scale(0.5);
}

/* Dark mode states */
.theme-toggle.dark .icon-sun {
  opacity: 0;
  transform: rotate(90deg) scale(0.5);
}

.theme-toggle.dark .icon-moon {
  opacity: 1;
  transform: rotate(0deg) scale(1);
}
```

### Sun/Moon SVG Icons

```html
<!-- Sun Icon -->
<svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
  <circle cx="12" cy="12" r="5"/>
  <line x1="12" y1="1" x2="12" y2="3"/>
  <line x1="12" y1="21" x2="12" y2="23"/>
  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
  <line x1="1" y1="12" x2="3" y2="12"/>
  <line x1="21" y1="12" x2="23" y2="12"/>
  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
</svg>

<!-- Moon Icon -->
<svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
</svg>
```

---

## Bouncy Overshoot Easing

All animations use the signature bouncy overshoot easing:

```css
/* The signature easing curve */
transition-timing-function: cubic-bezier(0.34, 1.2, 0.64, 1);

/* Applied to:
   - Indicator sliding between buttons
   - Button hover/active states
   - Theme toggle bounce animation
*/
```

---

## JavaScript for Interactivity

```javascript
class LiquidGoldNavbar {
  constructor(container) {
    this.container = container;
    this.buttons = container.querySelectorAll('.gold-nav-btn');
    this.indicator = container.querySelector('.gold-indicator');
    this.themeToggle = container.querySelector('.theme-toggle');
    
    this.init();
  }
  
  init() {
    // Set initial active state
    this.buttons.forEach((btn, index) => {
      btn.addEventListener('click', () => this.setActive(index));
    });
    
    // Theme toggle
    this.themeToggle?.addEventListener('click', () => this.toggleTheme());
  }
  
  setActive(index) {
    // Remove active from all
    this.buttons.forEach(btn => btn.classList.remove('active'));
    
    // Add active to clicked
    this.buttons[index].classList.add('active');
    
    // Move indicator
    const btn = this.buttons[index];
    const btnRect = btn.getBoundingClientRect();
    const containerRect = this.container.getBoundingClientRect();
    
    const offsetLeft = btnRect.left - containerRect.left;
    const offsetTop = btnRect.top - containerRect.top;
    
    this.indicator.style.transform = `translate(${offsetLeft}px, ${offsetTop}px)`;
  }
  
  toggleTheme() {
    // Add bounce animation
    this.themeToggle.classList.add('bouncing');
    
    // Toggle dark class
    this.themeToggle.classList.toggle('dark');
    document.body.classList.toggle('dark-mode');
    
    // Remove animation class after completes
    setTimeout(() => {
      this.themeToggle.classList.remove('bouncing');
    }, 600);
  }
}
```

---

## Complete Implementation Example

### HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Liquid Gold Navbar</title>
  <style>
    /* All CSS from above sections */
  </style>
</head>
<body>
  <div class="gold-nav-container">
    <!-- Floating toolbar -->
    <nav class="gold-nav-toolbar">
      <!-- Theme toggle -->
      <button class="theme-toggle" aria-label="Toggle theme">
        <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
      
      <!-- Nav buttons -->
      <div class="gold-nav-buttons">
        <button class="gold-nav-btn active" data-index="0" aria-label="Home">
          <svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" fill="none">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9,22 9,12 15,12 15,22"/>
          </svg>
        </button>
        
        <button class="gold-nav-btn" data-index="1" aria-label="Search">
          <svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" fill="none">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
        </button>
        
        <button class="gold-nav-btn" data-index="2" aria-label="User">
          <svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" fill="none">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </button>
      </div>
      
      <!-- Active indicator ring -->
      <div class="gold-indicator">
        <div class="indicator-glow"></div>
        <div class="indicator-clip">
          <div class="indicator-spin"></div>
        </div>
        <div class="indicator-inner"></div>
      </div>
    </nav>
  </div>
  
  <script>
    // Initialize the navbar
    document.querySelectorAll('.gold-nav-container').forEach(container => {
      new LiquidGoldNavbar(container);
    });
  </script>
</body>
</html>
```

---

## Implementation Checklist

- [ ] Container centered on screen with `position: fixed` or `position: absolute`
- [ ] Glassmorphism toolbar with blur, border, and shadows
- [ ] Film grain noise overlay (opacity: 0.035)
- [ ] Radial ambient glow behind toolbar
- [ ] 4-layer golden indicator ring
- [ ] Conic gradient with gold-dominant colors (70%)
- [ ] White hotspot reflections (~3% width)
- [ ] Pink and blue chromatic hints (~1.5% each)
- [ ] Pattern repeating twice across 360°
- [ ] Inner plate showing only 2px of spinning ring
- [ ] Bouncy overshoot easing on all transitions
- [ ] 3 nav buttons with thin stroke icons
- [ ] Theme toggle with sun/moon crossfade
- [ ] Toggle bounce animation (1.25× scale)
- [ ] JavaScript for indicator positioning
- [ ] Proper ARIA labels for accessibility

---

## Error Handling

- **Indicator not moving**: Ensure the indicator element is positioned absolutely within a positioned container
- **Spinning not smooth**: Use `will-change: transform` on the spinning element
- **Gradient not visible**: Check that the clip container has `overflow: hidden` and proper border-radius
- **Grain overlay not appearing**: Ensure `pointer-events: none` is set to allow clicks through
- **Theme toggle animation broken**: Verify the `bouncing` class is removed after animation completes

---

## Notes

- The conic gradient size at 200% with -50% offset creates a smooth spinning effect from center
- The pink/blue hints should be minimal — the ring should read as GOLD, not rainbow
- The bouncy easing `(0.34, 1.2, 0.64, 1)` provides a distinctive premium feel
- Film grain adds tactile realism — keep opacity low (0.03–0.04)
- The radial glow behind the toolbar creates depth and draws attention
