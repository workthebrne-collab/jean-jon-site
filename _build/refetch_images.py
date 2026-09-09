"""Muat turun semula gambar produk resolusi penuh dari CDN.

Folder sumber asal (jean-jon-catalog/, 5.2GB) telah dipadam. URL CDN asal
masih tersimpan dalam site_data.json, jadi gambar boleh diambil semula terus
tanpa perlu scrape laman web.

Output: catalog-images/<kategori>/<nama-produk>-<n>.jpg

Sifat penting:
  - Resumable: fail yang sudah wujud dan sah akan dilangkau.
  - Nama fail dari nama produk (slug), bukan hash, supaya boleh dibaca manusia.
  - Nama pendua diberi suffix -2, -3 supaya tiada fail bertindih.
  - Setiap muat turun disahkan sebagai imej sah sebelum disimpan.
"""
import json, os, re, sys, time, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT  = os.path.join(ROOT, "catalog-images")

data  = json.load(open(os.path.join(HERE, "site_data.json")))
items = data["items"]
CATS  = {c["key"]: c["name"] for c in data["cats"]}

def slug(s: str) -> str:
    s = s.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)[:70] or "item"

def cat_dir(key: str) -> str:
    """Folder ikut nama kategori yang boleh dibaca, bukan key."""
    return slug(CATS.get(key, key or "uncategorised"))

def ext_of(url: str) -> str:
    m = re.search(r"\.(jpe?g|png|webp|gif)(?:\?|$)", url, re.I)
    return "." + (m.group(1).lower().replace("jpeg", "jpg") if m else "jpg")

def valid_image(path: str) -> bool:
    try:
        from PIL import Image
        with Image.open(path) as im:
            im.verify()
        return os.path.getsize(path) > 1024
    except Exception:
        return False

# --- rancang: bina senarai (url, destinasi) dengan nama unik ---------------
plan, used = [], set()
for it in items:
    urls = it.get("images") or []
    base = slug(it["name"])
    d    = os.path.join(OUT, cat_dir(it.get("cat")))
    for i, u in enumerate(urls):
        stem = base if len(urls) == 1 else f"{base}-{i+1}"
        key  = (d, stem)
        n = 2
        while key in used:                      # nama produk boleh berulang
            stem = f"{base}-{i+1}-{n}" if len(urls) > 1 else f"{base}-{n}"
            key = (d, stem); n += 1
        used.add(key)
        plan.append((u, os.path.join(d, stem + ext_of(u)), it["name"]))

print(f"produk: {len(items)}   gambar: {len(plan)}   kategori: {len(CATS)}")

if "--plan" in sys.argv:                        # dry run
    from collections import Counter
    c = Counter(os.path.basename(os.path.dirname(p)) for _, p, _ in plan)
    for k, v in sorted(c.items(), key=lambda t: -t[1]):
        print(f"  {k:24} {v:4}")
    print("\ncontoh:")
    for _, p, nm in plan[:5]:
        print(f"  {os.path.relpath(p, ROOT)}")
    sys.exit()

# --- muat turun ------------------------------------------------------------
# Guna curl, bukan urllib: Python di macOS ini tiada bundle sijil CA, jadi
# urlopen() gagal dengan CERTIFICATE_VERIFY_FAILED untuk semua URL https.
# curl memakai keychain sistem, jadi pengesahan TLS kekal aktif (bukan
# dimatikan) dan muat turun berfungsi.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")
ok = skip = fail = 0
failures = []

for n, (url, dest, name) in enumerate(plan, 1):
    if os.path.exists(dest) and valid_image(dest):
        skip += 1
        continue
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    for attempt in range(3):
        r = subprocess.run(
            ["curl", "-sS", "--fail", "--location", "--max-time", "60",
             "-A", UA, "-o", tmp, url],
            capture_output=True, text=True)
        if r.returncode == 0 and valid_image(tmp):
            os.replace(tmp, dest); ok += 1
            break
        if os.path.exists(tmp):
            os.remove(tmp)
        if attempt == 2:
            fail += 1
            err = (r.stderr or "bukan imej sah").strip().replace("\n", " ")[:120]
            failures.append(f"{name}\t{url}\t{err}")
        else:
            time.sleep(1.5 * (attempt + 1))
    if n % 50 == 0:
        print(f"  {n}/{len(plan)}  turun={ok} langkau={skip} gagal={fail}", flush=True)

print(f"\nSIAP  turun={ok}  langkau={skip}  gagal={fail}")
if failures:
    fp = os.path.join(OUT, "_gagal.txt")
    open(fp, "w").write("\n".join(failures))
    print("senarai gagal:", fp)
