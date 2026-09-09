import json, re, collections, os
# REQUIRES jean-jon-catalog/ — DELETED 2026-09-08 to reclaim 5.2GB.
# This script (builds site_data.json from catalog.json) cannot run until it is
# restored by re-scraping jean-jon.com. The generated site does not need it:
# all 1469 webp images and 448 cutouts live in assets/img/.
CAT="/Users/iqbalothman/Desktop/Jeaness & Jon/jean-jon-catalog"
c=json.load(open(os.path.join(CAT,"catalog.json")))

# ---- form factor = navigation (mutually exclusive, priority order) ----
FORM=[
 ("lips","Lips","Lipstick, lipmatte, liptint and lip balm casings",
  ["lipstick","lipmatte-liptint-case","lips-treatment-casing","lipstick-glossy-acrylic",
   "lipstick-glossy-plastic","lipmatte-glossy-plastic","lipmatte-matte-plastic"],
  r"lipstick|lipmatte|lip matte|liptint|lipbalm|lip balm"),
 ("powder-colour","Powder & Colour","Compacts, cushions, eyeshadow, brow and mascara",
  ["compact-powder","compact-powder-blender","loose-powder-case","bb-cushion-case",
   "eye-shadow-case","mascara","eyebrow-pencil","blush-set","nail-polish-3g","nail-polish-bottle"],
  r"eye ?shadow|compact|cushion|mascara|blush|brow|nail polish"),
 ("tubes","Tubes","Soft tubes and pump tubes",
  ["soft-tube-collections","pump-tube"], r"\btube\b"),
 ("droppers","Droppers","Serum and essential oil droppers",
  ["serum-dropper","essential-oil"], r"dropper"),
 ("boxes","Boxes & Packaging","Gift boxes and outer packaging",
  ["cylinder-shape-box"], r"\bbox\b"),
 ("jars","Jars & Containers","Cream jars, pomade jars and toner pad containers",
  ["variety-of-jar","jar-collection-glossy-glass","glossy-aluminium"],
  r"\bjar\b|pomade|container|toner pad"),
 ("bottles","Bottles & Pumps","Airless, spray, mist and pump bottles",
  ["bottles","spray-bottle-collections","perfumed-glass-spray-collection","moist-spray","mist-spray",
   "shaker-bottles","supplement-bottle","acrylic-bottle-pump-collection","bottle-plastic-pump-collections"],
  r"bottle|pump|spray|mist|airless|perfume|roll-?on|capsule"),
 ("caps","Caps & Closures","Screw, flip, roller, pump and tear-off caps",
  ["screw-cap","flip-cap","roller-cap","tear-off","twist-cap-tear-off-pouch"],
  r"flip cap|screw cap|roller cap|tear off"),
 ("sachets","Sachets & Pouches","Foil sachets, pouches and food grade packaging",
  ["aluminium-foil-sachet","food-grade-pouch","pillow-sachet-15cm-x-4cm","three-side-sachet"], r"sachet|pouch"),
 ("accessories","Accessories","Puffs, blenders, bags, brushes and applicators",
  ["makeup-accessories","makeupaccessories","beauty-blender","cushion-air-puff",
   "loose-powder-puff","cosmetic-bag","eye-shadow-blusher"],
  r"buffer|funnel|bag|cotton pad|puff|blender|brush|cloth"),
 ("equipment","Equipment","Manufacturing and salon equipment",
  ["essentials-equipment","preloved-cosmetic-manufactured-machine"], r"machine|mixer|dryer|compressor|fridge|tank"),
]
# ---- use case = cross filter (non exclusive) ----
USE={"facial-cleanser":"Cleanser","sunscreen-container":"Sunscreen","moisturizer-jar":"Moisturiser",
     "serum-dropper":"Serum","essential-oil":"Essential Oil","lips-treatment-casing":"Lip Care",
     "supplement-bottle":"Supplement","food-grade-pouch":"Food Grade"}
MATERIAL={"glass":"Glass","matte-glass":"Glass","jar-collection-glossy-glass":"Glass",
 "acrylic":"Acrylic","matte-acrylic":"Acrylic","glossy-acrylic":"Acrylic","lipstick-glossy-acrylic":"Acrylic",
 "plastic":"Plastic","matte-plastic":"Plastic","matte-plastic-1":"Plastic",
 "glossy-plastic":"Plastic","glossy-plastic-1":"Plastic","glossy-aluminium":"Aluminium"}
BADGE={"new-arrival":"New","top-selling-product":"Bestseller"}

pid2slugs=collections.defaultdict(set); prod={}
for title,d in c.items():
    for p in d['products']:
        pid2slugs[p['id']].add(d['slug']); prod[p['id']]=p

assigned={}
for key,name,desc,slugs,pat in FORM:
    s=set(slugs)
    for pid,ps in pid2slugs.items():
        if pid not in assigned and (ps & s): assigned[pid]=key
for pid,p in prod.items():
    if pid in assigned: continue
    n=p['name'].lower()
    for key,name,desc,slugs,pat in FORM:
        if re.search(pat,n): assigned[pid]=key; break
    else: assigned[pid]="accessories"

items=[]
for pid,p in prod.items():
    sl=pid2slugs[pid]
    items.append({
      "id":pid,"name":p["name"],"sku":p["sku"],"price":float(p["price_myr"] or 0),
      "url":p["url"],"cat":assigned[pid],
      "uses":sorted({USE[s] for s in sl if s in USE}),
      "materials":sorted({MATERIAL[s] for s in sl if s in MATERIAL}),
      "badges":sorted({BADGE[s] for s in sl if s in BADGE}),
      "images":p["images"],
    })
items.sort(key=lambda x:(x["cat"],x["name"]))
cats=[{"key":k,"name":n,"desc":d,"count":sum(1 for i in items if i["cat"]==k)} for k,n,d,_,_ in FORM]
out={"cats":cats,"items":items,
     "uses":sorted({u for i in items for u in i["uses"]}),
     "materials":sorted({m for i in items for m in i["materials"]})}
json.dump(out,open("/private/tmp/claude-501/-Users-iqbalothman-Desktop-Jeaness---Jon/5aa85757-3edd-436c-943c-844e17d88166/scratchpad/site_data.json","w"))
for x in cats: print(f"  {x['count']:4d}  {x['name']}")
print("  ----\n  ",len(items),"products |",sum(x['count'] for x in cats),"in nav")
print("  uses:",out["uses"]); print("  materials:",out["materials"])
print("  with >=1 image:",sum(1 for i in items if i["images"]))
