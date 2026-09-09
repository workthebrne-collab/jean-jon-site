"""U2Net + pembetulan warna tepi (buang sisa backdrop pada piksel separa-telus)."""
import json, os, time, subprocess
import numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
from collections import deque

SCR="/private/tmp/claude-501/-Users-iqbalothman-Desktop-Jeaness---Jon/5aa85757-3edd-436c-943c-844e17d88166/scratchpad"
SITE="/Users/iqbalothman/Desktop/Jeaness & Jon/jean-jon-site"
IMG=os.path.join(SITE,"assets","img")
d=json.load(open(os.path.join(SITE,"_build","site_data.json")))

so=ort.SessionOptions(); so.intra_op_num_threads=4
sess=ort.InferenceSession(os.path.join(SCR,"models","u2net.onnx"), so,
                          providers=["CPUExecutionProvider"])
inp=sess.get_inputs()[0].name
MEAN=np.array([0.485,0.456,0.406],dtype=np.float32)
STD =np.array([0.229,0.224,0.225],dtype=np.float32)

def process(path, erode=2, gamma=2.6):
    im=Image.open(path).convert("RGB")
    x=im.resize((320,320), Image.LANCZOS)
    a=((np.asarray(x).astype(np.float32)/255.0-MEAN)/STD).transpose(2,0,1)[None].astype(np.float32)
    m=sess.run(None,{inp:a})[0][0,0]
    m=(m-m.min())/(m.max()-m.min()+1e-8)
    mk=Image.fromarray((m*255).astype(np.uint8)).resize(im.size, Image.LANCZOS)
    if erode: mk=mk.filter(ImageFilter.MinFilter(erode*2+1))   # kecilkan sedikit
    al=np.clip((np.asarray(mk).astype(np.float32)/255.0-0.5)*gamma+0.5,0,1)

    rgb=np.asarray(im).astype(np.float32)
    corners=np.concatenate([rgb[:8,:8].reshape(-1,3),rgb[:8,-8:].reshape(-1,3),
                            rgb[-8:,:8].reshape(-1,3),rgb[-8:,-8:].reshape(-1,3)])
    bg=np.median(corners,0)
    A=al[...,None]; safe=np.clip(A,0.25,1.0)
    un=(rgb-(1-A)*bg)/safe                       # buang sumbangan backdrop
    blend=np.clip((1-al)/0.75,0,1)[...,None]
    rgb=np.clip(rgb*(1-blend)+un*blend,0,255)

    out=Image.fromarray(rgb.astype(np.uint8)).convert("RGBA")
    out.putalpha(Image.fromarray((al*255).astype(np.uint8)))
    bb=out.getbbox()
    if bb: out=out.crop(bb)
    return out, float((al>0.67).mean())

def frags(im):
    t=im.copy(); t.thumbnail((110,110))
    op=(np.asarray(t)[:,:,3]>170)
    if op.sum()<20: return 9
    h,w=op.shape; seen=np.zeros_like(op); comps=[]
    for y in range(h):
        for x in range(w):
            if op[y,x] and not seen[y,x]:
                q=deque([(y,x)]); seen[y,x]=True; n=0
                while q:
                    cy,cx=q.popleft(); n+=1
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny,nx=cy+dy,cx+dx
                        if 0<=ny<h and 0<=nx<w and op[ny,nx] and not seen[ny,nx]:
                            seen[ny,nx]=True; q.append((ny,nx))
                comps.append(n)
    comps.sort(reverse=True)
    return sum(1 for c in comps[1:] if c>comps[0]*0.02)

items=[i for i in d["items"] if i["img"]]
mapping={}; rejected=[]
t0=time.time()
for n,it in enumerate(items,1):
    fn=os.path.basename(it["img"][0])
    try:
        im,cov=process(os.path.join(IMG,fn))
        f=frags(im)
        if cov<0.012 or cov>0.985 or f>=4:
            rejected.append({"id":it["id"],"name":it["name"],"cov":round(cov,3),"frag":f}); continue
        png=os.path.join(IMG,"cut-"+fn.replace(".webp",".png"))
        im.save(png)
        webp=png.replace(".png",".webp")
        r=subprocess.run(["cwebp","-quiet","-q","86","-alpha_q","100",png,"-o",webp],
                         capture_output=True)
        if r.returncode==0 and os.path.exists(webp):
            os.remove(png); mapping[it["id"]]=os.path.basename(webp)
        else:
            mapping[it["id"]]=os.path.basename(png)
    except Exception as e:
        rejected.append({"id":it["id"],"name":it["name"],"err":str(e)[:60]})
    if n%100==0: print(f"  {n}/{len(items)} ({time.time()-t0:.0f}s)", flush=True)
json.dump(mapping,open(os.path.join(SITE,"_build","cutouts.json"),"w"))
json.dump(rejected,open(os.path.join(SCR,"rejected.json"),"w"))
tot=sum(os.path.getsize(os.path.join(IMG,f)) for f in os.listdir(IMG) if f.startswith("cut-"))
print(f"\nsiap {time.time()-t0:.0f}s | berjaya {len(mapping)} | ditolak {len(rejected)} | {tot/1048576:.1f} MB")
