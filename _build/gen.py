import json, os, re, html, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chrome import CHEV, SEARCH, ICON_QUOTE, CAT_ICONS, BESPOKE_ICON
SITE="/Users/iqbalothman/Desktop/Jeaness & Jon/jean-jon-site"
d=json.load(open(os.path.join(SITE,"_build","site_data.json")))
DESC_PATH=os.path.join(SITE,"_build","descriptions.json")
DESC=json.load(open(DESC_PATH)) if os.path.exists(DESC_PATH) else {}
CUT_PATH=os.path.join(SITE,"_build","cutouts.json")
CUT=json.load(open(CUT_PATH)) if os.path.exists(CUT_PATH) else {}

def hero_img(it):
    """Gambar asal yang di-scrape — bukan versi buang latar."""
    return (it["img"][0], "")
items,cats=d["items"],d["cats"]
byk={c["key"]:c for c in cats}
E=html.escape

JUNK=re.compile(r"whatsapp|screenshot|^image[\s_-]|\.(jpg|jpeg|png)\b|^website[\s_-]*\d*$|^\d{4}-\d\d-\d\d|^\d{8}[_-]\d+",re.I)
SMALL={"with","and","on","in","for","the","of","to","a"}
KEEP={"BB","CC","ML","UV","PP","PE","SPF","3D","LED","PVC","PET"}
def clean_sku(s):
    s=(s or "").strip()
    return "" if (not s or s.upper()=="COMING-SOON" or JUNK.search(s)) else s
def nice(n):
    if not n.isupper(): return n
    out=[]
    for i,w in enumerate(n.split()):
        u=w.strip("|()").upper()
        if u in KEEP or re.search(r"\d",w): out.append(w)
        elif w.lower() in SMALL and i>0: out.append(w.lower())
        else: out.append(w.capitalize())
    return " ".join(out)

SPEC_ORDER=["Head","Neck","Body","Cap","Base","Material","Capacity","Size","Volume","Colour","Color"]

def copy_block(it):
    """Render the scraped product copy: lead, availability tags, sections."""
    dd=DESC.get(it["id"]) or {}
    secs=dd.get("sections") or []
    if not secs: return "", {}
    facts={k:v for k,v in (dd.get("facts") or {}).items()}
    lead=""; tags=[]; blocks=[]
    for sec in secs:
        head=sec.get("heading"); items=[x for x in sec.get("items") or [] if x]
        if not items: continue
        if head is None:
            # first line is the availability lead; the rest are short selling
            # points, unless a question introduces its own dashed answer list
            lead=items[0]
            rest=items[1:]
            qi=next((n for n,x in enumerate(rest) if x.rstrip().endswith("?")), None)
            if qi is not None:
                tags=[x for x in rest[:qi] if len(x)<=34]
                ans=[re.sub(r"^[-–•]\s*","",x) for x in rest[qi+1:] if x.strip(" -–•")]
                if ans:
                    lis="".join(f"<li>{E(x)}</li>" for x in ans)
                    blocks.append(f'<div class="pcopy__sec"><h3 class="pcopy__h">{E(rest[qi])}</h3>'
                                  f'<ul class="pcopy__list">{lis}</ul></div>')
            else:
                tags=[x for x in rest[:4] if len(x)<=34]
        else:
            lis="".join(f"<li>{E(x)}</li>" for x in items)
            blocks.append(f'<div class="pcopy__sec"><h3 class="pcopy__h">{E(head)}</h3>'
                          f'<ul class="pcopy__list">{lis}</ul></div>')
    if not (lead or tags or blocks): return "", facts
    out=['<div class="pcopy">']
    if lead: out.append(f'<p class="pcopy__lead">{E(lead)}</p>')
    if tags:
        out.append('<div class="pcopy__tags">'
                   +"".join(f'<span class="pcopy__tag">{E(t)}</span>' for t in tags)
                   +'</div>')
    out+=blocks
    out.append('</div>')
    return "".join(out), facts

def slugify(s):
    s=re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
    return s[:70] or "item"
seen={}
for it in items:
    it["name"]=nice(it["name"]); it["sku"]=clean_sku(it["sku"])
    b=slugify(it["name"]); s=b; n=2
    while s in seen: s=f"{b}-{n}"; n+=1
    seen[s]=1; it["slug"]=s
price=lambda v: f"RM {v:,.2f}"
CAT_ICONS_G={}
ICON_SEARCH_G=('<svg width="14" height="14" viewBox="0 0 15 15" fill="none" '
  'stroke="currentColor" stroke-width="1.4"><circle cx="6.6" cy="6.6" r="5"/>'
  '<path d="M10.3 10.3 14 14"/></svg>')
ICON_QUOTE_G=('<svg width="13" height="13" viewBox="0 0 14 14" fill="none" '
  'stroke="currentColor" stroke-width="1.3"><path d="M3 1h5l3 3v9H3z"/>'
  '<path d="M8 1v3h3"/></svg>')
