import json, os, subprocess, hashlib
from concurrent.futures import ThreadPoolExecutor
SITE="/Users/iqbalothman/Desktop/Jeaness & Jon/jean-jon-site"
# REQUIRES jean-jon-catalog/ — DELETED 2026-09-08 to reclaim 5.2GB.
# This script (re-encodes source photos to webp) cannot run until it is
# restored by re-scraping jean-jon.com. The generated site does not need it:
# all 1469 webp images and 448 cutouts live in assets/img/.
CAT="/Users/iqbalothman/Desktop/Jeaness & Jon/jean-jon-catalog"
d=json.load(open("/private/tmp/claude-501/-Users-iqbalothman-Desktop-Jeaness---Jon/5aa85757-3edd-436c-943c-844e17d88166/scratchpad/site_data.json"))
IMG=os.path.join(SITE,"assets","img"); os.makedirs(IMG,exist_ok=True)

# map remote image url -> local scraped file
local={}
for root,_,files in os.walk(CAT):
    if "product.json" in files:
        p=json.load(open(os.path.join(root,"product.json")))
        for u,f in zip(p["images"],p.get("image_files",[])):
            fp=os.path.join(root,f)
            if os.path.exists(fp): local.setdefault(u,fp)

jobs=[]
for it in d["items"]:
    outs=[]
    for u in it["images"]:
        src=local.get(u)
        if not src: continue
        name=hashlib.md5(u.encode()).hexdigest()[:16]+".webp"
        jobs.append((src,os.path.join(IMG,name)))
        outs.append("assets/img/products/"+name)
    it["img"]=outs
json.dump(d,open("/private/tmp/claude-501/-Users-iqbalothman-Desktop-Jeaness---Jon/5aa85757-3edd-436c-943c-844e17d88166/scratchpad/site_data.json","w"))

def conv(a):
    src,dst=a
    if os.path.exists(dst) and os.path.getsize(dst)>200: return True
    r=subprocess.run(["cwebp","-quiet","-q","78","-resize","800","0",src,"-o",dst],
                     capture_output=True)
    if r.returncode!=0 or not os.path.exists(dst):
        # source smaller than 800px wide -> no resize
        r=subprocess.run(["cwebp","-quiet","-q","78",src,"-o",dst],capture_output=True)
    return os.path.exists(dst)

print("converting",len(jobs),"images",flush=True)
with ThreadPoolExecutor(8) as ex: res=list(ex.map(conv,jobs))
print("ok:",sum(res),"failed:",len(res)-sum(res),flush=True)
tot=sum(os.path.getsize(os.path.join(IMG,f)) for f in os.listdir(IMG))
print("web image payload: %.1f MB"%(tot/1048576),flush=True)
