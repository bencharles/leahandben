# Leah & Ben Wedding Website

**URL:** https://leahandben.us
**Hosting:** GitHub Pages with custom domain
**Wedding Date:** August 15, 2026
**Location:** Montclair, NJ (Ceremony) / North Haledon, NJ (Reception)

## Architecture

This is a static site built with a Python template system. No frameworks — just HTML, CSS, and vanilla JS.

### Template System

Pages are built from templates in `templates/` and assembled by `build.py`.

- `templates/base.html` — shared shell (html tag, head, :root vars, nav, body wrapper)
- `templates/index.html` — home page content (hero, schedule, countdown, loader)
- `templates/rsvp.html` — RSVP page content (photo, RSVPify embed)
- `build.py` — assembles templates into final files and encrypts the index page

**To rebuild after any change:**
```bash
python build.py
```

This generates three files:
- `index-unprotected.html` — assembled home page (gitignored)
- `rsvp.html` — assembled RSVP page (committed)
- `index.html` — password-protected gate page with encrypted home page (committed)

### Template Format

Each page template declares metadata at the top and content in tagged sections:

```
{{TITLE: Page Title}}
{{NAV_ACTIVE: welcome|rsvp}}
{{NAV_CLASS: scrolled}}          (optional — adds class to <nav>)

{{STYLES}}
    /* page-specific CSS here */
{{/STYLES}}

{{BODY}}
  <!-- page-specific HTML here -->
{{/BODY}}

{{SCRIPTS}}
  <script>/* page-specific JS here */</script>
{{/SCRIPTS}}
```

### Password Protection

The index page uses client-side AES-GCM encryption (PBKDF2, 600,000 iterations).

- **Password:** `leahben26`
- **How it works:** `build.py` reads `index-unprotected.html`, encrypts it, and wraps it in a gate page (`index.html`) that prompts for the password
- **Caching:** After first entry, the password is saved to `localStorage` (`lb_pw`). On subsequent visits, the gate auto-decrypts without showing the password prompt
- **Cache invalidation:** If the password changes, the cached one fails decryption and the gate reappears
- **RSVP auth:** `rsvp.html` checks `sessionStorage` or `localStorage` for auth state and redirects to `index.html` if not authenticated
- **Transition:** After decryption, the gate does a DOM swap (`DOMParser` + `innerHTML`) instead of `document.write()` to avoid a white flash. The `<html>` element stays alive with its olive background throughout

### Key Design Decisions

- **Inline :root CSS vars** are duplicated in both `base.html` and `style.css`. This is intentional — the inline version ensures the loader curtains render with the correct olive background before `style.css` finishes loading (prevents a transparent-curtain flash)
- **Nav scroll behavior:** On the index page, the nav starts transparent over the hero and turns solid on scroll (JS adds `.scrolled` class). On the RSVP page, the nav starts with `class="scrolled"` since there's no hero. Both use the same CSS rules from `style.css`
- **`<link rel="preload" href="style.css">` in the gate page** pre-caches the stylesheet while the user types the password

## File Structure

```
leahandben/
  build.py                  # Build script (assembles + encrypts)
  style.css                 # Shared stylesheet
  index.html                # Password gate (generated, committed)
  index-unprotected.html    # Assembled home page (generated, gitignored)
  rsvp.html                 # Assembled RSVP page (generated, committed)
  CNAME                     # GitHub Pages custom domain
  images/
    grassland.jpg            # Hero background
    doorway.jpg              # RSVP page photo
  templates/
    base.html                # Shared HTML shell
    index.html               # Home page template
    rsvp.html                # RSVP page template
```

## Color Palette

```
--amber:      #C8985A   (gold accents, buttons)
--amber-dark: #9A7230   (text accents)
--sage:       #6B7A35   (eyebrow text)
--sage-light: #AABB72   (loader date text)
--cream:      #F6EFE0   (section backgrounds)
--warm-dark:  #26180A   (body text)
--forest:     #4A5320   (primary dark olive — overscroll bg, loader curtains)
```

## Venues

- **Ceremony:** Immaculate Conception Church, 30 N Fullerton Ave, Montclair, NJ 07042
- **Reception:** The Tides Estate, 1245 Belmont Ave, North Haledon, NJ 07508

## Dependencies

- Python `cryptography` library (for AES-GCM encryption in build.py)
- Google Fonts: Cinzel, Cormorant Garamond, Jost
- RSVPify embed: `https://leahandben.rsvpify.com/embed`

## Mobile Compatibility

**All changes must work on mobile browsers**, including iOS Safari and Android Chrome. Follow these rules:

- **Safe area insets:** Nav uses `env(safe-area-inset-top)` for notch/Dynamic Island support
- **Viewport height:** Always include `min-height:100vh` fallback before `min-height:100svh`
- **Hover states:** Wrap `:hover` transforms in `@media(hover:hover)` so they don't fire on touch devices
- **Touch targets:** Interactive elements should be at least 44×44px (nav tabs use `min-height:44px`)
- **`backdrop-filter`:** Always include `-webkit-backdrop-filter` alongside `backdrop-filter`
- **IntersectionObserver:** Always wrap with `if ('IntersectionObserver' in window)` and add a fallback that immediately shows elements
- **`background-attachment: fixed`:** Use `@supports(-webkit-touch-callout:none)` to switch to `scroll` on iOS
- **Meta tags in base.html:** `color-scheme: light` prevents dark mode inversion; `theme-color: #4A5320` colors the browser UI chrome

## Workflow

**Always run `python build.py` after any change** — to templates, style.css, or anything else. The build assembles pages from templates and re-encrypts the gate page. Never leave the user with stale generated files.

After building, tell the user it's ready to push. The sandbox can't push to GitHub (SSH blocked), so the user pushes manually.

## Git Notes

- `*-unprotected.html` and `*-protected.html` are in `.gitignore`
- Templates and `build.py` are version-controlled
- Files to push after a build: `index.html`, `rsvp.html`, `style.css`, and any changed templates or `build.py`
