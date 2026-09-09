import sys, json, os
sys.path.insert(0,'/private/tmp/claude-501/-Users-iqbalothman-Desktop-Jeaness---Jon/5aa85757-3edd-436c-943c-844e17d88166/scratchpad')
from desc import fetch, parse, structure
from concurrent.futures import ThreadPoolExecutor

SD="/Users/iqbalothman/Desktop/Jeaness & Jon/jean-jon-site/_build/site_data.json"
OUT="/private/tmp/claude-501/-Users-iqbalothman-Desktop-Jeaness---Jon/5aa85757-3edd-436c-943c-844e17d88166/scratchpad/descriptions.json"
d=json.load(open(SD))
items=d["items"]
done=json.load(open(OUT)) if os.path.exists(OUT) else {}

def work(it):
    pid=it["id"]
    if pid in done: return None
    h=fetch(it["url"])
    if not h: return (pid,{"error":"fetch"})
    lines=parse(h)
    if not lines: return (pid,{"facts":{},"sections":[]})
    f,secs=structure(lines)
    return (pid,{"facts":f,"sections":secs})

todo=[i for i in items if i["id"] not in done]
print("to fetch:",len(todo),flush=True)
with ThreadPoolExecutor(6) as ex:
    for n,r in enumerate(ex.map(work,todo),1):
        if r: done[r[0]]=r[1]
        if n%50==0:
            json.dump(done,open(OUT,"w"))
            print(f"  {n}/{len(todo)}",flush=True)
json.dump(done,open(OUT,"w"))
withdesc=sum(1 for v in done.values() if v.get("sections") or v.get("facts"))
errs=sum(1 for v in done.values() if v.get("error"))
print(f"\nDONE total={len(done)} with_content={withdesc} empty={len(done)-withdesc-errs} errors={errs}")
