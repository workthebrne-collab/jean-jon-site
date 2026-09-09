# Jean & Jon — rebuilt site

Static site. No build step, no dependencies: open `index.html` in a browser.

## Structure
- `index.html` — home (hero, stats, first 4 category rows)
- `components.html`, `components-2/3.html` — paginated category listing (4 rows/page)
- `category/*.html` — 11 category pages, grid + sort
- `product/*.html` — 450 product pages
- `assets/` — css, js, webp images
- `_build/` — the scripts that generated this from the scraped catalog

## Regenerating
Source data is `../jean-jon-catalog/`. From `_build/`:
    python3 build_data.py   # catalog.json -> site_data.json (categories, filters)
    python3 mkimg.py        # source images -> optimised webp
    python3 gen.py          # writes all 463 html pages

## Notes
- Images were re-encoded to 800px WebP: 5.2 GB -> 9.1 MB.
- Categories are by form factor; use-case (Cleanser, Sunscreen…) and material
  (Glass, Acrylic…) are cross-cutting filters, because the same bottle is sold
  for several uses on the original site.
- "Request a quote" links out to the original product page on jean-jon.com.
- Layout follows an industrial/B2B catalogue pattern: category rows with a
  left description column + 3 product cards, A–Z / grid toggle, pagination.

## Design system

All spacing and type come from tokens in `:root` — no arbitrary values anywhere
in the stylesheet.

**Spacing — 4px base scale**
`--s-1:4` `--s-2:8` `--s-3:12` `--s-4:16` `--s-5:20` `--s-6:24`
`--s-8:32` `--s-10:40` `--s-12:48` `--s-16:64` `--s-20:80` `--s-24:96`

Fluid composites, used for every section so rhythm is identical site-wide:
- `--sect`     — between major sections (32→64px)
- `--sect-sm`  — tighter blocks (24→40px)
- `--gut`      — page side gutter (16→64px)
- `--gap`      — grid gap (12→20px)

**Type ramp**
`--t-2xs:9` `--t-xs:11` `--t-sm:12` `--t-base:13` `--t-md:14` `--t-lg:16`
`--t-xl:20` `--t-2xl` (22→30) `--t-3xl` (34→56) `--t-4xl` (38→76)

**Shared control height** `--ctrl-h:36px` — selects, toggles, and icon buttons
all align on the same baseline.

### Rules
- Never write a raw px value for padding/margin/gap — use a token.
- Section spacing is `--sect` / `--sect-sm`, never bespoke.
- Images inside a fixed-ratio tile use flex + `max-width/max-height:100%`
  (NOT `width/height:100%` with `object-fit`, which overflows the box).

### Verified
28/28 checks clean — 4 page types x 7 breakpoints (375/560/820/1080/1440/1920/2560):
no overflow, uniform card heights, identical section padding, consistent control
heights, no image overflow, no overlap.

## Product copy

Descriptions are scraped from the original product pages on jean-jon.com and
stored in `_build/descriptions.json`, keyed by product id.

    python3 _build/scrape_desc.py   # refetch (resumable — skips ids already stored)
    python3 _build/gen.py           # rebuild pages

**Coverage:** 250 of 450 products have copy on the source site; the other 200
have no description there at all (spot-checked and confirmed, not a parser gap).
Those pages fall back to name, price, SKU and category — no invented copy.

**What the parser does**
- Converts the site's Unicode maths-bold text (𝗥𝗲𝗰𝗼𝗺𝗺𝗲𝗻𝗱𝗲𝗱) to plain ASCII.
- Splits content into ordered sections keyed by their heading
  ("Recommended Filling", "Actual Item", "Why you should use this packaging?").
- Pulls `Head - …` / `Neck - …` / `Body - …` and `Material :` / `Dimension :`
  pairs into the spec table, merged with the site's own category/material data.
- Stops at the reviews widget so its markup never leaks into the copy.

## Logo

Source: `../logoAsset 1logo.png` (3748x943 PNG with alpha).

Generated web assets in `assets/img/`:
- `logo-dark.webp`  — 480px wide, header (renders 79-103px, so ~4.6x on retina)
- `logo-white.webp` — same mark recoloured white, for the dark footer
- `favicon.png`     — 180px square, full wordmark on white

To regenerate after replacing the source, see `_build/mklogo.py`.

## Colour

Warm blush / cream / rose-gold palette. All colour lives in `:root` tokens —
change these nine values to reskin the whole site.

    --ink #2A2320    --body #5C5049   --muted #73635B
    --line #EADFD8   --line-2 #DDCDC3
    --bg #FBF7F2     --tile #F7E4DE
    --accent #A2563C --accent-dark #8A452E
    --footer #2A2320 --footer-fg #C9B8AF --on-dark #FDFAF7

Every text/background pair was contrast-checked in the browser and clears
WCAG AA (4.5:1): body 7.30, card name 12.58, brand label 4.67, CTA 5.13,
footer link 8.06, breadcrumb 5.37.

`--muted` is #73635B rather than a lighter taupe specifically so small meta text
stays AA-compliant on the blush tile as well as the cream ground.

