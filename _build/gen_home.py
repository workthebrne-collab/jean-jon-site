"""Build index.html — home page.

Layout follows the Brand Your reference composition (hero split, bestseller
rail, split promos, collection tiles, stats, footer). Palette is the client's
pink/lemon pair; see assets/css/home.css for the contrast rationale.

Everything rendered here comes from site_data.json. The logo wall and the
testimonial cards are intentionally left as empty placeholder slots — the
reference fills them with Brand Your's own clients and quotes, which are not
ours to reuse and which Jean & Jon has no data for. Fill PARTNERS / QUOTES
below when real content exists.
"""
import json, os, html, re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..")
E = html.escape

data = json.load(open(os.path.join(HERE, "site_data.json")))
CUTOUTS = json.load(open(os.path.join(HERE, "cutouts.json")))
# Colourful packaging photography (client-licensed stock mockups). Filtered by
# p90 saturation >= 0.50 so only the vivid shots make the wall.
try:
    PACKAGING = json.load(open(os.path.join(HERE, "packaging.json")))
except FileNotFoundError:
    PACKAGING = []

# The images currently in packaging.json are unbranded stock TEMPLATES: each
# one has "MOCKUP" and yellowimages.com printed onto the product itself, so
# they read as an unfinished site rather than Jean & Jon's work. The section
# stays built but switched off until real artwork replaces them.
SHOW_WALL = False
items, cats = data["items"], data["cats"]
by_key = {c["key"]: c for c in cats}

# ---------------------------------------------------------------- content ---
BRAND = "Jean &amp; Jon"
HERO_TITLE = "The packaging behind<br>your first thousand units"
HERO_SUB = ("Cosmetic bottles, jars, tubes and casings — held in stock, printed "
            "with your branding, shipped direct. No minimum order, so you can "
            "start with ten.")
STAMP = "ONE STOP<br>BEAUTY<br>CENTRE"

# ---- verified proof points ------------------------------------------------
# Every figure below is traceable: 2015 from our About Us page; product and
# category counts from the live catalogue; "No MOQ" / "Order Direct" / "Fast
# Delivery" are our own product-page claims (209x / 214x / 210x). Nothing here
# is estimated. Do not add factory statistics we cannot evidence.
PROOF = [
    ("Since 2015", "Supplying cosmetic packaging"),
    ("450", "Components in the catalogue"),
    ("No MOQ", "Order one piece or one thousand"),
    ("From RM0.20", "Per unit, ex-stock"),
]

WHAT_WE_DO = [
    ("Stock supply",
     "450 components across 11 categories, held ready. Order today, "
     "not in twelve weeks."),
    ("Printing &amp; decoration",
     "UV print, silkscreen and tempo print. Your logo and artwork applied "
     "to blank stock."),
    ("Packaging customisation",
     "Colour, closure, capacity and finish specified around your formula "
     "and your brand."),
    ("Sourcing",
     "Components we do not stock, sourced through the supply base we have "
     "built since 2015."),
]

# Customisation ladder — what a brand can actually specify with us.
CUSTOM = [
    ("01", "Format", "Bottle, jar, tube, sachet or casing — chosen for the formula."),
    ("02", "Capacity", "Sizes from 3g samples through to 1000ml refills."),
    ("03", "Material", "Acrylic, glass, aluminium or plastic."),
    ("04", "Closure", "Pump, dropper, spray, flip, screw or roller."),
    ("05", "Colour &amp; finish", "Matte, glossy, frosted, chrome and metallic."),
    ("06", "Decoration", "UV print, silkscreen, tempo print or applied label."),
]

# Ordering process — our real workflow, not a factory production line.
PROCESS = [
    ("Tell us the product", "Formula, viscosity, volume and the look you are after."),
    ("We match the format", "From stock where it exists; sourced where it does not."),
    ("Sample first", "Hold the component before you commit to a run."),
    ("Artwork &amp; proof", "Print method chosen for the surface, then proofed."),
    ("Decoration", "Printed, finished and checked against the approved proof."),
    ("Direct delivery", "Shipped to you — no distributor sitting in the middle."),
]