STRIP_G=sorted(cats, key=lambda c:-c["count"])[:6]

ARROW='<svg width="13" height="9" viewBox="0 0 13 9" fill="none" stroke="#111214" stroke-width="1.2"><path d="M8.4.8 12 4.5 8.4 8.2M12 4.5H.6"/></svg>'
CARET='<svg width="8" height="5" viewBox="0 0 8 5" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M1 1l3 3 3-3"/></svg>'

FONT=('<link rel="preconnect" href="https://fonts.googleapis.com">'
 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
 'family=DM+Sans:wght@400;500;600;700;800&display=swap">')

def header(rel,crumb):
    # Mega-menu: satu sumber kebenaran, tiga paksi tapisan sebenar
    col_format="".join(f'<a href="{rel}category/{c["key"]}.html">{E(c["name"])}'
                       f'<i>{c["count"]}</i></a>' for c in cats)
    col_use="".join(f'<a href="{rel}uses/{slugify(u)}.html">{E(u)}</a>' for u in d["uses"])
    col_mat="".join(f'<a href="{rel}materials/{slugify(m)}.html">{E(m)}</a>' for m in d["materials"])
    return f"""<div class="hdr__strip" aria-hidden="true"></div>
<header class="hdr">
  <div class="hdr__bar">
    <a class="hdr__logo" href="{rel}index.html" aria-label="Jean &amp; Jon — home">
      <img src="{rel}assets/img/brand/logo-dark.webp" alt="Jean &amp; Jon" width="480" height="121"></a>
    <nav class="hdr__nav" aria-label="Primary">
      <a href="{rel}components.html">Components {CHEV}</a>
    </nav>
    <div class="hdr__search">
      <label class="sr" for="q">Search products</label>
      {SEARCH}
      <input id="q" type="search" placeholder="Search for bottles, jars, tubes" autocomplete="off">
    </div>
    <div class="hdr__end">
      <span>MY (RM) {CHEV}</span>
      <a class="hdr__quote" href="https://www.jean-jon.com/pages/contact-us" target="_blank" rel="noopener">
        {ICON_QUOTE}Request a quote</a>
    </div>
  </div>
  <nav class="catbar" aria-label="Categories">
    <div class="catbar__in">
    {"".join(f'<a href="{rel}category/{c["key"]}.html">{CAT_ICONS.get(c["key"],"")}{E(c["name"])}</a>' for c in STRIP_G)}
      <a href="{rel}components.html">{BESPOKE_ICON}Bespoke</a>
    </div>
  </nav>
</header>"""

def footer(rel):
    a="".join(f'<li><a href="{rel}category/{c["key"]}.html">{E(c["name"])}</a></li>' for c in cats[:5])
    b="".join(f'<li><a href="{rel}category/{c["key"]}.html">{E(c["name"])}</a></li>' for c in cats[5:10])
    return f"""<footer class="ftr"><div class="wrap"><div class="ftr__in">
<div><img class="ftr__lg" src="{rel}assets/img/brand/logo-white.webp" alt="Jean &amp; Jon" width="480" height="121">
<p style="max-width:36ch;margin:0">High-quality custom made cosmetic packaging. One-stop solution
from bottles and jars to caps, tubes and sachets.</p></div>
<div><h4>Components</h4><ul>{a}</ul></div>
<div><h4>More</h4><ul>{b}</ul></div>
<div><h4>Company</h4><ul><li><a href="{rel}components.html">All components</a></li>
<li><a href="https://www.jean-jon.com" rel="noopener">jean-jon.com</a></li></ul></div>
</div><div class="ftr__base"><span>&copy; 2026 Jean &amp; Jon</span>
<span>{len(items)} components &middot; {len(cats)} categories</span></div></div></footer>"""

def page(title,desc,body,rel="",crumb=""):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
{FONT}<link rel="stylesheet" href="{rel}assets/css/main.css">
<link rel="icon" type="image/png" href="{rel}assets/img/brand/favicon.png">
<link rel="apple-touch-icon" href="{rel}assets/img/brand/favicon.png">
</head><body>{header(rel,crumb)}<main>{body}</main>{footer(rel)}
<script src="{rel}assets/js/site.js" defer></script></body></html>"""

def card(it,rel=""):
    brand=E(byk[it["cat"]]["name"])
    return f"""<article class="pc" data-p="{it['price']}"><span class="pc__brand">{brand}</span>
