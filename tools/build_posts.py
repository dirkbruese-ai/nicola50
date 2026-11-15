"""Erzeugt posts.js aus dem Padlet-CSV-Export.
Aufruf: python3 tools/build_posts.py <posts.csv> <photos.json> <media-dir>"""
import csv, json, os, sys

# Gruppe pro Padlet-Beitragsnummer: family, old (Münster Girls), new (From home), aus (Gold Coast)
GROUP = {12: "family", 13: "family", 38: "family",
         22: "old", 33: "old", 14: "old", 15: "old", 29: "old",
         3: "aus", 10: "aus", 11: "aus", 16: "aus", 17: "aus", 21: "aus", 23: "aus", 30: "aus",
         35: "aus", 36: "aus", 40: "aus"}
NAME = {2: "Sonja & Christian", 5: "Uwe", 12: "Die Viersener", 13: "Die Viersener", 15: "Ena",
        18: "Susi & Corinna", 20: "Susi & Corinna", 22: "Catherine", 23: "Kate", 24: "DEHNS",
        26: "Nicola (DEHNS)", 33: "Catherine", 34: "Anna-Maria", 38: "Die Buddenbergs"}
SKIP = {1}
CITY = {2: "Gerresheim", 12: "Viersen", 13: "Viersen", 14: "Olching", 15: "Olching", 22: "Hamburg",
        24: "Oberkassel", 26: "Oberkassel", 27: "Oberkassel", 32: "Christchurch", 34: "Düsseldorf"}

csv_path, photos_path, media = sys.argv[1:4]
photos = json.load(open(photos_path))
dur = lambda f: os.path.exists(f) and float(os.popen(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{f}"').read() or 0)
mmss = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
out = []
for r in csv.DictReader(open(csv_path, encoding="utf-8-sig")):
    n = int(r["Post number"])
    if n in SKIP: continue
    clean = lambda k: r[k].strip()
    p = {"n": n, "name": NAME.get(n) or clean("Your (Nick-) Name:") or clean("Author"),
         "group": GROUP.get(n, "new")}
    for key, col in [("title", "Subject"), ("note", "Body"), ("isFor", "Nici is for me..."),
                     ("moment", "My special moment with her..."), ("wish", "I wish Nici...")]:
        if clean(col): p[key] = clean(col)
    if p.get("title") == p.get("note"): p.pop("title")
    if n == 5: p.pop("note", None)
    if n in CITY: p["city"] = CITY[n]
    if str(n) in photos: p["imgs"] = photos[str(n)]
    v, a = f"{media}/v{n}.mp4", f"{media}/a{n}.mp3"
    if os.path.exists(v): p["clip"] = f"v{n}"; p["video"] = mmss(dur(v))
    if os.path.exists(a): p["audio"] = f"a{n}"; p["voice"] = mmss(dur(a))
    out.append(p)
open("posts.js", "w").write("// Erzeugt mit tools/build_posts.py aus dem Padlet-Export\nconst friends = " +
                            json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
print(len(out), "Beiträge")
