"""Erzeugt posts.js aus dem Padlet-CSV-Export.
Aufruf: python3 tools/build_posts.py <posts.csv> <photos.json> <media-dir>"""
import csv, json, os, sys

# Gruppe pro Padlet-Beitragsnummer: family, old (Münster Girls), new (From home), aus (Gold Coast)
GROUP = {50: "family", 53: "family", 12: "family", 13: "family", 55: "family",
         37: "old", 14: "old", 15: "old", 2: "old", 22: "old", 33: "old", 47: "old", 49: "old", 54: "old", 25: "old",
         31: "close", 18: "close", 20: "close", 52: "close", 6: "close", 62: "close", 29: "close", 64: "close",
         24: "close", 26: "close", 27: "close", 28: "close", 19: "close", 66: "close", 67: "close",
         3: "aus", 10: "aus", 11: "aus", 16: "aus", 17: "aus", 23: "aus", 30: "aus",
         35: "aus", 36: "aus", 40: "aus", 41: "aus", 21: "aus"}
# Gold Coast unterteilt (Dirk 16.11.)
TEAM = {17: "Hockey", 21: "Hockey", 11: "Hockey", 3: "School", 41: "School", 23: "School",
        10: "Padel", 30: "Padel", 16: "Padel", 36: "Padel", 35: "Padel", 40: "Padel"}
# Reihenfolge innerhalb der Gruppen: Beitragsnummern zuerst in dieser Folge, Rest nach Eingang, LAST ganz ans Ende
ORDER = [50, 53, 12, 13, 55,
         17, 21, 11, 3, 41, 23, 10, 36, 30, 16, 35, 40,
         37, 14, 15, 2, 22, 33, 47, 49, 54, 25,
         # From home (Dirks Liste 16.11.); Platzhalter: Steffi & Hendrik Rinsche, Nicole & Jens Ritter nach 44
         31, 18, 52, 44, 67, 28, 24, 27, 6, 62, 26, 29, 64, 19, 56, 59, 34, 51, 42, 43, 38, 45, 39, 60, 61,
         46, 65, 58, 4, 57, 7, 5, 48, 8, 9, 63, 32, 66]
LAST = []
NAME = {10: "Lieke", 16: "Candice & Brent", 30: "Alex & Lex", 36: "Jess G", 2: "Sonja & Christian", 5: "Uwe", 12: "Die Viersener", 13: "Die Viersener", 15: "Ena",
        18: "Susi & Corinna", 20: "Susi & Corinna", 22: "Catherine", 23: "Kate", 24: "DEHNS",
        26: "Nicola (DEHNS)", 33: "Catherine", 34: "Anna-Maria", 38: "Die Buddenbergs",
        47: "K-Ro", 49: "Verena", 50: "Mami & Papi", 53: "Katja, Christian, Julia & Alexander",
        54: "Suse", 55: "Viersen Brüses", 58: "Andrea & Geo", 59: "Nina",
        61: "Séchés & Kleins", 63: "Claudi", 65: "Lisa & Stefan", 66: "Katrin & Tim", 67: "Steffi & Hendrik"}
SKIP = {1}  # Export 17.11.: alter Beitrag 66 (Fotos Lisa & Stefan) gelöscht, Fotos liegen bei 65; 66 = Katrin & Tim
CITY = {2: "Gerresheim", 12: "Viersen", 13: "Viersen", 14: "Olching", 15: "Olching", 22: "Hamburg",
        24: "Oberkassel", 26: "Oberkassel", 27: "Oberkassel", 32: "Munich · Christchurch", 34: "Düsseldorf",
        8: "Cologne", 9: "Cologne", 37: "Hamburg", 31: "Düsseldorf", 29: "Düsseldorf", 6: "Düsseldorf",
        55: "Viersen", 50: "Krefeld", 53: "Krefeld", 45: "Düsseldorf", 60: "Düsseldorf",
        63: "Christchurch", 65: "Bonn"}

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
    if n in TEAM: p["team"] = TEAM[n]
    if str(n) in photos: p["imgs"] = photos[str(n)]
    v, a = f"{media}/v{n}.mp4", f"{media}/a{n}.mp3"
    if os.path.exists(v): p["clip"] = f"v{n}"; p["video"] = mmss(dur(v))
    if os.path.exists(a): p["audio"] = f"a{n}"; p["voice"] = mmss(dur(a))
    out.append(p)
# Beiträge zusammenlegen: Quelle -> Ziel (Texte angehängt, Fotos/Medien übernommen)
MERGE = {20: 18}
byn = {p["n"]: p for p in out}
for src, dst in MERGE.items():
    a, b = byn.get(src), byn.get(dst)
    if not a or not b: continue
    for k in ("note", "isFor", "moment", "wish"):
        if a.get(k) and a[k] != b.get(k): b[k] = (b[k] + ("\n\n" if k == "note" else " · ") + a[k]) if b.get(k) else a[k]
    for k in ("imgs", "clip", "video", "audio", "voice", "city", "title"):
        if a.get(k) and not b.get(k): b[k] = a[k]
    out.remove(a)
BEFORE = {}
key = lambda n: ORDER.index(n) if n in ORDER else 1000 + LAST.index(n) if n in LAST else 100 + n
out.sort(key=lambda p: key(BEFORE[p["n"]]) - 0.5 if p["n"] in BEFORE else key(p["n"]))
open("posts.js", "w").write("// Erzeugt mit tools/build_posts.py aus dem Padlet-Export\nconst friends = " +
                            json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
print(len(out), "Beiträge")