<a href="{rel}product/{it['slug']}.html">
<div class="pc__m"><img src="{rel}{hero_img(it)[0]}"{hero_img(it)[1]} alt="{E(it['name'])}" loading="lazy" decoding="async"></div>
<div class="pc__f"><p class="pc__n">{E(it['name'])}</p><span class="pc__v">View</span></div>
</a></article>"""

os.makedirs(f"{SITE}/category",exist_ok=True); os.makedirs(f"{SITE}/product",exist_ok=True)

def crow(c,rel=""):
    sub=[i for i in items if i["cat"]==c["key"]][:6]
    return f"""<section class="crow">
<div class="crow__l"><h2>{E(c['name'])}</h2><p>{E(c['desc'])}</p>
<a class="viewall" href="{rel}category/{c['key']}.html"><i>{ARROW}</i>View all</a></div>
<div class="crow__r">{''.join(card(i,rel) for i in sub)}</div></section>"""

# ---------- components listing (paginated, 4 rows/page) ----------
PER=4
pages_n=math.ceil(len(cats)/PER)
for pg in range(1,pages_n+1):
    chunk=cats[(pg-1)*PER:pg*PER]
    def pl(n): return "components.html" if n==1 else f"components-{n}.html"
    links="".join(
      (f'<span class="on">{n}</span>' if n==pg else f'<a href="{pl(n)}">{n}</a>')
      for n in range(1,pages_n+1))
    prev=f'<a class="nav" href="{pl(pg-1)}">&lsaquo;</a>' if pg>1 else '<span class="nav">&lsaquo;</span>'
    nxt=f'<a class="nav" href="{pl(pg+1)}">&rsaquo;</a>' if pg<pages_n else '<span class="nav">&rsaquo;</span>'
    az="".join(f"""<div class="azgroup"><h3>{E(c['name'])}</h3><ul>{''.join(
        f'<li><a href="product/{i["slug"]}.html">{E(i["name"])}</a></li>'
        for i in items if i["cat"]==c["key"])}</ul></div>""" for c in cats)
    body=f"""<div class="wrap"><div class="ptitle"><h1>Components</h1></div><div class="rule"></div>
<div class="fbar"><span class="fbar__lab">Industry:</span>
<span class="selwrap"><select id="indsel"><option value="">All industries</option>
{''.join(f'<option value="{c["key"]}">{E(c["name"])}</option>' for c in cats)}</select></span>
<span class="fbar__end"><span class="vtog">
<button id="vaz" aria-pressed="false" title="A–Z list">A-Z</button>
<button id="vgr" aria-pressed="true" title="Grid"><svg width="11" height="11" viewBox="0 0 11 11" fill="currentColor"><rect width="4.6" height="4.6"/><rect x="6.4" width="4.6" height="4.6"/><rect y="6.4" width="4.6" height="4.6"/><rect x="6.4" y="6.4" width="4.6" height="4.6"/></svg></button>
</span></span></div>
<div id="rows">{''.join(crow(c) for c in chunk)}</div>
<div class="azview" id="azview" hidden>{az}</div>
<nav class="pag" id="pag">{prev}{links}{nxt}</nav></div>"""
    open(f"{SITE}/{pl(pg)}","w").write(page(
      "Components — Jean & Jon","All cosmetic packaging components by category.",
      body,crumb='<a href="index.html">Home</a> / Components'))

# ---------- home ----------
home=f"""<div class="wrap"><section class="hero">
<h1>Cosmetic packaging components</h1>
<p>We supply high-quality custom made cosmetic packaging — bottles, jars, tubes,
caps and casings — with a one-stop solution for every part of your range.</p>
<a class="hero__b" href="components.html">Browse components {ARROW.replace('#111214','#fff')}</a>
</section></div>
<div class="wrap"><div class="stats">
<div><b>{len(items)}</b><span>Components</span></div>
<div><b>{len(cats)}</b><span>Categories</span></div>
<div><b>Low</b><span>Minimum order</span></div>
<div><b>Custom</b><span>Branding &amp; print</span></div>
</div></div>
<div class="wrap">{''.join(crow(c) for c in cats[:4])}
<nav class="pag"><a href="components.html">View all components</a></nav></div>"""
# NOTE: index.html dimiliki oleh gen_home.py (halaman utama jenama sebenar).
# Versi lama di sini dikekalkan sebagai rujukan tetapi TIDAK ditulis lagi —
# menulisnya akan memadam halaman utama.
# open(f"{SITE}/index.html","w").write(page(...))

# ---------- category pages ----------
for c in cats:
    sub=[i for i in items if i["cat"]==c["key"]]
    body=f"""<div class="wrap"><div class="ptitle"><h1>{E(c['name'])}</h1>