**Product photos never carry a colour cast.** They sit on `--plate` (white) with
no `mix-blend-mode` — the blush `--tile` is only the card surround. Blend modes
tint the artwork itself, which misrepresents the product. Image frames are 1:1 to
match the source photography (395 of 400 sampled images are square), so they fill
edge to edge with no pillarboxing.

Logo assets are tinted to `--ink` / `--on-dark`; rerun `_build/mklogo.py` if the
palette changes.

## Platform landing page

`platform.html` — a B2B SaaS-style landing page built to a supplied reference
composition (Lumi). Built by `_build/gen_landing.py`, styled by
`assets/css/landing.css`.

**It shares the catalogue's brand palette exactly** — all 13 colour tokens in
`landing.css` match `main.css` byte for byte (cream ground, warm near-black type,
rose-gold accent, dark footer). The reference's blue CTA and pure-white ground
were NOT carried over; only the composition was. If you change a colour, change
it in both files or the two halves of the site drift apart.

**Content variables** live in the `C` dict at the top of `gen_landing.py`:
BRAND_NAME, BRAND_LOGO, PRIMARY_CTA, HERO_HEADLINE, FEATURE_1..4_TITLE /
_DESCRIPTION, SECTION_2_HEADLINE, SECTION_2_DESCRIPTION. Dashboard and collage
products come from `picks.json` (curated from the real catalogue).

**Full-bleed shell, measured content.** The page ground, header, footer and
product collage span the whole viewport (same `--gut` scale as the catalogue:
16px mobile -> 64px desktop). Only the reading blocks stay measured, because
line length is a readability constraint, not a page-width one:
hero headline 640px, capability row 920px, dashboard 980px.

The collage is height-capped (`clamp(140px,13vw,200px)`) so products keep a
sane scale on a 2560px screen instead of inflating with the grid cells.

**Collage cut-outs**: `assets/img/cut-*.png` are background-removed versions of
catalogue photos, generated by edge flood-fill (the studio backdrops are near
white and uniform, so they key cleanly). Regenerate by re-running the cutout
step if the product picks change.

Verified: page never scrolls horizontally at 360-1920px (only the dashboard
scrolls internally on mobile, by design); dashboard holds 620px and shares the
hero's centre axis; dashboard tiles are uniform height.

## Two type systems — deliberate split

The catalogue and the landing page use **different type scales on purpose**.
The catalogue is dense operational UI where compactness aids scanning; the
landing page is marketing copy that must read instantly. Applying the
catalogue's UI scale to marketing text made it needlessly hard to read.

Hierarchy is what carries over from the reference, not absolute pixel sizes:
BIG hero > MEDIUM section headline > SMALL feature text > SMALLEST dashboard UI.

**Catalogue (`main.css`) — compact**

    --t-xs 11px   meta        --t-sm 12px   nav, card names
    --t-base 13px body        --t-md 14px   lead

**Landing (`landing.css`) — marketing ramp, larger**

    --lp-nav 13px            header + footer links
    --lp-hero clamp(46px,6vw,64px)
    --lp-feat-title 14px     capability titles (600 weight)
    --lp-feat-body 13.5px    capability descriptions
    --lp-section clamp(38px,4.5vw,52px)
    --lp-section-body 16px   section lead
    --lp-label 12px          collage labels

**Dashboard chrome stays compact — it is UI, not marketing**

    --ui-nav 11px   --ui-title 17px   --ui-ctrl 11px
    --ui-card 11.5px   --ui-card-meta 10.5px

Measured hierarchy ratios at 1280px+: hero/section 1.23, section/feature 3.71,
feature/UI-card 1.22 — strictly descending at every breakpoint.

## Struktur gambar

    assets/img/
      products/   1,018  gambar asal dari jean-jon.com (backdrop studio)
      cutouts/      448  latar dibuang, PNG/WebP lutsinar
      brand/          3  logo-dark, logo-white, favicon

**Jangan pindahkan fail secara manual.** Laluan ini ditulis oleh generator
(`gen.py`, `gen_landing.py`, `mkimg.py`, `mklogo.py`) dan `site_data.json`.
Kalau folder diubah, keempat-empat fail itu perlu dikemas kini serentak atau
rebuild seterusnya akan hasilkan pautan rosak.

`_build/cutouts.json` memetakan id produk -> nama fail dalam `cutouts/`.
Produk tanpa entri di situ akan guna gambar asal dari `products/`.

### Cara cut-out dijana

Model U²-Net (sama yang digunakan rembg) melalui `onnxruntime`.
Pakej `rembg` sendiri tak dapat dipasang di sini — rantaian
`pymatting` -> `numba` -> `llvmlite` perlu LLVM untuk compile. Jadi model ONNX
dipanggil terus: `_build/u2net_v2.py` (venv Python 3.11 dalam scratchpad).

Dua langkah penting dalam skrip itu:
- **erosion 2px** pada mask, supaya jalur backdrop di pinggir terpotong
- **pembetulan warna tepi** — piksel separa-telus mengandungi campuran
  produk + backdrop. Formula `(diperhati - (1-a)*backdrop) / a` memulihkan
  warna produk sebenar. Tanpa ini, gambar berlatar biru keluar bergaris biru
  (130 gambar terjejas; selepas pembetulan tinggal 24, semuanya produk yang
  memang berwarna biru/ungu).