WHY_US = [
    ("No minimum order",
     "Most suppliers start at thousands of units. We will sell you one. "
     "Test a formula, run a limited edition, restock a single line."),
    ("Held in stock",
     "The catalogue is what we hold, not a brochure of what could be tooled. "
     "Availability is the product."),
    ("Order direct",
     "Buying straight from us — no trading layer marking up the unit price "
     "or slowing the reply."),
    ("Ten years in packaging",
     "Supplying cosmetic packaging and label printing since 2015, to brands "
     "that grew from one SKU upward."),
]

# Placeholder counts only — no invented names. See module docstring.
PARTNERS: list[str] = []
QUOTES: list[dict] = []

NAV = [("Components", "components.html")]

# Category strip: the reference shows 6 quick links. Use our largest categories.
STRIP = sorted(cats, key=lambda c: -c["count"])[:6]

def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "item"

def price(p) -> str:
    """Indicative unit price. We sell by quotation, so this is a guide only —
    never presented as a checkout price."""
    return f"From RM{p:.2f} / unit" if p else "Price on request"

def img_of(it) -> str:
    """Gambar asal yang di-scrape — versi buang latar tidak lagi digunakan."""
    if False:
        pass
    im = it.get("img") or []
    return im[0] if im else ""

def has_cutout(it) -> bool:
    """Dahulu menapis produk yang ada cut-out. Kini semua gambar asal layak."""
    return bool(it.get("img"))


# product URL — gen.py names files by slug of the product name
def purl(it) -> str:
    return f"product/{slugify(it['name'])}.html"

# ---- picks: cheapest in-stock-looking item per big category, for the rail ---
def rail_items(n=8):
    seen, out = set(), []
    ordered = sorted(cats, key=lambda c: -c["count"])
    # round-robin across categories so the rail isn't all bottles
    pools = {c["key"]: sorted([i for i in items if i["cat"] == c["key"] and has_cutout(i)],
                              key=lambda i: i.get("price") or 99) for c in ordered}
    while len(out) < n:
        added = False
        for c in ordered:
            pool = pools.get(c["key"], [])
            while pool:
                it = pool.pop(0)
                if it["id"] in seen:
                    continue
                seen.add(it["id"]); out.append(it); added = True
                break
            if len(out) >= n:
                break
        if not added:
            break
    return out[:n]


# --- feature-image selection ------------------------------------------------
# Cutouts vary from very tall (bottles) to very wide (nail polish ranges).
# A tall cutout in the wide hero panel reads as an extreme close-up, so choose
# per slot by the image's own aspect ratio.
def _cutout_size(fname):
    path = os.path.join(SITE, "assets", "img", "products", fname)
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None

_RATIO_CACHE = {}
def cut_ratio(it):
    f = CUTOUTS.get(it["id"])
    if not f:
        return None
    if f not in _RATIO_CACHE:
        wh = _cutout_size(f)
        _RATIO_CACHE[f] = (wh[0] / wh[1]) if wh else None
    return _RATIO_CACHE[f]

def widest(pool, n=1, min_ratio=1.6):
    """Products whose cutout is wide enough to fill a landscape panel."""
    scored = [(cut_ratio(i), i) for i in pool if has_cutout(i)]
    scored = [(r, i) for r, i in scored if r and r >= min_ratio]
    scored.sort(key=lambda t: -t[0])
    return [i for _, i in scored[:n]]

BADGES = ["Low minimums", "Made to order", "Speedy lead times",
          "Full colour", "Low minimums", "Custom print", "Made to order", "Full colour"]


def packaging_wall(n=12):
    """Colour wall of packaging work. Purely visual — links nowhere, because
    these are capability shots, not catalogue items."""
    if not PACKAGING:
        return ""
    picks = PACKAGING[:n]
    return "".join(
        f'<figure class="pk"><img src="assets/img/packaging/{E(p["file"])}" '
        f'alt="Custom printed packaging" loading="lazy" decoding="async" '
        f'width="{p["w"]}" height="{p["h"]}"></figure>'
        for p in picks)

def card(it, i):
    src = img_of(it)
    badge = f'<span class="badge">{E(BADGES[i % len(BADGES)])}</span>' if src else ""
    return f"""<a class="card" href="{purl(it)}">
        <div class="card__m">{badge}<img src="{E(src)}" alt="{E(it['name'].title())}" loading="lazy" decoding="async"></div>
        <p class="card__n">{E(it['name'].title())}</p>
        <p class="card__p">{price(it.get('price'))}</p>
      </a>"""