<p>{E(c['desc'])}</p></div><div class="rule"></div>
<div class="fbar"><span class="fbar__lab">{len(sub)} components</span>
<span class="fbar__end"><span class="selwrap"><select id="sort">
<option value="feat">Sort: Featured</option><option value="az">Sort: A–Z</option>
<option value="lo">Price: low to high</option><option value="hi">Price: high to low</option>
</select></span></span></div>
<div class="gridview" id="grid">{''.join(card(i,'../') for i in sub)}</div></div>"""
    open(f"{SITE}/category/{c['key']}.html","w").write(page(
      f"{c['name']} — Jean & Jon",c["desc"],body,rel="../",
      crumb=f'<a href="../components.html">Components</a> / {E(c["name"])}'))

# ---------- application (use) + material pages ----------
def facet_pages(kind, values, label_sing, blurb):
    """Satu halaman per kegunaan/bahan supaya link nav tidak mati."""
    for v in values:
        sub=[i for i in items if v in i[kind]]
        if not sub: continue
        key=slugify(v)
        body=f"""<div class="wrap"><div class="ptitle"><h1>{E(v)}</h1>
<p>{E(blurb.format(v=v))}</p></div><div class="rule"></div>
<div class="fbar"><span class="fbar__lab">{len(sub)} components</span>
<span class="fbar__end"><span class="selwrap"><select id="sort">
<option value="feat">Sort: Featured</option><option value="az">Sort: A-Z</option>
<option value="lo">Price: low to high</option><option value="hi">Price: high to low</option>
</select></span></span></div>
<div class="gridview" id="grid">{''.join(card(i,'../') for i in sub)}</div></div>"""
        open(f"{SITE}/{kind}/{key}.html","w").write(page(
          f"{v} - Jean & Jon", blurb.format(v=v), body, rel="../",
          crumb=f'<a href="../components.html">Components</a> / {E(label_sing)} / {E(v)}'))

os.makedirs(f"{SITE}/uses",exist_ok=True); os.makedirs(f"{SITE}/materials",exist_ok=True)
facet_pages("uses", d["uses"], "Application",
            "Packaging suited to {v} formulations.")
facet_pages("materials", d["materials"], "Material",
            "Components manufactured in {v}.")

# ---------- product pages ----------
for it in items:
    c=byk[it["cat"]]
    rel=[i for i in items if i["cat"]==it["cat"] and i["id"]!=it["id"]][:4]
    th="".join(f'<button aria-selected="{"true" if n==0 else "false"}" data-src="../{p}">'
               f'<img src="../{p}" alt="" loading="lazy"></button>'
               for n,p in enumerate(it["img"]))
    copy_html, dfacts = copy_block(it)
    rows=""
    if it["sku"]: rows+=f"<tr><th>Article no.</th><td>{E(it['sku'])}</td></tr>"
    for k in SPEC_ORDER:
        if k in dfacts: rows+=f"<tr><th>{E(k)}</th><td>{E(dfacts[k])}</td></tr>"
    for k,v in dfacts.items():
        if k not in SPEC_ORDER: rows+=f"<tr><th>{E(k)}</th><td>{E(v)}</td></tr>"
    rows+=f'<tr><th>Category</th><td><a href="../category/{c["key"]}.html">{E(c["name"])}</a></td></tr>'
    if it["materials"]: rows+=f"<tr><th>Material</th><td>{E(', '.join(it['materials']))}</td></tr>"
    if it["uses"]: rows+=f"<tr><th>Application</th><td>{E(', '.join(it['uses']))}</td></tr>"
    if it["badges"]: rows+=f"<tr><th>Status</th><td>{E(', '.join(it['badges']))}</td></tr>"
    body=f"""<div class="wrap"><p class="crumb"><a href="../components.html">Components</a> /
<a href="../category/{c['key']}.html">{E(c['name'])}</a> / {E(it['name'])}</p>
<div class="pdp"><div>
<div class="pdp__main"><img id="hero" src="../{hero_img(it)[0]}"{hero_img(it)[1]} alt="{E(it['name'])}"></div>
{f'<div class="pdp__th" id="thumbs">{th}</div>' if len(it['img'])>1 else ''}</div>
<div><p class="pdp__brand">{E(c['name'])}</p><h1>{E(it['name'])}</h1>
<p class="pdp__price">{price(it['price'])}</p>
<div class="pdp__buy">
<a class="cta" href="{E(it['url'])}" target="_blank" rel="noopener">Request a quote</a>
<a class="cta cta--alt" href="../category/{c['key']}.html">All {E(c['name'])}</a></div>
<table class="spec"><tbody>{rows}</tbody></table>
{copy_html}</div></div>
{f'''<h2 class="secth">Related components</h2>
<div class="gridview" style="padding-top:0">{''.join(card(i,'../') for i in rel)}</div>''' if rel else ''}
</div>"""
    open(f"{SITE}/product/{it['slug']}.html","w").write(page(
      f"{it['name']} — Jean & Jon",f"{it['name']} — {c['name']}.",body,rel="../",
      crumb=f'<a href="../category/{c["key"]}.html">{E(c["name"])}</a>'))

print("pages:",1+pages_n+len(cats)+len(items),"| listing pages:",pages_n)
