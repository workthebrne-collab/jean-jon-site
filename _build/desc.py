import re, html, json, subprocess, unicodedata

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"

def fetch(url, tries=3):
    for a in range(tries):
        p=subprocess.run(["curl","-sS","-L","--max-time","45","-A",UA,url],
                         capture_output=True, timeout=70)
        if p.returncode==0 and p.stdout: return p.stdout.decode("utf-8","ignore")
    return None

# Unicode maths-bold/italic -> plain ASCII (site uses 𝗥𝗲𝗰𝗼𝗺𝗺𝗲𝗻𝗱𝗲𝗱 etc.)
def deunicode(s):
    out=[]
    for ch in s:
        o=ord(ch)
        if 0x1D400<=o<=0x1D7FF:
            d=unicodedata.normalize("NFKD",ch)
            out.append(d if d.isascii() else ch)
        else: out.append(ch)
    return "".join(out)

def clean(t):
    t=html.unescape(t)
    t=deunicode(t)
    t=t.replace(" "," ").replace("​","")
    return re.sub(r"[ \t]+"," ",t).strip()

def parse(page_html):
    m=re.search(r'<div[^>]*product__description[^>]*>(.*?)(?=<div class="product-|<section|</main)',
                page_html, re.S)
    if not m: return None
    frag=m.group(1)
    frag=re.sub(r'<link[^>]*>','',frag)
    frag=re.sub(r'<(script|style)[^>]*>.*?</\1>','',frag,flags=re.S)
    # block-level -> newline, list items -> bullet
    frag=re.sub(r'<li[^>]*>',"\n• ",frag,flags=re.I)
    frag=re.sub(r'<br\s*/?>',"\n",frag,flags=re.I)
    frag=re.sub(r'</(p|div|ul|ol|h\d)>',"\n",frag,flags=re.I)
    txt=re.sub(r'<[^>]+>','',frag)
    txt=clean(txt)
    lines=[re.sub(r'\s+',' ',l).strip() for l in txt.split("\n")]
    lines=[l for l in lines if l and l not in {"•"}]
    # dedupe consecutive repeats
    out=[]
    for l in lines:
        if not out or out[-1]!=l: out.append(l)
    return out

# everything from here on belongs to the reviews widget, not the description
STOP=re.compile(r'^(×|Reviews|Ratings|\(\d+\)|Be the first to review|Write an review|'
                r'How would you rate|More thought about|Submit|Cancel|Sort by|'
                r'Customer Reviews|Related Products|You may also like)', re.I)

def structure(lines):
    """Return ordered sections: [{heading, items}], plus flat key/value specs."""
    facts={}; sections=[]; cur={"heading":None,"items":[]}
    for l in lines:
        if STOP.match(l.lstrip("• ").strip()): break
        b=l.startswith("• ")
        t=l[2:].strip() if b else l
        if not t: continue
        # "Head - Glossy Acrylic" style spec
        m2=re.match(r'^(Head|Neck|Body|Cap|Base|Material|Capacity|Size|Colour|Color|Volume)\s*[-–]\s*(.+)$', t, re.I)
        if m2:
            facts[m2.group(1).capitalize()]=m2.group(2).strip(); continue
        # "Label :" heading, or "Label : value" pair
        m=re.match(r'^([A-Za-z][A-Za-z /&\'-]{2,28})\s*[:：]\s*(.*)$', t)
        if m and len(m.group(1).split())<=4:
            k,v=m.group(1).strip(),m.group(2).strip()
            if v:
                facts[k]=v
            else:
                if cur["items"]: sections.append(cur)
                cur={"heading":k,"items":[]}
            continue
        cur["items"].append(t)
    if cur["items"]: sections.append(cur)
    return facts, sections