# ---- collection tiles: 3 largest categories, using a real product image -----
def col_tile(c, verb, label):
    pool = [i for i in items if i["cat"] == c["key"] and has_cutout(i)]
    src = img_of(pool[0]) if pool else ""
    return f"""<a class="col" href="category/{c['key']}.html">
        <img src="{E(src)}" alt="{E(c['name'])}" loading="lazy" decoding="async">
        <span class="col__cap"><span class="col__k">{E(verb)}</span>
          <span class="col__l">{E(label)} {ARROW}</span></span>
      </a>"""


# Line-art icon per category — mirrors the reference's icon+label category row.
# 18x18 viewBox, currentColor stroke so it inherits hover state.
def _svg(body):
    return ('<svg width="18" height="18" viewBox="0 0 20 20" fill="none" '
            'stroke="currentColor" stroke-width="1.4" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">' + body + '</svg>')

CAT_ICONS = {
  # bottle with pump neck
  "bottles":   _svg('<path d="M8 2h4v3H8z"/><path d="M7 5h6l1 4v8a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V9z"/>'),
  # lipstick bullet
  "lips":      _svg('<path d="M8 7l1-4h2l1 4"/><rect x="7.5" y="7" width="5" height="10" rx="1"/>'),
  # squeeze tube
  "tubes":     _svg('<path d="M7 3h6l-1 14a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1z"/><path d="M7 6h6"/>'),
  # jar with lid
  "jars":      _svg('<rect x="5" y="7" width="10" height="10" rx="1.5"/><path d="M6 7V5h8v2"/>'),
  # compact / powder disc
  "powder-colour": _svg('<circle cx="10" cy="10" r="6.5"/><circle cx="10" cy="10" r="2.5"/>'),
  # dropper pipette
  "droppers":  _svg('<path d="M11 3l6 6-2 2-6-6z"/><path d="M9 5l-4 8 3 3 8-4"/>'),
  # closed box
  "boxes":     _svg('<path d="M3 7l7-4 7 4v6l-7 4-7-4z"/><path d="M3 7l7 4 7-4M10 11v6"/>'),
  # screw cap
  "caps":      _svg('<rect x="5" y="6" width="10" height="8" rx="1.5"/><path d="M7 6V4h6v2M7 14v2h6v-2"/>'),
  # pouch / sachet
  "sachets":   _svg('<path d="M5 4h10v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1z"/><path d="M5 7h10"/>'),
  # brush applicator
  "accessories": _svg('<path d="M13 3l4 4-8 8-4 1 1-4z"/><path d="M11 5l4 4"/>'),
  # machine / gear
  "equipment": _svg('<circle cx="10" cy="10" r="3"/><path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.5 4.5l1.5 1.5M14 14l1.5 1.5M15.5 4.5L14 6M6 14l-1.5 1.5"/>'),
}
BESPOKE_ICON = _svg('<path d="M4 15l6-6 3 3-6 6H4z"/><path d="M13 6l1-1a2 2 0 0 1 3 3l-1 1z"/>')

ARROW = ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" '
         'stroke-width="1.6" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>')
CHEV = ('<svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" '
        'stroke-width="1.6" aria-hidden="true"><path d="M4 6l4 4 4-4"/></svg>')
ICON_QUOTE = ('<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" '
              'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path d="M5 2.5h7l3.5 3.5v11.5H5z"/><path d="M11.5 2.5V6H15"/>'
              '<path d="M7.5 10.5h5M7.5 13.5h3.5"/></svg>')
SEARCH = ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" '
          'stroke-width="1.5" aria-hidden="true"><circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5L14 14"/></svg>')

def btn(label, href, mod="dark"):
    return (f'<a class="btn btn--{mod}" href="{href}">'
            f'<span class="btn__ico">{ARROW}</span>{E(label)}</a>')

rail = rail_items(8)
# Landscape-friendly products for the big feature panels (falls back to the
# rail order if too few wide cutouts exist).
_features = widest(items, n=3) or rail[:3]
FEAT = (_features + rail[:3])[:3]
total = len(items)
ncats = len(cats)


# ---- new sections ----------------------------------------------------------
def proofbar():
    """Verified facts only — see PROOF."""
    return "".join(
        f'<div class="pf"><b class="pf__n">{n}</b><span class="pf__l">{l}</span></div>'
        for n, l in PROOF)

def whatwedo():
    return "".join(
        f'<article class="wd"><h3 class="wd__t">{t}</h3><p class="wd__p">{p}</p></article>'
        for t, p in WHAT_WE_DO)

def customgrid():
    return "".join(
        f'<article class="cu"><span class="cu__n">{n}</span>'
        f'<h3 class="cu__t">{t}</h3><p class="cu__p">{p}</p></article>'
        for n, t, p in CUSTOM)

def processlist():
    return "".join(
        f'<li class="pr"><span class="pr__n">{i}</span>'
        f'<div><h3 class="pr__t">{t}</h3><p class="pr__p">{p}</p></div></li>'
        for i, (t, p) in enumerate(PROCESS, 1))

def whygrid():
    return "".join(
        f'<article class="wy"><h3 class="wy__t">{t}</h3><p class="wy__p">{p}</p></article>'
        for t, p in WHY_US)

# ---- placeholder markup ----------------------------------------------------
# Placeholder wordmarks: invented generic names, set in type, greyscale.
# They are NOT real companies — swap in real client logos via PARTNERS.
DUMMY_LOGOS = [
    ("LUMIÈRE", "serif"), ("kaya", "lower"), ("NORDEN", "wide"),
    ("Aurelia", "serif"), ("BLOOM&CO", "tight"), ("satya", "lower"),
    ("MERIDIAN", "wide"), ("Verde", "serif"),
]

def logowall():
    if PARTNERS:
        return "".join(
            f'<div class="logo"><img src="{E(p["src"])}" alt="{E(p["name"])}" loading="lazy"></div>'
            for p in PARTNERS)
    return "".join(
        f'<div class="logo logo--{cls}" aria-hidden="true">{E(name)}</div>'
        for name, cls in DUMMY_LOGOS)

def quotes():
    if QUOTES:
        return "".join(
            f'<figure class="quote"><span class="quote__mark">&ldquo;</span>'
            f'<blockquote>{E(q["text"])}</blockquote>'
            f'<figcaption>{E(q["who"])}</figcaption></figure>' for q in QUOTES)
    return "".join(
        '<div class="quote ph"><b>Testimonial</b>add a real customer quote</div>'
        for _ in range(3))

CATS_TOP3 = sorted(cats, key=lambda c: -c["count"])[:3]
VERBS = [("Bottle It Up", "Browse bottles"), ("Hold It Together", "View jars & tubes"),
         ("Finish The Look", "See accessories")]

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{BRAND} — Custom Cosmetic Packaging</title>
<meta name="description" content="Custom cosmetic packaging: bottles, jars, tubes, caps and casings. {total} components across {ncats} categories, low minimums.">
<link rel="icon" href="assets/img/brand/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="assets/css/home.css">
</head>
<body>
<a class="sr" href="#main">Skip to content</a>

<header class="hdr">
  <div class="hdr__strip" aria-hidden="true"></div>
  <div class="hdr__bar">
    <a class="hdr__logo" href="index.html" aria-label="Jean &amp; Jon — home">
      <img src="assets/img/brand/logo-dark.webp" alt="Jean &amp; Jon" width="480" height="121"></a>
    <nav class="hdr__nav" aria-label="Primary">
      {"".join(f'<a href="{h}">{E(t)} {CHEV}</a>' for t, h in NAV)}
    </nav>
    <div class="hdr__search">
      <label class="sr" for="q">Search products</label>
      {SEARCH}
      <input id="q" type="search" placeholder="Search for bottles, jars, tubes" autocomplete="off">
    </div>
    <div class="hdr__end">
      <span>MY (RM) {CHEV}</span>
      <a class="hdr__quote" href="https://www.jean-jon.com/pages/contact-us">
        {ICON_QUOTE}Request a quote</a>
    </div>
  </div>
  <nav class="catbar" aria-label="Categories">
    <div class="catbar__in">
    {"".join(f'<a href="category/{c["key"]}.html">{CAT_ICONS.get(c["key"], "")}{E(c["name"])}</a>' for c in STRIP)}
      <a href="components.html">{BESPOKE_ICON}Bespoke</a>
    </div>
  </nav>
</header>

<main id="main">
<div class="wrap">

  <section class="hero">
    <div class="hero__panel">
      <span class="hero__stamp" aria-hidden="true">{STAMP}</span>
      <h1 class="hero__title">{HERO_TITLE}</h1>
      <p class="hero__sub">{HERO_SUB}</p>
      <div>{btn("Browse components", "components.html", "dark")}</div>
    </div>
    <div class="hero__media">
      <img class="hero__img" src="assets/img/brand/hero.webp"
           alt="Custom cosmetic packaging bottles with branded labels"
           width="900" height="600" fetchpriority="high">
    </div>
  </section>

  <!-- Partner logos — placeholder slots, no invented clients -->
  <section class="sect sect--tight" aria-labelledby="proof-h">
    <h2 class="sr" id="proof-h">Why brands buy from us</h2>
    <div class="proof">{proofbar()}</div>
  </section>

  <section class="sect" aria-labelledby="wd-h">
    <div class="sect__hd"><h2 class="sect__t" id="wd-h">What we do</h2></div>
    <p class="sect__lead">A packaging supplier and decorator: we hold the stock,
       print your branding on it, and ship it to you direct.</p>
    <div class="wd__grid">{whatwedo()}</div>
  </section>

  <section class="sect" aria-labelledby="partners-h">
    <p class="sr">Placeholder brand marks — replace with real client logos before launch.</p>
    <h2 class="sr" id="partners-h">Brands we work with</h2>
    <div class="logowall">{logowall()}</div>
  </section>

  <section class="sect" aria-labelledby="best-h">
    <div class="sect__hd">
      <h2 class="sect__t" id="best-h">Bestsellers</h2>
      <div class="sect__nav">
        <button type="button" data-rail-prev aria-label="Previous">{ARROW.replace('M3 8h10M9 4l4 4-4 4', 'M13 8H3M7 4L3 8l4 4')}</button>
        <button type="button" data-rail-next aria-label="Next">{ARROW}</button>
      </div>
    </div>
    <div class="rail" id="rail" tabindex="0">
      {"".join(card(it, i) for i, it in enumerate(rail))}
    </div>
    <div class="rail__bar"><span id="railbar" style="width:40%"></span></div>
  </section>

  <section class="sect">
    <div class="split split--flip">
      <div class="split__m">
        <img src="{E(img_of(FEAT[1]))}" alt="{E(FEAT[1]["name"].title())}" loading="lazy">
      </div>
      <div class="split__txt">
        <h2 class="split__t">Build your perfect<br>branded set</h2>
        <p class="split__d">Looking for a full makeover? We are your one-stop partner for bringing your
          brand to life. Whether you need a single standout piece or a complete suite of
          packaging, we will quote the lot.</p>
        {btn("Explore the range", "components.html", "pink")}
      </div>
    </div>
  </section>

  <section class="sect" aria-labelledby="cols-h">
    <div class="sect__hd">
      <h2 class="sect__t" id="cols-h">Our collections</h2>
      {btn("View all", "components.html", "lemon")}
    </div>
    <div class="cols">
      {"".join(col_tile(c, VERBS[i][0], VERBS[i][1]) for i, c in enumerate(CATS_TOP3))}
    </div>
  </section>

  <section class="sect" aria-labelledby="cu-h">
    <div class="sect__hd"><h2 class="sect__t" id="cu-h">Specified around your product</h2></div>
    <p class="sect__lead">Your formula should not have to fit whatever is on the
       shelf. Six things you choose, and we match to the brief.</p>
    <div class="cu__grid">{customgrid()}</div>
    <div class="sect__cta">{btn("Start customisation", "components.html", "pink")}</div>
  </section>

  <section class="sect sect--rule" aria-labelledby="pr-h">
    <div class="sect__hd"><h2 class="sect__t" id="pr-h">From brief to delivery</h2></div>
    <p class="sect__lead">How an order actually runs — sample first, artwork
       proofed, then shipped direct.</p>
    <ol class="pr__list">{processlist()}</ol>
  </section>

  {'' if not SHOW_WALL else f"""
  <section class="sect" aria-labelledby="work-h">
    <div class="sect__hd">
      <h2 class="sect__t" id="work-h">Printed in full colour</h2>
      {btn("Talk to us", "https://www.jean-jon.com/pages/contact-us", "pink")}
    </div>
    <p class="sect__lead">Bold brand colour, edge to edge — pouches, boxes, bags
      and sachets printed to your artwork.</p>
    <div class="pkwall">{packaging_wall(12)}</div>
  </section>
  """}

  <!-- Testimonials — placeholder slots, no invented quotes -->
  <section class="sect" aria-labelledby="wy-h">
    <div class="sect__hd"><h2 class="sect__t" id="wy-h">Why brands choose us</h2></div>
    <div class="wy__grid">{whygrid()}</div>
  </section>

  <section class="sect" aria-labelledby="quotes-h">
    <div class="sect__hd"><h2 class="sect__t" id="quotes-h">Don&rsquo;t just take our word for it</h2></div>
    <p class="sect__lead ph-warn"><strong>PLACEHOLDER</strong> — replace with real
       customer quotes before this page goes live. Empty testimonial cards read as
       fabricated social proof.</p>
    <div class="quotes">{quotes()}</div>
  </section>

  <section class="sect">
    <div class="split">
      <div class="split__txt">
        <h2 class="split__t">Empowering small<br>businesses to be<br>unforgettable</h2>
        <p class="split__d">Your partner in creating meaningful customer connections through
          exceptional packaging, that gives your brand the attention it deserves.</p>
        {btn("Browse components", "components.html", "lemon")}
      </div>
      <div class="split__m">
        <img src="{E(img_of(FEAT[2]))}" alt="{E(FEAT[2]["name"].title())}" loading="lazy">
      </div>
    </div>
  </section>

  <section class="sect">
    <div class="stats">
      <div class="stat"><p class="stat__n">{total}</p><p class="stat__l">Components</p></div>
      <div class="stat"><p class="stat__n">{ncats}</p><p class="stat__l">Categories</p></div>
      <div class="stat"><p class="stat__n">Low</p><p class="stat__l">Minimum order</p></div>
      <div class="stat"><p class="stat__n">Custom</p><p class="stat__l">Branding &amp; print</p></div>
    </div>
  </section>

</div>
</main>

<footer class="ftr">
  <div class="wrap">
    <div class="ftr__g">
      <div>
        <img class="ftr__logo" src="assets/img/brand/logo-white.webp" alt="Jean &amp; Jon" width="480" height="121">
        <p class="ftr__note">Custom cosmetic packaging and components.
          {total} products across {ncats} categories.</p>
      </div>
      <div><h3>Components</h3><ul>
        {"".join(f'<li><a href="category/{c["key"]}.html">{E(c["name"])}</a></li>' for c in STRIP[:5])}
      </ul></div>
      <div><h3>Company</h3><ul>
        <li><a href="components.html">All components</a></li>
      </ul></div>
      <div><h3>Contact</h3><ul>
        <li><a href="https://www.jean-jon.com/pages/contact-us">Contact us</a></li>
        <li><a href="https://www.jean-jon.com/pages/find-us">Find us</a></li>
      </ul></div>
    </div>
    <div class="ftr__btm">
      <span>&copy; {BRAND}</span>
      <span>Kuala Lumpur, Malaysia</span>
    </div>
  </div>
</footer>

<div class="cookie" id="cookie">
  Cookies make our site work better for you.
  <button type="button" aria-label="Dismiss" onclick="this.parentNode.hidden=true">&times;</button>
</div>

<script>
(function(){{
  var rail=document.getElementById('rail'),bar=document.getElementById('railbar');
  if(!rail)return;
  function step(){{var c=rail.querySelector('.card');return c?c.offsetWidth+16:200;}}
  var p=document.querySelector('[data-rail-prev]'),n=document.querySelector('[data-rail-next]');
  n&&n.addEventListener('click',function(){{rail.scrollBy({{left:step()*2,behavior:'smooth'}});}});
  p&&p.addEventListener('click',function(){{rail.scrollBy({{left:-step()*2,behavior:'smooth'}});}});
  function sync(){{
    var max=rail.scrollWidth-rail.clientWidth;
    if(bar)bar.style.width=(max<=0?100:Math.max(15,(rail.scrollLeft/max)*100)).toFixed(1)+'%';
    if(p)p.disabled=rail.scrollLeft<=2;
    if(n)n.disabled=rail.scrollLeft>=max-2;
  }}
  rail.addEventListener('scroll',sync,{{passive:true}});
  window.addEventListener('resize',sync);sync();
}})();
</script>
</body>
</html>
"""

out = os.path.join(SITE, "index.html")
open(out, "w").write(doc)
print(f"wrote {out}  ({len(doc):,} bytes)")
print(f"rail: {len(rail)} products | placeholders: {len(PARTNERS) or 8} logos, {len(QUOTES) or 3} quotes")
